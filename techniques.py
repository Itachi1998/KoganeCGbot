




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
                stun: int = None,
                stack: int = None, # Projection Techniques
                charge: bool=False, # Kashimo or Nobara techniques
                summon: dict=None,
                sure_hit=None,
                negates: bool =None,
                duration: int=None,
                cooldown: int=None,
                invisible: bool=None,
                self_dmg: int=None,
                self_heal: int=None,
                heal: dict=None,
                extern_strength: int=None,
                intern_strength: int=None
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
            self.negates=negates
            self.duration=duration
            self.cooldown=cooldown
            self.invisible=invisible
            self.self_dmg=self_dmg
            self.self_heal=self_heal
            self.heal=heal
            self.intern_strength=intern_strength
            self.extern_strength=extern_strength


class CursedTools():
    def __init__(self, 
                name: str, 
                cost: int, 
                broken: bool, 
                hp: int, 
                max_hp: int,
                act_body: tuple,
                aoe: int,
                strength: int,
                speed: int,
                type: str,
                soul: bool = None,
                buff: tuple = None,
                debuff: tuple = None,
                poison: tuple = None,
                stun: int = None,
                negates: bool = None,
                self_dmg: int = None,
                charge: int =None
                ):
                
            self.name=name
            self.cost=cost
            self.broken=broken
            self.hp=hp
            self.max_hp=max_hp
            self.act_body=act_body
            self.aoe=aoe
            self.strength=strength
            self.speed=speed
            self.type=type
            self.soul=soul
            self.buff=buff
            self.debuff=debuff
            self.poison=poison
            self.stun=stun
            self.negates=negates
            self.self_dmg=self_dmg
            self.charge=charge