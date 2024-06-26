import discord
import json
from discord.ext import commands


NUMBER_EMOJIS = 10

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(name='setup', description='Setup the bot (it will add custom emojis and roles to the server)')
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.describe(
        reputation = 'Do you want to setup the reputation system? (This will set up some custom roles for the reputation system, this can be toggled on/off later)'
    )
    @discord.app_commands.choices(
        reputation = [
            discord.app_commands.Choice[int](name='Yes', value=1),
            discord.app_commands.Choice[int](name='No', value=0)
        ]
    )
    async def setup(self, interaction: discord.Interaction, reputation: int) -> None:
        common_emoji_uri: str = './res/emojis/common.png'
        uncommon_emoji_uri: str = './res/emojis/uncommon.png'
        rare_emoji_uri: str = './res/emojis/rare.png'
        super_rare_emoji_uri: str = './res/emojis/superrare.png'
        legendary_emoji_uri: str = './res/emojis/legendary.png'
        shiny_emoji_uri: str = './res/emojis/shiny.png'
        form_emoji_uri: str = './res/emojis/form.png'
        shiny_form_emoji_uri: str = './res/emojis/shinyform.png'
        gigantamax_emoji_uri: str = './res/emojis/gigantamax.png'
        golden_emoji_uri: str = './res/emojis/golden.png'
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
        with open(golden_emoji_uri, 'rb') as golden_emoji:
            golden_emoji_bytes = golden_emoji.read()
            emoji_list.append(golden_emoji_bytes)
        
        await interaction.response.send_message("Setting up the bot...")
        guild: discord.Guild = interaction.guild
        
        # Check if there are enough emoji slots available
        if guild.emoji_limit < len(guild.emojis) + NUMBER_EMOJIS:
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
                    emoji_name = 'golden'
                case _:
                    emoji_name = 'unknown'
            emoji: discord.Emoji = await guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
            emoji_string: str = f'<:{emoji_name}:{emoji.id}>'
            emoji_dict[emoji_name] = emoji_string
            
        # Save custom emojis in configuration file
        with open('./configuration/configuration.json', 'r') as config_file:
            config: dict = json.load(config_file)
            config['emojis'] = emoji_dict
        with open('./configuration/configuration.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

        # Add custom roles
        # TODO: This will be a future feature (reputation system with roles, this will be able to be toggled on/off)
        await interaction.edit_original_response(content="Bot setup complete!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
