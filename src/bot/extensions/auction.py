from discord.utils import MISSING
from ...database.database import get_database_manager
from ...database.models import Auction as AuctionModel
from ...database.models import Pokemon as PokemonModel
from configuration.configuration import load_config
from configuration.utils import hex_to_int, rarity_to_string, rarity_to_formatted_string
import asyncio
import datetime
import discord
from discord.ext import commands, tasks


CONTENT_AUCTION_MESSAGE: str = "- Roles to ping | WIP\n> Please use the buttons below to bid on the auction!\n\n- **Remember, you must own what you are bidding!**"
BUNDLE_IMAGE: str = 'https://cdn.discordapp.com/attachments/1256251099858337846/1257322212705439775/bundle.png?ex=6683fc0f&is=6682aa8f&hm=f968feee9546b5bd636f6f96ffbfeee69036cb69f954ac739d04da585a260025&'

def auction_embed_builder(interaction: discord.Interaction, auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str) -> discord.Embed:
    current_bid: int = auction.current_bid if auction.current_bid is not None else 0
    autobuy: int | str = auction.auto_buy if auction.auto_buy is not None else 'None'
    if isinstance(autobuy, int):
        autobuy = f'{autobuy:,}'
    if not auction.bundle:
        pokemon: PokemonModel = auction.pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} {pokemon.name} | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**\n- Dex Number: **{pokemon.dex_number}**",
            color=embed_color
        )
        embed.add_field(name="Current Bid", value=f"{pokecoins_emoji} {current_bid:,}")
        embed.add_field(name="Bidder", value=f"{interaction.guild.get_member(auction.bidder_id).mention if auction.bidder_id != None else 'None'}")
        embed.add_field(name="Auto Buy", value=f"{pokecoins_emoji} {autobuy}")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="End Time", value=f"<t:{auction.end_time}:R>")
        embed.add_field(name="Auction Host", value=f"{interaction.guild.get_member(auction.user_id).mention if auction.user_id != None else 'None'}")
        embed.set_image(url=pokemon.gif)
    else:
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} Bundle | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**",
            color=embed_color
        )
        embed.add_field(name="Current Bid", value=f"{pokecoins_emoji} {current_bid:,}")
        embed.add_field(name="Bidder", value=f"{interaction.guild.get_member(auction.bidder_id).mention if auction.bidder_id != None else 'None'}")
        embed.add_field(name="Auto Buy", value=f"{pokecoins_emoji} {autobuy}")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="End Time", value=f"<t:{auction.end_time}:R>")
        embed.add_field(name="Auction Host", value=f"{interaction.guild.get_member(auction.user_id).mention if auction.user_id != None else 'None'}")
        embed.set_image(url=BUNDLE_IMAGE)
    return embed

def ended_auction_embed_builder(auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, bot: commands.Bot | None = None, interaction: discord.Interaction | None = None) -> discord.Embed:
    bot_or_interaction_guild: commands.Bot | discord.Interaction = bot if bot is not None else interaction.guild
    if auction.bidder_id is not None:
        bidder: discord.User | discord.Member = bot_or_interaction_guild.get_user(auction.bidder_id) if isinstance(bot_or_interaction_guild, commands.Bot) else bot_or_interaction_guild.get_member(auction.bidder_id)
    else:
        bidder = None
    if not auction.bundle:
        pokemon: PokemonModel = auction.pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} {pokemon.name} | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**\n- Dex Number: **{pokemon.dex_number}**",
            color=embed_color
        )
        embed.add_field(name="Final Bid", value=f"{pokecoins_emoji} {auction.current_bid:,}")
        embed.add_field(name="Bidder", value=f"{bidder.mention if bidder is not None else 'None'}")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="Auction Ended", value=f"<t:{auction.end_time}:R>")
        user: discord.User | discord.Member = bot_or_interaction_guild.get_user(auction.user_id) if isinstance(bot_or_interaction_guild, commands.Bot) else bot_or_interaction_guild.get_member(auction.user_id)
        embed.add_field(name="Auction Host", value=f"{user.mention if user is not None else 'None'}")
        embed.set_image(url=pokemon.gif)
    else:
        pokemon: PokemonModel = auction.pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} Bundle | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**",
            color=embed_color
        )
        embed.add_field(name="Final Bid", value=f"{pokecoins_emoji} {auction.current_bid:,}")
        embed.add_field(name="Bidder", value=f"{bidder.mention if bidder is not None else 'None'}")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="Auction Ended", value=f"<t:{auction.end_time}:R>")
        user: discord.User | discord.Member = bot_or_interaction_guild.get_user(auction.user_id) if isinstance(bot_or_interaction_guild, commands.Bot) else bot_or_interaction_guild.get_member(auction.user_id)
        embed.add_field(name="Auction Host", value=f"{user.mention if user is not None else 'None'}")
        embed.set_image(url=BUNDLE_IMAGE)
    return embed

def new_auction_embed_builder(auction: AuctionModel, embed_color: int, formatted_rarity: str, user: discord.User, channel: discord.TextChannel) -> discord.Embed:
    if not auction.bundle:
        pokemon: PokemonModel = auction.pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=":wrench: | New Auction Started!",
            description=f"{user.mention} has started an auction for Pokemon {pokemon.name}\n**Dex Number:** {pokemon.dex_number}\n**Name:** {pokemon.name}\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: {':white_check_mark:' if auction.bundle else ':x:'}\n - Accepted Pokemon: {':white_check_mark:' if auction.accepted else ':x:'}\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n**Channel:** {channel.mention}",
            color=embed_color
        )
        embed.set_image(url=pokemon.gif)
    else:
        embed: discord.Embed = discord.Embed(
            title=":wrench: | New Auction Started!",
            description=f"{user.mention} has started an auction for a Bundle\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: {':white_check_mark:' if auction.bundle else ':x:'}\n - Accepted Pokemon: {':white_check_mark:' if auction.accepted else ':x:'}\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n**Channel:** {channel.mention}",
            color=embed_color
        )
        embed.set_image(url=BUNDLE_IMAGE)
    return embed

def confirmed_embed_builder(pokemon: list[PokemonModel], auction: AuctionModel, embed_color: int, formatted_rarity: str, bundle: bool, accepted: bool) -> discord.Embed:
    if not bundle:
        pokemon: PokemonModel = pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=":wrench: | Confirm Auction",
            description=f"Are you sure you want to start an auction for Pokemon {pokemon.name}?\n**Dex Number:** {pokemon.dex_number}\n**Name:** {pokemon.name}\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: **{'Yes' if bundle else 'No'}**\n - Accepted Pokemon: **{'Yes' if accepted else 'No'}**\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n- Use the buttons below to confirm or cancel the auction.\n\n> **Remember, you must own the pokemon you are auctioning!**",
            color=embed_color
        )
        embed.set_image(url=pokemon.gif)
    else:
        embed: discord.Embed = discord.Embed(
            title=":wrench: | Confirm Auction",
            description=f"Are you sure you want to start an auction for a Bundle?\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: **{'Yes' if bundle else 'No'}**\n - Accepted Pokemon: **{'Yes' if accepted else 'No'}**\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n- Use the buttons below to confirm or cancel the auction.\n\n> **Remember, you must own the pokemon you are auctioning!**",
            color=embed_color
        )
        embed.set_image(url=BUNDLE_IMAGE)
    return embed

def rarity_check(pokemon_list: list[PokemonModel]) -> int:
    rarity: int = pokemon_list[0].rarity
    for pokemon in pokemon_list:
        if pokemon.rarity != rarity:
            return -1
    return rarity

async def end_auction(config: dict, interaction: discord.Interaction, auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str) -> None:
    database_manager = get_database_manager()
    auction.ended = True
    updated: bool = await database_manager.update(auction, id=auction.id)
    if not updated:
        print(f"An error occurred while updating the auction with id {auction.id}")
        return
    
    # Auction channels
    completed_channel_id: int = config['completed_channel']
    ongoing_channel_id: int = config['ongoing_channel']
    completed_channel: discord.TextChannel = interaction.guild.get_channel(completed_channel_id)
    ongoing_channel: discord.TextChannel = interaction.guild.get_channel(ongoing_channel_id)
    auction_channel: discord.TextChannel = interaction.guild.get_channel(auction.channel_id)
    
    # Send the completed message, delete the ongoing message and the auction channel
    completed_embed: discord.Embed = ended_auction_embed_builder(auction, embed_color, formatted_rarity, rarity_emoji, pokecoins_emoji, interaction=interaction)
    await completed_channel.send(embed=completed_embed)
    ongoing_message: discord.Message = await ongoing_channel.fetch_message(auction.ongoing_message_id)
    await ongoing_message.delete()
    await auction_channel.delete()
    
class AuctionView(discord.ui.View):
    def __init__(self, *, auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, auction_message: discord.Message | None = None):
        super().__init__(timeout=None)
        self.auction: AuctionModel = auction
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.pokecoins_emoji: str = pokecoins_emoji
        self.auction_message: discord.Message | None = auction_message
        self.remove_item(self.bundle_button) if not self.auction.bundle else None
    
    @discord.ui.button(label='Bid', style=discord.ButtonStyle.primary)
    async def bid_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id == self.auction.user_id:
            await interaction.response.send_message("You can't bid on your own auction!", ephemeral=True)
            return
        await interaction.response.send_modal(BidModal(auction_message=self.auction_message, embed_color=self.embed_color, formatted_rarity=self.formatted_rarity, rarity_emoji=self.rarity_emoji, pokecoins_emoji=self.pokecoins_emoji))

    @discord.ui.button(label='Bundle', style=discord.ButtonStyle.secondary)
    async def bundle_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        pokemon_info = [
            f"- Dex Number: {pokemon.dex_number}\n- Name: {pokemon.name}\n\n"
            for pokemon in self.auction.pokemon
        ]
        message = f"**Bundle Information**\n\n{''.join(pokemon_info)}"
        await interaction.response.send_message(message, ephemeral=True)


class ConfirmView(discord.ui.View):
    def __init__(self, *, pokemon: list[PokemonModel], auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, timeout: float | None = 60):
        super().__init__(timeout=timeout)
        self.config = load_config()
        self.pokemon: list[PokemonModel] = pokemon
        self.auction: AuctionModel = auction
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.database_manager = get_database_manager()
        
    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        user: discord.User = interaction.user
        pokecoins_emoji: str = self.config['emojis']['pokecoins']
        patreon_tokens_emoji: str = self.config['emojis']['patreontokens']
        if not self.auction.bundle:
            self.pokemon: PokemonModel = self.pokemon[0]
        await interaction.response.edit_message(content=f"{user.mention}, you have started an auction for: {self.pokemon.name if not self.auction.bundle else 'Bundle'}", embed=None, view=None)
        
        category_id: int = self.config['auctions_category']
        category: discord.CategoryChannel = interaction.guild.get_channel(category_id)
        new_channel: discord.TextChannel = await interaction.guild.create_text_channel(name=f'{self.formatted_rarity}-{self.pokemon.name if not self.auction.bundle else "Bundle"}', category=category)
        self.auction.channel_id = new_channel.id
        
        auction_embed: discord.Embed = auction_embed_builder(interaction, self.auction, self.embed_color, self.formatted_rarity, self.rarity_emoji, pokecoins_emoji)
        auction_view: AuctionView = AuctionView(auction=self.auction, embed_color=self.embed_color, formatted_rarity=self.formatted_rarity, rarity_emoji=self.rarity_emoji, pokecoins_emoji=pokecoins_emoji)
        auction_message: discord.Message = await new_channel.send(content=CONTENT_AUCTION_MESSAGE, embed=auction_embed, view=auction_view)
        auction_view.auction_message = auction_message
        
        new_auction_embed: discord.Embed = new_auction_embed_builder(self.auction, self.embed_color, self.formatted_rarity, user, new_channel)
        
        ongoing_channel_id: int = self.config['ongoing_channel']
        ongoing_channel: discord.TextChannel = interaction.guild.get_channel(ongoing_channel_id)
        ongoing_message: discord.Message = await ongoing_channel.send(embed=new_auction_embed)
        self.auction.ongoing_message_id = ongoing_message.id
        
        inserted: bool = await self.database_manager.insert(self.auction, channel_id=new_channel.id)
        if not inserted:
            await interaction.response.edit_message(content="An error occurred while creating the auction!", embed=None, view=None)
            return
        
        await interaction.channel.send(embed=new_auction_embed)
        
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Auction has been cancelled!", embed=None, view=None)
        

class BidModal(discord.ui.Modal):
    def __init__(self, *, auction_message:discord.Message, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, title: str = 'Auction Bid', timeout: float | None = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.auction_message: discord.Message = auction_message
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.pokecoins_emoji: str = pokecoins_emoji
        self.database_manager = get_database_manager()
        self.config: dict = load_config()
        
    pokecoins: discord.TextInput = discord.ui.TextInput(
        label='Pokecoins',
        placeholder='Enter the amount of pokecoins you want to bid',
        min_length=1,
        max_length=11,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        auction: AuctionModel = await self.database_manager.fetch_one(AuctionModel, channel_id=interaction.channel.id)
        if auction is None:
            await interaction.response.send_message("Auction not found!", ephemeral=True)
            return
        try:
            new_bid: int = int(self.pokecoins.value)
        except ValueError:
            await interaction.response.send_message("Invalid bid amount, please enter a valid number!", ephemeral=True)
            return
        if auction.bidder_id == interaction.user.id:
            await interaction.response.send_message("You can't bid twice!", ephemeral=True)
            return
        if auction.ended:
            await interaction.response.send_message("Auction has already ended!", ephemeral=True)
            return
        if auction.current_bid >= new_bid:
            await interaction.response.send_message("Your bid must be higher than the current bid!", ephemeral=True)
            return
        if auction.auto_buy is not None:
            if new_bid >= auction.auto_buy:
                new_bid = auction.auto_buy
                auction.current_bid = new_bid
                auction.bidder_id = interaction.user.id
                auction.end_time = int(datetime.datetime.now().timestamp())
                updated: bool = await self.database_manager.update(auction, id=auction.id)
                if not updated:
                    await interaction.response.send_message("An error occurred while updating the auction!", ephemeral=True)
                    return
                await interaction.response.send_message(f"{interaction.user.mention}, you have successfully triggered the auto buy with {new_bid:,} pokecoins!", ephemeral=True)
                await end_auction(self.config, interaction, auction, self.embed_color, self.formatted_rarity, self.rarity_emoji, self.pokecoins_emoji)
                return

        has_previous_bidder: bool = auction.bidder_id is not None
        
        if not has_previous_bidder:
            await interaction.response.send_message(f"{interaction.user.mention}, you have successfully bid {new_bid:,} pokecoins on the auction!", delete_after=10)
        else:
            previous_bidder: discord.User = interaction.guild.get_member(auction.bidder_id)
            await interaction.response.send_message(f"{interaction.user.mention}, you have successfully outbid {previous_bidder.mention} with {new_bid:,} pokecoins!", delete_after=10)
        
        auction.current_bid = new_bid
        auction.bidder_id = interaction.user.id
        updated: bool = await self.database_manager.update(auction, id=auction.id)
        if not updated:
            await interaction.response.send_message("An error occurred while updating the auction!", ephemeral=True)
            return
        
        auction_embed: discord.Embed = auction_embed_builder(interaction, auction, self.embed_color, self.formatted_rarity, self.rarity_emoji, self.pokecoins_emoji)
        await self.auction_message.edit(content=CONTENT_AUCTION_MESSAGE, embed=auction_embed, view=AuctionView(auction=auction, embed_color=self.embed_color, formatted_rarity=self.formatted_rarity, rarity_emoji=self.rarity_emoji, pokecoins_emoji=self.pokecoins_emoji, auction_message=self.auction_message))

class Auction(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.database_manager = get_database_manager()
        self.config = load_config()
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_auctions.start()
        
    async def cog_unload(self) -> None:
        self.check_auctions.stop()

    @tasks.loop(seconds=15)
    async def check_auctions(self) -> None:
        auctions: list[AuctionModel] = await self.database_manager.fetch_all(AuctionModel, ended=False)
        for auction in auctions:
            if auction.end_time <= int(datetime.datetime.now().timestamp()):
                auction.ended = True
                updated: bool = await self.database_manager.update(auction, id=auction.id)
                if not updated:
                    print(f"An error occurred while updating the auction with id {auction.id}")
                    continue
                
                # Information for the embed
                rarity_string: str = rarity_to_string(auction.pokemon.rarity)
                embed_color: int = hex_to_int(self.config['colors'][rarity_string])
                formatted_rarity: str = rarity_to_formatted_string(auction.pokemon.rarity)
                rarity_emoji: str = self.config['emojis'][rarity_string]
                pokecoins_emoji: str = self.config['emojis']['pokecoins']
                
                # Auction channels
                completed_channel_id: int = self.config['completed_channel']
                ongoing_channel_id: int = self.config['ongoing_channel']
                completed_channel: discord.TextChannel = self.bot.get_channel(completed_channel_id)
                ongoing_channel: discord.TextChannel = self.bot.get_channel(ongoing_channel_id)
                auction_channel: discord.TextChannel = self.bot.get_channel(auction.channel_id)
                
                # Send the completed message, delete the ongoing message and the auction channel
                completed_embed: discord.Embed = ended_auction_embed_builder(auction, embed_color, formatted_rarity, rarity_emoji, pokecoins_emoji, bot=self.bot)
                await completed_channel.send(embed=completed_embed)
                ongoing_message: discord.Message = await ongoing_channel.fetch_message(auction.ongoing_message_id)
                await ongoing_message.delete()
                await auction_channel.delete()
                
    @check_auctions.before_loop
    async def before_check_auctions(self) -> None:
        await self.bot.wait_until_ready()
                
        
    @discord.app_commands.command(name='auction', description='Start an auction')
    @discord.app_commands.choices(
        runtime = [
            discord.app_commands.Choice[int](name='1 Minute', value=60), # Tests
            discord.app_commands.Choice[int](name='30 Minutes', value=1800),
            discord.app_commands.Choice[int](name='45 Minutes', value=2700),
            discord.app_commands.Choice[int](name='1 Hour', value=3600),
            discord.app_commands.Choice[int](name='1 Hour 30 Minutes', value=5400),
            discord.app_commands.Choice[int](name='2 Hours', value=7200),
            discord.app_commands.Choice[int](name='3 Hours', value=10800),
            discord.app_commands.Choice[int](name='4 Hours', value=14400),
        ],
        accepted = [
            discord.app_commands.Choice[int](name='Yes', value=1),
            discord.app_commands.Choice[int](name='No', value=0)
        ]
    )
    @discord.app_commands.describe(
        dex_number='The dex number of the pokemon you want to auction (if bundle separate by commas)',
        runtime='The time the auction will last',
        accepted='Does the auction accept pokemon? | WIP',
        autobuy='The price at which the auction will be automatically bought (Optional)'
    )
    async def auction(self, interaction: discord.Interaction, dex_number: str, runtime: int, accepted: int, autobuy: int | None = None) -> None:
        dex_number_list: list[str] = dex_number.split(',')
        bundle: bool = len(dex_number_list) > 1
        
        try:
            dex_numbers: list[int] = [int(dex) for dex in dex_number_list]
        except ValueError:
            await interaction.response.send_message("Invalid dex number, please enter a valid number!", ephemeral=True)
            return
        
        pokemon: list[PokemonModel] = await self.database_manager.fetch_all(PokemonModel, dex_number=dex_numbers)
        if len(pokemon) == 0:
            await interaction.response.send_message("Pokemon not found!", ephemeral=True)
            return
        auction_creation_time: int = int(datetime.datetime.now().timestamp())
        auction_end_time: int = auction_creation_time + runtime
        auction: AuctionModel =  AuctionModel(user_id=interaction.user.id, end_time=auction_end_time, ended=False, bundle=bundle, accepted=bool(accepted), auto_buy=autobuy, pokemon=pokemon)
        rarity: int = rarity_check(pokemon)
        if rarity == -1:
            await interaction.response.send_message("All pokemon must have the same rarity!", ephemeral=True)
            return
        rarity_string: str = rarity_to_string(rarity)
        rarity_emoji: str = self.config['emojis'][rarity_string]
        formatted_rarity: str = rarity_to_formatted_string(rarity)
        embed_color: int = hex_to_int(self.config['colors'][rarity_string])
        
        confirm_embed: discord.Embed = confirmed_embed_builder(pokemon, auction, embed_color, formatted_rarity, bundle, bool(accepted))
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True, view=ConfirmView(pokemon=pokemon, auction=auction, embed_color=embed_color, formatted_rarity=formatted_rarity, rarity_emoji=rarity_emoji))
            

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Auction(bot))
