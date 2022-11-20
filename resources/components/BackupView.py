import discord


class BackupView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        self.selected = None
        super().__init__(timeout=20)

    @discord.ui.select(
        placeholder="Select Backup:",
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction):
        self.selected = select.values[0]
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction):
        print(self.selected)
        self.bot[str(interaction.guild_id)].delete_backup(self.selected)
        await interaction.response.send_message(f"Successfully deleted.", ephemeral=True)
        await interaction.message.delete(delay=0)

    @discord.ui.button(label="Download", style=discord.ButtonStyle.blurple)
    async def download(self, interaction: discord.Interaction):
        link = self.bot[str(interaction.guild_id)].download_backup(self.selected)
        embed = discord.Embed(title="Download Link", description=f"[Click Here]({link['attributes']['url']})")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.message.delete(delay=0)

    async def on_timeout(self):
        await self.message.delete()
