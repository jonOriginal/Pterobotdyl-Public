import discord.ui

from discord.commands import slash_command
from discord.ext import commands

from resources.components.ApiView import ApiView


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @slash_command(name="register")
    async def register(self, ctx):
        guild: str = str(ctx.guild.id)
        if guild in self.bot:
            error_embed = discord.Embed(title='Already Registered', color=discord.Color.blue())
            return await ctx.respond(embed=error_embed, ephemeral=True)
        else:
            return await ctx.send_modal(modal=ApiView(bot=self.bot, title='Server Registration'))

    @commands.has_permissions(administrator=True)
    @slash_command(name="deregister")
    async def deregister(self, ctx):
        guild: str = str(ctx.guild.id)
        if guild in self.bot:
            del self.bot[guild]
            embed = discord.Embed(title='Server Deregistered', color=discord.Color.green())
            await ctx.respond(embed=embed)
        else:
            error_embed = discord.Embed(title='This server is not registered', color=discord.Color.dark_red())
            await ctx.respond(embed=error_embed)


def setup(bot):
    bot.add_cog(Registration(bot))
