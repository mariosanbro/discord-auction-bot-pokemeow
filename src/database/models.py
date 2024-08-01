import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, BINARY
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy.types import TypeDecorator

Base = declarative_base()

class UUID(TypeDecorator):
    impl = BINARY(16)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value.bytes
        return uuid.UUID(value).bytes
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(bytes=value)

class AuctionPokemon(Base):
    __tablename__ = "auction_pokemon"
    
    auction_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey('auctions.id'), primary_key=True)
    pokemon_id: Mapped[int] = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    quantity: Mapped[int] = Column(Integer, nullable=False, default=1)
    
    auction: Mapped['Auction'] = relationship("Auction", back_populates='auction_pokemon')
    pokemon: Mapped['Pokemon'] = relationship("Pokemon", back_populates='auction_pokemon')
    
    def __repr__(self):
        return f"<AuctionPokemon auction_id={self.auction_id} pokemon_id={self.pokemon_id} quantity={self.quantity}>"

class AuctionAccepted(Base):
    __tablename__ = "auction_accepted"
    
    auction_id: Mapped[uuid.UUID] = Column(UUID, ForeignKey('auctions.id'), primary_key=True)
    pokemon_id: Mapped[int] = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    price: Mapped[int] = Column(Integer, nullable=False)
    
    auction: Mapped['Auction'] = relationship("Auction", back_populates='auction_accepted')
    pokemon: Mapped['Pokemon'] = relationship("Pokemon", back_populates='auction_accepted')
    
    def __repr__(self):
        return f"<AuctionAccepted auction_id={self.auction_id} pokemon_id={self.pokemon_id} price={self.price}>"


class Pokemon(Base):
    __tablename__ = "pokemon"
    
    id: Mapped[int | None] = Column(Integer, primary_key=True, autoincrement=True, index=True)
    dex_number: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    rarity: Mapped[int] = Column(Integer, nullable=False)
    gif: Mapped[str] = Column(String, nullable=False)
    auction_pokemon: Mapped[list[AuctionPokemon]] = relationship(back_populates='pokemon')
    auction_accepted: Mapped[list[AuctionAccepted]] = relationship(back_populates='pokemon')
    
    def __repr__(self):
        return f"<Pokemon id={self.id} dex_number={self.dex_number} name={self.name} rarity={self.rarity} gif={self.gif}>"

class Auction(Base):
    __tablename__ = "auctions"
    
    id: Mapped[uuid.UUID] = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    channel_id: Mapped[int] = Column(Integer, nullable=False)
    auction_message_id: Mapped[int] = Column(Integer, nullable=False)
    ongoing_message_id: Mapped[int] = Column(Integer, nullable=False)
    user_id: Mapped[int] = Column(Integer, nullable=False)
    current_bid: Mapped[int] = Column(Integer, nullable=False, default=0)
    accepted_coins: Mapped[int] = Column(Integer, nullable=False, default=0)
    accepted_pokemon: Mapped[str] = Column(String, nullable=False, default='')
    bidder_id: Mapped[int | None] = Column(Integer)
    auto_buy: Mapped[int | None] = Column(Integer)
    end_time: Mapped[int] = Column(Integer, nullable=False)
    accepted: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    bundle: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    ended: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    auction_pokemon: Mapped[list[AuctionPokemon]] = relationship(back_populates='auction')
    auction_accepted: Mapped[list[AuctionAccepted]] = relationship(back_populates='auction')
    accepted_pokemon: Mapped[list['AcceptedPokemon']] = relationship(back_populates='auction')
    
    def __repr__(self):
        return f"<Auction id={self.id} channel_id={self.channel_id} ongoing_message_id={self.ongoing_message_id} user_id={self.user_id} current_bid={self.current_bid} bidder_id={self.bidder_id} auto_buy={self.auto_buy} end_time={self.end_time} accepted={self.accepted} bundle={self.bundle} ended={self.ended}>"

class Accepted(Base):
    __tablename__ = "accepted"
    
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = Column(Integer)
    
    pokemon: Mapped['Pokemon'] = relationship("Pokemon", back_populates='auction_accepted')
    
class AcceptedPokemon(Base):
    __tablename__ = "accepted_pokemon"
    
    accepted_id: Mapped[int] = Column(Integer, ForeignKey('accepted.id'), primary_key=True)
    pokemon_id: Mapped[int] = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    price: Mapped[int] = Column(Integer, nullable=False)
    
    pokemon: Mapped['Pokemon'] = relationship("Pokemon", back_populates='accepted_pokemon')
