import asyncio
import os
import re
from ast import literal_eval

import aiofiles
import aiohttp
import discord.errors
import requests
import datetime
import websockets
from discord.ext import tasks

import tempfile


class Instance:
    def __init__(self, data, scope, bot):
        self.data = data
        self.api_key = self.data['api_key']
        self.server_id = self.data['server_id']
        self.guild_id = self.data['guild_id']
        self.channel_id = self.data['channel_id']

        self.bot = bot
        self.channel = scope

        self.stats = {}
        self.message_queue = []

        self.dactyl = None
        self.active = False
        self.console = False
        self.pong_api.start()
        self.console_pong.start()
        self.send_message.start()
        self.connection = None

    async def check_perms(self, ctx):
        if str(ctx.channel.id) == self.channel_id and self.active:
            return True
        elif not self.active:
            embed = discord.Embed(
                title='Server is unreachable, it may be suspended', color=discord.Color.dark_red())
            await ctx.respond(embed=embed, ephemeral=True)
            return False
        else:
            await ctx.respond('No perms?')
            return False

    @tasks.loop(seconds=0.2)
    async def send_message(self):
        if len(self.message_queue) == 0:
            return
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
            current_time = datetime.datetime.now()
            self.dactyl = self.bot.api(self.api_key)
            self.dactyl.client.servers.get_server_utilization(
                self.server_id, detail=False)
        except requests.HTTPError as e:
            status_code = e.response.status_code
            if status_code != 401:
                print(e)
            elif self.active:
                self.active = False
                print("disconnected " + current_time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            if not self.active:
                self.active = True
                print("connected " + current_time.strftime("%Y-%m-%d %H:%M:%S"))

    @tasks.loop(seconds=5)
    async def console_pong(self):
        if not self.console:
            try:
                self.connection = asyncio.ensure_future(self.init_connect())
                self.console = True
            except Exception as e:
                print(e)
                self.connection = None
                self.console = False

    @tasks.loop(minutes=7.0)
    async def set_topic(self):
        cpu = self.stats["cpu_absolute"]
        status = self.stats["state"]
        memory = self.stats["memory_bytes"]

        topic = f'CPU: {cpu}% - RAM: {memory / 1000000:.2f}MB - STATUS: {status}'
        try:
            await self.channel.edit(topic=topic)
        except discord.errors.Forbidden:
            embed = discord.Embed(
                title='⚠️Missing manage channel permissions ⚠️', color=discord.Color.brand_red())
            await self.channel.send(embed=embed)

    async def get_last_message(self):
        message = await self.channel.fetch_message(self.channel.last_message_id)
        try:
            if message.author == self.bot.user and message.content[-1] == '`':
                return message
        except IndexError:
            return None

    async def message_handler(self, websocket: websockets.WebSocketClientProtocol):
        async for message in websocket:
            message = literal_eval(message)
            if message['event'] == 'console output':
                stripped = re.sub(
                    '(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]', '', message['args'][0])
                self.message_queue.append(stripped)

            if message['event'] == 'stats':
                self.stats = literal_eval(message['args'][0])
                if not self.set_topic.is_running():
                    self.set_topic.start()

            if message['event'] in ('token expiring', 'token expired'):
                print('refreshing socket')
                await websocket.close()
                self.connection.cancel()
                self.connection = asyncio.ensure_future(self.init_connect())

    async def init_connect(self):
        credentials = self.dactyl.client.servers.get_websocket(self.server_id)[
            'data']
        token, socket = credentials['token'], credentials['socket']
        async with websockets.connect(socket, origin=self.bot.ADDRESS) as ws:
            await ws.send('{"event":"auth","args":["' + token + '"]}')
            await self.message_handler(ws)

    def send_power(self, action):
        self.dactyl.client.servers.send_power_action(self.server_id, action)

    def create_backup(self):
        self.dactyl.client.servers.backups.create_backup(self.server_id)

    def delete_backup(self, backup_id):
        self.dactyl.client.servers.backups.delete_backup(
            self.server_id, backup_id)

    def download_backup(self, backup_id):
        return self.dactyl.client.servers.backups.get_backup_download(self.server_id, backup_id)

    def get_backups(self):
        data = self.dactyl.client.servers.backups.list_backups(self.server_id)
        api_response = literal_eval(str(data))['data']
        backups = {backup['attributes']['uuid']                   : backup['attributes']['name'] for backup in api_response}
        return backups

    def send_power_action(self, power):
        self.dactyl.client.servers.send_power_action(self.server_id, power)

    def send_command(self, message):
        if not self.active:
            return
        elif str(message.channel.id) == str(self.channel_id):
            self.dactyl.client.servers.send_console_command(
                self.server_id, message.content[1:])

    def get_files(self, path=None):
        data = self.dactyl.client.servers.files.list_files(self.server_id, path)[
            'data']
        directory = {file['attributes']['name']                     : file['attributes']['is_file'] for file in data}
        return directory

    def get_size(self, path, file):
        data = self.dactyl.client.servers.files.list_files(self.server_id, path)[
            'data']
        size = list(filter(lambda x: (x['attributes']['name'] == file), data))[
            0]['attributes']['size']
        return size

    def delete_file(self, filepath):
        split_filepath = filepath.split('/')
        file = split_filepath[-1]
        path = '/' + '/'.join(split_filepath[:-1])
        self.dactyl.client.servers.files.delete_files(
            self.server_id, [file], path)

    def file_contents(self, path):
        return self.dactyl.client.servers.files.get_file_contents(self.server_id, path)

    def get_file_download(self, filepath):
        return self.dactyl.client.servers.files.download_file(self.server_id, filepath)

    def get_upload(self):
        content = self.dactyl.client.servers.files.get_upload_file_url(
            self.server_id)
        return content

    def write_file(self, file_url, upload_url):
        sema = asyncio.BoundedSemaphore(5)

        async def fetch_file(url):
            temp_dir = tempfile.TemporaryDirectory()
            fname = file_url.split("/")[-1]

            async with sema, aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    assert resp.status == 200
                    data = await resp.read()

            async with aiofiles.open(os.path.join(temp_dir.name, fname), "wb") as outfile:
                await outfile.write(data)

            with open(os.path.join(temp_dir.name, fname), "rb") as f:
                r = requests.post(upload_url, f)
                print(r)

            temp_dir.cleanup()

        loop = asyncio.get_event_loop()
        task = loop.create_task(fetch_file(file_url))
        asyncio.ensure_future(task)
