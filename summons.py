from game import Enemy, human_body_parts
from techniques import Techniques


class Mahoraga(Enemy):
        
    def __init__(self):

    tech={
        "Attack" : 

            { 
                "Sword Swing" :
                Techniques(
                    name="Sword Swing",
                    level=1,
                    act_speed=1,
                    act_cost=1,
                    act_body=("Arms"),
                    aoe=1,
                    strength=1000,
                    speed=1000,
                    type="Melee",
                    buff=("strength")
                ),
                "RCT Sword Swing" : 
                Techniques(
                    name="RCT Sword Swing",
                    level=1,
                    act_speed=1,
                    act_cost=1,
                    act_body=("Arms"),
                    aoe=1,
                    strength=1000,
                    speed=1000,
                    type="Melee",
                    buff=("strength")
                ),
                "Adapt": 
                Techniques(
                    name="Adaptation",
                    level=1,
                    act_speed=1,
                    act_cost=1,
                    act_body=("Full Body"),
                    aoe=1,
                    strength=1500,
                    speed=1500,
                    type="Melee",
                    buff=("strength", "speed"),
                    negates=True,
                ),
                "Extermination Sword" : 
                Techniques(
                    name="Extermination Sword",
                    level=1,
                    act_speed=1,
                    act_cost=1,
                    act_body=("Arms"),
                    aoe=1,
                    strength=1000,
                    speed=1000,
                    type="Melee",
                    buff=("strength")
                )

            },
            
        "Defense" : 
        {
            "Adapt" :
            Techniques(
                name="Technique Adaptation",
                level=1,
                act_speed=1,
                act_cost=1,
                act_body=("Head"),
                aoe=1,
                strength=2000,
                speed=2000,
                type="Melee",
                buff=("strength", "speed"),
                negates=True,
                duration=5
                )
            }

    }
    
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

mahoraga = Mahoraga(name="Mahoraga",
            level=1,
            max_hp=1000,
            max_ce=1000,
            strength=1000,
            speed=1000,
            technique=None,
            playerclass="summon",
            colony=0,
            inventory=["Dharma Chakra Wheel"],
            equipped=["Dharma Chakra Wheel"],
            xp=10000,
            cgp=0,
            bodyparts=human_body_parts)

