import os, json, models
from models import Player, Colony, Technique, Enemy, User
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload

from dotenv import find_dotenv, load_dotenv
dotfile = find_dotenv('.env')
loaded = load_dotenv(dotfile)
passw = os.getenv('PASS')

db_url = "sqlite:///database.db"

engine = create_engine(db_url)

# Update create_player function

def create_player(player):
    with Session(engine) as session:
        existing_colony = session.query(Colony).filter_by(colony_id=player.colony).first()
        if not existing_colony:
            return False
        
        existing_player = session.query(Player).filter_by(user_id=player.user_id, colony_id=player.colony).first()
        if existing_player:
            return False
        
        new_player = Player(
            user_id=player.user_id,
            colony_id=player.colony,
            entered=datetime.now().astimezone().strftime("%c"),
            level=1,
            name=player.name,
            equipped=player.equipped,
            # inventory=player.inventory,
            max_hp=player.max_hp,
            max_ce=player.max_ce,
            speed=player.speed,
            strength=player.strength,
            cgp=player.cgp,
            xp=player.xp,
            skp=player.skp,
            playerclass=player.playerclass,
            six_eyes=player.six_eyes
        )
        new_tech = Technique(name=player.technique,
            player=new_player
        )
        existing_user = session.query(User).filter_by(user_id=player.user_id).first()
        session.add(new_player)
        session.add(new_tech)
        if existing_user:
            # If the user already exists, just append the new player to the existing user's players
            existing_user.players.append(new_player)
        else:   
            new_user = User(
                user_id = player.user_id,
                players=[new_player]
            )
            session.add(new_user)
            
        
        
        # Flush to get the ID for the new player
        session.flush()
        
        # No need to manually append since we already set player=new_player
        # new_player.techniques.append(new_tech)
        
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
            # special_grades=colony_data.get('special_grades', [])
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
            
            enemy = Enemy(name=e.name,
                          level=e.level,
                          xp=e.xp,
                          colony_id=colony.colony_id,
                          killed=False,
                          killcount=0
                            )
            if int(enemy.level) >= 100:
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
        session.close()
        return True
    
def delete_user(user_id):
    with Session(engine) as session:
        existing_user = session.query(User).filter_by(user_id=user_id).first()
        if not existing_user:
            raise ValueError("User does not exist")
        # No need to manually update colony.players, SQLAlchemy relationships handle this
        session.delete(existing_user)
        session.commit()
        session.close()
        return True

def create_technique(tech_data):
        with Session(engine) as session:
            existing_tech = session.query(Technique).filter_by(name=tech_data["name"], user_id=tech_data["user_id"]).first()
            if existing_tech:
                raise ValueError("Technique already exists")
            else:
                technique = Technique(
                    name=tech_data['name'],
                    # level=tech_data['level'],
                    # rct=tech_data['rct'],
                    # six_eyes=tech_data['six eyes'],
                    user_id=tech_data['user id'],
                #     colony_id=tech_data['colony id']
                )
                session.add(technique)
                session.commit()
                session.close()
                return technique 
            
def create_vow(vow_data: dict):
    with Session(engine) as session:
        existing_vow = session.query(Technique).filter_by(name=vow_data["name"], user_id=vow_data["user_id"]).first()
        if existing_vow:
            raise ValueError("Vow already exists")
        else:
            vow = Technique(
                name=vow_data['name'],
                level=vow_data['level'],
                rct=vow_data['rct'],
                user_id=vow_data['user id'],
                colony_id=vow_data['colony id']
            )
            session.add(vow)
            session.commit()
            session.close()
            return vow
# Update read_technique function to match new model
def read_technique(player_id, value=None):
    with Session(engine) as session:
        existing_tech = session.query(Technique).filter_by(
            player_id = player_id
        ).first()
        if not existing_tech:
             return False
        tech_data = {
            column.name: getattr(existing_tech, column.name)
            for column in existing_tech.__table__.columns
        }
        return tech_data
    
def read_user(user_id: int, value=None):
    with Session(engine) as session:
        # filter by the actual column instead of Ellipsis
        u = (
            session.query(User)
                   .options(joinedload(User.players))
                   .filter_by(user_id=user_id)
                   .first()
        )

        if not u:
             return False

        if value:
             return {
                **{c.name: getattr(u, c.name) for c in u.__table__.columns},
                "players": [
                   {c.name: getattr(p, c.name) for c in p.__table__.columns}
                   for p in u.players
                ]
             }
        else:
             return u
        
def read_colony(colony_id: int, value=None):
            with Session(engine) as session:
                    existing_colony = session.query(Colony).options(
                        joinedload(Colony.enemies)
                    ).filter_by(colony_id=colony_id).first()
                    if existing_colony:
                         if value:
                               session.close()
                               return {column.name: getattr(existing_colony, column.name) for column in existing_colony.__table__.columns}
                         else:
                               return existing_colony
                    else:
                         session.close()
                         return False

def read_player(user_id, colony_id, value=None):
    with Session(engine) as session:
        existing_player = session.query(Player)\
                                 .options(joinedload(Player.techniques))\
                                 .filter_by(user_id=user_id, colony_id=colony_id)\
                                 .first()
        
        if existing_player:
            if value:
                player_dict = {column.name: getattr(existing_player, column.name) for column in existing_player.__table__.columns}
                player_dict['techniques'] = [
                    {column.name: getattr(tech, column.name) for column in tech.__table__.columns}
                    for tech in existing_player.techniques
                ]

                session.close()
                return player_dict
            else:
                player_dict = {column.name: getattr(existing_player, column.name) for column in existing_player.__table__.columns}
                player_dict['techniques'] = [
                    {column.name: getattr(tech, column.name) for column in tech.__table__.columns}
                    for tech in existing_player.techniques
                ]
                session.close()
                return player_dict
        else:
            session.close()
            return False
                
def read_enemy(colony_id: int, enemy_name: str):
    with Session(engine) as session:
        query = session.query(Enemy).filter_by(colony_id=colony_id, name=enemy_name)
        existing_enemy = query.first()
        if existing_enemy:
            enemy_dict = {column.name: getattr(existing_enemy, column.name) 
                         for column in existing_enemy.__table__.columns}
            del enemy_dict['id']
            session.close()
            return enemy_dict
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
     
def delete_technique(player_id):
     with Session(engine) as session:
          existing_tech= session.query(Technique).filter_by(player_id = player_id).first()
          if not existing_tech:
               return False
          session.delete(existing_tech)
          session.commit()
          session.close()
          return True