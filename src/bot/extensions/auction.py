from ...database.database import DatabaseManager, get_database_manager
from ...database.models import Auction as AuctionModel
from ...database.models import Pokemon as PokemonModel
from ...database.models import AuctionPokemon as AuctionPokemonModel
from ...database.models import AuctionAccepted as AuctionAcceptedModel
from configuration.configuration import load_config
from configuration.utils import hex_to_int, rarity_to_string, rarity_to_formatted_string
import asyncio
import datetime
import discord
import uuid
from discord.ext import commands, tasks

CONTENT_AUCTION_MESSAGE: str = "- Roles to ping | WIP\n> Please use the buttons below to bid on the auction!\n\n- **Remember, you must own what you are bidding!**"
BUNDLE_IMAGE: str = 'https://cdn.discordapp.com/attachments/1256251099858337846/1257322212705439775/bundle.png?ex=6683fc0f&is=6682aa8f&hm=f968feee9546b5bd636f6f96ffbfeee69036cb69f954ac739d04da585a260025&'
POKEMON_SEPARATOR: str = ','
QUANTITY_SEPARATOR: str = '-'

def auction_embed_builder(interaction: discord.Interaction, auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str) -> discord.Embed:
    current_bid: int = auction.current_bid if auction.current_bid is not None else 0
    autobuy: int | str = auction.auto_buy if auction.auto_buy is not None else 'None'
    if isinstance(autobuy, int):
        autobuy = f'{autobuy:,}'
    if not auction.bundle:
        pokemon: PokemonModel = auction_pokemon_list[0].pokemon
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} {pokemon.name} | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**\n- Dex Number: **{pokemon.dex_number}**",
            color=embed_color
        )
        embed.add_field(name="Current Bid", value=f"{pokecoins_emoji} {current_bid:,}")
        embed.add_field(name="Bidder", value=f"{interaction.guild.get_member(auction.bidder_id).mention if auction.bidder_id != None else 'None'}")
        embed.add_field(name="Auto Buy", value=f"{pokecoins_emoji} {autobuy}")
        embed.add_field(name="Quantity", value=f"{auction_pokemon_list[0].quantity}")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
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

def ended_auction_embed_builder(auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, bot: commands.Bot | None = None, interaction: discord.Interaction | None = None) -> discord.Embed:
    bot_or_interaction_guild: commands.Bot | discord.Interaction = bot if bot is not None else interaction.guild
    if auction.bidder_id is not None:
        bidder: discord.User | discord.Member = bot_or_interaction_guild.get_user(auction.bidder_id) if isinstance(bot_or_interaction_guild, commands.Bot) else bot_or_interaction_guild.get_member(auction.bidder_id)
    else:
        bidder = None
    if not auction.bundle:
        pokemon: PokemonModel = auction_pokemon_list[0].pokemon
        embed: discord.Embed = discord.Embed(
            title=f"{rarity_emoji} {pokemon.name} | {formatted_rarity}",
            description=f"- Rarity: **{formatted_rarity}**\n- Dex Number: **{pokemon.dex_number}**",
            color=embed_color
        )
        embed.add_field(name="Final Bid", value=f"{pokecoins_emoji} {auction.current_bid:,}")
        embed.add_field(name="Bidder", value=f"{bidder.mention if bidder is not None else 'None'}")
        embed.add_field(name="⠀", value="⠀")
        embed.add_field(name="Quantity", value=f"{auction_pokemon_list[0].quantity}")
        embed.add_field(name="Bundle", value=":white_check_mark:" if auction.bundle else ":x:")
        embed.add_field(name="Accepted", value=":white_check_mark:" if auction.accepted else ":x:")
        embed.add_field(name="Auction Ended", value=f"<t:{auction.end_time}:R>")
        user: discord.User | discord.Member = bot_or_interaction_guild.get_user(auction.user_id) if isinstance(bot_or_interaction_guild, commands.Bot) else bot_or_interaction_guild.get_member(auction.user_id)
        embed.add_field(name="Auction Host", value=f"{user.mention if user is not None else 'None'}")
        embed.set_image(url=pokemon.gif)
    else:
        pokemon: PokemonModel = auction_pokemon_list[0].pokemon
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

def new_auction_embed_builder(auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], embed_color: int, formatted_rarity: str, user: discord.User, channel: discord.TextChannel) -> discord.Embed:
    if not auction.bundle:
        pokemon: PokemonModel = auction_pokemon_list[0].pokemon
        embed: discord.Embed = discord.Embed(
            title=":wrench: | New Auction Started!",
            description=f"{user.mention} has started an auction for Pokemon {pokemon.name}\n**Dex Number:** {pokemon.dex_number}\n**Name:** {pokemon.name}\n**Quantity:** {auction_pokemon_list[0].quantity}\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: {':white_check_mark:' if auction.bundle else ':x:'}\n - Accepted Pokemon: {':white_check_mark:' if auction.accepted else ':x:'}\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n**Channel:** {channel.mention}",
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

def confirmed_embed_builder(pokemon: list[PokemonModel], auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], embed_color: int, formatted_rarity: str, bundle: bool, accepted: bool) -> discord.Embed:
    if not bundle:
        pokemon: PokemonModel = pokemon[0]
        embed: discord.Embed = discord.Embed(
            title=":wrench: | Confirm Auction",
            description=f"Are you sure you want to start an auction for Pokemon {pokemon.name}?\n**Dex Number:** {pokemon.dex_number}\n**Name:** {pokemon.name}\n**Quantity:** {auction_pokemon_list[0].quantity}\n**Rarity:** {formatted_rarity}\n\n- Auction Information:\n - Bundle: **{'Yes' if bundle else 'No'}**\n - Accepted Pokemon: **{'Yes' if accepted else 'No'}**\n\n> **Auction will end <t:{auction.end_time}:R>**\n\n- Use the buttons below to confirm or cancel the auction.\n\n> **Remember, you must own the pokemon you are auctioning!**",
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

async def end_auction(config: dict, interaction: discord.Interaction, auction: AuctionModel, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, database_manager: DatabaseManager) -> None:
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
    completed_embed: discord.Embed = ended_auction_embed_builder(auction, auction.auction_pokemon, embed_color, formatted_rarity, rarity_emoji, pokecoins_emoji, interaction.bot, interaction)
    await completed_channel.send(embed=completed_embed)
    ongoing_message: discord.Message = await ongoing_channel.fetch_message(auction.ongoing_message_id)
    await ongoing_message.delete()
    await auction_channel.delete()

async def start_auction(config: dict, interaction: discord.Interaction, auction: AuctionModel, pokemon: list[PokemonModel], runtime: int, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, user: discord.User, database_manager: DatabaseManager, *, auction_pokemon_list: list[AuctionPokemonModel] = [], accepted_list: list[AuctionAcceptedModel] = []) -> None:
    if not auction.bundle:
        pokemon: PokemonModel = pokemon[0]
    await interaction.response.edit_message(content=f"{user.mention}, you have started an auction for: {pokemon.name if not auction.bundle else 'Bundle'}", embed=None, view=None)
    
    category_id: int = config['auctions_category']
    category: discord.CategoryChannel = interaction.guild.get_channel(category_id)
    new_channel: discord.TextChannel = await interaction.guild.create_text_channel(name=f'{formatted_rarity}-{pokemon.name if not auction.bundle else "Bundle"}', category=category)
    auction_creation_time: int = int(datetime.datetime.now().timestamp())
    auction_end_time: int = auction_creation_time + runtime
    auction.channel_id = new_channel.id
    auction.end_time = auction_end_time
    
    auction_embed: discord.Embed = auction_embed_builder(interaction, auction, auction_pokemon_list, embed_color, formatted_rarity, rarity_emoji, pokecoins_emoji)
    auction_view: AuctionView = AuctionView(is_bundle=auction.bundle, is_accepted=auction.accepted, embed_color=embed_color, formatted_rarity=formatted_rarity, rarity_emoji=rarity_emoji, pokecoins_emoji=pokecoins_emoji, database_manager=database_manager)
    auction_message: discord.Message = await new_channel.send(content=CONTENT_AUCTION_MESSAGE, embed=auction_embed, view=auction_view)
    auction_view.auction_message = auction_message
    auction.auction_message_id = auction_message.id
    
    new_auction_embed: discord.Embed = new_auction_embed_builder(auction, auction_pokemon_list, embed_color, formatted_rarity, user, new_channel)
    ongoing_channel_id: int = config['ongoing_channel']
    ongoing_channel: discord.TextChannel = interaction.guild.get_channel(ongoing_channel_id)
    ongoing_message: discord.Message = await ongoing_channel.send(embed=new_auction_embed)
    auction.ongoing_message_id = ongoing_message.id
    
    inserted: bool = await database_manager.insert(auction, channel_id=new_channel.id)
    if not inserted:
        await interaction.response.edit_message(content="An error occurred while creating the auction!", embed=None, view=None)
        return

    auction_pokemon_to_insert: list[AuctionPokemonModel] = [
        AuctionPokemonModel(
            auction_id=auction_pokemon.auction.id,
            pokemon_id=auction_pokemon.pokemon.id,
            quantity=auction_pokemon.quantity
        ) for auction_pokemon in auction_pokemon_list
    ]
    for auction_pokemon in auction_pokemon_to_insert:
        await database_manager.insert(auction_pokemon, auction_id=auction_pokemon.auction_id, pokemon_id=auction_pokemon.pokemon_id)
    if auction.accepted:
        for accepted in accepted_list:
            await database_manager.insert(accepted, auction_id=accepted.auction_id, pokemon_id=accepted.pokemon_id)
    
    await interaction.channel.send(embed=new_auction_embed)

class AuctionView(discord.ui.View):
    def __init__(self, *, is_bundle: bool, is_accepted: bool, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, database_manager: DatabaseManager, auction_message: discord.Message | None = None):
        super().__init__(timeout=None)
        self.is_bundle: bool = is_bundle
        self.is_accepted: bool = is_accepted
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.pokecoins_emoji: str = pokecoins_emoji
        self.database_manager: DatabaseManager = database_manager
        self.auction_message: discord.Message | None = auction_message
        self.remove_item(self.bundle_button) if not is_bundle else None
        self.remove_item(self.accepted_button) if not is_accepted else None
    
    @discord.ui.button(label='Bid', style=discord.ButtonStyle.primary)
    async def bid_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        auction: AuctionModel = await self.database_manager.fetch_one(AuctionModel, channel_id=interaction.channel.id)
        if interaction.user.id == auction.user_id:
            await interaction.response.send_message("You can't bid on your own auction!", ephemeral=True)
            return
        await interaction.response.send_modal(BidModal(auction_view=self, auction_message=self.auction_message, embed_color=self.embed_color, formatted_rarity=self.formatted_rarity, rarity_emoji=self.rarity_emoji, pokecoins_emoji=self.pokecoins_emoji, database_manager=self.database_manager))

    @discord.ui.button(label='Bundle', style=discord.ButtonStyle.secondary)
    async def bundle_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        auction: AuctionModel = await self.database_manager.fetch_one(AuctionModel, channel_id=interaction.channel.id)
        pokemon_info = [
            f"- Dex Number: {auction_pokemon.pokemon.dex_number}\n- Name: {auction_pokemon.pokemon.name}\n- Quantity: {auction_pokemon.quantity}\n\n"
            for auction_pokemon in auction.auction_pokemon
        ]
        message = f"**Bundle Information**\n\n{''.join(pokemon_info)}"
        await interaction.response.send_message(message, ephemeral=True)
        
    @discord.ui.button(label='Accepted', style=discord.ButtonStyle.secondary)
    async def accepted_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        auction: AuctionModel = await self.database_manager.fetch_one(AuctionModel, channel_id=interaction.channel.id)
        accepted_list: list[AuctionAcceptedModel] = auction.auction_accepted
        await interaction.response.send_message("**Accepted Pokemon**\n\n" + '\n'.join([f"{rarity_to_formatted_string(accepted.pokemon.rarity)} {accepted.pokemon.name} | {accepted.price:,}" for accepted in accepted_list]), ephemeral=True)


class AcceptedModal(discord.ui.Modal):
    def __init__(self, *, accepted_view: 'AcceptedView', database_manager: DatabaseManager, title: str = 'Accepted Pokemon', timeout: float | None = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.accepted_view: AcceptedView = accepted_view
        self.database_manager: DatabaseManager = database_manager
        
    pokemon: discord.TextInput = discord.ui.TextInput(
        label='Pokemon',
        placeholder='Enter the dex number of the pokemon you want to accept',
        min_length=1,
        max_length=4,
        required=True
    )
    
    price: discord.TextInput = discord.ui.TextInput(
        label='Price',
        placeholder='Enter the price of the pokemon',
        min_length=1,
        max_length=12,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not self.pokemon.value.isdigit():
            await interaction.response.send_message("Invalid dex number, please enter a valid number!", ephemeral=True)
            return
        if not self.price.value.isdigit():
            await interaction.response.send_message("Invalid price, please enter a valid number!", ephemeral=True)
            return
        pokemon: PokemonModel = await self.database_manager.fetch_one(PokemonModel, dex_number=int(self.pokemon.value))
        accepted: AuctionAcceptedModel = AuctionAcceptedModel(
            auction_id=self.accepted_view.auction.id,
            pokemon_id=pokemon.id,
            price=int(self.price.value)
        )
        self.accepted_view.accepted_list.append(accepted)
        self.accepted_view.timeout = 60
        await interaction.response.send_message(f"{rarity_to_formatted_string(pokemon.rarity)} {pokemon.name} has been added to the accepted list!", ephemeral=True)
        

class AcceptedSelect(discord.ui.Select):
    def __init__(self, *, accepted_view: 'AcceptedView') -> None:
        self.accepted_view: AcceptedView = accepted_view
        options: list[discord.SelectOption] = []
        options.append(discord.SelectOption(label='Cancel', value=-1))
        options.extend([
            discord.SelectOption(label=f"{rarity_to_formatted_string(accepted.pokemon.rarity)} {accepted.pokemon.name} | {accepted.price:,}", value=f"{self.accepted_view.accepted_list_instances.index(accepted)}")
            for accepted in self.accepted_view.accepted_list_instances
        ])
        super().__init__(placeholder='Choose which accepted to remove', min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction) -> None:
        index: int = int(self.values[0])
        if index == -1:
            for button in self.accepted_view.children:
                button.disabled = False
            self.accepted_view.remove_item(self)
            await self.accepted_view.accepted_message.edit(view=self.accepted_view)
            await interaction.response.send_message("Selection has been cancelled!", ephemeral=True)
            return
        self.accepted_view.accepted_list.pop(index)
        self.options.pop(index + 1)
        await self.accepted_view.accepted_message.edit(view=self.accepted_view)
        await interaction.response.defer(ephemeral=True)

class AcceptedView(discord.ui.View):
    def __init__(self, *, auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], accepted_list: list[AuctionAcceptedModel], embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, runtime: int, accepted_message: discord.Message | None = None, database_manager: DatabaseManager, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.config = load_config()
        self.auction: AuctionModel = auction
        self.auction_pokemon_list: list[AuctionPokemonModel] = auction_pokemon_list
        self.accepted_list: list[AuctionAcceptedModel] = accepted_list if len(accepted_list) > 0 else []
        self.accepted_list_instances: list[AuctionAcceptedModel] = []
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.pokecoins_emoji: str = pokecoins_emoji
        self.runtime: int = runtime
        self.accepted_message: discord.Message | None = None
        self.database_manager: DatabaseManager = database_manager
        
    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
            
    @discord.ui.button(label='Add', style=discord.ButtonStyle.primary)
    async def add_button_av(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(AcceptedModal(accepted_view=self, database_manager=self.database_manager))
        
    @discord.ui.button(label='Remove', style=discord.ButtonStyle.danger)
    async def remove_button_av(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for btn in self.children:
            btn.disabled = True
        for accepted in self.accepted_list:
            pokemon_instance: PokemonModel = await self.database_manager.fetch_one(PokemonModel, id=accepted.pokemon_id)
            self.accepted_list_instances.append(
                AuctionAcceptedModel(
                    pokemon=pokemon_instance,
                    price=accepted.price
                )
            )
        self.add_item(AcceptedSelect(accepted_view=self))
        await interaction.response.defer(ephemeral=True)
        await self.accepted_message.edit(view=self)
    
    @discord.ui.button(label='Done', style=discord.ButtonStyle.success)
    async def done_button_av(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if len(self.accepted_list) == 0:
            await interaction.response.send_message("You must add at least one accepted pokemon!", ephemeral=True)
            return
        pokemon: list[PokemonModel] = [auction_pokemon.pokemon for auction_pokemon in self.auction_pokemon_list]
        await start_auction(self.config, interaction, self.auction, pokemon, self.runtime, self.embed_color, self.formatted_rarity, self.rarity_emoji, self.pokecoins_emoji, interaction.user, self.database_manager, auction_pokemon_list=self.auction_pokemon_list, accepted_list=self.accepted_list)
        for button in self.children:
            button.disabled = True


class ConfirmView(discord.ui.View):
    def __init__(self, *, pokemon: list[PokemonModel], auction: AuctionModel, auction_pokemon_list: list[AuctionPokemonModel], runtime: int, embed_color: int, formatted_rarity: str, rarity_emoji: str, database_manager: DatabaseManager, timeout: float | None = 60):
        super().__init__(timeout=timeout)
        self.config = load_config()
        self.pokemon: list[PokemonModel] = pokemon
        self.auction: AuctionModel = auction
        self.auction_pokemon_list: list[AuctionPokemonModel] = auction_pokemon_list
        self.runtime: int = runtime
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.database_manager: DatabaseManager = database_manager
        
    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.success)
    async def confirm_button_cv(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        user: discord.User = interaction.user
        pokecoins_emoji: str = self.config['emojis']['pokecoins']
        patreon_tokens_emoji: str = self.config['emojis']['patreontokens']
        
        if self.auction.accepted:
            for button in self.children:
                button.disabled = True
            accepted_view: AcceptedView = AcceptedView(auction=self.auction, auction_pokemon_list=self.auction_pokemon_list, accepted_list=[], embed_color=self.embed_color, formatted_rarity=self.formatted_rarity, rarity_emoji=self.rarity_emoji, pokecoins_emoji=pokecoins_emoji, runtime=self.runtime, database_manager=self.database_manager)
            await interaction.response.send_message("Please add the accepted pokemon!", ephemeral=True, view=accepted_view)
            accepted_message: discord.Message = await interaction.original_response()
            accepted_view.accepted_message = accepted_message
            return
        await start_auction(self.config, interaction, self.auction, self.pokemon, self.runtime, self.embed_color, self.formatted_rarity, self.rarity_emoji, pokecoins_emoji, user, self.database_manager, auction_pokemon_list=self.auction_pokemon_list)
        
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
    async def cancel_button_cv(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Auction has been cancelled!", embed=None, view=None)


class BidModal(discord.ui.Modal):
    def __init__(self, *, auction_view: AuctionView, auction_message:discord.Message, embed_color: int, formatted_rarity: str, rarity_emoji: str, pokecoins_emoji: str, database_manager: DatabaseManager, title: str = 'Auction Bid', timeout: float | None = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.auction_view: AuctionView = auction_view
        self.auction_message: discord.Message = auction_message
        self.embed_color: int = embed_color
        self.formatted_rarity: str = formatted_rarity
        self.rarity_emoji: str = rarity_emoji
        self.pokecoins_emoji: str = pokecoins_emoji
        self.database_manager: DatabaseManager = database_manager
        self.config: dict = load_config()
        
    pokecoins: discord.TextInput = discord.ui.TextInput(
        label='Pokecoins',
        placeholder='Amount of pokecoins you want to bid',
        min_length=1,
        max_length=12,
        required=False
    )
    
    pokemon: discord.TextInput = discord.ui.TextInput(
        label='Pokemon',
        placeholder='Dex number of the pokemon you want to bid (only if accepted)',
        min_length=1,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        auction: AuctionModel | None = await self.database_manager.fetch_one(AuctionModel, channel_id=interaction.channel.id)
        if auction is None:
            await interaction.response.send_message("Auction not found!", ephemeral=True)
            return
        if self.pokecoins.value == '' and self.pokemon.value == '':
            await interaction.response.send_message('You must specify a bid!', ephemeral=True)
            return
        coins: int = 0
        if self.pokecoins.value != '':
            try:
                coins: int = int(self.pokecoins.value)
            except ValueError:
                await interaction.response.send_message("Invalid bid amount, please enter a valid number!", ephemeral=True) # TODO change since is optional
                return
        auction.accepted_coins = coins
        
        price_accepted_pokemon: int = 0
        if self.pokemon.value != '':
            if auction.accepted == False:
                await interaction.response.send_message("This auction doesn't accept pokemon!", ephemeral=True)
                return
            dex_number_list: list[int] = self.pokemon.value.replace(' ', '').split(',')
            try:
                dex_number_dict: list[dict[str, int]] = [
                    {
                        'dex_number': int(dex.split(QUANTITY_SEPARATOR)[0]),
                        'quantity': int(dex.split(QUANTITY_SEPARATOR)[1]) if len(dex.split(QUANTITY_SEPARATOR)) > 1 else 1
                    }
                    for dex in dex_number_list
                ]
                dex_number_dict.sort(key=lambda x: x['dex_number'])
            except ValueError:
                await interaction.response.send_message("Invalid dex number, please enter a valid number!", ephemeral=True)
                return
            dex_number_to_quantity = {dex['dex_number']: dex['quantity'] for dex in dex_number_dict}
            dex_number_accepted: list[int] = [accepted.pokemon.dex_number for accepted in auction.auction_accepted]
            for dex_number in dex_number_dict:
                if dex_number['dex_number'] not in dex_number_accepted:
                    await interaction.response.send_message(f"{dex_number['dex_number']} is not in the accepted list!", ephemeral=True)
                    return
            
            auction.accepted_pokemon = ','.join([f"{dex_number['dex_number']}{QUANTITY_SEPARATOR}{dex_number['quantity']}" for dex_number in dex_number_dict])
            price_accepted_pokemon = sum(accepted.price * dex_number_to_quantity.get(accepted.pokemon.dex_number, 0)
                            for accepted in auction.auction_accepted)
        else:
            auction.accepted_pokemon = ''
        total_bid: int = coins + price_accepted_pokemon
        if total_bid < 1:
            await interaction.response.send_message("You must bid at least 1 coin.", ephemeral=True)
            return
        if auction.bidder_id == interaction.user.id:
            await interaction.response.send_message("You can't bid twice!", ephemeral=True)
            return
        if auction.ended:
            await interaction.response.send_message("Auction has already ended!", ephemeral=True)
            return
        if auction.current_bid >= total_bid:
            await interaction.response.send_message("Your bid must be higher than the current bid!", ephemeral=True)
            return
        if auction.auto_buy is not None and total_bid >= auction.auto_buy:
            total_bid = auction.auto_buy
            auction.current_bid = total_bid
            auction.bidder_id = interaction.user.id
            auction.end_time = int(datetime.datetime.now().timestamp())
            updated: bool = await self.database_manager.update(auction, id=auction.id)
            if not updated:
                await interaction.response.send_message("An error occurred while updating the auction!", ephemeral=True)
                return
            await interaction.response.send_message(f"{interaction.user.mention}, you have successfully triggered the auto buy with {coins:,} pokecoins!", ephemeral=True)
            await end_auction(self.config, interaction, auction, self.embed_color, self.formatted_rarity, self.rarity_emoji, self.pokecoins_emoji, self.database_manager)
            return

        has_previous_bidder: bool = auction.bidder_id is not None
        
        if not has_previous_bidder:
            await interaction.response.send_message(f"{interaction.user.mention}, you have successfully bid {total_bid:,} pokecoins on the auction!", delete_after=10)
        else:
            previous_bidder: discord.User = interaction.guild.get_member(auction.bidder_id)
            await interaction.response.send_message(f"{interaction.user.mention}, you have successfully outbid {previous_bidder.mention} with {total_bid:,} pokecoins!", delete_after=10)
        
        auction.accepted_coins = coins
        auction.current_bid = total_bid
        auction.bidder_id = interaction.user.id
        updated: bool = await self.database_manager.update(auction, id=auction.id)
        if not updated:
            await interaction.response.send_message("An error occurred while updating the auction!", ephemeral=True)
            return
        
        auction_embed: discord.Embed = auction_embed_builder(interaction, auction, auction.auction_pokemon, self.embed_color, self.formatted_rarity, self.rarity_emoji, self.pokecoins_emoji)
        await self.auction_message.edit(content=CONTENT_AUCTION_MESSAGE, embed=auction_embed, view=self.auction_view)

class Auction(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = load_config()
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_auctions.start()
        
    async def cog_unload(self) -> None:
        self.check_auctions.stop()

    @tasks.loop(seconds=15)
    async def check_auctions(self) -> None:
        database_manager: DatabaseManager = get_database_manager()
        auctions: list[AuctionModel] = await database_manager.fetch_all(AuctionModel, ended=False)
        for auction in auctions:
            if auction.end_time <= int(datetime.datetime.now().timestamp()):
                auction.ended = True
                updated: bool = await database_manager.update(auction, id=auction.id)
                if not updated:
                    print(f"An error occurred while updating the auction with id {auction.id}")
                    continue
                
                # Information for the embed
                rarity_string: str = rarity_to_string(auction.auction_pokemon[0].pokemon.rarity)
                embed_color: int = hex_to_int(self.config['colors'][rarity_string])
                formatted_rarity: str = rarity_to_formatted_string(auction.auction_pokemon[0].pokemon.rarity)
                rarity_emoji: str = self.config['emojis'][rarity_string]
                pokecoins_emoji: str = self.config['emojis']['pokecoins']
                
                # Auction channels
                completed_channel_id: int = self.config['completed_channel']
                ongoing_channel_id: int = self.config['ongoing_channel']
                completed_channel: discord.TextChannel = self.bot.get_channel(completed_channel_id)
                ongoing_channel: discord.TextChannel = self.bot.get_channel(ongoing_channel_id)
                auction_channel: discord.TextChannel = self.bot.get_channel(auction.channel_id)
                
                # Send the completed message, delete the ongoing message and the auction channel
                completed_embed: discord.Embed = ended_auction_embed_builder(auction, auction.auction_pokemon, embed_color, formatted_rarity, rarity_emoji, pokecoins_emoji, self.bot)
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
        dex_number=f'The dex number of the pokemon you want to auction (format: dex_number{QUANTITY_SEPARATOR}quantity (if no quantity, default is 1), if bundle separate by commas)',
        runtime='The time the auction will last',
        accepted='Does the auction accept pokemon?',
        autobuy='The price at which the auction will be automatically bought (Optional)'
    )
    async def auction(self, interaction: discord.Interaction, dex_number: str, runtime: int, accepted: int, autobuy: int | None = None) -> None:
        database_manager: DatabaseManager = get_database_manager()
        dex_number = dex_number.replace(' ', '')
        dex_number_list: list[str] = dex_number.split(POKEMON_SEPARATOR)
        try:
            dex_number_dict: list[dict[str, int]] = [
                {
                    'dex_number': int(dex.split(QUANTITY_SEPARATOR)[0]),
                    'quantity': int(dex.split(QUANTITY_SEPARATOR)[1]) if len(dex.split(QUANTITY_SEPARATOR)) > 1 else 1
                }
                for dex in dex_number_list
            ]
            dex_number_dict.sort(key=lambda x: x['dex_number'])
        except ValueError:
            await interaction.response.send_message("Invalid dex number, please enter a valid number!", ephemeral=True)
            return
        dex_numbers: list[int] = [dex.get('dex_number', -1) for dex in dex_number_dict]
        quantities: list[int] = [dex.get('quantity', 1) for dex in dex_number_dict]
        bundle: bool = len(dex_numbers) > 1
        
        pokemon: list[PokemonModel] = await database_manager.fetch_all(PokemonModel, dex_number=dex_numbers)
        if len(pokemon) == 0:
            await interaction.response.send_message("Pokemon not found!", ephemeral=True)
            return
        auction_creation_time: int = int(datetime.datetime.now().timestamp())
        auction_end_time: int = auction_creation_time + runtime
        auction: AuctionModel =  AuctionModel(
            id= uuid.uuid4(),
            user_id=interaction.user.id,
            end_time=auction_end_time,
            ended=False,
            bundle=bundle,
            accepted=bool(accepted),
            auto_buy=autobuy,
        )
        auction_pokemon_list: list[AuctionPokemonModel] = [
            AuctionPokemonModel(
                auction=auction,
                pokemon=pkmn,
                quantity=quantity
            )
            for pkmn, quantity in zip(pokemon, quantities)
        ]
        rarity: int = rarity_check(pokemon)
        if rarity == -1:
            await interaction.response.send_message("All pokemon must have the same rarity!", ephemeral=True)
            return
        rarity_string: str = rarity_to_string(rarity)
        rarity_emoji: str = self.config['emojis'][rarity_string]
        formatted_rarity: str = rarity_to_formatted_string(rarity)
        embed_color: int = hex_to_int(self.config['colors'][rarity_string])
        
        confirm_embed: discord.Embed = confirmed_embed_builder(pokemon, auction, auction_pokemon_list, embed_color, formatted_rarity, bundle, bool(accepted))
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True, view=ConfirmView(pokemon=pokemon, auction=auction, auction_pokemon_list=auction_pokemon_list, runtime=runtime, embed_color=embed_color, formatted_rarity=formatted_rarity, rarity_emoji=rarity_emoji, database_manager=database_manager))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Auction(bot))
