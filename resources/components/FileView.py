import discord
from discord.ext import pages


class FileView(discord.ui.View):
    def __init__(self, bot, ctx, filepath, size, custom_id, *args, **kwargs):
        super().__init__(timeout=30, *args, **kwargs)
        self.bot = bot
        self.filepath = filepath
        self.custom_id = custom_id
        self.size = size
        self.confirmation = 0
        if size > 100000:
            self.children[1].disabled = True

    @discord.ui.button(label='Download')
    async def download(self, button, interaction):
        link = self.bot[str(interaction.guild_id)].get_file_download(self.filepath)

        embed = discord.Embed(title="Download Link", description=f"[{self.custom_id}]({link})")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label='Upload')
    async def download(self, button, interaction):
        link = self.bot[str(interaction.guild_id)].get_file_download(self.filepath)

        embed = discord.Embed(title="Download Link", description=f"[{self.custom_id}]({link})")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label='View')
    async def view(self, button, interaction):
        # get file contents from the current path + the file name clicked
        data = self.bot[str(interaction.guild.id)].file_contents(f'{self.filepath}')

        # for some reason all newlines do not work, so this fixes them as well as removing some unnecessary characters
        string = str(data.content).replace('\\n', '\n')[2:-1]

        # splits the string into lengths of 1990 character so discord can handle it, also adds code markdown characters
        paragraphs = [f'```{string[i:i + 1990]}```' for i in range(0, len(string), 1990)]

        # send paginator
        paginator = pages.Paginator(pages=paragraphs, show_menu=False)
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(interaction, ephemeral=True)

    @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
    async def delete(self, button, interaction):
        if self.confirmation == 0:
            self.confirmation = 1
            embed = discord.Embed(title=f'{self.custom_id[:79]},{self.size/1000}kb', description='Push again to confirm')

        elif self.confirmation == 1:
            self.bot[str(interaction.guild_id)].delete_file(self.filepath)
            embed = discord.Embed(title=f'{self.custom_id[:79]},{self.size / 1000}kb', description='File deleted', color=discord.Color.red())
            self.disable_all_items()

        await self.message.edit(embed=embed, view=self)
        await interaction.response.defer()

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(content=self.filepath, view=self)
