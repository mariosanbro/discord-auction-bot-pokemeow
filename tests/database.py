import pytest
import pytest_asyncio
from src.database.database import DatabaseManager, DATABASE_URL
from src.database.models import Pokemon

@pytest_asyncio.fixture
async def db_manager():
    database_manager = DatabaseManager(DATABASE_URL)
    await database_manager.create_tables()
    return database_manager
    
@pytest.mark.asyncio
async def test_insert_pokemon(db_manager):
    # Arrange
    pokemon1 = Pokemon(dex_number=1, name="Bulbasaur", rarity=1)
    pokemon2 = Pokemon(dex_number=2, name="Ivysaur", rarity=2)
    pokemon3 = Pokemon(dex_number=3, name="Venusaur", rarity=3)
    
    # Act
    result1: bool = await db_manager.insert(pokemon1)
    result2: bool = await db_manager.insert(pokemon2)
    result3: bool = await db_manager.insert(pokemon3)
    
    # Assert
    assert result1 == True
    assert result2 == True
    assert result3 == True
    
@pytest.mark.asyncio
async def test_fetch_all_pokemon(db_manager):
    # Act
    pokemons = await db_manager.fetch_all(Pokemon)
    
    # Assert
    assert len(pokemons) == 3
    assert pokemons[0].name == "Bulbasaur"
    assert pokemons[1].name == "Ivysaur"
    assert pokemons[2].name == "Venusaur"
    
@pytest.mark.asyncio
async def test_fetch_one_pokemon(db_manager):
    # Act
    pokemon = await db_manager.fetch_one(Pokemon, dex_number=2)
    
    # Assert
    assert pokemon.name == "Ivysaur"
    
@pytest.mark.asyncio
async def test_update_pokemon(db_manager):
    # Arrange
    where = {"dex_number": 2}
    kwargs = {"name": "Ivysaur (Updated)"}
    
    # Act
    result = await db_manager.update(Pokemon, where=where, **kwargs)
    
    # Assert
    assert result == True
    
@pytest.mark.asyncio
async def test_delete_pokemon(db_manager):
    # Act
    result = await db_manager.delete(Pokemon, dex_number=2)
    
    # Assert
    assert result == True
    
@pytest.mark.asyncio
async def test_drop_tables(db_manager):
    # Act
    result = await db_manager.drop_tables()
    
    # Assert
    assert result == True
