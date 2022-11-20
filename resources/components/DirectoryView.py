import discord
from resources.components.FileView import FileView


class UploadButton(discord.ui.Button):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def callback(self, interaction):
        path = self.view.path
        split_path = path.split('/')[:-2]
        new_path = '/'+'/'.join([x.strip() for x in split_path if x.strip()])
        self.view.path = new_path
        view = DirectoryView(self.bot, new_path, interaction)
        await interaction.response.defer()
        await self.view.message.edit(content=new_path, view=view)


class DefaultButton(discord.ui.Button):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def callback(self, interaction):
        filepath = f'{self.view.path}{self.custom_id}'
        size = self.bot[str(interaction.guild_id)].get_size(
            self.view.path, self.custom_id)
        view = FileView(self.bot, interaction, filepath, size, self.custom_id)
        embed = discord.Embed(title=f'{self.custom_id[:79]}, {size/1000}kb')
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class Dropdown(discord.ui.Select):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def callback(self, interaction):
        path = f'{self.view.path}{self.values[0]}/'
        view = DirectoryView(self.bot, path, interaction)
        await interaction.response.defer()
        await self.view.message.edit(content=path, view=view)


class DirectoryView(discord.ui.View):
    def __init__(self, bot, path, ctx, *args, **kwargs):
        super().__init__(timeout=60, *args, **kwargs)
        self.bot = bot
        self.path = path
        self.message = ctx.message
        directory = self.bot[str(ctx.guild_id)].get_files(path)
        folders = Dropdown(bot, placeholder='Folders', row=0)
        self.add_item(folders)
        for name, is_file in directory.items():
            if is_file:
                self.add_item(DefaultButton(
                    bot, label=name[:79], custom_id=name))
            elif not is_file:
                folders.add_option(label=name[:79], value=name)
        if not folders.options:
            self.remove_item(folders)

    @discord.ui.button(label='Upload', style=discord.ButtonStyle.blurple, row=1)
    async def upload(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        embed = discord.Embed(title=f"Upload to {self.path}",
                              description="Reply to this message with a file attachment. Max size: 7mb.",
                              color=discord.Color.blue()
                              )
        await self.message.edit(embed=embed)
        await interaction.response.defer()

        def check(m):
            if m.reference is not None and m.reference.message_id == self.message.id:
                if m.attachments:
                    return True
            return False

        attachment_message = await self.bot.wait_for("message", check=check, timeout=60)
        if all([x.size < 7000000 for x in attachment_message.attachments]):
            attachments_url: list = [
                attachment.url for attachment in attachment_message.attachments][0]
            upload_url: str = self.bot[interaction.guild_id].get_upload()
            self.bot[interaction.guild_id].write_file(
                attachments_url, upload_url)
        else:
            embed = discord.Embed(
                title="File sizes must be less than 7mb", color=discord.Color.red())
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label='⤴', style=discord.ButtonStyle.blurple, row=1)
    async def dir_up(self, button, interaction):
        split_path = self.path.split('/')[:-2]
        new_path = '/'+'/'.join([x.strip() for x in split_path if x.strip()])
        self.path = new_path
        view = DirectoryView(self.bot, new_path, interaction)
        await interaction.response.defer()
        await self.message.edit(content=new_path, view=view, embed=None)

    @discord.ui.button(label='🔄️', style=discord.ButtonStyle.green, row=1)
    async def refresh(self, button, interaction):
        view = DirectoryView(self.bot, self.path, interaction)
        await self.message.edit(content=self.path, view=view, embed=None)
        await interaction.response.defer()

    async def on_timeout(self):
        await self.message.delete()
