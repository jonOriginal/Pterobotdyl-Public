import discord


class SelectView(discord.ui.View):

    def __init__(self, bot, api_key):
        super().__init__()
        self.bot = bot
        self.api_key = api_key

    @discord.ui.select(
        placeholder="Select Server:",
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction):
        server = str(select.values[0])
        api_key = self.api_key
        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)

        self.bot[guild_id] = {'guild_id': guild_id, 'channel_id': channel_id, 'server_id': server, 'api_key': api_key}
        embed = discord.Embed(title='Successfully registered', color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
