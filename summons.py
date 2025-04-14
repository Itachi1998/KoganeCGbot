from game import Enemy, human_body_parts

#region White Divine Dog
class White_Divine_Dog(Enemy):
    def __init__(self):
        super().__init__(
            name="White Divine Dog",
            level=1,
            max_hp=300,
            max_ce=100,
            strength=300,
            speed=500,
            technique="Divine Dog",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

white_divine_dog = White_Divine_Dog()
#endregion

#region Black Divine Dog
class Black_Divine_Dog(Enemy):
    def __init__(self):
        super().__init__(
            name="Black Divine Dog",
            level=1,
            max_hp=300,
            max_ce=100,
            strength=300,
            speed=500,
            technique="Divine Dog",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

black_divine_dog = Black_Divine_Dog()
#endregion

#region Rabbit Escape
class Rabbit_Escape(Enemy): 
    def __init__(self):
        super().__init__(
            name="Rabbit Escape",
            level=1,
            max_hp=10,
            max_ce=10,
            strength=10,
            speed=500,
            technique="Rabbit Escape",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

rabbit_escape = Rabbit_Escape()
#endregion

#region Toad
class Toad(Enemy):
    def __init__(self):
        super().__init__(
            name="Toad",
            level=1,
            max_hp=200,
            max_ce=100,
            strength=100,
            speed=800,
            technique="Toad",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

toad = Toad()
#endregion

#region Nue
class Nue(Enemy):
    def __init__(self):
        super().__init__(
            name="Nue",
            level=1,
            max_hp=300,
            max_ce=150,
            strength=300,
            speed=700,
            technique="Nue",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

nue = Nue()
#endregion

#region Great Serpent
class Great_Serpent(Enemy):
    def __init__(self):
        super().__init__(
            name="Great Serpent",
            level=1,
            max_hp=300,
            max_ce=150,
            strength=100,
            speed=600,
            technique="Great Serpent",
            playerclass="summon",
            colony=0,
            xp=500,
            cgp=0,
            bodyparts=human_body_parts
        )

great_serpent = Great_Serpent()
#endregion

#region Max Elephant
class Max_Elephant(Enemy):
    def __init__(self):
        super().__init__(
            name="Max Elephant",
            level=1,
            max_hp=700,
            max_ce=300,
            strength=800,
            speed=300,
            technique="Max Elephant",
            playerclass="summon",
            colony=0,
            xp=750,
            cgp=0,
            bodyparts=human_body_parts
        )

max_elephant = Max_Elephant()
#endregion

#region Piercing Ox
class Piercing_Ox(Enemy):
    def __init__(self):
        super().__init__(
            name="Piercing Ox",
            level=1,
            max_hp=1000,
            max_ce=500,
            strength=100, # base
            speed=100,
            technique="Piercing Ox",
            playerclass="summon",
            colony=0,
            xp=1000,
            cgp=0,
            bodyparts=human_body_parts
        )

piercing_ox = Piercing_Ox()
#endregion

#region Funeral Tiger
class Funeral_Tiger(Enemy):
    def __init__(self):
        super().__init__(
            name="Funeral Tiger",
            level=1,
            max_hp=1000,
            max_ce=500,
            strength=500,
            speed=500,
            technique="Funeral Tiger",
            playerclass="summon",
            colony=0,
            xp=1000,
            cgp=0,
            bodyparts=human_body_parts
        )

funeral_tiger = Funeral_Tiger()
#endregion

#region Round Deer
class Round_Deer(Enemy):
    def __init__(self):
        super().__init__(
            name="Round Deer",
            level=1,
            max_hp=1000,
            max_ce=500,
            strength=200,
            speed=100,
            technique="Round Deer",
            playerclass="summon",
            colony=0,
            xp=0,
            cgp=1000,
            bodyparts=human_body_parts
        )

round_deer = Round_Deer()
#endregion

#region Mahoraga
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
#endregion

shikigami_list = [white_divine_dog, black_divine_dog, rabbit_escape, toad, 
                  nue, great_serpent, max_elephant, piercing_ox, funeral_tiger, 
                  round_deer, mahoraga]