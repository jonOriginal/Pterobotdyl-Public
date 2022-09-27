import discord.ui
import requests
from discord.commands import slash_command
from discord.ext import commands
import traceback


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
            return await ctx.send_modal(modal=RegisterView(bot=self.bot, title='Server Registration'))

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


class RegisterView(discord.ui.Modal):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.add_item(discord.ui.InputText(label="Server Name", required=True))
        self.add_item(discord.ui.InputText(label="Api Key", required=True))

    async def callback(self, interaction):
        server_name = self.children[0].value
        api_key = self.children[1].value
        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)
        try:
            api = self.bot.api(api_key)
            server = self.get_server(api, server_name)
            print(server)
            self.bot[guild_id] = {'guild_id': guild_id, 'channel_id': channel_id, 'server_id': server, 'api_key': api_key}
        except IndexError:
            error_embed = discord.Embed(title='Invalid server name', color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed)
        except requests.exceptions.HTTPError:
            error_embed = discord.Embed(title='Invalid api key', color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed)
        except:
            traceback.print_exc()
            error_embed = discord.Embed(title='Something went wrong.', color=discord.Color.dark_red())
            return await interaction.response.send_message(embed=error_embed)
        else:
            success_embed = discord.Embed(title='Registered Successfully', color=discord.Color.green())
            return await interaction.response.send_message(embed=success_embed)

    @staticmethod
    def get_server(api, server_name):
        server_details = api.client.servers.list_servers()
        server_list = {
            server_details[i]['attributes']['name'].lower(): server_details[i]['attributes']['identifier']
            for i, e in enumerate(server_details)}
        if server_name.lower() in server_list:
            return server_list[server_name.lower()]
        else:
            raise IndexError


def setup(bot):
    bot.add_cog(Registration(bot))
