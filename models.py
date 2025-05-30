from __future__ import annotations
import os
from typing import List, Optional
from sqlalchemy import create_engine, String, JSON, UniqueConstraint, ForeignKey, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:///database.db"

engine = create_engine(db_url)

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__="user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    players: Mapped[List["Player"]] = relationship("Player", back_populates="user", cascade="all, delete-orphan")
    # cosmetics: Mapped[Optional[List]] = relationship("Cosmetics", back_populates="user_id", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'id', name='uq_user_id'),
    )


class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship("User", back_populates="players")
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony", back_populates="players")
    # rank: Mapped[Optional['Leaderboard']] = relationship("Leaderboard", back_populates="player", cascade="all, delete-orphan")
    entered: Mapped[str]
    level: Mapped[int]
    name: Mapped[str] = mapped_column(String(200))
    equipped: Mapped[List] = mapped_column(JSON)
    # inventory: Mapped[List["Inventory"]] = relationship(
    #     "Inventory", back_populates="player", cascade="all, delete-orphan"
    # )
    max_hp: Mapped[int]
    max_ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    skp: Mapped[int]
    strength: Mapped[int]
    speed: Mapped[int]
    techniques: Mapped[Optional[List["Technique"]]] = relationship("Technique", back_populates="player", cascade="all, delete-orphan")
    playerclass: Mapped[str] = mapped_column(String(100))
    six_eyes: Mapped[bool]
    __table_args__ = (
        UniqueConstraint('user_id', 'colony_id', 'id', name='uq_user_colony'),
    )

class Colony(Base):
    __tablename__ = "colony"
    id: Mapped[int] = mapped_column(primary_key=True)
    colony_name: Mapped[str]
    colony_id: Mapped[int] = mapped_column(unique=True)
    creation_date: Mapped[str]
    color: Mapped[str]
    players: Mapped[List["Player"]] = relationship("Player", back_populates="colony")
    enemies: Mapped[List["Enemy"]] = relationship("Enemy", back_populates="colony")
    # shop: Mapped[List["Shop"]] = relationship(
    #     "Shop", back_populates="colony", cascade="all, delete-orphan"
    # )
    # leaderboard: Mapped[List["Leaderboard"]] = relationship(
    #     "Leaderboard", back_populates="colony", cascade="all, delete-orphan"
    # )
    ce: Mapped[int]
    xp: Mapped[int]
    six_eyes: Mapped[bool]
    __table_args__ = (
        UniqueConstraint('colony_id', 'id', name='uq_colony_id_name'),
    )
    # Remove redundant JSON leaderboard column




# class Shop(Base):
#     __tablename__ = "shop"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     level: Mapped[int]
#     max_hp: Mapped[Optional[int]]
#     max_ce: Mapped[Optional[int]]
#     cost: Mapped[int]
#     owned: Mapped[bool]
#     owner: Mapped[Optional[int]]
#     type: Mapped[str]
#     colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
#     colony: Mapped["Colony"] = relationship("Colony", back_populates="shop")
#     player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("player.id"))
#     player: Mapped[Optional["Player"]] = relationship("Player", back_populates="shop")

    

# class ShopHistory(Base):
#     __tablename__ = "shop_history"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     shop_id: Mapped[int] = mapped_column(ForeignKey("shop.id"))
#     shop: Mapped["Shop"] = relationship("Shop", back_populates="history")
#     player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
#     player: Mapped["Player"] = relationship("Player", back_populates="shop_history")
#     action: Mapped[str]
#     item_name: Mapped[str]
#     item_type: Mapped[str]
#     item_id: Mapped[int]
#     quantity: Mapped[int]
#     cost: Mapped[int]
#     date: Mapped[str]
#     __table_args__ = (
#         UniqueConstraint('shop_id', 'player_id', 'action', 'item_name', 'item_type', 'item_id', 'quantity', 'cost', name='uq_shop_history'),
#         )



class Enemy(Base):
    __tablename__ = "enemy"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]
    xp: Mapped[int]
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony", back_populates="enemies")
    killed: Mapped[Optional[bool]]
    tamed: Mapped[Optional[int]]
    killcount: Mapped[Optional[int]]

# class Leaderboard(Base):
#     __tablename__ = "leaderboard"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     player: Mapped["Player"] = relationship("Player", back_populates="rank")
#     colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
#     colony: Mapped[Colony] = relationship(Colony, back_populates=("leaderboard"))
#     rank: Mapped[int]

class Technique(Base):
    __tablename__ = "technique"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    player: Mapped["Player"] = relationship("Player", back_populates="techniques")
    name: Mapped[str]


# class Cosmetics(Base):
#     __tablename__ = "cosmetics"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
#     item_name: Mapped[str]
#     item_type: Mapped[str]
#     quantity: Mapped[int]
#     item_url: Mapped[str]

# class Inventory(Base):
#     __tablename__ = "inventory"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
#     player: Mapped["Player"] = relationship("Player", back_populates="inventory")
#     item_name: Mapped[str]
#     item_type: Mapped[str]
#     item_id: Mapped[int]
#     max_hp: Mapped[Optional[int]]
#     max_ce: Mapped[Optional[int]]
#     hp: Mapped[Optional[int]]
#     ce: Mapped[Optional[int]]
#     cost: Mapped[int]
#     owned: Mapped[bool]
#     equipped: Mapped[bool]
#     sale:   Mapped[Optional[bool]]
#     __table_args__ = (
#         UniqueConstraint( 'player_id','item_id', name='uq_player_item_id'),
#     )

Base.metadata.create_all(bind=engine)


