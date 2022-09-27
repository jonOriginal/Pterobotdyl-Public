import traceback

import discord.ui
import requests
from discord.commands import slash_command
from discord.ext import commands


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @slash_command(name="register")
    async def register(self, ctx):
        guild = str(ctx.guild.id)
        if guild in self.bot:
            error_embed = discord.Embed(title='Already Registered', color=discord.Color.blue())
            return await ctx.respond(embed=error_embed, ephemeral=True)
        else:
            return await ctx.send_modal(modal=ApiView(bot=self.bot, title='Server Registration'))

    @commands.has_permissions(administrator=True)
    @slash_command(name="deregister")
    async def deregister(self, ctx):
        guild = str(ctx.guild.id)
        if guild in self.bot:
            del self.bot[guild]
            embed = discord.Embed(title='Server Deregistered', color=discord.Color.green())
            await ctx.respond(embed=embed)
        else:
            error_embed = discord.Embed(title='This server is not registered', color=discord.Color.dark_red())
            await ctx.respond(embed=error_embed)


class ApiView(discord.ui.Modal):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.add_item(discord.ui.InputText(label="Api Key", required=True))

    async def callback(self, interaction):
        api_key = self.children[0].value
        try:
            api = self.bot.api(api_key)
            servers = api.client.servers.list_servers()
            server_dict = {server[i]['attributes']['identifier']: server[i]['attributes']['name'] for i, server in
                           enumerate(servers)}
            await interaction.response.send_message('Select server:', view=SelectView(server_dict, self.bot, api_key),
                                                    ephemeral=True)
        except requests.exceptions.HTTPError:
            error_embed = discord.Embed(title='Invalid api key', color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except:
            traceback.print_exc()
            error_embed = discord.Embed(title='Something went wrong.', color=discord.Color.dark_red())
            return await interaction.response.send_message(embed=error_embed)


class SelectView(discord.ui.View):
    servers = []

    def __init__(self, servers, bot, api_key):
        super().__init__()
        self.bot = bot
        self.api_key = api_key
        for value, name in servers.items():
            self.servers.append(discord.SelectOption(label=str(name), value=str(value)))

    @discord.ui.select(
        placeholder="Select Server:",
        # the placeholder text that will be displayed if nothing is selected
        options=servers,
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction):
        self.servers.clear()
        server = str(select.values[0])
        api_key = self.api_key
        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)

        self.bot[guild_id] = {'guild_id': guild_id, 'channel_id': channel_id, 'server_id': server, 'api_key': api_key}
        embed = discord.Embed(title='Successfully registered', color=discord.Color.green())
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Registration(bot))
