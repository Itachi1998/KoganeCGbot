import os, json, models
from models import Player, Colony, Technique, Enemy, Base
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:///database.db"

engine = create_engine(db_url)

# Update create_player function

def create_player(user_id: int, colony_id: int, playername: str,
                  playerclass: str, technique: str, max_ce: int, max_hp: int, six_eyes: bool):
    with Session(engine) as session:
        existing_colony = session.query(Colony).filter_by(colony_id=colony_id).first()
        if not existing_colony:
            return False
        
        existing_player = session.query(Player).filter_by(user_id=user_id, colony_id=colony_id).first()
        if existing_player:
            return False
        
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
            playerclass=playerclass,
            six_eyes=six_eyes
        )
        
        session.add(new_player)
        # Flush to get the ID for the new player
        session.flush()
        new_tech = Technique(
            name=technique,
            level=1,
            rct=False,
            six_eyes=six_eyes,
            user_id=user_id,
            colony_id=colony_id,
            player=new_player,
        )
        
        session.add(new_tech)
        session.commit()
        return True

# Update create_colony function
def create_colony(colony_data, enemies):
    with Session(engine) as session:
        existing_colony = session.query(Colony).filter_by(colony_id=colony_data["colony id"]).first()
        if existing_colony:
            raise ValueError("Colony already exists")
        
        # Create colony without players and enemies initially
        colony = Colony(
            colony_name=colony_data['name'],
            colony_id=colony_data['colony id'],
            creation_date=colony_data['creation date'],
            color=colony_data['color'],
            ce=colony_data['ce'],
            xp=colony_data['xp'],
            six_eyes=colony_data['six eyes'],
            special_grades=colony_data.get('special_grades', [])
        )
        
        session.add(colony)
        session.flush()  # Flush to get the ID
        
        # Add enemies to colony
        for e in enemies:
            existing_enemy = session.query(Enemy).filter_by(
                colony_id=colony_data['colony id'], name=e.name
            ).first()
            
            if existing_enemy:
                raise ValueError("Enemy already exists")
            
            enemy = Enemy(
                name=e.name,
                level=e.level,
                max_hp=e.max_hp,
                hp=e.hp,
                max_ce=e.max_ce,
                ce=e.ce,
                strength=e.strength,
                speed=e.speed,
                technique=e.technique,
                colony_id=colony.colony_id,
                colony=colony,
                playerclass=e.playerclass,
                tamed=e.tamed,
                bodyparts=e.bodyparts,
                cgp=e.cgp,
                xp=e.xp
            )
            session.add(enemy)
        
        session.commit()
        return colony

# Update delete_player function
def delete_player(colony_id, user_id):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(colony_id=colony_id, user_id=user_id).first()
        if not existing_player:
            raise ValueError("Player does not exist")
        
        # No need to manually update colony.players, SQLAlchemy relationships handle this
        session.delete(existing_player)
        session.commit()
        return True

def create_technique(tech_data):
        with Session(engine) as session:
            existing_tech = session.query(Technique).filter_by(name=tech_data["name"], user_id=tech_data["user_id"]).first()
            if existing_tech:
                raise ValueError("Technique already exists")
            else:
                technique = Technique(
                    name=tech_data['name'],
                    level=tech_data['level'],
                    rct=tech_data['rct'],
                    six_eyes=tech_data['six eyes'],
                    innate=tech_data['innate'],
                    user_id=tech_data['user id'],
                    colony_id=tech_data['colony id'],
                    binding_vows=tech_data['binding vows']
                )
                session.add(technique)
                session.commit()
                session.close()
                return technique 
            

# Update check_relationship function
def check_relationship():
    with Session(engine) as session:
        colonies = session.query(Colony).all()
        for colony in colonies:
            print(f"Colony: {colony.colony_name} (ID: {colony.colony_id})")
            print(f"Players: {len(colony.players)}")
            print(f"Enemies: {len(colony.enemies)}")
            print(f"Shop items: {len(colony.shop)}")
        
        players = session.query(Player).all()
        for player in players:
            print(f"Player: {player.player_name} - Techniques: {len(player.techniques)}")

# Update read_technique function to match new model
def read_technique(techname: str, colony_id: int, user_id: int, value=None):
    with Session(engine) as session:
        existing_tech = session.query(Technique).filter_by(
            name=techname, colony_id=colony_id, user_id=user_id
        ).first()
        
        if existing_tech:
            if value:
                tech_data = {
                    column.name: getattr(existing_tech, column.name) 
                    for column in existing_tech.__table__.columns
                }
                session.close()
                return tech_data
            else:
                session.close()
                return existing_tech
        else:
            session.close()
            return False

def read_colony(colony_id: int, value=None):
            with Session(engine) as session:
                     existing_colony = session.query(Colony).filter_by(colony_id=colony_id).first()
                     if existing_colony:
                         if value:
                               session.close()
                               return {column.name: getattr(existing_colony, column.name) for column in existing_colony.__table__.columns}
                         else:
                               session.close()
                               return existing_colony
                     else:
                         session.close()
                         return False

def read_player(user_id: int, colony_id: int, value=None):
        with Session(engine) as session:
                existing_player = session.query(Player).filter_by(user_id=user_id, colony_id=colony_id).first()
                if existing_player:
                        if value:
                            session.close()
                            return {column.name: getattr(existing_player, column.name) for column in existing_player.__table__.columns}
                        else:
                            session.close()
                            return existing_player
                else:
                        session.close()
                        return False
                
def read_enemy(colony_id: int, value=None):
        with Session(engine) as session:
                existing_enemy = session.query(Enemy).filter_by(colony_id=colony_id).first()
                if existing_enemy:
                        for e in Enemy.__subclasses__:
                             if e.name == existing_enemy.name:
                                  enemy=Enemy(**existing_enemy)
                                  return enemy
                        else:
                            session.close()
                            return True
                else:
                        session.close()
                        return False

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
               return False
          
          for key, val in value.items():
               setattr(existing_colony, key, val)
        
          session.commit()
          session.close()
          return True
     
def update_technique(colony_id, user_id, value=None):
     with Session(engine) as session:
          existing_tech= session.query(Technique).filter_by(colony_id=colony_id, user_id=user_id).first()
          if not existing_tech:
               return False
          for key, val in value.items():
               setattr(existing_tech, key, val)
        
          session.commit()
          session.close()
          return existing_tech
     
def update_enemy(colony_id, value=None):
        with Session(engine) as session:
            existing_enemy = session.query(Enemy).filter_by(colony_id=colony_id).first()
            if not existing_enemy:
                return False
            for key, val in value.items():
                setattr(existing_enemy, key, val)
            
            session.commit()
            session.close()
            return True

def delete_player(colony_id, user_id):
    with Session(engine) as session:
        existing_player = session.query(Player).filter_by(colony_id=colony_id, user_id=user_id).first()
        existing_colony = session.query(Colony).filter_by(colony_id=colony_id).first()
        if not existing_player:
            raise ValueError("Player does not exist")
        existing_players = existing_colony.players
        if user_id in existing_players:
            existing_players.remove(int(user_id))
            update_colony(colony_id, {"players": existing_players})
        else:
            raise ValueError("User ID not found in the players list")
        session.delete(existing_player)
        session.commit()
        session.close()
        return True
    
def delete_enemy(colony_id, user_id):
    with Session(engine) as session:
        existing_enemy = session.query(Enemy).filter_by(colony_id=colony_id, tamed=user_id).first()
        if not existing_enemy:
            return False
        session.delete(existing_enemy)
        session.commit()
        session.close()
        return True



def delete_colony(colony_id, user_id):
     with Session(engine) as session:
          existing_colony= session.query(Colony).filter_by(colony_id=colony_id).first()
          if not existing_colony:
               return False
          session.delete(existing_colony)
          session.commit()
          session.close()
          return True
     
def delete_technique(colony_id, user_id):
     with Session(engine) as session:
          existing_tech= session.query(Technique).filter_by(colony_id=colony_id, user_id=user_id).first()
          if not existing_tech:
               return False
          session.delete(existing_tech)
          session.commit()
          session.close()
          return True