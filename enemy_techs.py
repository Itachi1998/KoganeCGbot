from techniques import Techniques

enemy_techs = {
    "Femhito" : # Femhito - special grade
        [
            {"Attack" :
                { "Callous Formation" : Techniques(
                    name="Soul Manipulation: Callous Formation",
                    level=1,
                    act_speed=2,
                    act_cost=50,
                    act_body=("hands", "legs"),
                    aoe=1,
                    strength=1000,
                    speed=600,
                    type="melee",
                    soul=200,
                    buff=(1, "strength", 200)
                    ),
                "Soul Transmute" : Techniques( # change the form or nature of the soul (self) - will need sub techniques for separate abilities
                    name="Soul Manipulation: Soul Transmute", 
                    level=1,
                    act_speed=1,
                    act_cost=50,
                    act_body=("full"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="melee"
                    )
                }   
            },
            {"Defense" :
                {"Body Morph" : Techniques( # will need sub techniques for separate abilities
                    name="Soul Manipulation : Body Morph",
                    level=1,
                    act_speed=1,
                    act_cost=50,
                    act_body=("hands","legs", "torso", "head"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="dodge" # wings/legs or smth
                    )
                }
            }
        ],
        
    "Orbmaster" : # grade 1
        [    
            {"Attack" : 
                {"Impending Doom" : Techniques(
                    name="Orbmaster: Impending Doom",
                    level=1,
                    act_speed=10,
                    act_cost=100,
                    act_body=("hands", "torso"),
                    aoe=1,
                    strength=420,
                    speed=100,
                    type="projectile", # attack projectile, attack melee
                    sure_hit=True
                    )
                }
            },
            {"Defense" :         
                {"Foresight" : Techniques(
                    name="Orbmaster: Foresight",
                    level=1,
                    act_speed=10,
                    act_cost=100,
                    act_body=("head"),
                    aoe=1,
                    strength=400,
                    speed=200,
                    type="counter", #defense tank, defense dodge, defense counter
                    sure_hit=True
                    )
                }
            }
        ],

    "Charger" : 
        [ 
            {"Attack" :
                {"Charged Punch" : Techniques(
                    name="Charger : Charged Punch",
                    level=1,
                    act_speed=3,
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=1,
                    strength=500,
                    speed=300,
                    buff=(2, 'strength', 100),
                    type="melee"
                    ),
                "Electric Ground-pound" : Techniques(
                    name="Charger : Electric Ground-pound",
                    level=1,
                    act_speed=3,
                    act_cost=50,
                    act_body=("right arm", "left arm"),
                    aoe=5,
                    strength=400,
                    speed=300,
                    type="projectile" # add a 'wave' or 'spread' type of attack?
                    )
                }
            },
            {"Defense" : 
                {"Charged Field" : Techniques(
                    name="Charger : Charged Field",
                    level=1,
                    act_speed=2,
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=5,
                    strength=400,
                    speed=500,
                    type="tank"
                    )
                }
            }
        ],

    "Stinkaspore" : # grade 2
        [
            {"Attack" : 
                {"Hydrogen Sulfide Bomb" : Techniques( # rotten egg smelling gas that can cause; unconsciousness, memory loss, death
                    name="Stinkaspore: Hydrogen Sulfide Bomb",
                    level=1,
                    act_speed=3,
                    act_cost=20,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=50,
                    speed=100,
                    type="poison",
                    poison=(range(10, 20), 2)
                    ),
                "Carbon Monoxide Disperse" : Techniques( # colorless odorless gas that can be fatal in high enough quantities
                    name="Stinkaspore : Carbon Monoxide Disperse",
                    level=1,
                    act_speed=3,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=100,
                    speed=100,
                    type="poison"
                    #sure_hit=True - Maybe
                    )
                }
            },
            {"Defense" :
                {"Ammonia Cloud" : Techniques( # can cause skin burns, respitory damage and is highly flammable
                    name="Stinkaspore : Ammonia Cloud", 
                    level=1,
                    act_speed=3,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=80,
                    speed=150,
                    type="counter"
                    )
                }
            }
        ],

    "Primate" : 
        [ 
            {"Attack" :
                {"Head Twirl" : Techniques(
                    name="Primate: Head Twirl",
                    level=1,
                    act_speed=2,
                    act_cost=30,
                    act_body=("Head", "Torso"),
                    aoe=1,
                    strength=200,
                    speed=500,
                    type="stun"
                    )
                }
            },
            {"Defense" :
                {"" : 
                 Techniques(
                    name="Swing around",
                    level=1,
                    act_speed=2,
                    act_cost=50,
                    act_body=("Head"),
                    aoe=5,
                    strength=300,
                    speed=400,
                    type="dodge"
                    )
                }
            }
        ]

}    
for k, v in enemy_techs.items():
    print(k,v)