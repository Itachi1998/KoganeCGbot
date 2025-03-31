class Techniques():
    def __init__(self, 
                 name: str,  # "Blood Manipulation: Piercing Blood"
                 level: int, # 1-5
                 act_speed: int, # activation speed of technique: 1-5 (can be changed with binding vows) 
                 act_cost: int,
                 act_body: tuple, # activation cost per turn of activating this technique: can be changed with binding vows
                 aoe: int, # amount of players targetable (can be changed with binding vows)
                 strength: int, # strength of attack or defense (will be used in attack vs defense checks, can be changed with binding vows)
                 speed: int, # speed of attack or defense (will be used in attack vs defense checks, can be changed with binding vows) 
                 type: str,
                 soul: int=None,
                 buff: tuple=None,
                 debuff: tuple=None,
                 poison: tuple = None,
                 stun: int = None, # St
                 stack: int = None, # Projection Techniques
                 charge: list=None, # Kashimo or Nobara techniques
                 summon: dict=None,
                 sure_hit=None,
                 target=None,
                 negates: bool =None,
                 duration: int=None,
                 cooldown: int=None,
                 visability: int=None
                 ):
            
            self.name = name
            self.level=level
            self.act_speed = act_speed
            self.act_cost = act_cost
            self.act_body= act_body
            self.aoe = aoe
            self.strength = strength
            self.speed = speed
            self.type=type
            self.soul=soul
            self.buff=buff
            self.debuff=debuff
            self.poison=poison
            self.stun=stun
            self.stack=stack
            self.charge=charge
            self.summon=summon
            self.sure_hit=sure_hit
            self.target=target
            self.negates=negates
            self.duration=duration
<<<<<<< HEAD
            self.cooldown=cooldown 

=======
            self.cooldown=cooldown
            self.visability=visability
>>>>>>> 5120e3bbd7d3e9d8babe988a18233fd83e7937c1
