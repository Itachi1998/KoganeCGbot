from techniques import Techniques
from random import randint
# region ### BIRD MANIP

bird_manip = {
     "Bird Manipulation" : [
          {"Attack" : 
               { "Talon Attack" : 
                    Techniques(
                         name="Bird Manip: Talon Attack",
                         level=1,
                         act_speed=100,
                         act_cost=100,
                         act_body=("Head", "Right Arm", "Left Arm"),
                         aoe=3,
                         strength=50,
                         speed=250,
                         type="projectile"
                    ),

               "Bird Flock" : 
                    Techniques(
                         name="Bird Manip: Bird Flock",
                         level=2,
                         act_speed=50,
                         act_cost=300,
                         act_body=("head", "left arm", "right arm"),
                         aoe=3,
                         strength=200,
                         speed=400,
                         type="projectile"
                    ),
                    
               "Bird Sacrifice" : 
                    Techniques(
                         name="Bird Manip: Bird Sacrifice",
                         level=3,
                         act_speed=20,
                         act_cost=400,
                         act_body=("Head", "left arm", "right arm"),
                         aoe=2,
                         strength=1500,
                         speed=500,
                         stun=3,
                         type="Projectile"
                    )
               }
           },
           {"Defense": 
               {"Feather Screen" : 
                    Techniques(
                              name="Bird Manip: Feathered Screen",
                              level=1,
                              act_speed=40,
                              act_cost=50,
                              act_body=("Head", "left arm", "right arm"),
                              aoe=3,
                              strength=50,
                              speed=100,
                              type="dodge"
                              ),
                    "Birds Eye" : 
                         Techniques(
                              name="Bird Manip: Birds Eye",
                              level=2,
                              act_speed=20,
                              act_cost=10,
                              act_body=("head"),
                              aoe=5,
                              strength=150,
                              speed=500,
                              buff=("speed", 550),
                              type="dodge"
                              )

               }
          }
     ],
     "Rarity" : 80
}

# endregion



# region ### PLAYER TECH BLOOD MANIP
blood_manip= {"Blood Manip" : [
          {
             "Attack" : {
                    "Piercing Blood" :
                         Techniques(
                              name="Blood Manip: Piercing Blood", 
                              level=1,
                              act_speed=100,
                              act_cost=100,
                              act_body=("Head", "left arm", "right arm"),
                              aoe=1,
                              strength=400,
                              speed=1200,
                              type="projectile",
                              poison=(10, 4),
                              stun=1
                              ),

                    "Blood Edge" : 
                         Techniques(
                              name="Blood Manip: Blood Edge",
                              level=2,
                              act_speed=50,
                              act_cost=300,
                              act_body=("Head", "left arm", "right arm"),
                              aoe=5,
                              strength=800,
                              speed=500,
                              type="Projectile",
                              poison=(5, 8)
                              ),

                    "Red Scale" : 
                         Techniques(name="Blood Manip: Red Scale",
                              level=1,
                              act_speed=10,
                              act_cost=500,
                              act_body=("Head", "right arm", "left arm", "left leg", "right leg"),
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
                "Defense" : {
                "Blood Meteor" : 
                Techniques(name="Blood Manip: Blood Meteor",
                                                        level=1,
                                                        act_speed=100,
                                                        act_cost=300,
                                                        act_body=("Head", "left arm", "right arm"),
                                                        aoe=1,
                                                        strength=400,
                                                        speed=100,
                                                        type="Counter",
                                                        stun=3
                                                        ),
                "Blood Armor":
                Techniques(name="Blood Manip: Blood Armor",
                                           level=3,
                                           act_speed=20,
                                           act_cost=500,
                                           act_body=("Head", "Torso", "Right Arm", "Left Arm", "Right Leg", "Left Leg"),
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

# region ### PLAYER TECH BOOGIE WOOGIE
boogie_woogie = {

"Boogie Woogie" : 
     [
          {
               "Attack" :
                 {
                    "Rock Throw" : 
                         Techniques(
                              name="Boogie Woogie: Rock Throw",
                              level=1,
                              act_speed=10,
                              act_cost=20,
                              act_body=("Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"),
                              aoe=1,
                              strength=200,
                              speed=500,
                              type="Melee",
                              buff=("strength", "speed")
                              ),

                    "Double Switch Fake" : 
                         Techniques(
                              name="Boogie Woogie: Double Switch Fake",
                              level=2,
                              act_speed=0,
                              act_cost=0,
                              act_body=("Head", "Torso", "Left Leg", "Right Leg", "Right Arm", "Left Arm"),
                              aoe=5,
                              strength=400,
                              speed=400,
                              type="Melee",
                              stun=2),
                    "Over Here" : 
                         Techniques(
                              name="Boogie Woogie: Over Here",
                              level=2,
                              act_speed=10,
                              act_cost=50,
                              act_body=("Head", "Torso", "Right Arm", "Left Arm"),
                              aoe=5,
                              strength=800,
                              speed=2000,
                              type="Melee",
                              stun=1
                              )
               }
          },

          {
               "Defense" : 
               {
                    "Clap Swap" : 
                         Techniques(
                              name="Boogie Woogie: Clap Swap",
                              level=1,
                              act_speed=10,
                              act_cost=50,
                              act_body=("Head", "Torso", "Left Arm", "Right Arm"),
                              aoe=5,
                              strength=10,
                              speed=2000,
                              type="Dodge"
                              ),
                    "Reverse Swap" : 
                         Techniques(
                              name="Boogie Woogie: Reverse Swap",
                              level=3,
                              act_speed=10,
                              act_cost=50,
                              act_body=("Head", "Torso", "Left Arm", "Right Arm"),
                              aoe=1,
                              strength=10,
                              speed=2000,
                              type="counter"
                              ),
                    "Vibra Swap" : 
                         Techniques(
                              name="Boogie Woogie: Vibra Swap",
                              level=4,
                              act_speed=1,
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=5,
                              strength=10,
                              speed=5000,
                              type="dodge"
                              )
               }
          }
     ],

"Rarity" : 50
}
# endregion

# region ### PLAYER TECH COMEDIAN

comedian={
"Comedian" : 
     [
          {
               "Attack" : 
               {
                    "Punchline" : 
                         Techniques(
                              name="Comedian: Punchline",
                              level=1,
                              act_speed=1,
                              act_cost=10,
                              act_body=("head", "torso", "arms", "legs"),
                              aoe=1,
                              strength=500,
                              speed=900,
                              type="Melee",
                              buff=("strength", "speed")
                              ),
                    "One Liner" :
                         Techniques(
                              name="Comedian: One Liner",
                              level=1,
                              act_speed=1,
                              act_cost=10,
                              act_body=("Head", "torso", "arms", "legs"),
                              aoe=4,
                              strength=700,
                              speed=900,
                              type="Melee",
                              buff=("strength", "speed")),
                    "Skit" : 
                         Techniques(
                              name="Comedian: Skit",
                              level=2,
                              act_speed=1,
                              act_cost=10,
                              act_body=("Head", "Torso", "Arms", "Legs"),
                              aoe=4,
                              strength=900,
                              speed=1500,
                              type="Melee",
                              buff=("strength", "Speed")
                              ),
                    "Truck Kun" :
                         Techniques(
                              name="Comedian: Truck Kun",
                              level=3,
                              act_speed=10,
                              act_cost=10,
                              act_body=("Head", "Torso", "Arms", "Legs"),
                              aoe=1,
                              strength=1500,
                              speed=2000,
                              type="Projectile",
                              stun=1,
                              sure_hit=True
                         ),
                    "Wouldn't It Be Funny" :
                         Techniques(
                              name="Comedian: Wouldn't it be funny",
                              level=5,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Head", "torso", "arms", "legs"),
                              aoe=4,
                              strength=2000,
                              speed=1000,
                              type="Projectile",
                              sure_hit=True
                              )
                    }
                },
          {
               "Defense" :
                 {
                    "Red is Taboo" : 
                         Techniques(
                              name="Comedian: Red is Taboo",
                              level=1,
                              act_speed=10,
                              act_cost=10,
                              act_body=("Head", "arms", "torso"),
                              aoe=4,
                              strength=200,
                              speed=1000,
                              type="counter",
                              negates=True
                              ),
                    "Fanta Sea":
                         Techniques(
                              name="Comedian: Fanta Sea",
                              level=2,
                              act_speed=10,
                              act_cost=10,
                              act_body=("Head", "arm", "torso"),
                              aoe=5,
                              strength=1500,
                              speed=1500,
                              type="counter"
                              ),
                    "Slimed" :
                         Techniques(
                              name="Comedian: Slimed",
                              level=1,
                              act_speed=10,
                              act_cost=10,
                              act_body=("full"),
                              aoe=2,
                              strength=900,
                              speed=900,
                              type="dodge"
                              ),
                    "Ya Trying To Kill Me?" : # LMAO
                         Techniques(
                              name="Comedian: Ya Trying To Kill Me?",
                              level=3,
                              act_speed=10,
                              act_cost=10,
                              act_body=("full"),
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

# endregion #### PLAYER TECH COMEDIAN

# region ### PLAYER TECH CONSTRUCTION

construction={
     "Construction": [
          {
            "Attack" : 
                    {
                    "Blade" : 
                         Techniques(
                              name="Construction: Blade",
                              level=1,
                              act_speed=40,
                              act_cost=400,
                              act_body=("Full"),
                              aoe=1,
                              strength=850,
                              speed=500,
                              type="Melee",
                         ),
                    "Ammo" : 
                         Techniques(
                              name="Construction: Ammo",
                              level=1,
                              act_speed=30,
                              act_cost=400,
                              act_body=("Full"),
                              aoe=1,
                              strength=700,
                              speed=600,
                              type="Projectile"
                         ),
                    "Liquid Metal" : 
                         Techniques(
                              name="Construction: Liquid Metal",
                              level=4,
                              act_speed=40,
                              act_cost=150,
                              act_body=("Full"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="Projectile",
                              poison=(10, 10)
                         ),
                    "Air To Surface Missile" : 
                         Techniques(name="Six Eyes Construction: Air to Surface Missiles",
                                   level=3,
                                   act_speed=1,
                                   act_cost=5,
                                   act_body=("Full"),
                                   aoe=5,
                                   strength=1500,
                                   speed=1500,
                                   type="Projectile"),
                    "Nuclear Warhead" : 
                         Techniques(name="Six Eyes Construction: Nuclear Warhead",
                                   level=5,
                                   act_speed=20,
                                   act_cost=200,
                                   act_body=("full"),
                                   aoe=5,
                                   strength=5500,
                                   speed=2000,
                                   type="Projectile"),
                                   
                    "True Sphere Orbs" : 
                         Techniques(name="Six Eyes Construction: True Sphere Orbs",
                                   level=3,
                                   act_speed=10,
                                   act_cost=20,
                                   act_body=("full"),
                                   aoe=4,
                                   strength=3500,
                                   speed=25000,
                                   type="Projectile"
                                   ) 
                    }
          },
          {
            "Defense" : 
                    {
                    "Bug Armor": 
                         Techniques(name="Construction: Blood Armor",
                                   level=3,
                                   act_speed=20,
                                   act_cost=150,
                                   act_body=("Full"),
                                   aoe=1,
                                   strength=2000,
                                   speed=2000,
                                   type="Counter",
                                   buff=("strength", "speed")
                                   ),
                    "Armored Sentinels":
                         Techniques(name="Six Eyes Construction: Armored Sentinels",
                                   level=1,
                                   act_speed=1,
                                   act_cost=50,
                                   act_body=("Full"),
                                   aoe=1,
                                   strength=10000,
                                   speed=1000,
                                   type="Summon",
                                   summon={"Sentinel" : {'dmg' : 1000, 'speed' : 1000, "max_hp" : 900, "tamed" : True}}
                                   ),
                    "Liquid Metal Shield" : 
                         Techniques(
                                   name="Construction: Liquid Metal Shield",
                                   level=1,
                                   act_speed=20,
                                   act_cost=300,
                                   act_body=("full"),
                                   aoe=3,
                                   strength=600,
                                   speed=600,
                                   type="tank"
                              )
                    }
          }
],
"Rarity" : 15, 
"Six Eyes" : False
}

# endregion

# region ### PLAYER COPY TECH

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
                         act_body=("Head"),
                         aoe=5,
                         strength=10,
                         speed=800,
                         type="Projectile",
                         stun=4),
                    "Die" : 
                         Techniques(
                              name="Copied Technique: Die",
                              level=2,
                              act_speed=30,
                              act_cost=500,
                              act_body=("full"),
                              aoe=4,
                              strength=400,
                              speed=1000,
                              type="Projectile"
                         ),
                    "Sword Blast" : 
                         Techniques(
                              name="Sword Reinforcement Discharge",
                              level=3,
                              act_speed=3,
                              act_cost=300,
                              act_body=("Full", "sword"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="Melee"
                         ),
                    "Authentic Love Beam" : 
                         Techniques(
                              name="Authentic Love Beam",
                              level=1,
                              act_speed=20,
                              act_cost=500,
                              act_body=("Full", "Rika"),
                              aoe=5,
                              strength=2000,
                              speed=2000,
                              type="Projectile"
                         ),
                    "Rika Summon" : 
                         Techniques(
                              name="Come out, RIKA",
                              level=1,
                              act_speed=1,
                              act_cost=100,
                              act_body=("Head"),
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
               "Don't Move" : Techniques(
                    name="Copied technique: Don't Move",
                    level=1,
                    act_speed=20,
                    act_cost=50,
                    act_body=("Head"),
                    aoe=3,
                    strength=50,
                    speed=800,
                    type="counter",
                    stun=2,
                    
                    )
               }
          }
],
"Rarity" : 15,
"Six Eyes" : False,
}


# endregion



# region ### CURSED SPEECH TECH

cursed_speech={
     "Cursed Speech" :
       [
          {
               "Attack" : 
               {
                    "Freeze" : 
                         Techniques(
                              name="Freeze!", 
                              level=1, 
                              act_speed=10, 
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=2,
                              strength=600,
                              speed=900,
                              type="projectile",
                              stun=3,
                              visable=False
                         ),

                    "Blast Away" :
                         Techniques(
                              name="Blast Away!",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="Projectile",
                              visable=False
                         ),

                    "Plummet" : 
                         Techniques(
                              name="Plummet!",
                              level=3,
                              act_speed=10,
                              act_cost=100,
                              act_body=("Head", "torso"),
                              aoe=2,
                              strength=1000,
                              speed=1000,
                              type="Projectile",
                              stun=1,
                              visable=False
                         )
          }
          },
          {
               "Defend" :
               {
                         
                    "Freeze" : 
                         Techniques(
                              name="Freeze!", 
                              level=1, 
                              act_speed=10, 
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=2,
                              strength=600,
                              speed=900,
                              type="counter",
                              stun=3,
                              visable=False
                         ),
                    
                    "Blast Away" :
                         Techniques(
                              name="Blast Away!",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="counter",
                              visable=False
                         )
                    
                }
          }
     ],
     "Rarity" : 80
}

#endregion



# region ### Cursed Spirit Manipulation
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
                                   act_body=("Full"),
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
                              act_body=("Full"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="Summon",
                              summon={}
                         )
                    }
          }
     ],
"Rarity" : 5
}

# endregion



# region ### HR: Zero

hr_zero={
      
"Heavenly Restriction: Zero" : [
            {
                  "Attack" : 
                         {
                         "3 Piece" : 
                               Techniques(
                                     name="Three Piece Combo",
                                     level=1,
                                     act_speed=1,
                                     act_cost=1,  # Updated act_cost to 1
                                     act_body=("Left Arm", "Right Arm"),
                                     aoe=3,
                                     strength=1000,
                                     speed=1000,
                                     type="Melee"
                               ),
                         "Spinning Back Kick":
                               Techniques(
                                     name="Spinning Back Kick",
                                     level=1,
                                     act_speed=3,
                                     act_cost=1,  # Updated act_cost to 1
                                     act_body=("Left Leg", "Right Leg"),
                                     aoe=1,
                                     strength=1200,
                                     speed=1200,
                                     type="Melee"
                               ),
                         "Yeet Car" : 
                               Techniques(
                                     name="Yeet Car",
                                     level=1,
                                     act_speed=10,
                                     act_cost=1,  # Updated act_cost to 1
                                     act_body=("arms", "legs"),
                                     aoe=1,
                                     strength=800,
                                     speed=800,
                                     type="Projectile"
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
                                     act_body=("Full"),
                                     aoe=1,
                                     strength=2000,
                                     speed=2000,
                                     type="tank"
                               )
             
                  }
            }
      ],
"Rarity" : 20
}

# endregion



# region ### Idle Transfiguration

soul_manipulation={
     
"Soul Manipulation" :
     [
          {
               "Attack" : 
               {
                    "Transmutate" : 
                         Techniques(
                              name="Soul Manipulation: Transmutate",
                              level=1,
                              act_speed=1,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=800,
                              type="Melee",
                              soul=True
                         ),
                    "Transmutated Souls":
                         Techniques(
                              name="Soul Manipulation: Transmutated Souls",
                              level=1,
                              act_speed=3,
                              act_cost=50,
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=2,
                              strength=700,
                              speed=600,
                              type="summon",
                              summon={"Polymorphic Soul Isomer" : {"Speed" : 600, "strength" : 700, "Max CE" : 200}}
                         )

                    # "ISBODK Transform" : # make a general move like a domain?
                    #      Techniques(
                    #           name="ISBODK Transform",
                    #           level=3,
                    #           act_speed=2,
                    #           act_cost=150,
                    #           act_body=("Full"),
                    #           aoe=0,
                    #           strength=1200,
                    #           speed=1000,
                    #           type="transform" ###
                    #         )
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
                         act_body=("Full"),
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
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=200,
                            speed=800,
                            type="dodge"
                            )
           
               }
          }
     ],
"Rarity" : 15
}

# endregion


# region ### Limitless

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
                            act_body=("Left Arm", "Right Arm"),
                            aoe=(1, 5),
                            strength=1000,
                            speed=1600,
                            type="projectile"
                         ),
                    
                    "Red": # RCT required
                        Techniques(
                            name="Red",
                            level=2,
                            act_speed=2,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1600,
                            speed=1000,
                            type="projectile"
                         ),
                    
                    "Void Punch" : 
                        Techniques(
                            name="Void Punch",
                            level=4,
                            act_speed=1,
                            act_cost=25,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=500,
                            speed=1600,
                            type="melee"
                         ),

                    "Hollow Purple" : 
                        Techniques(
                            name="Hollow Purple",
                            level=4,
                            act_speed=3,
                            act_cost=150,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=2500,
                            speed=1000,
                            type="projectile"
                         ),
                    
                    "Unlimited Hollow Purple" : # add self_dmg in checks
                        Techniques(
                            name="Unlimited Hollow Purple",
                            level=5,
                            act_speed=3,
                            act_cost=150,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=10,
                            strength=2500,
                            speed=2000,
                            type="projectile",
                            self_dmg=1250
                         )
                }
            },

          {
               "Defend": 
           
               {
                    "Infinity" :
                        Techniques(
                            name="Infinty",
                            level=1,
                            act_speed=0,
                            act_cost=1,
                            act_body=("Full"),
                            aoe=1,
                            strength=9999,
                            speed=9999,
                            type="tank"
                        ),

                    "Blue" : 
                        Techniques(
                            name="Blue",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=(1, 5),
                            strength=1000,
                            speed=1600,
                            type="dodge"
                        ),
                    
                    "Red": # RCT required
                        Techniques(
                            name="Red",
                            level=2,
                            act_speed=2,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1600,
                            speed=1000,
                            type="counter"
                        ),

                    "Void Punch" : 
                        Techniques(
                            name="Void Punch",
                            level=4,
                            act_speed=1,
                            act_cost=25,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=500,
                            speed=1600,
                            type="counter"
                         )
                }
            }
        ],
"Rarity" : 3,
"Six Eyes" : False # Lowkey useless without it
}

# endregion



# region ### MBA

mba={
     
"Mythic Beast Amber" : # add self_dmg in checks
        [
            {
                "Attack" : 
                {
                    "Lighting Dash" :
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_body=("Full"),
                            aoe=1,
                            strength=500,
                            speed=900,
                            type="melee"
                        ),

                    "Lighting Rod" : # requires cursed tool - add in checks
                        Techniques(
                            name="Lightning Rod",
                            level=3,
                            act_speed=1,
                            act_cost=150,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1000,
                            speed=1200,
                            type="projectile",
                            cooldown=3
                         ),

                    "Corona Blast" : 
                        Techniques(
                            name="Corona Blast",
                            level=4,
                            act_speed=2,
                            act_cost=80,
                            act_body=("Head"),
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
                    "Lighting Dash" : 
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_body=("Full"),
                            aoe=1,
                            strength=500,
                            speed=900,
                            type="dodge"
                        ),

                    "Corona Discharge" : # localized electric discharge created by a strong electrical field ionizes the surrounding air
                        Techniques(
                            name="Corona Discharge",
                            level=4,
                            act_speed=2,
                            act_cost=80,
                            act_body=("Full"),
                            aoe=5,
                            strength=600,
                            speed=1200,
                            type="counter"
                        )
                }
            }
        ],
"Rarity" : 7
}

# endregion



# region ### Projection Sorcery

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
                            act_body=("Left Arm", "Right Arm"),
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
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="dodge"
                        ),
                    
                    "Projection Stun" : 
                        Techniques(
                            name="Projection Stun",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="counter",
                            stun=True
                        )
                }
            }
        ],
"Rarity" : 25
}

# endregion



# region ### Auspicious Beasts Summon

auspicious_beasts_summon={
     
"Auspicious Beasts Summon" :
        [
            {
                "Attack" : 
                {
                    "Auspicious Beasts Summon Kaichi" : # spinning cone horn projectile thing
                        Techniques(
                            name="Auspicious Beasts Summon Kaichi",
                            level=1,
                            act_speed=1,
                            act_cost=20,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=200,
                            speed=600,
                            type="projectile"
                         ),
                    
                    "Auspicious Beasts Summon Ryu" : # dragon attack 
                        Techniques(
                            name="Auspicious Beasts Summon Reiki",
                            level=3,
                            act_speed=1,
                            act_cost=100,
                            act_body=("Left Arm", "Right Arm"),
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
                    "Auspicious Beasts Summon Reiki" : # cursed water that increases speed and can cushion attacks
                        Techniques(
                            name="Auspicious Beasts Summon Reiki",
                            level=1,
                            act_speed=1,
                            act_cost=30,
                            act_body=("Full"),
                            aoe=1,
                            strength=300,
                            speed=700,
                            type="dodge"
                         ),
                    
                    "Auspicious Beasts Summon Kirin" : # nullifies pain (ig add def or overall stat boost?) - also stuns self after technique ends
                        Techniques(
                            name="Auspicious Beasts Summon Kirin",
                            level=2,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Full"),
                            aoe=1,
                            strength=500,
                            speed=1000,
                            type="tank"
                        )
                }
            }
        ],
"Rarity" : 80
}

# endregion



# region ### Shrine

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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="projectile",
                              visable=False
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
                              visable=False
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
                              visable=False
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
                    "Dismantle Parry" :
                         Techniques(
                              name="Dismantle Parry",
                              level=3,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
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
                              strength=500,
                              speed=1000,
                              type="tank"
                         ),
                    
                    "Cleave Spider Web" :
                         Techniques(
                              name="Cleave Spider Web",
                              level=4,
                              act_speed=2,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1500,
                              speed=1000, 
                              type="counter"
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
                        speed=1000,
                        type="dodge"
                    )
                }
            }
        ],
"Rarity" : 5
}

# endregion



# region ### Star Rage

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
                              act_body=("Left Arm", "Right Arm", "Left Leg", "Right Leg"),
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
                              act_body=("Left Leg", "Right Leg"),
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
                              act_body=("Full"),
                              aoe=10,
                              strength=9999,
                              speed=2000,
                              type="projectile",
                              self_dmg=9999
                         )
                }
            },

          {
               "Defend": 
           
               {
                    "It's Mass" : 
                         Techniques(
                              name="It's Mass",
                              level=1,
                              act_speed=1,                             
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm", "Left Leg", "Right Leg"),
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



# region ### Straw Doll

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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=800,
                              type="projectile"
                         ),
                    
                    "Reasonance" : 
                         Techniques(
                              name="Reasonance",
                              level=3,
                              act_speed=2,                              
                              act_cost=40,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=2000, # ???
                              type="melee", #melee on doll that links attack to target (effigy)
                              soul=True, 
                              sure_hit=True
                         )
                         
                }
            },

          {
               "Defend": 
           
               {
                    "Squeaky Hammer" :
                         Techniques(
                              name="Squeaky Hammer",
                              level=1,
                              act_speed=1,                              
                              act_cost=10,
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=400,
                              speed=800,
                              type="counter"
                         )
                }
            }
        ],
"Rarity" : 40
}

# endregion


# region ### Ten Shadows

ten_shadows={
     
"Ten Shadows" :
        [
            {
                "Attack" : 
                {
                    "Divine Dog Claw" : 
                         Techniques(
                              name="Divine Dog Claw",
                              level=1,
                              act_speed=2,                              
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=600,
                              type="summon",
                              summon={"Divine Dogs" : {"Speed" : 600, "strength" : 400, "Max CE" : 100}}
                         ),
                    
                    "Nue Lightning" : 
                         Techniques(
                              name="Nue Lightning",
                              level=1,
                              act_speed=2,                            
                              act_cost=25,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=400,
                              speed=700,
                              type="summon",
                              summon={"Nue" : {"Speed" : 700, "strength" : 400, "Max CE" : 100}}
                         ),

                    "Great Serpent Choke" : 
                         Techniques(
                              name="Great Serpent Choke",
                              level=1,
                              act_speed=2,                             
                              act_cost=30,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=600,
                              type="summon",
                              summon={"Great Serpent" : {"Speed" : 600, "strength" : 500, "Max CE" : 100}}
                         ),
                    
                    "Max Elephant Drop" : 
                         Techniques(
                              name="Max Elephant Drop",
                              level=1,
                              act_speed=3,                              
                              act_cost=35,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=500,
                              type="summon",
                              summon={"Max Elephant" : {"Speed" : 500, "strength" : 800, "Max CE" : 200}}
                         ),

                    "Piercing Ox" : 
                         Techniques(
                              name="Piercing Bull Charge",
                              level=2,
                              act_speed=3,
                              act_cost=50,
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                    "Rabbit Escape" : 
                         Techniques(
                              name="Rabbit Escape",
                              level=1,
                              act_speed=1,
                              act_cost=20,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=100,
                              speed=800,
                              type="summon",
                              summon={"Rabbit Escape" : {"Speed" : 800, "strength" : 100, "Max CE" : 100}}
                         ),
                    
                    "Toad Tongue" : 
                         Techniques(
                              name="Toad Tongue",
                              level=1,
                              act_speed=1,
                              act_cost=30,
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=600,
                              speed=600,
                              type="summon",
                              summon={"Round Deer" : {"Speed" : 600, "strength" : 600, "Max CE" : 400}}
                         ),
                }
            }
        ],
"Rarity" : 15
}

# endregion


# region ### Sky Manipulation

sky_manipulation={
     
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=800,
                              speed=1000,
                              type="projectile"
                         ),

                    "Cloaked Attack" : # cloaks entire body to become virtually invisable
                         Techniques(
                              name="Cloaked Attack",
                              level=3,
                              act_speed=2,                              
                              act_cost=50,
                              act_body=("Full"),
                              aoe=1,
                              strength=500,
                              speed=500,
                              type="melee",
                              visable=False
                         )
                }
            },

          {
               "Defend": 
           
               {
                    "Redirect" : # redirects opponent attack back on themself
                         Techniques(
                              name="Redirect",
                              level=1,
                              act_speed=2,                              
                              act_cost=50,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=0, # pull attack dmg in checks?
                              speed=1000,
                              type="counter"
                         ),

                    "Cloaked Dodge" :
                         Techniques(
                              name="Cloaked Dodge",
                              level=3,
                              act_speed=1,                              
                              act_cost=50,
                              act_body=("Full"),
                              aoe=1,
                              strength=0, #?
                              speed=500,
                              type="dodge",
                              visable=False
                         )
                }
            }
        ],
"Rarity" : 15
}

# endregion


# region ### Ice Manipulation

ice_manipulation={
     
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Head"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Left Arm", "Right Arm"),
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
                              act_body=("Head"),
                              aoe=5,
                              strength=1200,
                              speed=1000,
                              type="counter",
                              stun=3
                         )
                }
            }
        ],
"Rarity" : 10
}

# endregion


# region ### Cursed Energy Discharge

cursed_energy_discharge={
     
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
                              act_body=("Head"),
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
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=500,
                              speed=1000,
                              type="tank"
                         )
               }
          }
     ],
"Rarity" : 20
}

# endregion


# region ### TEMPLATE

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
#                               act_body=("Left Arm", "Right Arm"),
#                               aoe=1,
#                               strength=0,
#                               speed=0,
#                               type=""
#                          )
#                }
#           },

#           {
#                "Defend": 
#                {
#                     "" :
#                          Techniques(
#                               name="",
#                               level=1,
#                               act_speed=1,                              
#                               act_cost=1,
#                               act_body=("Left Arm", "Right Arm"),
#                               aoe=1,
#                               strength=0,
#                               speed=0,
#                               type=""
#                          )
#                 }
#             }
#         ],
# "Rarity" : 100
# }

# endregion


technique_list = [star_rage, mba, blood_manip, ten_shadows, 
                  cursed_speech, construction, copy, shrine, 
                  limitless, straw_doll, boogie_woogie, 
                  projection_sorcery, auspicious_beasts_summon, 
                  soul_manipulation, hr_zero, sky_manipulation, 
                  ice_manipulation, cursed_energy_discharge]