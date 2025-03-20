import os, json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:////kgc.db"

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
    technique: Mapped[List[str]] = mapped_column(JSON)
    playerclass: Mapped[str] = mapped_column(String(100))
    six_eyes: Mapped[bool]
    buffs: Mapped[Optional[List]] = mapped_column(JSON)
    debuffs: Mapped[Optional[List]] = mapped_column(JSON)
    heals: Mapped[Optional[List]] = mapped_column(JSON)
    kills: Mapped[Optional[List]] = mapped_column(JSON)


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



def create_player(user_id: int, colony_id: int, playername: str, playerclass:str, technique: str, max_ce: int, max_hp: int, six_eyes:bool):
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
            date_entered=datetime.now().astimezone().strftime("%c"),
            player_level=1,
            player_name=playername,
            player_equipped=[],
            player_inventory=[],
            max_hp=max_hp,
            hp=max_hp,
            max_ce=max_ce,
            ce=max_ce,
            cgp=0,
            xp=0,
            skp=0,
            grade=grade,
            technique=technique,
            playerclass=playerclass,
            six_eyes=six_eyes,
            buffs=[],
            debuffs=[],
            heals=[],
            kills=[]
        )
        col.players.append(new_player.user_id)
        session.add(new_player)
        session.commit()
        session.close()
        
def create_colony(colony_data):
        with Session(engine) as session:
             existing_colony = session.query(Colony).filter_by(colony_id=colony_id).first()
             if existing_colony:
                  raise ValueError("Colony already exists")
             else:
                colony = Colony(
                    colony_name=colony_data['name'],
                    colony_id=colony_data['colonyid'],
                    creation_date=colony_data['creation date'],
                    owner_id=colony_data['owner id'],
                    color=colony_data['color'],
                    players=json.dumps(colony_data.get('players', [])),
                    enemies=json.dumps(colony_data.get('enemies', [])),
                    items=json.dumps(colony_data.get('items', [])),
                    ce=colony_data['ce'],
                    xp=colony_data['xp'],
                    six_eyes=colony_data['six eyes'],
                    shop=json.dumps(colony_data.get('shop', [])),
                    rules=json.dumps(colony_data.get('rules', [])),
                    districts=json.dumps(colony_data.get('districts', [])),
                    graveyard=json.dumps(colony_data.get('graveyard', [])),
                    leaderboard=json.dumps(colony_data.get('leaderboard', [])),
                    special_grades=json.dumps(colony_data.get('special_grades', [])),
                    events=json.dumps(colony_data.get('events', []))
                )
                session.add(colony)
                session.commit()
                session.close()

def read_colony(colony_id, value=None):
     with Session(engine) as session:
          existing_colony= session.query(Colony).filter_by(colony_id=colony_id).first()
          if value:
                    session.close()
                    return getattr(existing_colony, value)

          else:
                    session.close()
                    return existing_colony
    

def read_player(player_id: int, user_id: int, colony_id: int, value=None):
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