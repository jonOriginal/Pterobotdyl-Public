import discord
from discord import SlashCommandGroup
from discord.ext import commands
from resources.components.BackupView import BackupView


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("backup", "Backup Commands")

    @group.command(name="create")
    async def create_backup(self, ctx):
        guild_id = str(ctx.guild.id)
        self.bot[guild_id].create_backup()
        await ctx.respond('Created backup successfully.', ephemeral=True)

    @group.command(name='manage')
    async def delete_backup(self, ctx):
        guild_id = str(ctx.guild.id)
        backups = self.bot[guild_id].get_backups()
        if len(backups) == 0:
            embed = discord.Embed(title="There are no backups available.")
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            select_backup_view = BackupView(self.bot)
            backup_dropdown = select_backup_view.children[0]
            for value, name in backups.items():
                backup_dropdown.add_option(label=str(name), value=str(value))
            await ctx.respond(f'Select Backup:', view=select_backup_view)


def setup(bot):
    bot.add_cog(Backup(bot))
