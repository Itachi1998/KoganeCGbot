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


class Technique(Base):
    __tablename__ = 'technique'
    name: Mapped[str] = mapped_column(String(255))
    ct_level: Mapped[int] = mapped_column()
    domain: Mapped[Optional[int]] = mapped_column(nullable=True)
    maximum: Mapped[Optional[int]] = mapped_column(nullable=True)
    rct: Mapped[Optional[int]] = mapped_column(nullable=True)
    poison: Mapped[Optional[int]] = mapped_column(nullable=True)
    shikigami: Mapped[Optional[int]] = mapped_column(nullable=True)
    cursed_spirits: Mapped[Optional[int]] = mapped_column(nullable=True)
    souls: Mapped[Optional[int]] = mapped_column(nullable=True)
    
class Colony(Base):
    __tablename__ = 'colony'
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column()
    colony_id: Mapped[int] = mapped_column()
    
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))

    enemy_id: Mapped[int] = mapped_column(ForeignKey('enemy.id'))

    technique_id: Mapped[int] = mapped_column(ForeignKey("technique.id"))

    tech: Mapped[List["Technique"]] = relationship("Technique", backref="colony")
    players: Mapped[List["Player"]] = relationship("Player", backref="colony")
    enemies: Mapped[List['Enemy']] = relationship("Enemy", backref="colony")

class Player(Base):
    __tablename__ = 'player'
    name: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column()
    level: Mapped[int] = mapped_column()

    def __repr__(self):
        return f"Player {self.name} is level {self.level}"

class Enemy(Base):
    __tablename__ = 'enemy'
    name: Mapped[str] = mapped_column()
    level: Mapped[int] = mapped_column()
 
# Create tables
Base.metadata.create_all(engine)

# Create a session
session = Session(engine)

# Add data to the tables
colony1 = Colony(
    name="Colony1",
    owner_id=1,
    colony_id=1,
    player_id=1,
    enemy_id=1,
    technique_id=2
)

colony2 = Colony(
    name="Colony2",
    owner_id=2,
    colony_id=2,
    player_id=2,
    enemy_id=2,
    technique_id=3,
)

player1 = Player(
    name="Player1",
    user_id=1,
    level=1
)

player2 = Player(
    name="Player2",
    user_id=2,
    level=2
)

player3 = Player(
    name="Player3",
    user_id=3,
    level=3
)

enemy1 = Enemy(
    name="Enemy1",
    level=1
)

enemy2 = Enemy(
    name="Enemy2",
    level=2
)

enemy3 = Enemy(
    name="Enemy3",
    level=3
)


technique1 = Technique(
    name="Technique1",
    ct_level=1,
    domain=None,
    maximum=None,
    rct=None,
    poison=None,
    shikigami=None,
    cursed_spirits=None,
    souls=None
)

technique2 = Technique(
    name="Technique2",
    ct_level=2,
    domain=1,
    maximum=2,
    rct=3,
    poison=4,
    shikigami=5,
    cursed_spirits=6,
    souls=7
)

technique3 = Technique(
    name="Technique3",
    ct_level=2,
    domain=3,
    maximum=2,
    rct=3,
    poison=4,
    shikigami=5,
    cursed_spirits=6,
    souls=7
)
session.add_all([technique1, technique2])

session.add_all([colony1, colony2, player1, player2, player3, enemy1, enemy2, enemy3, technique1, technique2, technique3])
session.commit()
session.close()



