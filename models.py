import os, json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:///kogane.db"

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
    player_inventory: Mapped[List]  = mapped_column(JSON)
    max_hp: Mapped[int]
    hp: Mapped[int]
    max_ce: Mapped[int]
    ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    skp: Mapped[int]
    technique: Mapped[List[str]] = mapped_column(JSON)
    playerclass: Mapped[str] = mapped_column(String(100))
    six_eyes: Mapped[bool]
    # buffs: Mapped[Optional[List]] = mapped_column(JSON)
    # debuffs: Mapped[Optional[List]] = mapped_column(JSON)
    # heals: Mapped[Optional[List]] = mapped_column(JSON)
    # kills: Mapped[Optional[List]] = mapped_column(JSON)
    # bodyparts: Mapped[Optional[List]] = mapped_column(JSON)


class Colony(Base):
    __tablename__ = "colony"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    colony_name: Mapped[str]
    colony_id: Mapped[int]
    owner_id: Mapped[int]
    creation_date: Mapped[str]
    color: Mapped[str]
    players: Mapped[Optional[List]] = mapped_column(JSON)
    enemies: Mapped[Optional[List]] = mapped_column(JSON)
    items: Mapped[Optional[List]] = mapped_column(JSON)
    ce: Mapped[int]
    xp: Mapped[int]
    six_eyes: Mapped[bool]
    shop: Mapped[Optional[List]] = mapped_column(JSON)
    rules: Mapped[Optional[List]] = mapped_column(JSON)
    districts: Mapped[Optional[List]] = mapped_column(JSON)
    graveyard: Mapped[Optional[List]] = mapped_column(JSON)
    leaderboard: Mapped[Optional[List]] = mapped_column(JSON)
    special_grades: Mapped[Optional[List]] = mapped_column(JSON)
    events: Mapped[Optional[List]] = mapped_column(JSON)

Base.metadata.create_all(bind=engine)
