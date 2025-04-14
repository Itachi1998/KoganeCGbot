import os, json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, String, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session, relationship

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:///database.db"

engine = create_engine(db_url)

class Base(DeclarativeBase):
    pass

class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony", back_populates="players")
    rank: Mapped[Optional['ColonyLeaderboard']] = relationship("ColonyLeaderboard", back_populates="player", cascade="all, delete-orphan")
    entered: Mapped[str]
    level: Mapped[int]
    name: Mapped[str] = mapped_column(String(200))
    equipped: Mapped[List] = mapped_column(JSON)
    inventory: Mapped[List] = mapped_column(JSON)
    max_hp: Mapped[int]
    hp: Mapped[int]
    max_ce: Mapped[int]
    ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    skp: Mapped[int]
    strength: Mapped[int]
    speed: Mapped[int]
    techniques: Mapped[Optional[List["Technique"]]] = relationship("Technique", back_populates="player", cascade="all, delete-orphan")
    playerclass: Mapped[str] = mapped_column(String(100))
    six_eyes: Mapped[bool]
    __table_args__ = (
        UniqueConstraint('user_id', 'colony_id', name='uq_user_colony'),
    )

class Colony(Base):
    __tablename__ = "colony"
    id: Mapped[int] = mapped_column(primary_key=True)
    colony_name: Mapped[str]
    colony_id: Mapped[int] = mapped_column(unique=True)
    creation_date: Mapped[str]
    color: Mapped[str]
    players: Mapped[List["Player"]] = relationship("Player", back_populates="colony", cascade="all, delete-orphan")
    enemies: Mapped[List["Enemy"]] = relationship("Enemy", back_populates="colony", cascade="all, delete-orphan")
    shop: Mapped[List["Shop"]] = relationship("Shop", back_populates="colony", cascade="all, delete-orphan")
    leaderboard: Mapped[List["ColonyLeaderboard"]] = relationship("ColonyLeaderboard", back_populates="colony", cascade="all, delete-orphan")
    ce: Mapped[int]
    xp: Mapped[int]
    six_eyes: Mapped[bool]
    # Remove redundant JSON leaderboard column
    special_grades: Mapped[Optional[List]] = mapped_column(JSON)


class Technique(Base):
    __tablename__ = "technique"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]
    rct: Mapped[bool]
    six_eyes: Mapped[bool]
    user_id: Mapped[int] = mapped_column(ForeignKey("player.user_id"))
    player: Mapped["Player"] = relationship("Player", back_populates="techniques")
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony")
    __table_args__ = (UniqueConstraint('colony_id', 'user_id', 'name', name='uq_name_user_id')),


class Shop(Base):
    __tablename__ = "shop"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]
    max_hp: Mapped[Optional[int]]
    hp: Mapped[Optional[int]]
    max_ce: Mapped[Optional[int]]
    ce: Mapped[Optional[int]]
    cost: Mapped[int]
    owned: Mapped[bool]
    owner: Mapped[Optional[int]]
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony", back_populates="shop")
    
class Enemy(Base):
    __tablename__ = "enemy"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]
    max_hp: Mapped[int]
    hp: Mapped[int]
    max_ce: Mapped[int]
    ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    strength: Mapped[int]
    speed: Mapped[int]
    technique: Mapped[str]
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped["Colony"] = relationship("Colony", back_populates="enemies")
    playerclass: Mapped[str] = mapped_column(String(100))
    killed: Mapped[Optional[bool]]
    tamed: Mapped[Optional[int]]
    bodyparts: Mapped[Optional[List]] = mapped_column(JSON)
   

class ColonyLeaderboard(Base):
    __tablename__ = "leaderboard"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("player.user_id"))
    player: Mapped["Player"] = relationship("Player", back_populates="rank")
    colony_id: Mapped[int] = mapped_column(ForeignKey("colony.colony_id"))
    colony: Mapped[Colony] = relationship(Colony, back_populates=("leaderboard"))
    rank: Mapped[int]
Base.metadata.create_all(bind=engine)


