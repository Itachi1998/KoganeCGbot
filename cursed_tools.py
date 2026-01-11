from techniques import CursedTools


cursed_tools={
#region Katana    
    "Katana":
    CursedTools(name="Katana",
                cost=25,
                broken=False,
                hp=50,
                max_hp=50,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee",
                emoji="<:katana:1414044436811350128>"
                ),
#endregion
#region 9mm Pistol
    "9mm Pistol":
    CursedTools(name="9mm Pistol",
                cost=50,
                broken=False,
                hp=50,
                max_hp=50,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=1,
                type="projectile", # won't factor in player stats other than speed/perception?
                emoji="<:soulblicky:1277633038251196497>"
                ),
#endregion
#region Steel Arm
    "Steel Arm":
    CursedTools(name="Steel Arm",
                cost=50,
                broken=False,
                hp=75,
                max_hp=75,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=10,
                speed=1,
                type="melee",
                emoji="<:steelarm:1414044081155473539>"
                ),
#endregion
#region Dull Melee
    "Dull Melee": # add a random bodypart system that will multiply strength if hitting the right bodypart (ratio technique)
    CursedTools(name="Dull Melee",
                cost=175,
                broken=False,
                hp=150,
                max_hp=150,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee",
                emoji="<:cow_blade:1277632737683046431>"
                ),
#endregion
#region ISOH
    "ISOH":
    CursedTools(name="ISOH",
                cost=300,
                broken=False,
                hp=300,
                max_hp=300,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=500,
                speed=2,
                type="melee",
                emoji="<:ISOH_FULL:1275114973055684618>",
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
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee",
                emoji="<:dragonbone:1277632814367506567>"
                ),
#endregion
#region Maichan
    "Maichan":
    CursedTools(name="Maichan",
                cost=250,
                broken=False,
                hp=150,
                max_hp=150,
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=2,
                type="melee",
                emoji="<:soulsplit:1277632881640083456>",
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
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=3,
                type="melee",
                emoji="<:playfulcloud:1277632921720586362>",
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
                act_req=("Left Arm", "Right Arm"),
                aoe=1,
                strength=20,
                speed=3,
                type="melee",
                emoji="<:blackrope:1277632984928882769>",
                negates=True,
                self_dmg=5 # not exactly sure how this works
                )
#endregion
}