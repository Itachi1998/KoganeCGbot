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
    colony_id: Mapped[int] 
    date_entered: Mapped[str]
    player_level: Mapped[int]
    player_name: Mapped[str] = mapped_column(String(200))
    player_equipped: Mapped[List] = mapped_column(JSON)
    player_inventory: Mapped[List] = mapped_column(JSON)
    max_hp: Mapped[int]
    hp: Mapped[int]
    max_ce: Mapped[int]
    ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    skp: Mapped[int]
    technique: Mapped[str]
    playerclass: Mapped[str] = mapped_column(String(100))
    killed: Mapped[Optional[List]] = mapped_column(JSON)
    six_eyes: Mapped[bool]
    __table_args__ = (
        UniqueConstraint('user_id', 'colony_id', name='uq_user_colony'),
    )

class Colony(Base):
    __tablename__ = "colony"
    id: Mapped[int] = mapped_column(primary_key=True)
    colony_name: Mapped[str]
    colony_id: Mapped[int]  = mapped_column(unique=True)
    creation_date: Mapped[str]
    color: Mapped[str]
    players: Mapped[Optional[int]] = mapped_column(JSON)  # Store player.user_id as a JSON string
    enemies: Mapped[Optional[List["Enemy"]]] = relationship(
        "Enemy", 
        back_populates="colony",
        cascade="all, delete-orphan"
    )
    items: Mapped[Optional[List]] = mapped_column(JSON)
    ce: Mapped[int]
    xp: Mapped[int]
    six_eyes: Mapped[bool]
    shop: Mapped[Optional[List]] = mapped_column(JSON)
    # rules: Mapped[Optional[List]] = mapped_column(JSON)
    # districts: Mapped[Optional[List]] = mapped_column(JSON)
    # graveyard: Mapped[Optional[List]] = mapped_column(JSON)
    leaderboard: Mapped[Optional[List]] = mapped_column(JSON)
    special_grades: Mapped[Optional[List]] = mapped_column(JSON)
    # events: Mapped[Optional[List]] = mapped_column(JSON)


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
    respawn: Mapped[Optional[int]]
   

    

class Technique(Base):
    __tablename__ = "technique"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int]
    rct: Mapped[bool]
    six_eyes: Mapped[bool]
    innate: Mapped[bool]
    user_id: Mapped[int]
    colony_id: Mapped[int]
    user_id: Mapped[int]
    binding_vows: Mapped[Optional[List]] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint('colony_id', 'user_id', 'name', name='uq_name_user_id')),




Base.metadata.create_all(bind=engine)


