import asyncio
import colorama
import discord
import dotenv
import os
import time
from discord.ext import commands
from ..database.database import DatabaseManager, DATABASE_URL

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_MANAGER = DatabaseManager(DATABASE_URL)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='discord-auction-bot', intents=intents) # Prefix will not be used in this bot (only app commands)
tree = bot.tree

extensions_folder = 'src.bot.extensions.'
extensions = ['auction', 'pokemon', 'setup']

async def main():
    if __name__ == "__main__":
        await DATABASE_MANAGER.create_tables()
        for extension in extensions:
            try:
                await bot.load_extension(extensions_folder + extension)
            except Exception as e:
                print(colorama.Fore.RED + colorama.Style.BRIGHT + f"  EXTENSIONS ERROR | {extension} | {e}" + colorama.Style.RESET_ALL)
                time.sleep(30)
asyncio.run(main())

TITLE = r"""
 _____   __  ______  ______  ______  ______  _____       ______  __  __  ______  ______ __  ______  __   __       ______  ______  ______  
/\  __-./\ \/\  ___\/\  ___\/\  __ \/\  == \/\  __-.    /\  __ \/\ \/\ \/\  ___\/\__  _/\ \/\  __ \/\ "-.\ \     /\  == \/\  __ \/\__  _\ 
\ \ \/\ \ \ \ \___  \ \ \___\ \ \/\ \ \  __<\ \ \/\ \   \ \  __ \ \ \_\ \ \ \___\/_/\ \\ \ \ \ \/\ \ \ \-.  \    \ \  __<\ \ \/\ \/_/\ \/ 
 \ \____-\ \_\/\_____\ \_____\ \_____\ \_\ \_\ \____-    \ \_\ \_\ \_____\ \_____\ \ \_\\ \_\ \_____\ \_\\"\_\    \ \_____\ \_____\ \ \_\ 
  \/____/ \/_/\/_____/\/_____/\/_____/\/_/ /_/\/____/     \/_/\/_/\/_____/\/_____/  \/_/ \/_/\/_____/\/_/ \/_/     \/_____/\/_____/  \/_/ 
                                                                                                                                          
"""
MADEBY = "Made by Dragice"

def clear():
    if os.name in ('nt', 'dos'):
        os.system('cls')
    elif os.name in ('linux', 'osx', 'posix'):
        os.system('clear')
    else:
        print("\n" * 100)
        
def project():
    PROJECT = colorama.Style.RESET_ALL + colorama.Fore.CYAN + colorama.Style.BRIGHT + TITLE + colorama.Style.RESET_ALL + "\n"
    MADEBY = colorama.Fore.LIGHTGREEN_EX + colorama.Style.BRIGHT + "Made by Dragice" + colorama.Style.RESET_ALL + "\n"
    print(PROJECT + MADEBY)
    
@bot.event
async def setup_hook():
    clear()
    project()
    await tree.sync()

bot.run(token=TOKEN, reconnect=True)
