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
    six_eyes: Mapped[bool]


class Colony(Base):
    __tablename__ = "colony"

    owner_id: Mapped[int]
    colony_id: Mapped[int]
    players: Mapped[list]
    enemies: Mapped[list]
    items: Mapped[list]
    ce: Mapped[int]
    xp: Mapped[int]
    shop: Mapped[list]
    rules: Mapped[list]
    districts: Optional[Mapped[list]]
    graveyard: Mapped[list]
    six_eyes: Mapped[bool]


def create_player(user_id, colony_id, playername, playerclass, technique, max_ce, max_hp, six_eyes):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(user_id=user_id, colony_id=colony_id).first()
        if existing_player:
            raise ValueError("You cannot create more than one player per colony")
        grade="Grade 4"
        if six_eyes==True:
            grade="Special Grade"
        col = session.query(Colony).filter_by(colony_id=colony_id).first()

        new_player = Player(
            user_id=user_id,
            colony_id=colony_id,
            player_level=1
            player_name=playername,
            player_equipped=[],
            player_inventory=[],
            max_hp=max_hp,
            hp=max_hp
            max_ce=max_ce,
            ce=max_ce,
            cgp=0,
            xp=0,
            skp=0,
            grade=grade,
            technique=technique,
            playerclass=playerclass,
            six_eyes=six_eyes
        )
        col.players.append(new_player.user_id)
        session.add(new_player)
        session.commit()
        session.close()
        
def create_colony(colony_id, owner_id, districts=None):
        with Session(engine) as session:
             existing_colony = session.query(Colony).filter_by(colony_id=colony_id).first()
             if existing_colony:
                  raise ValueError("Colony already exists")
             else:
                  new_colony=Colony(
                       colony_id=colony_id,
                       owner_id=owner_id,
                       players=[],
                       enemies=[]
                       items=[],
                       ce=0,
                       xp=0,
                       shop=[],
                       rules=[],
                       graveyard=[],
                       districts=districts
                       graveyard=[],
                       six_eyes=False
                  )


def read_colony(colony_id, value=None):
     with Session(engine) as session:
          existing_colony= session.query(Colony).filter_by(colony_id).first()
          if existing_colony:
               if value:
                    session.close()
                    return getattr(existing_colony, value)

               else:
                    session.close()
                    return existing_colony
          else:
               session.close()
               raise ValueError("Error reading colony_id. Colony does not exist")

def read_player(player_id, user_id, colony_id, value=None):
        with Session(engine) as session:
       
                existing_player = session.query(Player).filter_by(id=player_id, user_id=user_id, colony_id=colony_id).first()
                if existing_player:
                        if value:
                            session.close()
                            return {column.name: getattr(existing_player, column.name) for column in existing_player.__table__.columns}
                        else:
                            session.close()
                            return existing_player
                else:
                        session.close()
                        raise ValueError("Error reading player. Player does not exist")
                
                
def update_player(user_id, colony_id, value=None):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(user_id=user_id, colony_id=colony_id).first()
        if not existing_player:
            raise ValueError("Player does not exist")
        
        for key, val in value.items():
            setattr(existing_player, key, val)

        session.commit()
        session.close()
        return existing_player

def update_colony(colony_id, value=None):
     with Session(engine) as session:
          existing_colony= session.query(Colony).filter_by(colony_id=colony_id).first()
        
          if not existing_colony:
               raise ValueError("Colony does not exist")

          for key, val in value.items():
               setattr(existing_colony, key, val)
        
          session.commit()
          session.close()
          return existing_colony

def del_player(colony_id, user_id):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(colony_id=colony_id, user_id=user_id).first()

        if not existing_player:
            raise ValueError("Player does not exist")
        
        session.delete(existing_player)
        session.commit()
        session.close()


def del_colony(colony_id, user_id):
     with Session(engine) as session:
          existing_colony= session.query(Colony).filter_by(colony_id=colony_id).first()
          if not existing_colony:
               raise ValueError("Colony does not exist")
          session.delete(existing_colony)
          session.commit()
          session.close()