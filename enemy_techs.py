from techniques import Techniques

enemy_tech = {
#region Divine Dog
"Divine Dog" : 
[
    {'Attack' : 
     {
         "Divine Claw" : 
         Techniques(
             name="Divine Claw",
             level=1,
             act_speed=1,
             act_cost=10,
             act_body=("Head"),
             aoe=1,
             strength=200,
             speed=400,
             type="melee"
         ),
         "Divine Bite":
         Techniques(
             name="Divine Bite",
             level=2,
             act_speed=2,
             act_cost=10,
             act_body=("Head"),
             aoe=1,
             strength=300,
             speed=300,
             type="melee"
        )
    }},
    {"Defense" : {
        "Divine Claw" : 
         Techniques(
             name="Divine Claw",
             level=1,
             act_speed=1,
             act_cost=10,
             act_body=("Head"),
             aoe=1,
             strength=200,
             speed=400,
             type="counter"
         ),
         "Divine Bite":
         Techniques(
             name="Divine Bite",
             level=2,
             act_speed=2,
             act_cost=10,
             act_body=("Head"),
             aoe=1,
             strength=300,
             speed=300,
             type="counter"
        )  
    }}
],
#endregion
#region Rabbit Escape
"Rabbit Escape" : 
[
    {'Attack' : 
     {
         "Rabbit Kung Fu" : 
         Techniques(
             name="Rabbit Kung Fu",
             level=1,
             act_speed=1,
             act_cost=25,
             act_body=("Full"),
             aoe=1,
             strength=10,
             speed=500,
             type="melee"
         )
     }},
     {"Defense" : {
       "Escape" : 
       Techniques(
            name="Escape",
            level=1,
            act_speed=1,
            act_cost=25,
            act_body=("Full"),
            aoe=1,
            strength=10,
            speed=500,
            type="dodge",
            invisable=True
       )
     }}
],
#endregion
#region Toad
"Toad" : 
[
    {'Attack' : 
     {
         "Frog Grab" : 
         Techniques(
             name="Frog Grab",
             level=1,
             act_speed=1,
             act_cost=30,
             act_body=("Head"),
             aoe=1,
             strength=50,
             speed=600,
             type="projectile",
             stun=1
         ),
         "Frog Throw":
         Techniques(
             name="Frog Throw",
             level=2,
             act_speed=2,
             act_cost=5,
             act_body=("Head"),
             aoe=2,
             strength=200,
             speed=600,
             type="melee",
             charge=True,
         )
     }},
     {"Defense" : {
       "Frog Grab" : 
       Techniques(
           name="Frog Grab",
           level=1,
             act_speed=1,
             act_cost=30,
             act_body=("Head"),
             aoe=1,
             strength=50,
             speed=600,
             type="counter",
             stun=1,
       ),
       "Frog Hop" : 
       Techniques(
           name="Frog Hop",
           level=1,
           act_speed=1,
           act_cost=5,
           act_body=("Head"),
           aoe=1,
           strength=10,
           speed=600,
           type="dodge",
       )  }}
],
#endregion
#region Nue
"Nue" : 
[
    {'Attack' : 
     {
         "Lighting Dive" : 
         Techniques(
             name="Lighting Dive",
             level=1,
             act_speed=2,
             act_cost=50,
             act_body=("Full"),
             aoe=1,
             strength=300,
             speed=500,
             type="melee"
         )
     }},
     {"Defense" : {
       "Hitch A Ride" : 
       Techniques(
            name="Hitch A Ride",
            level=1,
            act_speed=2,
            act_cost=25,
            act_body=("Full"),
            aoe=1,
            strength=10,
            speed=500,
            type="dodge"
       )
     }}
],
#endregion
#region Great Serpent
"Great Serpent" : 
[
    {'Attack' : 
     {
         "Choke" : 
         Techniques(
            name="Choke",
            level=1,
            act_speed=1,
            act_cost=50,
            act_body=("Full"),
            aoe=1,
            strength=300,
            speed=500,
            type="melee"
         )
     }},
     {"Defense" : {
       "Choke" : 
         Techniques(
            name="Choke",
            level=1,
            act_speed=1,
            act_cost=50,
            act_body=("Full"),
            aoe=1,
            strength=300,
            speed=500,
            type="counter"
         )
     }}
],
#endregion
#region Max Elephant
"Max Elephant" : 
[
    {'Attack' : 
     {
        "Water Flood" : 
         Techniques(
            name="Water Flood",
            level=1,
            act_speed=2,
            act_cost=50,
            act_body=("Head"),
            aoe=5,
            strength=300,
            speed=500,
            type="melee"
         ),
        "Certain Death From Above" : 
         Techniques(
            name="Certain Death From Above",
            level=1,
            act_speed=2,
            act_cost=50,
            act_body=("Full"),
            aoe=1,
            strength=800,
            speed=500,
            type="melee"
         )
     }},
     {"Defense" : {
        "Water Flood" : 
         Techniques(
            name="Water Flood",
            level=1,
            act_speed=2,
            act_cost=50,
            act_body=("Head"),
            aoe=5,
            strength=300,
            speed=500,
            type="counter"
         ),
        "Certain Death From Above" : 
         Techniques(
            name="Certain Death From Above",
            level=1,
            act_speed=2,
            act_cost=50,
            act_body=("Full"),
            aoe=1,
            strength=800,
            speed=500,
            type="counter"
         )
     }}
],
#endregion 
#region Mahoraga
    "Mahoraga" : 
    [
        {"Attack" : 

            {
                "Sword Swing" :
                Techniques(
                    name="Sword Swing",
                    level=1,
                    act_speed=1,
                    act_cost=1,
                    act_body=("Arms"),
                    aoe=1,
                    strength=800,
                    speed=800,
                    type="melee",
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
                    type="melee",
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
                    type="melee",
                    buff=("strength")
                )

            }},

            {
        "Defend" : 
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
                type="tank",
                buff=("strength", "speed"),
                negates=True,
                duration=5
                )
            } },],
#endregion
#region Finger Bearer
    "Finger Bearer" : 
    [
        {
            "Atttack" : 
            {
                    "Energy Blast" : Techniques(
                        name="Energy Blast",
                        level=1,
                        act_speed=5,
                        act_cost=50,
                    act_body=("hands"),
                    aoe=2,
                    strength=500,
                    speed=500,
                    type="projectile",
                    ),
                    "Claw Cleave": Techniques(
                    name="Claw Cleave",
                    level=1,
                    act_speed=1,
                    act_cost=100,
                    act_body=("hands"),
                    aoe=1,
                    strength=700,
                    speed=700,
                    type="melee",
                    
                    )  
            }
        },
        {
            "Defense" : 
            {
                "Energy Shield" : Techniques(
                    name="Energy Shield",
                    level=1,
                    act_speed=5,
                    act_cost=50,
                    act_body=("hands"),
                    aoe=2,
                    strength=500,
                    speed=500,
                    type="tank",
                ),

                "Self Heal" : Techniques(
                    name="Self Heal",
                    level=1,
                    act_speed=5,
                    act_cost=50,
                    act_body=("hands"),
                    aoe=2,
                    strength=500,
                    speed=500,
                    type="heal",
                    
                ),
                "Body Flicker" : Techniques(
                    name="Body Flicker",
                    level=1,
                    act_speed=5,
                    act_cost=150,
                    act_body=("hands"),
                    aoe=2,
                    strength=000,
                    speed=200,
                    type="dodge"
                )

            }
        }
    ],
#endregion
#region Orbmaster
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
            }]
        ,
#endregion
#region Charger
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
#endregion
#region Stinkaspore
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
                    strength=150,
                    speed=100,
                    type="pprojectile",
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
                    type="projectile",
                    poison=(range(10, 20), 2),
                    sure_hit=True 
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
                    strength=180,
                    speed=150,
                    type="counter",
                    poison=(range(10, 20), 2)

                    )
                }
            }
        ],
#endregion
#region Primate
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
                    type="projectile",
                    stun=2
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
        ],
#endregion
#region Furrpede
        "Furrpede" : 
        [
            {"Attack" : {
                    "Eye Beam" : Techniques(
                        name="Eye Beam",
                        level=1,
                        act_speed=5,
                        act_cost=50,
                        act_body=("eyes"),
                        aoe=2,
                        strength=500,
                        speed=500,
                        type="projectile",
                    ),
                    "Underground Strike" : Techniques(
                        name="Underground Strike",
                        level=1,
                        act_speed=5,
                        act_cost=50,
                        act_body=("hands"),
                        aoe=2,
                        strength=500,
                        speed=500,
                        type="melee",
                    ),}},
            {"Defend" : {
                "Furr Spikes" : Techniques(
                    name="Furr Spikes",
                    level=1,
                    act_speed=5,
                    act_cost=50,
                    act_body=("hands"),
                    aoe=2,
                    strength=100,
                    speed=200,
                    type="counter",
                    poison=(range(10, 20), 2)
                )

            }}
        ],
#endregion
#region Anxious Ears
    "Anxious Ears" : 
    [
        {"Attack" : {
            "Sound Clap" : Techniques(
                name="Anxious Ears: Sound Clap",
                level=1,
                act_speed=1,
                act_cost=50,
                act_body=("head", "torso"),
                aoe=1,
                strength=300,
                speed=300,
                type="projectile",
                stun=1
            ),
        }},
        {"Defend" :
         {
             "Sound Reflection" : Techniques(
                 "Anxious Ears: Sound Reflection",
                 level=1,
                    act_speed=1,
                    act_cost=50,
                    act_body=("head", "torso"),
                    aoe=1,
                    strength=300,
                    speed=300,
                    type="counter",
                
             )
         } }
    ],
#endregion
}