from techniques import CursedTools


cursed_tools={
    
    "Katana":
    CursedTools(name="Katana",
                cost=25,
                broken=False,
                hp=50,
                max_hp=50,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=2,
                type="blade"
                ),

    "9mm Pistol":
    CursedTools(name="9mm Pistol",
                cost=50,
                broken=False,
                hp=50,
                max_hp=50,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=1,
                type="gun" # won't factor in player stats other than speed/perception?
                ),

    "Steel Arm":
    CursedTools(name="Steel Arm",
                cost=50,
                broken=False,
                hp=75,
                max_hp=75,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=10,
                strike_speed=1,
                type="gauntlet"
                ),

    "Dull Blade": # add a random bodypart system that will multiply damage if hitting the right bodypart (ratio technique)
    CursedTools(name="Dull Blade",
                cost=175,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=2,
                type="blade"
                ),

    "ISOH":
    CursedTools(name="ISOH",
                cost=300,
                broken=False,
                hp=300,
                max_hp=300,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=2,
                type="blade",
                negates=True
                ),
    
    "Dragon Bone":
    CursedTools(name="Dragon Bone",
                cost=50,
                broken=False,
                hp=100,
                max_hp=100,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=2,
                type="blade"
                ),

    "Maichan":
    CursedTools(name="Maichan",
                cost=250,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=2,
                type="blade",
                soul=True
                ),

    "Playful Cloud":
    CursedTools(name="Playful Cloud",
                cost=250,
                broken=False,
                hp=200,
                max_hp=200,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=3,
                type="nunchuck",
                buff=("player.strength" * 20) # multiplier of player physical strength by its dmg - doesn't take in account imbue
                ),

    "Black Rope":
    CursedTools(name="Black Rope",
                cost=250,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                damage=20,
                strike_speed=3,
                type="whip",
                negates=True,
                self_dmg=5 # not exactly sure how this works
                )

}