from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, Mapped

Base = declarative_base()

class AuctionPokemon(Base):
    __tablename__ = "auction_pokemon"
    
    auction_id: Mapped[int] = Column(Integer, ForeignKey('auctions.id'), primary_key=True)
    pokemon_id: Mapped[int] = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    quantity: Mapped[int] = Column(Integer, nullable=False, default=1)
    
    auction: Mapped['Auction'] = relationship("Auction", back_populates='auction_pokemon')
    pokemon: Mapped['Pokemon'] = relationship("Pokemon", back_populates='auction_pokemon')

class Pokemon(Base):
    __tablename__ = "pokemon"
    
    id: Mapped[int | None] = Column(Integer, primary_key=True, autoincrement=True, index=True)
    dex_number: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    rarity: Mapped[int] = Column(Integer, nullable=False)
    gif: Mapped[str] = Column(String, nullable=False)
    auction_pokemon: Mapped[list[AuctionPokemon]] = relationship(back_populates='pokemon')

class Auction(Base):
    __tablename__ = "auctions"
    
    id: Mapped[int | None] = Column(Integer, primary_key=True, autoincrement=True, index=True)
    channel_id: Mapped[int] = Column(Integer, nullable=False)
    ongoing_message_id: Mapped[int] = Column(Integer, nullable=False)
    user_id: Mapped[int] = Column(Integer, nullable=False)
    current_bid: Mapped[int] = Column(Integer, nullable=False, default=0)
    bidder_id: Mapped[int | None] = Column(Integer)
    auto_buy: Mapped[int | None] = Column(Integer)
    end_time: Mapped[int] = Column(Integer, nullable=False)
    accepted: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    accepted_list: Mapped[list[int]] = Column(String, nullable=False, default="")
    bundle: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    ended: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    auction_pokemon: Mapped[list[AuctionPokemon]] = relationship(back_populates='auction')
