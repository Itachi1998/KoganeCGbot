from techniques import Techniques

# Note: techs with a rarity of 0 are only available to enemies

# region Anti Gravity
anti_gravity={
"Anti Gravity" :
     [
          {
               "Attack" : 
               {
                    "Push Away" :
                         Techniques(
                              name="Push Away",
                              level=1,
                              act_speed=1,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=0,
                              speed=1000,
                              type="projectile"
                         ),
                    "Reversal Pull Down" :
                         Techniques(
                              name="Reversal Pull Down",
                              level=3,
                              act_speed=2,                              
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=500,
                              speed=2000,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
               {    
                   "Push Away" :
                         Techniques(
                              name="Push Away",
                              level=1,
                              act_speed=1,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=0,
                              speed=1000,
                              type="counter"
                         ),
                    "Reversal Pull Down" :
                         Techniques(
                              name="Reversal Pull Down",
                              level=3,
                              act_speed=2,                              
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=500,
                              speed=2000,
                              type="counter"
                         )
                }
            }
        ],
"Rarity" : 15
}
# endregion

# region Anxious Ears
anxious_ears={  
"Anxious Ears" :
     [
          {
               "Attack" : 
               {
                    "Sound Clap" : 
                         Techniques(
                              name="Sound Clap",
                              level=1,
                              act_speed=1,
                              act_cost=50,
                              act_req=("head", "torso"),
                              aoe=1,
                              strength=300,
                              speed=300,
                              type="projectile",
                              stun=1
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Sound Reflection" : 
                         Techniques(
                              "Sound Reflection",
                              level=1,
                              act_speed=1,
                              act_cost=50,
                              act_req=("head", "torso"),
                              aoe=1,
                              strength=300,
                              speed=300,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Auspicious Beasts Summon
auspicious_beasts_summon={
"Auspicious Beasts Summon" :
     [
          {
               "Attack" : 
               {
                    "Kaichi" : # spinning cone horn projectile thing
                        Techniques(
                            name="Kaichi",
                            level=1,
                            act_speed=1,
                            act_cost=20,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=200,
                            speed=600,
                            type="projectile"
                         ),
                    
                    "Ryu" : # dragon attack 
                        Techniques(
                            name="Ryu",
                            level=3,
                            act_speed=1,
                            act_cost=100,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=800,
                            speed=800,
                            type="projectile"
                        )
               }
          },

          {
               "Defend": 
           
               {
                    "Reiki" : # cursed water that increases speed and can cushion attacks
                        Techniques(
                            name="Reiki",
                            level=1,
                            act_speed=1,
                            act_cost=30,
                            act_req=("Full"),
                            aoe=1,
                            strength=100,
                            speed=700,
                            type="dodge"
                         ),
                    
                    "Kirin" : # nullifies pain (ig add def or overall stat boost?) - also stuns self after technique ends
                        Techniques(
                            name="Kirin",
                            level=2,
                            act_speed=1,
                            act_cost=50,
                            act_req=("Full"),
                            aoe=1,
                            strength=500,
                            speed=1000,
                            type="tank"
                        )
               }
          }
     ],
"Rarity" : 50
}
# endregion

# region Barehand
barehand={  
"Barehand" :
     [
          {
               "Attack" : 
               {
                    "Barehand Slap" :
                         Techniques(
                              name="Barehand Slap",
                              level=1,
                              act_speed=2,                              
                              act_cost=10,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=200,
                              speed=400,
                              type="melee"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Barehand Slap" :
                         Techniques(
                              name="Barehand Slap",
                              level=1,
                              act_speed=2,                              
                              act_cost=10,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=200,
                              speed=400,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Bird Manipulation
bird_manip = {
     "Bird Manipulation" : 
     [
          {
              "Attack" : 
               { 
               "Talon Attack" : 
                    Techniques(
                         name="Talon Attack",
                         level=1,
                         act_speed=1,
                         act_cost=100,
                         act_req=("Head", "Right Arm", "Left Arm"),
                         aoe=3,
                         strength=50,
                         speed=250,
                         type="projectile"
                    ),

               "Bird Flock" : 
                    Techniques(
                         name="Bird Flock",
                         level=2,
                         act_speed=5,
                         act_cost=300,
                         act_req=("head", "left arm", "right arm"),
                         aoe=3,
                         strength=200,
                         speed=400,
                         type="projectile"
                    ),
                    
               "Bird Sacrifice" : 
                    Techniques(
                         name="Bird Sacrifice",
                         level=3,
                         act_speed=2,
                         act_cost=400,
                         act_req=("Head", "left arm", "right arm"),
                         aoe=2,
                         strength=1500,
                         speed=500,
                         stun=3,
                         type="projectile"
                         )
               }
          },
          {
          "Defend": 
               {
               "Feather Screen" : 
                    Techniques(
                         name="Feathered Screen",
                         level=1,
                         act_speed=40,
                         act_cost=50,
                         act_req=("Head", "left arm", "right arm"),
                         aoe=3,
                         strength=100,
                         speed=100,
                         type="dodge"
                         ),
               "Birds Eye" : 
                    Techniques(
                         name="Birds Eye",
                         level=2,
                         act_speed=5,
                         act_cost=10,
                         act_req=("head"),
                         aoe=5,
                         strength=100,
                         speed=500,
                         buff=("speed", 550),
                         type="dodge"
                         )

               }
          }
     ],
"Rarity" : 50
}
# endregion

# region Blood Manipulation
blood_manip= {
    "Blood Manipulation" : 
          [
               {
                    "Attack" : 
                    {
                         "Piercing Blood" :
                              Techniques(
                                   name="Piercing Blood", 
                                   level=1,
                                   act_speed=100,
                                   act_cost=100,
                                   act_req=("Head", "left arm", "right arm"),
                                   aoe=1,
                                   strength=400,
                                   speed=1200,
                                   type="projectile",
                                   poison=(10, 4),
                                   stun=1
                                   ),

                         "Blood Edge" : 
                              Techniques(
                                   name="Blood Edge",
                                   level=2,
                                   act_speed=50,
                                   act_cost=300,
                                   act_req=("Head", "left arm", "right arm"),
                                   aoe=5,
                                   strength=800,
                                   speed=500,
                                   type="projectile",
                                   poison=(5, 8)
                                   ),

                         "Red Scale" : 
                              Techniques(name="Red Scale",
                                   level=1,
                                   act_speed=10,
                                   act_cost=500,
                                   act_req=("Head", "right arm", "left arm", "left leg", "right leg"),
                                   aoe=1,
                                   strength=500,
                                   speed=500,
                                   type="melee",
                                   duration=5,
                                   buff=("strength", "speed")
                                   ) 
                              
                    }
                    
               }, 
               {
                    "Defend" : 
                    {
                         "Blood Meteor" : 
                         Techniques(name="Blood Meteor",
                                   level=1,
                                   act_speed=100,
                                   act_cost=300,
                                   act_req=("Head", "left arm", "right arm"),
                                   aoe=1,
                                   strength=400,
                                   speed=100,
                                   type="counter",
                                   stun=3
                                   ),
                         "Blood Armor":
                         Techniques(name="Blood Armor",
                                   level=3,
                                   act_speed=20,
                                   act_cost=500,
                                   act_req=("Head", "Torso", "Right Arm", "Left Arm", "Right Leg", "Left Leg"),
                                   aoe=1,
                                   strength=1000,
                                   speed=1000,
                                   type="tank"
                                   )
                                                            
                    }
               }
          ], 
"Rarity" : 50
}
# endregion

# region Body Hop
body_hop={
     
"Body Hop" :
     [
          {
               "Attack" : # Need to make an option in the following turn after player or teammate defeats an opponent
               {
                    "Body Hop" :
                         Techniques(
                              name="Body Hop",
                              level=1,
                              act_speed=3,                              
                              act_cost=1,
                              act_req=("Head"),
                              aoe=1,
                              strength=1,
                              speed=1,
                              type="transform"
                         )
               }
          },

          {
               "Defend": 
               {
                    "Rotate Head" : # ability to reduce dmg of attack to head by "spinning the top"
                         Techniques(
                              name="Rotate Head",
                              level=5,
                              act_speed=1,                              
                              act_cost=1,
                              act_req=("Head"),
                              aoe=1,
                              strength=100,
                              speed=1000,
                              type="dodge"
                         )
               }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Womb Profusion",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=9000,
                              type="open", 
                              sure_hit=True
                         )
               }
          }
     ],
"Rarity" : 5
}
# endregion

# region Boogie Woogie
boogie_woogie = {

"Boogie Woogie" : 
     [
          {
               "Attack" :
                 {
                    "Rock Throw" : 
                         Techniques(
                              name="Rock Throw",
                              level=1,
                              act_speed=5,
                              act_cost=20,
                              act_req=("Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"),
                              aoe=1,
                              strength=200,
                              speed=500,
                              type="melee",
                              buff=("strength", "speed")
                              ),

                    "Double Switch Fake" : 
                         Techniques(
                              name="Double Switch Fake",
                              level=2,
                              act_speed=1,
                              act_cost=0,
                              act_req=("Head", "Torso", "Left Leg", "Right Leg", "Right Arm", "Left Arm"),
                              aoe=5,
                              strength=400,
                              speed=400,
                              type="melee",
                              stun=2),
                    "Over Here" : 
                         Techniques(
                              name="Over Here",
                              level=2,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Head", "Torso", "Right Arm", "Left Arm"),
                              aoe=5,
                              strength=800,
                              speed=2000,
                              type="melee",
                              stun=1
                              )
               }
          },

          {
               "Defend" : 
               {
                    "Clap Swap" : 
                         Techniques(
                              name="Clap Swap",
                              level=1,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Head", "Torso", "Left Arm", "Right Arm"),
                              aoe=5,
                              strength=100,
                              speed=2000,
                              type="dodge"
                              ),
                    "Reverse Swap" : 
                         Techniques(
                              name="Reverse Swap",
                              level=3,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Head", "Torso", "Left Arm", "Right Arm"),
                              aoe=1,
                              strength=0,
                              speed=2000,
                              type="counter reflect"
                              ),
                    "Vibra Swap" : 
                         Techniques(
                              name="Vibra Swap",
                              level=4,
                              act_speed=1,
                              act_cost=100,
                              act_req=("Head", "Torso"),
                              aoe=5,
                              strength=100,
                              speed=5000,
                              type="dodge"
                              )
               }
          }
     ],

"Rarity" : 30
}
# endregion

# region Bugfly
bugfly={  
"Bugfly" :
     [
          {
               "Attack" : 
               {
                    "Swat" :
                         Techniques(
                              name="Swat",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="melee"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Swat" :
                         Techniques(
                              name="Swat",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Charger
charger={  
"Charger" :
     [
          {
               "Attack" : 
               {
                    "Charged Punch" :
                         Techniques(
                              name="Charged Punch",
                              level=1,
                              act_speed=2,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=300,
                              type="melee"
                         ),
                    
                    "Electric Ground-pound" : 
                         Techniques(
                              name="Electric Ground-pound",
                              level=1,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=400,
                              speed=300,
                              type="projectile"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Charged Field" :
                         Techniques(
                              name="Charged Field",
                              level=1,
                              act_speed=2,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=500,
                              type="tank"
                         )
               }
          }
     ],
"Rarity" : 30
}
# endregion

# region Cursed Energy Discharge
ce_discharge={
     
"Cursed Energy Discharge" :
     [
          {
               "Attack" : 
               {
                    "Granite Blast" :
                         Techniques(
                              name="Granite Blast",
                              level=1,
                              act_speed=3,                              
                              act_cost=200,
                              act_req=("Head"),
                              aoe=3,
                              strength=1500,
                              speed=1000,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
               {
                    "Block" :
                         Techniques(
                              name="Block",
                              level=1,
                              act_speed=1,                              
                              act_cost=1,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=1000,
                              type="tank"
                         )
               }
          }
     ],
"Rarity" : 30
}
# endregion

# region Comedian
comedian={
"Comedian" : 
     [
          {
               "Attack" : 
               {
                    "Punchline" : 
                         Techniques(
                              name="Punchline",
                              level=1,
                              act_speed=1,
                              act_cost=10,
                              act_req=("head", "torso", "arms", "legs"),
                              aoe=1,
                              strength=500,
                              speed=900,
                              type="melee",
                              buff=("strength", "speed")
                              ),
                              
                    "One Liner" :
                         Techniques(
                              name="One Liner",
                              level=1,
                              act_speed=1,
                              act_cost=10,
                              act_req=("Head", "torso", "arms", "legs"),
                              aoe=4,
                              strength=700,
                              speed=900,
                              type="melee",
                              buff=("strength", "speed")),
                    "Skit" : 
                         Techniques(
                              name="Skit",
                              level=2,
                              act_speed=1,
                              act_cost=10,
                              act_req=("Head", "Torso", "Arms", "Legs"),
                              aoe=4,
                              strength=900,
                              speed=1500,
                              type="melee",
                              buff=("strength", "Speed")
                              ),
                    "Truck Kun" :
                         Techniques(
                              name="Truck Kun",
                              level=3,
                              act_speed=10,
                              act_cost=10,
                              act_req=("Head", "Torso", "Arms", "Legs"),
                              aoe=1,
                              strength=1500,
                              speed=2000,
                              type="projectile",
                              stun=1,
                              sure_hit=True
                         ),
                    "Wouldn't It Be Funny" :
                         Techniques(
                              name="Wouldn't it be funny",
                              level=5,
                              act_speed=1,
                              act_cost=20,
                              act_req=("Head", "torso", "arms", "legs"),
                              aoe=4,
                              strength=2000,
                              speed=1000,
                              type="projectile",
                              sure_hit=True
                              )
               }
          },
          {
               "Defend" :
               {
                    "Red is Taboo" : 
                         Techniques(
                              name="Red Is Taboo",
                              level=1,
                              act_speed=10,
                              act_cost=10,
                              act_req=("Head", "arms", "torso"),
                              aoe=4,
                              strength=200,
                              speed=1000,
                              type="counter",
                              negates=True
                              ),
                    "Fanta Sea":
                         Techniques(
                              name="Fanta Sea",
                              level=2,
                              act_speed=10,
                              act_cost=10,
                              act_req=("Head", "arm", "torso"),
                              aoe=5,
                              strength=1500,
                              speed=1500,
                              type="counter"
                              ),
                    "Slimed" :
                         Techniques(
                              name="Slimed",
                              level=1,
                              act_speed=10,
                              act_cost=10,
                              act_req=("full"),
                              aoe=2,
                              strength=100,
                              speed=900,
                              type="dodge"
                              ),
                    "Ya Trying To Kill Me?" : # LMAO
                         Techniques(
                              name="Ya Trying To Kill Me?",
                              level=3,
                              act_speed=10,
                              act_cost=10,
                              act_req=("full"),
                              aoe=1,
                              strength=1000,
                              speed=2000,
                              type="tank",
                              negates=True
                              )
                    }
          }

     ], 

"Rarity" : 15
}
# endregion

# region Construction
construction={
     "Construction": [
          {
            "Attack" : 
                    {
                    "Blade" : 
                         Techniques(
                              name="Blade",
                              level=1,
                              act_speed=40,
                              act_cost=400,
                              act_req=("Full"),
                              aoe=1,
                              strength=850,
                              speed=500,
                              type="melee",
                         ),
                    "Ammo" : 
                         Techniques(
                              name="Ammo",
                              level=1,
                              act_speed=30,
                              act_cost=400,
                              act_req=("Full"),
                              aoe=1,
                              strength=700,
                              speed=600,
                              type="projectile"
                         ),
                    "Liquid Metal" : 
                         Techniques(
                              name="Liquid Metal",
                              level=4,
                              act_speed=40,
                              act_cost=150,
                              act_req=("Full"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="projectile",
                              poison=(10, 10)
                         ),
                    "Air To Surface Missile" : 
                         Techniques(name="Six Eyes Construction: Air to Surface Missiles",
                                   level=3,
                                   act_speed=1,
                                   act_cost=5,
                                   act_req=("Full"),
                                   aoe=5,
                                   strength=1500,
                                   speed=1500,
                                   type="projectile"),
                    "Nuclear Warhead" : 
                         Techniques(name="Six Eyes Construction: Nuclear Warhead",
                                   level=5,
                                   act_speed=20,
                                   act_cost=200,
                                   act_req=("full"),
                                   aoe=5,
                                   strength=5500,
                                   speed=2000,
                                   type="projectile"),
                                   
                    "True Sphere Orbs" : 
                         Techniques(name="Six Eyes Construction: True Sphere Orbs",
                                   level=3,
                                   act_speed=10,
                                   act_cost=20,
                                   act_req=("full"),
                                   aoe=4,
                                   strength=3500,
                                   speed=25000,
                                   type="projectile"
                                   ) 
                    }
          },
          {
            "Defend" : 
                    {
                    "Bug Armor": # transform ability with duration
                         Techniques(name="Bug Armor",
                                   level=3,
                                   act_speed=20,
                                   act_cost=150,
                                   act_req=("Full"),
                                   aoe=1,
                                   strength=2000,
                                   speed=2000,
                                   type="counter",
                                   buff=("strength", "speed")
                                   ),
                    "Armored Sentinels":
                         Techniques(name="Armored Sentinels",
                                   level=1,
                                   act_speed=1,
                                   act_cost=50,
                                   act_req=("Full"),
                                   aoe=1,
                                   strength=10000,
                                   speed=1000,
                                   type="summon",
                                   summon={"Sentinel" : {'dmg' : 1000, 'speed' : 1000, "max_hp" : 900, "tamed" : True}}
                                   ),
                    "Liquid Metal Shield" : 
                         Techniques(
                                   name="Liquid Metal Shield",
                                   level=1,
                                   act_speed=20,
                                   act_cost=300,
                                   act_req=("full"),
                                   aoe=3,
                                   strength=600,
                                   speed=600,
                                   type="tank"
                              )
                    }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Three-fold Affliction",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=8000,
                              type="closed",
                              intern_strength=30,
                              extern_strength=30,
                              sure_hit=True

                         )
               }
          }
],
"Rarity" : 15, 
"Six Eyes" : False
}
# endregion

# region Contractual Recreation
contractual_recreation={  
"Contractual Recreation" :
     [
          {
               "Attack" : 
               {
                    "Knife Receipt" :
                         Techniques(
                              name="Knife Receipt",
                              level=1,
                              act_speed=3,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=600,
                              speed=400,
                              type="melee"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Knife Receipt" :
                         Techniques(
                              name="Knife Receipt",
                              level=1,
                              act_speed=3,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=600,
                              speed=400,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 10
}
# endregion

# region Copy
copy={ # change to be like cursed spirit manipulation?
     "Copy" : [
          {
               "Attack" : 
               {
                    "Freeze"  : 
                         Techniques(
                         name="Copied Technique: Freeze",
                         level=1,
                         act_speed=30,
                         act_cost=50,
                         act_req=("Head"),
                         aoe=5,
                         strength=10,
                         speed=800,
                         type="projectile",
                         stun=4),
                    "Die" : 
                         Techniques(
                              name="Copied Technique: Die",
                              level=2,
                              act_speed=30,
                              act_cost=500,
                              act_req=("full"),
                              aoe=4,
                              strength=400,
                              speed=1000,
                              type="projectile"
                         ),
                    "Sword Blast" : 
                         Techniques(
                              name="Sword Reinforcement Discharge",
                              level=3,
                              act_speed=3,
                              act_cost=300,
                              act_req=("Full", "sword"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="melee"
                         ),
                    "Authentic Love Beam" : 
                         Techniques(
                              name="Authentic Love Beam",
                              level=1,
                              act_speed=20,
                              act_cost=500,
                              act_req=("Full", "Rika"),
                              aoe=5,
                              strength=2000,
                              speed=2000,
                              type="projectile"
                         ),
                    "Rika Summon" : 
                         Techniques(
                              name="Come out, RIKA",
                              level=1,
                              act_speed=1,
                              act_cost=100,
                              act_req=("Head"),
                              aoe=1,
                              strength=4000,
                              speed=4000,
                              type="summon",
                              summon={"Rika" : {"Speed" : 4000, "strength" : 4000, "Max CE" : 4000}}
                         )
               }
          },
          {
          "Defend" :
               {
                    "Don't Move" : 
                         Techniques(
                              name="Copied technique: Don't Move",
                              level=1,
                              act_speed=20,
                              act_cost=50,
                              act_req=("Head"),
                              aoe=3,
                              strength=50,
                              speed=800,
                              type="counter",
                              stun=2,
                         )
               }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Authentic Mutual Love",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=8000,
                              type="closed",
                              intern_strength=30,
                              extern_strength=30,
                              sure_hit=True

                         )
               }
          }
     ],
"Rarity" : 15,

"Six Eyes" : False
}
# endregion

# region Cursed Speech
cursed_speech={
     "Cursed Speech" :
     [
          {
               "Attack" : 
               {
                    "Freeze" : 
                         Techniques(
                              name="Freeze", 
                              level=1, 
                              act_speed=10, 
                              act_cost=100,
                              act_req=("Head", "Torso"),
                              aoe=2,
                              strength=600,
                              speed=900,
                              type="projectile",
                              stun=3,
                              invisible=True
                         ),

                    "Blast Away" :
                         Techniques(
                              name="Blast Away",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_req=("Head", "Torso"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="projectile",
                              invisible=True
                         ),

                    "Plummet" : 
                         Techniques(
                              name="Plummet",
                              level=3,
                              act_speed=10,
                              act_cost=100,
                              act_req=("Head", "torso"),
                              aoe=2,
                              strength=1000,
                              speed=1000,
                              type="projectile",
                              stun=1,
                              invisible=True
                         )
               }
          },
          {
               "Defend" :
               {
                         
                    "Freeze" : 
                         Techniques(
                              name="Freeze", 
                              level=1, 
                              act_speed=10, 
                              act_cost=100,
                              act_req=("Head", "Torso"),
                              aoe=2,
                              strength=600,
                              speed=900,
                              type="counter",
                              stun=3,
                              invisible=True
                         ),
                    
                    "Blast Away" :
                         Techniques(
                              name="Blast Away",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_req=("Head", "Torso"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="counter",
                              invisible=True
                         )
                    
                }
          }
     ],
     "Rarity" : 50
}
# endregion

# region Cursed Spirit Manipulation
cursed_spirit_manip={
     "Cursed Spirit Manip" : [
          {
               "Attack" :
                    {
                         "Summon" : 
                         Techniques(
                              name="Cursed Spirit Manipulation: Summoning",
                              level=1,
                              act_speed=20,
                              act_cost=100,
                              act_req=("Full"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="summon",
                              summon={}
                              )
                    }
                 },
          {
               "Defend" : 
                    {
                         "Summon" :
                         Techniques(
                              name="Cursed Spirit Manipulation: Summoning",
                              level=1,
                              act_speed=10,
                              act_cost=50,
                              act_req=("Full"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="summon",
                              summon={}
                         )
                    }
          }
     ],
"Rarity" : 5
}
# endregion

# region Disaster Flames
disaster_flames={
     
"Disaster Flames" :
     [
          {
               "Attack" : 
               {
                    "Fire Cannon" :
                         Techniques(
                              name="Fire Cannon",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=900,
                              type="melee"
                         ),

                    "Inferno" :
                         Techniques(
                              name="Inferno",
                              level=2,
                              act_speed=1,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=10,
                              strength=200,
                              speed=1000,
                              type="projectile"
                         ),
                    
                    "Fireflies" :
                         Techniques(
                              name="Fireflies",
                              level=3,
                              act_speed=2,                              
                              act_cost=25,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=300,
                              speed=1200,
                              type="projectile"
                         ),
                    
                    "Lava Eruption" :
                         Techniques(
                              name="Lava Eruption",
                              level=3,
                              act_speed=3,                              
                              act_cost=100,
                              act_req=("Full"),
                              aoe=5,
                              strength=1200,
                              speed=800,
                              type="projectile"
                         ),
                    
                    "Lava Hands" :
                         Techniques(
                              name="Lava Hands",
                              level=4,
                              act_speed=3,                              
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=1000,
                              type="melee"
                         ),
                    
                    "Maximum Meteor" :
                         Techniques(
                              name="Maximum Meteor",
                              level=5,
                              act_speed=5,                              
                              act_cost=150,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=2000,
                              speed=500,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
               {
                    "Fire Cannon" :
                         Techniques(
                              name="Fire Cannon",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=900,
                              type="counter"
                         ),

                    "Inferno" :
                         Techniques(
                              name="Inferno",
                              level=2,
                              act_speed=1,                              
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=10,
                              strength=200,
                              speed=1000,
                              type="counter"
                         ),
                    
                     "Lava Surfboard" :
                         Techniques(
                              name="Lava Surfboard",
                              level=4,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Full"),
                              aoe=1,
                              strength=100,
                              speed=1000,
                              type="dodge"
                         )
                }   
                
            }
        ],
"Rarity" : 10
}
# endregion

# region Disaster Tides
disaster_tides={
     
"Disaster Tides" :
     [
          {
               "Attack" : 
               {
                    "Water Blast" :
                         Techniques(
                              name="Water Blast",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=100,
                              speed=800,
                              type="projectile",
                              debuff=('slow', 50) # slows targets down by 50% with water for the following round or smth
                         ), 

                    "Water Vortex" : # twisting water attack
                         Techniques(
                              name="Water Vortex",
                              level=2,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=800,
                              type="melee"
                         ),

               }
          },

          {
               "Defend": 
               {
                    "Water Blast" :
                         Techniques(
                              name="Water Blast",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Full"),
                              aoe=5,
                              strength=100,
                              speed=800,
                              type="counter",
                              debuff=('slow', 50) # slows targets down by 50% with water for the following round or smth
                         ), 

                    "Water Vortex" : # twisting water attack
                         Techniques(
                              name="Water Vortex",
                              level=2,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=800,
                              type="counter"
                         ),

                    "Water Jets" :
                         Techniques(
                              name="Water Jets",
                              level=3,
                              act_speed=1,                              
                              act_cost=10,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=800,
                              type="dodge"
                         )
                }
            }
        ],
"Rarity" : 50
}
# endregion

# region Explosive Flesh
explosive_flesh={
     
"Explosive Flesh" :
     [
          {
               "Attack" : 
               {
                    "Exploding Fingers" :
                         Techniques(
                              name="Exploding Fingers",
                              level=1,
                              act_speed=2,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=400,
                              speed=800,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
               {
                    "Exploding Fingers" :
                         Techniques(
                              name="Exploding Fingers",
                              level=1,
                              act_speed=2,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=400,
                              speed=800,
                              type="counter"
                         )
                }
            }
        ],
"Rarity" : 50
}
#endregion

# region Finger Bearer
finger_bearer={
"Finger Bearer" :
     [
          {
               "Attack" : 
               {
                    "Energy Blast" :
                         Techniques(
                              name="Energy Blast",
                              level=1,
                              act_speed=5,                              
                              act_cost=50,
                              act_req=("Hands"),
                              aoe=2,
                              strength=500,
                              speed=500,
                              type="projectile"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Energy Shield" : Techniques(
                         name="Energy Shield",
                         level=1,
                         act_speed=5,
                         act_cost=50,
                         act_req=("hands"),
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
                         act_req=("hands"),
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
                         act_req=("hands"),
                         aoe=2,
                         strength=000,
                         speed=200,
                         type="dodge"
                    )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Floatjelly
floatjelly={  
"Floatjelly" :
     [
          {
               "Attack" : 
               {
                    "Sting" :
                         Techniques(
                              name="Sting",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="melee",
                              poison=(1, 2)
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Sting" :
                         Techniques(
                              name="Sting",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="counter",
                              poison=(1, 2)
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Flymouth
flymouth={  
"Flymouth" :
     [
          {
               "Attack" : 
               {
                    "Chomp" :
                         Techniques(
                              name="Chomp",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Head"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="melee"
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Chomp" :
                         Techniques(
                              name="Chomp",
                              level=1,
                              act_speed=2,                              
                              act_cost=1,
                              act_req=("Head"),
                              aoe=1,
                              strength=100,
                              speed=100,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Furrpede
furrpede={  
"Furrpede" :
     [
          {
               "Attack" : 
               {
                    "Eye Beam" : 
                         Techniques(
                              name="Eye Beam",
                              level=1,
                              act_speed=5,
                              act_cost=50,
                              act_req=("Head"),
                              aoe=2,
                              strength=500,
                              speed=500,
                              type="projectile",
                         ),
                    "Underground Strike" : 
                         Techniques(
                              name="Underground Strike",
                              level=1,
                              act_speed=5,
                              act_cost=50,
                              act_req=("Hands"),
                              aoe=2,
                              strength=500,
                              speed=500,
                              type="melee",
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Furr Spikes" : 
                         Techniques(
                              name="Furr Spikes",
                              level=1,
                              act_speed=5,
                              act_cost=50,
                              act_req=("Torso"),
                              aoe=3,
                              strength=100,
                              speed=200,
                              type="counter",
                              poison=50
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Heavenly Restriction: Max
hr_max={   
"Heavenly Restriction: Max" :
     [
          {
               "Attack" : 
               {
                    "Mech Beam" :
                         Techniques(
                              name="Mech Beam",
                              level=1,
                              act_speed=1,                              
                              act_cost=30,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
               {
                    "Mech Beam" :
                         Techniques(
                              name="Mech Beam",
                              level=1,
                              act_speed=1,                              
                              act_cost=30,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 15
}
# endregion

# region Heavenly Restriction: Zero
hr_zero={
"Heavenly Restriction: Zero" : 
     [
          {
               "Attack" : 
               {
                    "Three Piece Combo" : 
                         Techniques(
                              name="Three Piece Combo",
                              level=1,
                              act_speed=1,
                              act_cost=1,  # Updated act_cost to 1
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=100,
                              speed=1200,
                              type="melee"
                         ),
                    "Spinning Back Kick":
                         Techniques(
                              name="Spinning Back Kick",
                              level=1,
                              act_speed=3,
                              act_cost=1,  # Updated act_cost to 1
                              act_req=("Left Leg", "Right Leg"),
                              aoe=1,
                              strength=200,
                              speed=1000,
                              type="melee"
                         ),
                    "Yeet Car" : 
                         Techniques(
                              name="Yeet Car",
                              level=1,
                              act_speed=10,
                              act_cost=1,  # Updated act_cost to 1
                              act_req=("arms", "legs"),
                              aoe=1,
                              strength=800,
                              speed=600,
                              type="projectile"
                         )
               }
          },

          {
               "Defend": 
          
               {
                    "Heavenly Body" : 
                         Techniques(
                              name="Heavenly Body",
                              level=1,
                              act_speed=0,
                              act_cost=1,
                              act_req=("Full"),
                              aoe=1,
                              strength=1200,
                              speed=9000,
                              type="tank"
                         ),

                    "Precognition" : 
                         Techniques(
                              name="Precognition",
                              level=3,
                              act_speed=1,
                              act_cost=1,
                              act_req=("full"),
                              aoe=1,
                              strength=100,
                              speed=1200,
                              type="dodge"
                         ),

                    "Read Like a Book" : 
                         Techniques(
                              name="Read Like a Book",
                              level=3,
                              act_speed=1,
                              act_cost=1,
                              act_req=("full"),
                              aoe=1,
                              strength=100,
                              speed=1200,
                              type="counter"
                         ),
                         
                    "Air Hop" : 
                         Techniques(
                              name="Air Hop",
                              level=5,
                              act_speed=1,
                              act_cost=1,
                              act_req=("full"),
                              aoe=1,
                              strength=100,
                              speed=1500,
                              type="dodge"
                         )
          
               }
          },
          {
          "RCT" :
               {
                    "Heal" :
                         Techniques(
                              name="Heal",
                              level=1,
                              act_speed=1,
                              act_cost=1,
                              act_req=("Full"),
                              aoe=1,
                              strength=200,
                              speed=1000,
                              type="heal",
                              #self_heal=200
                         )
               }
          }
     ],
"Rarity" : 15
}
# endregion

# region Ice Manipulation
ice_manip={
     
"Ice Manipulation" :
     [
          {
               "Attack" : 
               {
                    "Frostbite" :
                         Techniques(
                              name="Frostbite",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1200,
                              speed=0,
                              type="melee",
                              stun=1
                         ),
                    
                    "Ice Pillars" :
                         Techniques(
                              name="Ice Pillars",
                              level=2,
                              act_speed=3,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=1500,
                              speed=800,
                              type="projectile"
                         ),
                    
                    "Falling Icecicles" :
                         Techniques(
                              name="Falling Icecicles",
                              level=3,
                              act_speed=2,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=1000,
                              speed=1200,
                              type="projectile"
                         ),
                    
                    "Frost Calm" :
                         Techniques(
                              name="Frost Calm",
                              level=4,
                              act_speed=3,                              
                              act_cost=150,
                              act_req=("Head"),
                              aoe=5,
                              strength=1200,
                              speed=1000,
                              type="projectile",
                              stun=3
                         )
               }
          },

          {
               "Defend": 
               {
                    "Frostbite" :
                         Techniques(
                              name="Frostbite",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1200,
                              speed=0,
                              type="counter",
                              stun=1
                         ),

                    "Ice Pillars" :
                         Techniques(
                              name="Ice Pillars",
                              level=2,
                              act_speed=3,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=1500,
                              speed=800,
                              type="tank"
                         ),
                    
                    "Falling Icecicles" :
                         Techniques(
                              name="Falling Icecicles",
                              level=3,
                              act_speed=2,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=1000,
                              speed=1200,
                              type="counter"
                         ),
                    
                    "Frost Calm" :
                         Techniques(
                              name="Frost Calm",
                              level=4,
                              act_speed=3,                              
                              act_cost=150,
                              act_req=("Head"),
                              aoe=5,
                              strength=1200,
                              speed=1000,
                              type="counter",
                              stun=3
                         )
               }
          }
     ],
"Rarity" : 15
}
# endregion

# region Idle Transfiguration
idle_transfig={
"Idle Transfiguration" :
     [
          {
               "Attack" : 
               {
                    "Transmutate" : 
                         Techniques(
                              name="Transmutate",
                              level=1,
                              act_speed=1,
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=800,
                              type="melee",
                              soul=400
                         ),
                    "Transmutated Souls":
                         Techniques(
                              name="Transmutated Souls",
                              level=1,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=4,
                              strength=300,
                              speed=400,
                              type="summon",
                              summon={"Transfigured Humans" : {"Speed" : 400, "strength" : 300, "Max CE" : 100}} 
                         ),
                    "Polymorphic Soul Isomer" : 
                         Techniques(
                              name="Polymorphic Soul Isomer",
                              level=2,
                              act_speed=3,
                              act_cost=70,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=2,
                              strength=700,
                              speed=600,
                              type="summon",
                              summon={"Polymorphic Soul Isomer" : {"Speed" : 600, "strength" : 700, "Max CE" : 200}}
                         ),

                    "ISBODK Transform" :
                         Techniques(
                              name="ISBODK Transform",
                              level=3,
                              act_speed=2,
                              act_cost=150,
                              act_req=("Full"),
                              aoe=0,
                              strength=1200,
                              speed=1000,
                              type="transform"
                            )
               }
          },

          {
               "Defend": 
           
               {
                    "Soul Repel" : # always active
                    Techniques(
                         name="Soul Repel",
                         level=1,
                         act_speed=0,
                         act_cost=1,
                         act_req=("Full"),
                         aoe=1,
                         strength=500,
                         speed=1000,
                         type="tank",
                         soul=True
                       ),

                    "Soul Mulitiplicity" : 
                        Techniques(
                            name="Soul Mulitiplicity",
                            level=2,
                            act_speed=2,
                            act_cost=80,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=100,
                            speed=800,
                            type="dodge"
                            ),
                    
                    "ISBODK Transform" :
                         Techniques(
                              name="ISBODK Transform",
                              level=3,
                              act_speed=2,
                              act_cost=150,
                              act_req=("Full"),
                              aoe=0,
                              strength=1200,
                              speed=1000,
                              type="transform"
                            )
           
               }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Self-Embodiment of Perfection",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=8000,
                              type="closed",
                              intern_strength=30,
                              extern_strength=30,
                              sure_hit=True

                         )
               }
          }
     ],
"Rarity" : 5
}
# endregion

# region Limitless
limitless={
"Limitless" :
     [
          {
          "Attack" : 
               {
               "Blue" : 
                    Techniques(
                         name="Blue",
                         level=1,
                         act_speed=1,
                         act_cost=50,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=800,
                         speed=1200,
                         type="projectile"
                    ),
               
               "Red": # RCT required
                    Techniques(
                         name="Red",
                         level=2,
                         act_speed=2,
                         act_cost=50,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=1200,
                         speed=800,
                         type="projectile"
                    ),
               
               "Void Punch" : 
                    Techniques(
                         name="Void Punch",
                         level=4,
                         act_speed=1,
                         act_cost=50,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=800,
                         speed=1200,
                         type="melee"
                    ),

               "Hollow Purple" : 
                    Techniques(
                         name="Hollow Purple",
                         level=4,
                         act_speed=3,
                         act_cost=150,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=2000,
                         speed=2000,
                         type="projectile"
                    ),
               
               "Unlimited Hollow Purple" : # add self_dmg in checks
                    Techniques(
                         name="Unlimited Hollow Purple",
                         level=5,
                         act_speed=5,
                         act_cost=300,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=10,
                         strength=2000,
                         speed=2000,
                         type="projectile",
                         self_dmg=500
                    )
               }
          },

          {
          "Defend": 
          
          {
              "CE" :
                    Techniques(
                         name="CE",
                         level=1,
                         act_speed=0,
                         act_cost=0,
                         act_req=("Full"),
                         aoe=0,
                         strength=0,
                         speed=0,
                         type="tank"
                    ),
               "Infinity" :
                    Techniques(
                         name="Infinty",
                         level=1,
                         act_speed=0,
                         act_cost=10,
                         act_req=("Full"),
                         aoe=1,
                         strength=9000,
                         speed=9000,
                         type="tank"
                    ),

               "Blue" : 
                    Techniques(
                         name="Blue",
                         level=1,
                         act_speed=1,
                         act_cost=50,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=100,
                         speed=1200,
                         type="dodge"
                    ),

               "Red": # RCT required
                    Techniques(
                         name="Red",
                         level=2,
                         act_speed=2,
                         act_cost=50,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=1200,
                         speed=800,
                         type="counter"
                    ),

               "Void Punch" : # add a sneaky red move to combo lol
                    Techniques(
                         name="Void Punch",
                         level=4,
                         act_speed=1,
                         act_cost=25,
                         act_req=("Left Arm", "Right Arm"),
                         aoe=1,
                         strength=800,
                         speed=1200,
                         type="counter"
                    )
               }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion: Infinite Void" : #needs to match name to work
                         Techniques(
                              name="Domain Expansion: Infinite Void",
                              level=5,
                              act_speed=2,
                              act_cost=600,
                              act_req=("Right Arm"),
                              aoe=10,
                              strength=1000,
                              speed=9000,
                              type="closed",
                              stun=99,
                              intern_strength=50,
                              extern_strength=50,
                              sure_hit=True

                         )
               }
          },
          {
          "RCT" :
               {
                    "Heal" :
                         Techniques(
                              name="Heal",
                              level=4,
                              act_speed=1,
                              act_cost=50,
                              act_req=("Head"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="heal",
                              #self_heal=500
                         )
               }
          }
     ],
"Rarity" : 5,
"Six Eyes" : True
}
# endregion

# region Mythic Beast Amber
mba={
     
"Mythical Beast":
     [
          {
               "Attack" : 
               {
                    "Lightning Dash" :
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_req=("Full"),
                            aoe=1,
                            strength=500,
                            speed=900,
                            type="melee"
                        ),

                    "Lightning Rod" :
                        Techniques(
                            name="Lightning Rod",
                            level=3,
                            act_speed=1,
                            act_cost=150,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1000,
                            speed=1200,
                            type="projectile",
                            charge=3 # once the player.charge is set to 3 (3 rounds from start or use of tech) it is available to use
                         ),

                    "Corona Blast" : 
                        Techniques(
                            name="Corona Blast",
                            level=4,
                            act_speed=2,
                            act_cost=80,
                            act_req=("Head"),
                            aoe=3,
                            strength=600,
                            speed=1200,
                            type="projectile"
                        )

               }
          },

          {
               "Defend": 
           
               {
                    "Lightning Dash" : 
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_req=("Full"),
                            aoe=1,
                            strength=100,
                            speed=900,
                            type="dodge"
                        ),

                    "Corona Discharge" : # localized electric discharge created by a strong electrical field ionizes the surrounding air
                        Techniques(
                            name="Corona Discharge",
                            level=4,
                            act_speed=2,
                            act_cost=80,
                            act_req=("Full"),
                            aoe=5,
                            strength=600,
                            speed=1200,
                            type="counter"
                        )
               }
          }
     ],
"Rarity" : 15,
"Activated" : False
}
# endregion

# region Natures Wrath
natures_wrath={
"Natures Wrath" :
     [
          {
               "Attack" : 
               {
                    "Cursed Buds" :
                         Techniques(
                              name="Cursed Buds",
                              level=1,
                              act_speed=1,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=5,
                              strength=10,
                              speed=800,
                              type="projectile",
                              debuff=('burn ce', 50) # burns 50 ce per round if it hits target (won't hit if target has no ce imbued or is hr zero)
                         ), 

                    "Roots" :
                         Techniques(
                              name="Roots",
                              level=2,
                              act_speed=1,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=700,
                              speed=700,
                              type="projectile"
                         ),
               }
          },

          {
               "Defend" : 
               {
                    "Root Rider" :
                         Techniques(
                              name="Root Rider",
                              level=2,
                              act_speed=1,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=700,
                              type="dodge"
                         ),

                    "Roots" :
                         Techniques(
                              name="Roots",
                              level=2,
                              act_speed=1,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=700,
                              speed=700,
                              type="counter"
                         ),
                }
            }
        ],
"Rarity" : 35
}
# endregion

# region Orbmaster
orbmaster={
"Orbmaster" :
     [
          {
               "Attack" : 
               {
                    "Impending Doom" : 
                         Techniques(
                              name="Impending Doom",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_req=("hands", "torso"),
                              aoe=1,
                              strength=420,
                              speed=100,
                              type="projectile",
                              sure_hit=True
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Foresight" : 
                         Techniques(
                              name="Foresight",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_req=("head"),
                              aoe=1,
                              strength=400,
                              speed=200,
                              type="counter",
                              sure_hit=True
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Primate
primate={  
"Primate" :
     [
          {
               "Attack" : 
               {
                    "Head Twirl" : 
                         Techniques(
                              name="Head Twirl",
                              level=1,
                              act_speed=2,
                              act_cost=30,
                              act_req=("Head", "Torso"),
                              aoe=1,
                              strength=200,
                              speed=500,
                              type="projectile",
                              stun=2
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Tree Swing" : 
                         Techniques(
                              name="Tree Swing",
                              level=1,
                              act_speed=2,
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=400,
                              type="dodge"
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Projection Sorcery
projection_sorcery={
     
"Projection Sorcery" :
     [
          {
               "Attack" : 
               {
                    "Projection" : 
                        Techniques(
                            name="Projection",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="melee",
                            stun=True
                        )
               }
          },

          {
               "Defend": 
           
               {
                    "Projection Dodge" : 
                        Techniques(
                            name="Projection Dodge",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=100,
                            speed=1200,
                            type="dodge"
                        ),
                    
                    "Projection Stun" : 
                        Techniques(
                            name="Projection Stun",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_req=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="counter",
                            stun=True
                        )
               }
          },
          {
               "Barrier" :
               {
                   "Domain Expansion: Time Cell Moon Pallace" :
                         Techniques(
                              name="Domain Expansion: Time Cell Moon Pallace",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=8000,
                              type="closed",
                              intern_strength=30,
                              extern_strength=30,
                              sure_hit=True

                         )
               }
          }
     ],
"Rarity" : 30
}
# endregion

# region Shrine
shrine={
"Shrine" :
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
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1200,
                              type="projectile",
                              invisible=True
                         ),

                    "Multi Dismantle" :
                        Techniques(
                              name="Multi Dismantle",
                              level=2,
                              act_speed=1,
                              act_cost=60,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=500,
                              speed=1200,
                              type="projectile",
                              invisible=True
                         ),

                    "Cleave" :
                         Techniques(
                              name="Cleave",
                              level=1,
                              act_speed=1,
                              act_cost=60, # should be based off opponent hp - special case in battlechecks
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1500, # should be based off opponent hp - special case in battlechecks
                              speed=0,
                              type="melee"
                         ),

                    "Encanted Dismantle" :
                         Techniques(
                              name="Encanted Dismantle",
                              level=4,
                              act_speed=3,
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=1200,
                              type="projectile",
                              invisible=True
                         ),
                    
                    "Furnace" :
                         Techniques(
                              name="Furnace",
                              level=4,
                              act_speed=5,
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=2000,
                              speed=500,
                              type="projectile"
                         ),

                    "World Cutting Slash" : # requires mahoraga
                         Techniques(
                              name="World Cutting Slash",
                              level=5,
                              act_speed=3,
                              act_cost=80,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=9000,
                              speed=1200,
                              type="projectile",
                              invisible=True,
                              negates=True
                         )
               }
          },

          {
               "Defend": 
               {
                   "CE" :
                         Techniques(
                              name="CE reinforcement",
                              level=0,
                              act_speed=0,
                              act_cost=0,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=0,
                              strength=0,
                              speed=0, 
                              type="tank"
                         ),
                    "Cleave Spider Web" :
                         Techniques(
                              name="Cleave Spider Web",
                              level=1,
                              act_speed=2,
                              act_cost=100,
                              act_req=("Left Arm", "Right Arm"),
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
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="tank"
                         ),

                    "Dismantle Glove" : # like parry but strong since it envelops the hand
                         Techniques(
                              name="Dismantle Glove",
                              level=2,
                              act_speed=1,
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
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
                              act_req=("Left Arm", "Right Arm"),
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
                              act_req=("full"),
                              aoe=1,
                              strength=100,
                              speed=1500,
                              type="dodge"
                         )
               }
          },
          
          {
              
               "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Malevolent Shrine",
                              level=5,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=9000,
                              type="open",
                              sure_hit=True

                         ),
                    
                    "Domain Amplification" :
                         Techniques(
                              name="Domain Amplification",
                              level=5,
                              act_speed=0,
                              act_cost=50,
                              act_req=("Full"),
                              aoe=1,
                              strength=0,
                              speed=0,
                              type="envelop",
                              negates=True

                         )
               }
          }
     ],
"Rarity" : 5,
"Friction" : 0
}
# endregion

# region Sky Manipulation
sky_manip={
     
"Sky Manipulation" :
     [
          {
               "Attack" : 
                    {
                    "Thin Ice Breaker" : # main offense of tech
                         Techniques(
                              name="Thin Ice Breaker",
                              level=1,
                              act_speed=3,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=1000,
                              type="projectile"
                         ),

                    "Cloaked Attack" : # cloaks entire body to become virtually invisible
                         Techniques(
                              name="Cloaked Attack",
                              level=3,
                              act_speed=2,                              
                              act_cost=50,
                              act_req=("Full"),
                              aoe=1,
                              strength=500,
                              speed=500,
                              type="melee",
                              invisible=True
                         )
               }
          },

          {
               "Defend": 
               {
                   "CE" :
                         Techniques(
                              name="CE",
                              level=0,
                              act_speed=0,
                              act_cost=0,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=0,
                              strength=0,
                              speed=0, 
                              type="tank"
                         ),
           
               
                    "Redirect" : # redirects opponent attack back on themself
                         Techniques(
                              name="Redirect",
                              level=1,
                              act_speed=2,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=0,
                              speed=1000,
                              type="counter reflect"
                         ),

                    "Cloak Dodge" :
                         Techniques(
                              name="Cloak Dodge",
                              level=3,
                              act_speed=1,                              
                              act_cost=50,
                              act_req=("Full"),
                              aoe=1,
                              strength=100,
                              speed=500,
                              type="dodge",
                              invisible=True
                         )
               }
          },
     ],
"Rarity" : 15
}
# endregion

# region Star Rage
star_rage={
     
"Star Rage" :
     [
          {
               "Attack" : 
               {
                    "It's Mass" : 
                         Techniques(
                              name="It's Mass",
                              level=1,
                              act_speed=1,                             
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm", "Left Leg", "Right Leg"),
                              aoe=1,
                              strength=1500,
                              speed=700,
                              type="melee"
                         ),
                    
                    "Garuda Cannon Ball" : # requires summon - special check
                        Techniques(
                              name="Garuda Cannon Ball",
                              level=2,
                              act_speed=2,                             
                              act_cost=20,
                              act_req=("Left Leg", "Right Leg"),
                              aoe=1,
                              strength=1500,
                              speed=1000,
                              type="projectile"
                         ),

                    "Black Hole" : # kills self and the everyone unless stopped (this will have to be balanced lmaoo)
                        Techniques(
                              name="Black Hole",
                              level=1,
                              act_speed=3,                            
                              act_cost=500,
                              act_req=("Full"),
                              aoe=10,
                              strength=9000,
                              speed=2000,
                              type="projectile",
                              self_dmg=9000
                         )
                }
            },

          {
               "Defend": 
           
               {
                   "CE" :
                         Techniques(
                              name="CE reinforcement",
                              level=0,
                              act_speed=0,
                              act_cost=0,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=0,
                              strength=0,
                              speed=0, 
                              type="tank"
                         ),
                    "It's Mass" : 
                         Techniques(
                              name="It's Mass",
                              level=1,
                              act_speed=1,                             
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm", "Left Leg", "Right Leg"),
                              aoe=1,
                              strength=1500,
                              speed=700,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 15
}
# endregion

# region StinkaSpore
stinkaspore={  
"StinkaSpore" :
     [
          {
               "Attack" : 
               {
                    "Hydrogen Sulfide Bomb" : 
                         Techniques(
                              name="Hydrogen Sulfide Bomb",
                              level=1,
                              act_speed=3,
                              act_cost=20,
                              act_req=("Head", "Torso"),
                              aoe=5,
                              strength=150,
                              speed=100,
                              type="projectile",
                              poison=50
                         ),
                    
                    "Carbon Monoxide Disperse" : 
                         Techniques(
                              name="Carbon Monoxide Disperse",
                              level=1,
                              act_speed=3,
                              act_cost=60,
                              act_req=("Head", "Torso"),
                              aoe=5,
                              strength=100,
                              speed=100,
                              type="projectile",
                              poison=50,
                              sure_hit=True 
                         )
               }
          },

          {
               "Defend" : 
               {
                    "Ammonia Cloud" : 
                         Techniques(
                              name="Stinkaspore : Ammonia Cloud", 
                              level=1,
                              act_speed=3,
                              act_cost=60,
                              act_req=("Head", "Torso"),
                              aoe=5,
                              strength=180,
                              speed=150,
                              type="counter",
                              poison=50
                         )
               }
          }
     ],
"Rarity" : 0
}
# endregion

# region Straw Doll
straw_doll={
     
"Straw Doll" :
     [
          {
               "Attack" : 
               {
                    "Squeaky Hammer" :
                         Techniques(
                              name="Squeaky Hammer",
                              level=1,
                              act_speed=1,                              
                              act_cost=10,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=300,
                              speed=600,
                              type="melee"
                         ),

                    "Nails" : 
                         Techniques(
                              name="Nails",
                              level=1,
                              act_speed=2,                              
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=800,
                              type="projectile"
                         ),
                    
                    "Resonance" : 
                         Techniques(
                              name="Resonance",
                              level=3,
                              act_speed=2,                              
                              act_cost=40,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=0, # ???
                              type="melee", #melee on doll that links attack to target (effigy)
                              soul=400, 
                              sure_hit=True,
                              charge=1 # once the player.charge is set to 1, the technique is available
                         )
                         
               }
          },

          {
               "Defend": 
           
               {
                   "CE" : 
                         Techniques(
                              name="CE",
                              level=2,
                              act_speed=2,                             
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=400,
                              speed=800,
                              type="tank"
                         ),
                    "Squeaky Hammer" :
                         Techniques(
                              name="Squeaky Hammer",
                              level=1,
                              act_speed=1,                              
                              act_cost=10,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=300,
                              speed=600,
                              type="counter"
                         ),

                    "Nail Storm" : 
                         Techniques(
                              name="Nail Storm",
                              level=2,
                              act_speed=2,                             
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=400,
                              speed=800,
                              type="counter"
                         )
               }
          }
     ],
"Rarity" : 30
}
# endregion

# region Ten Shadows
ten_shadows={
"Ten Shadows" :
        [
            {
               "Attack" : 
               {
                   "White Dog" : 
                   Techniques(
                       name="White Dog",
                       level=1,
                       act_speed=2,
                       act_cost=50,
                       act_req=("Left Arm", "Right Arm"),
                       aoe=1,
                       strength=0,
                       speed=0,
                       type="summon"
                   ),

                    "Black Dog" : 
                         Techniques(
                              name="Black Dog",
                              level=1,
                              act_speed=2,                              
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=0,
                              speed=0,
                              type="summon",
                         ),
                    
                    "Nue" : 
                         Techniques(
                              name="Nue",
                              level=1,
                              act_speed=2,                            
                              act_cost=25,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=0,
                              speed=0,
                              type="summon",
                         ),

                    "Great Serpent" : 
                         Techniques(
                              name="Great Serpent",
                              level=1,
                              act_speed=2,                             
                              act_cost=30,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=600,
                              type="summon",
                              summon={"Great Serpent" : {"Speed" : 600, "strength" : 500, "Max CE" : 100}}
                         ),
                    
                    "Max Elephant" : 
                         Techniques(
                              name="Max Elephant",
                              level=1,
                              act_speed=3,                              
                              act_cost=35,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=500,
                              type="summon",
                              summon={"Max Elephant" : {"Speed" : 500, "strength" : 800, "Max CE" : 200}}
                         ),

                    "Piercing Ox" : 
                         Techniques(
                              name="Piercing Ox",
                              level=2,
                              act_speed=3,
                              act_cost=50,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1200,
                              speed=400,
                              type="summon",
                              summon={"Piercing Bull" : {"Speed" : 400, "strength" : 1200, "Max CE" : 300}}
                         ),

                    "Mahoraga" : 
                         Techniques(
                              name="Mahoraga",
                              level=1,
                              act_speed=3,
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1500,
                              speed=1000,
                              type="summon",
                              summon={"Mahoraga" : {"Speed" : 1000, "strength" : 1500, "Max CE" : 500}}
                         )
                         
               }
          },

          {
               "Defend": 
           
               {
                   "CE" :
                         Techniques(
                              name="CE reinforcement",
                              level=0,
                              act_speed=0,
                              act_cost=0,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=0,
                              strength=0,
                              speed=0, 
                              type="tank"
                         ),
                    "Rabbit Escape" : 
                         Techniques(
                              name="Rabbit Escape",
                              level=1,
                              act_speed=1,
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=800,
                              type="summon",
                              summon={"Rabbit Escape" : {"Speed" : 800, "strength" : 100, "Max CE" : 100}}
                         ),
                    
                    "Toad" : 
                         Techniques(
                              name="Toad",
                              level=1,
                              act_speed=1,
                              act_cost=30,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=1000,
                              type="summon",
                              summon={"Toad" : {"Speed" : 1000, "strength" : 100, "Max CE" : 100}}
                         ),

                    "Round Deer" :
                         Techniques(
                              name="Round Deer",
                              level=1,
                              act_speed=2,
                              act_cost=20,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=600,
                              speed=600,
                              type="summon",
                              summon={"Round Deer" : {"Speed" : 600, "strength" : 600, "Max CE" : 400}}
                         ),
               }
          },
          {
          "Barrier" :
               {
                   "Domain Expansion" :
                         Techniques(
                              name="Domain Expansion: Chimera Shadow Garden",
                              level=4,
                              act_speed=2,
                              act_cost=300,
                              act_req=("Left Arm", "Right Arm"),
                              aoe=20,
                              strength=1000,
                              speed=8000,
                              type="open",
                              sure_hit=True

                         )
               }
          }
     ],
"Rarity" : 5
}

# endregion

# region TEMPLATE
# _={  
# "" :
#      [
#           {
#                "Attack" : 
#                {
#                     "" :
#                          Techniques(
#                               name="",
#                               level=1,
#                               act_speed=1,                              
#                               act_cost=1,
#                               act_req=("Left Arm", "Right Arm"),
#                               aoe=1,
#                               strength=100,
#                               speed=100,
#                               type=""
#                          )
#                }
#           },

#           {
#                "Defend" : 
#                {
#                     "" :
#                          Techniques(
#                               name="",
#                               level=1,
#                               act_speed=1,                              
#                               act_cost=1,
#                               act_req=("Left Arm", "Right Arm"),
#                               aoe=1,
#                               strength=100,
#                               speed=100,
#                               type=""
#                          )
#                }
#           }
#      ],
# "Rarity" : 100
# }
# endregion

technique_list = [
                    anti_gravity, anxious_ears, auspicious_beasts_summon, barehand, bird_manip, 
                    blood_manip, body_hop, boogie_woogie, bugfly, charger, ce_discharge, 
                    comedian, construction, contractual_recreation, copy, cursed_speech, cursed_spirit_manip, 
                    disaster_flames, disaster_tides, explosive_flesh, finger_bearer, 
                    floatjelly, flymouth, furrpede, hr_max, hr_zero, ice_manip, idle_transfig, limitless, 
                    mba, natures_wrath, orbmaster, primate, projection_sorcery, 
                    shrine, sky_manip, star_rage, stinkaspore, straw_doll, ten_shadows
               ]