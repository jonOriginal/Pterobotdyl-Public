import discord
from discord.commands import slash_command
from discord.ext import commands
from resources.components.PowerView import PowerView


class Power(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="power")
    async def power(self, ctx):
        if not await self.bot[ctx.guild.id].check_perms(ctx):
            return

        guild_id = str(ctx.guild.id)
        status = self.bot.instances[guild_id].stats['state']
        if status == "running":
            color = discord.Color.green()
        elif status == 'offline':
            color = discord.Color.red()
        elif status == 'starting':
            color = discord.Color.gold()
        else:
            color = discord.Color.blurple()

        embed = discord.Embed(title=f'Server is currently {status}', color=color)
        await ctx.respond(f'power options:', embed=embed, view=PowerView(self.bot, ctx), delete_after=20,
                          ephemeral=True)


def setup(bot):
    bot.add_cog(Power(bot))
