from game import Enemy, human_body_parts
from techniques import Techniques


class Mahoraga(Enemy):
        
    def __init__(self):
        super().__init__(
            name="Mahoraga",
            level=1,
            max_hp=1000,
            max_ce=1000,
            strength=1000,
            speed=1000,
            technique="Mahoraga",
            playerclass="summon",
            colony=0,
            inventory=["Dharma Chakra Wheel"],
            equipped=["Dharma Chakra Wheel"],
            xp=10000,
            cgp=0,
            bodyparts=human_body_parts
        )


mahoraga = Mahoraga()