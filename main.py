import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from resources.api import Api
from resources.database import Database
from resources.instance import Instance

load_dotenv()

intents = discord.Intents.all()
TOKEN = os.environ['DISCORD_TOKEN']


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ADDRESS = os.environ['ADDRESS']
        self.db = Database(os.environ["DB_PATH"])
        self.api = Api(self.ADDRESS)
        self.instances = {}

    def __getitem__(self, item):
        return self.instances[item]

    def __setitem__(self, guild_id, data):
        channel_id = data["channel_id"]
        server_id = data["server_id"]
        api_key = data["api_key"]

        assigned_channel = self.get_channel(int(channel_id))
        self.instances[guild_id] = Instance(data, assigned_channel, self)
        self.db[guild_id] = {'channel': channel_id, 'server_id': server_id, 'api_key': api_key}

    def __delitem__(self, key):
        del self.instances[key]
        del self.db[key]

    def __contains__(self, item):
        if item in self.instances:
            return True
        else:
            return False

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            guild_id = str(guild.id)
            if guild_id in self.db:
                data = self.db[guild_id]
                self[guild_id] = data

    async def on_application_command_error(self, ctx, error):
        if isinstance(error, discord.errors.CheckFailure):
            pass
        elif isinstance(error, discord.errors.ApplicationCommandInvokeError):
            print(error)
            self[str(ctx.guild.id)].cogs_enabled = False
            await ctx.respond('Server may be removed or suspended. Run /reconnect to check again.', ephemeral=True)
        else:
            print(type(error))
            print(error)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if str(message.guild.id) in self.instances and message.content[0] == '/':
            self.instances[str(message.guild.id)].send_command(message)


def main():
    bot = Bot(command_prefix='$', intents=intents)
    for folder_name in os.listdir('./cogs'):  # for every folder in cogs
        for filename in os.listdir(f'./cogs/{folder_name}'):  # for every file in a folder in cogs
            if filename.endswith('.py'):  # if the file is a python file and if the file is a cog
                bot.load_extension(f'cogs.{folder_name}.{filename[:-3]}')  # load the extension
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
