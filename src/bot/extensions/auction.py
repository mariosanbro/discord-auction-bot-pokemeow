from ...database.database import get_database_manager
import discord
from discord.ext import commands


class Auction(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.database_manager = get_database_manager()
        
    @discord.app_commands.command(name="auction", description="Start an auction")
    async def auction(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Auction started")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Auction(bot))
