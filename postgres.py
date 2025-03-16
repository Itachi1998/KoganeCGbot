import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, ForeignKey, String, func, Column
from sqlalchemy.orm import mapped_column, relationship, Mapped, DeclarativeBase, Session

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = f"postgresql+psycopg2://postgres:{passw}@localhost/postgres"

engine = create_engine(db_url)

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Player(Base):
    __tablename__ = "player"
    
    user_id: Mapped[int]
    colony_id: Mapped[int]
    player_level: Mapped[int]
    player_name: Mapped[str] =  mapped_column(str(200))
    player_equipped: Mapped[list]
    player_inventory: Mapped[list]
    max_hp: Mapped[int]
    hp: Mapped[int]
    max_ce: Mapped[int]
    ce: Mapped[int]
    cgp: Mapped[int]
    xp: Mapped[int]
    skp: Mapped[int]
    grade: Mapped[str] = mapped_column(str(100))
    technique: Mapped[list]
    playerclass: Mapped[str] = mapped_column(str(100))


class Colony(Base):
    __tablename__ = "colony"

    owner_id: Mapped[int]
    colony_id: Mapped[int]
    players: Mapped[list]
    enemies: Mapped[list]
    items: Mapped[list]
    ce: Mapped[list]
    xp: Mapped[list]
    shop: Mapped[list]
    rules: Mapped[list]
    districts: Optional[Mapped[list]]
    graveyard: Mapped[list]


def create_player(user_id, colony_id, playername, playerclass, technique, max_ce):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(user_id=user_id, colony_id=colony_id).first()
        if existing_player:
            raise ValueError("You cannot create more than one player per colony")
        
        new_player = Player(
            user_id=user_id,
            colony_id=colony_id,
            player_level=1
            player_name=playername,
            player_equipped=[],
            player_inventory=[],
            max_hp=100,
            hp=100,
            max_ce=100,
            ce=100,
            cgp=0,
            xp=0,
            skp=0,
            grade="Grade 4",
            technique=technique,
            playerclass=playerclass""
        )
        session.add(new_player)
        session.commit()