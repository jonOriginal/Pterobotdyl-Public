import requests
import traceback
from resources.components.SelectView import SelectView
import discord


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

            select_server_view = SelectView(self.bot, api_key)

            for value, name in server_dict.items():
                dropdown = select_server_view.children[0]
                dropdown.add_option(label=str(name), value=str(value))

            await interaction.response.send_message('Select server:', view=select_server_view, ephemeral=True)

        except requests.exceptions.HTTPError:
            error_embed = discord.Embed(
                title='Invalid api key', color=discord.Color.red())
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)

        except:
            traceback.print_exc()
            error_embed = discord.Embed(
                title='Something went wrong.', color=discord.Color.dark_red())
            return await interaction.response.send_message(embed=error_embed)
