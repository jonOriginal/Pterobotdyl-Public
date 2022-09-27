import asyncio
import re
from ast import literal_eval

import discord.errors
import requests
import websockets
from discord.ext import tasks


class Instance:
    def __init__(self, data, scope, bot):
        self.data = data
        self.api_key = self.data['api_key']
        self.server_id = self.data['server_id']
        self.guild_id = self.data['guild_id']
        self.channel_id = self.data['channel_id']

        self.bot = bot
        self.channel = scope
        self.dactyl = self.bot.api(self.api_key)

        self.stats = {}
        self.message_queue = []

        self.cogs_enabled = True
        self.pong_api.start()
        self.send_message.start()
        asyncio.ensure_future(self.init_connect())

    async def check_perms(self, ctx):
        if str(ctx.channel.id) == self.channel_id and self.cogs_enabled:
            return True
        elif not self.cogs_enabled:
            embed = discord.Embed(title='Server is unreachable, it may be suspended', color=discord.Color.dark_red())
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.respond('No perms?')
            return False

    @tasks.loop(seconds=0.1)
    async def send_message(self):
        if len(self.message_queue) == 0:
            pass
        else:
            joined = '\n'.join(self.message_queue)
            previous_message = await self.get_last_message()
            if previous_message is None or len(previous_message.content) + len(joined) >= 1500:
                self.message_queue.clear()
                await self.channel.send(f'```{joined}```')
            else:
                combined = f'{previous_message.content[0:-3]}\n{joined}```'
                self.message_queue.clear()
                await previous_message.edit(content=combined)

    @tasks.loop(seconds=5)
    async def pong_api(self):
        try:
            self.dactyl.client.servers.get_server_utilization(self.server_id, detail=False)
        except requests.HTTPError:
            if self.cogs_enabled:
                self.cogs_enabled = False
                embed = discord.Embed(title='Disconnected', color=discord.Color.red())
                await self.channel.send(embed=embed)
        else:
            if not self.cogs_enabled:
                self.cogs_enabled = True
                embed = discord.Embed(title='Connected', color=discord.Color.green())
                await self.channel.send(embed=embed)

    @tasks.loop(minutes=7.0)
    async def set_topic(self):
        cpu = self.stats["cpu_absolute"]
        status = self.stats["state"]
        memory = self.stats["memory_bytes"]

        topic = f'CPU: {cpu}% - RAM: {memory / 1000000:.2f}MB - STATUS: {status}'
        try:
            await self.channel.edit(topic=topic)
        except discord.errors.Forbidden:
            embed = discord.Embed(title='⚠️Missing manage channel permissions ⚠️', color=discord.Color.brand_red())
            await self.channel.send(embed=embed)

    async def get_last_message(self):
        message = await self.channel.fetch_message(self.channel.last_message_id)
        try:
            if message.author == self.bot.user and message.content[-1] == '`':
                return message
        except IndexError:
            return None

    async def handler(self, websocket: websockets.WebSocketClientProtocol):
        async for message in websocket:
            message = literal_eval(message)
            if message['event'] == 'console output':
                stripped = re.sub('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', message['args'][0])
                self.message_queue.append(stripped)

            if message['event'] == 'stats':
                self.stats = literal_eval(message['args'][0])
                if not self.set_topic.is_running():
                    self.set_topic.start()

            if message['event'] in ('token expiring', 'token expired'):
                print('refreshing socket')
                await websocket.close()
                asyncio.ensure_future(self.init_connect())

    async def init_connect(self):
        try:
            credentials = self.dactyl.client.servers.get_websocket(self.server_id)['data']
        except requests.exceptions.HTTPError:
            self.cogs_enabled = False
            embed = discord.Embed(title='Websocket is unreachable, your server may be suspended.',
                                  color=discord.Color.red())
            await self.channel.send(embed=embed)
        else:
            token, socket = credentials['token'], credentials['socket']
            async with websockets.connect(socket, origin=self.bot.ADDRESS) as ws:
                await ws.send('{"event":"auth","args":["' + token + '"]}')
                await self.handler(ws)

    def send_power(self, action):
        self.dactyl.client.servers.send_power_action(self.server_id, action)

    def create_backup(self):
        self.dactyl.client.servers.backups.create_backup(self.server_id)

    def delete_backup(self, backup_id):
        self.dactyl.client.servers.backups.delete_backup(self.server_id, backup_id)

    def download_backup(self, backup_id):
        return self.dactyl.client.servers.backups.get_backup_download(self.server_id, backup_id)

    def get_backups(self):
        data = self.dactyl.client.servers.backups.list_backups(self.server_id)
        api_response = literal_eval(str(data))['data']
        backups = {backup['attributes']['uuid']: backup['attributes']['name'] for backup in api_response}
        return backups

    def send_power_action(self, power):
        self.dactyl.client.servers.send_power_action(self.server_id, power)

    def send_command(self, message):
        if str(message.channel.id) == str(self.channel_id):
            self.dactyl.client.servers.send_console_command(self.server_id, message.content[1:])
