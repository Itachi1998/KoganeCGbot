from techniques import CursedTools


cursed_tools={
#region Katana    
    "Katana":
    CursedTools(name="Katana",
                cost=25,
                broken=False,
                hp=50,
                max_hp=50,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee"
                ),
#endregion
#region 9mm Pistol
    "9mm Pistol":
    CursedTools(name="9mm Pistol",
                cost=50,
                broken=False,
                hp=50,
                max_hp=50,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=1,
                type="projectile" # won't factor in player stats other than speed/perception?
                ),
#endregion
#region Steel Arm
    "Steel Arm":
    CursedTools(name="Steel Arm",
                cost=50,
                broken=False,
                hp=75,
                max_hp=75,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=10,
                speed=1,
                type="melee"
                ),
#endregion
#region Dull Melee
    "Dull Melee": # add a random bodypart system that will multiply strength if hitting the right bodypart (ratio technique)
    CursedTools(name="Dull Melee",
                cost=175,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee"
                ),
#endregion
#region ISOH
    "ISOH":
    CursedTools(name="ISOH",
                cost=300,
                broken=False,
                hp=300,
                max_hp=300,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=500,
                speed=2,
                type="melee",
                negates=True
                ),
#endregion
#region Dragon Bone   
    "Dragon Bone":
    CursedTools(name="Dragon Bone",
                cost=50,
                broken=False,
                hp=100,
                max_hp=100,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee"
                ),
#endregion
#region Maichan
    "Maichan":
    CursedTools(name="Maichan",
                cost=250,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee",
                soul=250
                ),
#endregion
#region Playful Cloud
    "Playful Cloud":
    CursedTools(name="Playful Cloud",
                cost=250,
                broken=False,
                hp=200,
                max_hp=200,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=3,
                type="melee",
                buff={"strength" : 2, "speed" : 2} # multiplier of player physical strength by its dmg - doesn't take in account imbue
                ),
#endregion
#region Black Rope
    "Black Rope":
    CursedTools(
                name="Black Rope",
                cost=250,
                broken=False,
                hp=150,
                max_hp=150,
                act_body=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=3,
                type="melee",
                negates=True,
                self_dmg=5 # not exactly sure how this works
                )
#endregion
}