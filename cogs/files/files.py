import discord
from discord.commands import slash_command
from discord.ext import commands, pages
from resources.components.DirectoryView import *


class Files(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='files')
    async def file_manager(self, ctx):
        view = DirectoryView(self.bot, '/', ctx)
        await ctx.respond(content='/', view=view)


def setup(bot):
    return
    bot.add_cog(Files(bot))

