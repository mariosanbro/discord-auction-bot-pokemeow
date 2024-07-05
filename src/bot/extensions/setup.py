import discord
import json
from configuration.configuration import load_config, save_config
from discord.ext import commands


NUMBER_EMOJIS: int = 13

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = load_config()

    @discord.app_commands.command(name='setup', description='Setup the bot (it will add custom emojis and roles to the server)')
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.describe(
        reputation = 'Do you want to setup the reputation system? (This will set up some custom roles for the reputation system, this can be toggled on/off later) | WIP',
        auctions = 'The category where the auctions will be created (This can be changed later)',
        auction_info = 'The category where everything related to the auctions will be stored (This can be changed later)',
        trading = 'The category where the trading channels will be created (This can be changed later) | WIP'
    )
    @discord.app_commands.choices(
        reputation = [
            discord.app_commands.Choice[int](name='Yes', value=1),
            discord.app_commands.Choice[int](name='No', value=0)
        ]
    )
    async def setup(self, interaction: discord.Interaction, reputation: int, auctions: discord.CategoryChannel, auction_info: discord.CategoryChannel, trading: discord.CategoryChannel) -> None:
        """
        Sets up the bot by adding custom emojis and roles to the server, selecting categories and creating channels for auctions and trading, and optionally setting up the reputation system.

        Example Usage:
        /setup reputation:1 auctions:#auctions-category auction_info:#auction-info-category trading:#trading-category
        """
        common_emoji_uri: str = './res/emojis/common.png'
        uncommon_emoji_uri: str = './res/emojis/uncommon.png'
        rare_emoji_uri: str = './res/emojis/rare.png'
        super_rare_emoji_uri: str = './res/emojis/superrare.png'
        legendary_emoji_uri: str = './res/emojis/legendary.png'
        shiny_emoji_uri: str = './res/emojis/shiny.png'
        form_emoji_uri: str = './res/emojis/form.png'
        shiny_form_emoji_uri: str = './res/emojis/shinyform.png'
        gigantamax_emoji_uri: str = './res/emojis/gigantamax.png'
        shiny_gigantamax_emoji_uri: str = './res/emojis/shinygigantamax.png'
        golden_emoji_uri: str = './res/emojis/golden.png'
        pokecoins_emoji_uri: str = './res/emojis/pokecoins.png'
        patreon_tokens_emoji_uri: str = './res/emojis/patreontokens.png'
        emoji_list: list[bytes] = []
        emoji_dict: dict[str, str] = {}
        with open(common_emoji_uri, 'rb') as common_emoji:
            common_emoji_bytes = common_emoji.read()
            emoji_list.append(common_emoji_bytes)
        with open(uncommon_emoji_uri, 'rb') as uncommon_emoji:
            uncommon_emoji_bytes = uncommon_emoji.read()
            emoji_list.append(uncommon_emoji_bytes)
        with open(rare_emoji_uri, 'rb') as rare_emoji:
            rare_emoji_bytes = rare_emoji.read()
            emoji_list.append(rare_emoji_bytes)
        with open(super_rare_emoji_uri, 'rb') as super_rare_emoji:
            super_rare_emoji_bytes = super_rare_emoji.read()
            emoji_list.append(super_rare_emoji_bytes)
        with open(legendary_emoji_uri, 'rb') as legendary_emoji:
            legendary_emoji_bytes = legendary_emoji.read()
            emoji_list.append(legendary_emoji_bytes)
        with open(shiny_emoji_uri, 'rb') as shiny_emoji:
            shiny_emoji_bytes = shiny_emoji.read()
            emoji_list.append(shiny_emoji_bytes)
        with open(form_emoji_uri, 'rb') as form_emoji:
            form_emoji_bytes = form_emoji.read()
            emoji_list.append(form_emoji_bytes)
        with open(shiny_form_emoji_uri, 'rb') as shiny_form_emoji:
            shiny_form_emoji_bytes = shiny_form_emoji.read()
            emoji_list.append(shiny_form_emoji_bytes)
        with open(gigantamax_emoji_uri, 'rb') as gigantamax_emoji:
            gigantamax_emoji_bytes = gigantamax_emoji.read()
            emoji_list.append(gigantamax_emoji_bytes)
        with open(shiny_gigantamax_emoji_uri, 'rb') as shiny_gigantamax_emoji:
            shiny_gigantamax_emoji_bytes = shiny_gigantamax_emoji.read()
            emoji_list.append(shiny_gigantamax_emoji_bytes)
        with open(golden_emoji_uri, 'rb') as golden_emoji:
            golden_emoji_bytes = golden_emoji.read()
            emoji_list.append(golden_emoji_bytes)
        with open(pokecoins_emoji_uri, 'rb') as pokecoins_emoji:
            pokecoins_emoji_bytes = pokecoins_emoji.read()
            emoji_list.append(pokecoins_emoji_bytes)
        with open(patreon_tokens_emoji_uri, 'rb') as patreon_tokens_emoji:
            patreon_tokens_emoji_bytes = patreon_tokens_emoji.read()
            emoji_list.append(patreon_tokens_emoji_bytes)
        
        await interaction.response.send_message("Setting up the bot...")
        guild: discord.Guild = interaction.guild
        
        # Check if there are enough emoji slots available
        if guild.emoji_limit < sum([1 for e in guild.emojis if not e.animated]) + NUMBER_EMOJIS:
            await interaction.edit_original_response(content="Not enough emoji slots available, please free up some slots and try again")
            return
        
        # Add custom emojis
        for emoji_bytes in emoji_list:
            match emoji_list.index(emoji_bytes):
                case 0:
                    emoji_name = 'common'
                case 1:
                    emoji_name = 'uncommon'
                case 2:
                    emoji_name = 'rare'
                case 3:
                    emoji_name = 'superrare'
                case 4:
                    emoji_name = 'legendary'
                case 5:
                    emoji_name = 'shiny'
                case 6:
                    emoji_name = 'form'
                case 7:
                    emoji_name = 'shinyform'
                case 8:
                    emoji_name = 'gigantamax'
                case 9:
                    emoji_name = 'shinygigantamax'
                case 10:
                    emoji_name = 'golden'
                case 11:
                    emoji_name = 'pokecoins'
                case 12:
                    emoji_name = 'patreontokens'
                case _:
                    emoji_name = 'unknown'
            emoji: discord.Emoji = await guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
            emoji_string: str = f'<:{emoji_name}:{emoji.id}>'
            emoji_dict[emoji_name] = emoji_string
            
        # Save custom emojis and auctions categories in config file
        self.config['emojis'] = emoji_dict
        self.config['auctions_category'] = auctions.id
        self.config['auction_info_category'] = auction_info.id
        self.config['trading_category'] = trading.id
        
        # Create channels in auction info category (will be able to change the name from channels later)
        ongoing_channel: discord.TextChannel = await guild.create_text_channel('ongoing-auctions', category=auction_info)
        completed_channel: discord.TextChannel = await guild.create_text_channel('completed-auctions', category=auction_info)
        self.config['ongoing_channel'] = ongoing_channel.id
        self.config['completed_channel'] = completed_channel.id
        
        # Save and load config file
        save_config(self.config)
        self.config = load_config()

        # Add custom roles
        # TODO: This will be a future feature (reputation system with roles, this will be able to be toggled on/off) | WIP
        await interaction.edit_original_response(content="Bot setup complete!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
