from ...database.database import DatabaseManager, DATABASE_URL, get_database_manager
from ...database.models import Pokemon as PokemonModel
import discord
from discord.ext import commands


class Pokemon(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    pokemon_permissions = discord.Permissions(administrator=True)
    POKEMON = discord.app_commands.Group(name='pokemon', description='Pokemon related commands', default_permissions=pokemon_permissions)
        
    @POKEMON.command(name='add', description='Add a pokemon to the database')
    @discord.app_commands.choices(
        rarity = [
            discord.app_commands.Choice[int](name='Common', value=1),
            discord.app_commands.Choice[int](name='Uncommon', value=2),
            discord.app_commands.Choice[int](name='Rare', value=3),
            discord.app_commands.Choice[int](name='Super Rare', value=4),
            discord.app_commands.Choice[int](name='Legendary', value=5),
            discord.app_commands.Choice[int](name='Shiny', value=6),
            discord.app_commands.Choice[int](name='Form (Mega or Form)', value=7),
            discord.app_commands.Choice[int](name='Shiny Form (Mega or Form)', value=8),
            discord.app_commands.Choice[int](name='Gigantamax', value=9),
            discord.app_commands.Choice[int](name='Golden', value=10),
            ]
        )
    async def pokemon_add(self, interaction: discord.Interaction, dex_number: int, name: str, rarity: int, gif: str) -> None:
        database_manager = get_database_manager()
        pokemon = PokemonModel(dex_number=dex_number, name=name, rarity=rarity, gif=gif)
        await database_manager.insert(pokemon)
        
        await interaction.response.send_message(f"Pokemon {name} added to the database")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pokemon(bot))
