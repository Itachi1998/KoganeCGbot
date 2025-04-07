from techniques import Techniques

enemy_techs = { "King Of Curses" :
     [
          {
               "Attack" : 
               {
                    "Dismantle" : # need a visability attribute so it can't be seen by most sorcerers
                         Techniques(
                              name="Dismantle",
                              level=1,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="projectile",
                              invisable=True
                         ),
                    
                    "Multi Dismantle" :
                        Techniques(
                              name="Multi Dismantle",
                              level=2,
                              act_speed=1,
                              act_cost=60,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=500,
                              speed=1000,
                              type="projectile",
                              invisable=True
                         ),

                    "Cleave" :
                         Techniques(
                              name="Cleave",
                              level=1,
                              act_speed=1,
                              act_cost=60, # should be based off opponent hp - special case in battlechecks
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1500, # should be based off opponent hp - special case in battlechecks
                              speed=1000,
                              type="melee"
                         ),

                    "Encanted Dismantle" :
                         Techniques(
                              name="Dismantle",
                              level=4,
                              act_speed=2,
                              act_cost=40,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=1000,
                              type="projectile",
                              invisable=True
                         ),
                    
                    "Furnace" :
                         Techniques(
                              name="Furnace",
                              level=4,
                              act_speed=3,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=2000,
                              speed=500,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
           
               {
                    "Cleave Spider Web" :
                         Techniques(
                              name="Cleave Spider Web",
                              level=1,
                              act_speed=2,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1500,
                              speed=1000, 
                              type="counter"
                         ),

                    "Dismantle Parry" :
                         Techniques(
                              name="Dismantle Parry",
                              level=2,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="counter"
                         ),

                    "Dismantle Glove" : # like parry but strong since it envelopes the hand
                         Techniques(
                              name="Dismantle Glove",
                              level=2,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=1000,
                              type="tank"
                         ),

                    "Dismantle Shield" : # creating a forcefield out of slashes
                         Techniques(
                              name="Dismantle Shield",
                              level=4,
                              act_speed=1,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="tank"
                         ),
                    
                    "Air Hop" : 
                         Techniques(
                              name="Air Hop",
                              level=5,
                              act_speed=2,
                              act_cost=50,
                              act_body=("full"),
                              aoe=1,
                              strength=0,
                              speed=1500,
                              type="dodge"
                         )
               }
          },
          {
          "Domain" :
               {
                   "Malevolent Shrine" :
                         Techniques(
                              name="Malevolent Shrine",
                              level=5,
                              act_speed=2,
                              act_cost=300,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=2000,
                              speed=9999,
                              type="open",
                              sure_hit=True

                         )
               }
          }
     ],
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
            } }
    ],
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

    "Soul Curse" : # Femhito - special grade
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
        ]




}
