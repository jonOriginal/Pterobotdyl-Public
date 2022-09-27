import discord
from discord import SlashCommandGroup
from discord.ext import commands


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        try:
            return await self.bot[str(ctx.guild.id)].check_perms(ctx)
        except KeyError:
            embed = discord.Embed(title='Use /register to use this command', color=discord.Color.dark_gold())
            await ctx.respond(embed=embed, ephemeral=True)

    group = SlashCommandGroup("backup", "Backup Commands")

    @group.command(name="create")
    async def create_backup(self, ctx):
        guild_id = str(ctx.guild.id)
        self.bot.instances[guild_id].create_backup()
        await ctx.respond('Created backup successfully.', ephemeral=True)

    @group.command(name='manage')
    async def delete_backup(self, ctx):
        guild_id = str(ctx.guild.id)
        backups = self.bot[guild_id].get_backups()
        if len(backups) == 0:
            embed = discord.Embed(title="There are no backups available.")
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.respond(f'Select Backup:', view=BackupView(backups, self.bot), ephemeral=True)


class BackupView(discord.ui.View):
    option_list = []

    def __init__(self, options, bot):
        self.bot = bot
        super().__init__(timeout=0)
        self.option_list.clear()
        for value, name in options.items():
            self.option_list.append(discord.SelectOption(label=str(name), value=str(value)))

    @discord.ui.select(
        placeholder="Select Backup:",
        # the placeholder text that will be displayed if nothing is selected
        options=option_list,
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction):
        self.option_list.clear()
        self.selected = select.values[0]
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction):
        print(self.selected)
        self.bot[str(interaction.guild_id)].delete_backup(self.selected)
        await interaction.response.send_message(f"Successfully deleted.", ephemeral=True)
        await interaction.message.delete(delay=0)

    @discord.ui.button(label="Download", style=discord.ButtonStyle.blurple)
    async def download(self, interaction: discord.Interaction):
        link = self.bot[str(interaction.guild_id)].download_backup(self.selected)
        embed = discord.Embed(title="Download Link", description=f"[Click Here]({link['attributes']['url']})")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.delete(delay=0)


def setup(bot):
    bot.add_cog(Backup(bot))
