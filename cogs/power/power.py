import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ui import View


class Power(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        try:
            return await self.bot[str(ctx.guild.id)].check_perms(ctx)
        except KeyError:
            embed = discord.Embed(title='Use /register to use this command', color=discord.Color.dark_gold())
            await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="power")
    async def power(self, ctx):
        guild_id = str(ctx.guild.id)
        status = self.bot.instances[guild_id].stats['state']
        if status == "running":
            color = discord.Color.green()
        elif status == 'offline':
            color = discord.Color.red()
        elif status == 'starting':
            color = discord.Color.gold()
        else:
            color = discord.Color.blurple()
        embed = discord.Embed(title=f'Server is currently {status}', color=color)
        await ctx.respond(f'power options:', embed=embed, view=PowerView(self.bot, ctx), delete_after=20,
                          ephemeral=True)


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


def setup(bot):
    bot.add_cog(Power(bot))
