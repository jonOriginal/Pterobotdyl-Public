from discord.ui import View
import discord

class PowerView(View):
    def __init__(self, bot, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx

    def send_power(self, guild_id, action):
        self.bot.instances[str(guild_id)].send_power_action(action)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.bot[str(interaction.guild_id)].stats['state'] in ('running', 'starting'):
            await interaction.response.send_message("Server already started.", ephemeral=True)
        else:
            self.send_power(interaction.guild_id, "start")
            embed = discord.Embed(title='Server Started', color=discord.Color.green())
            await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.bot[str(interaction.guild_id)].stats['state'] == 'offline':
            await interaction.response.send_message("Server already stopped.", ephemeral=True)
        else:
            self.send_power(interaction.guild_id, "stop")
            embed = discord.Embed(title='Server Stopped', color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Restart", style=discord.ButtonStyle.blurple)
    async def restart(self, interaction: discord.Interaction):
        self.send_power(interaction.guild_id, "restart")
        embed = discord.Embed(title='Server Restarted', color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)
