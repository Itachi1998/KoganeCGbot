
from classes import NPC, BodyPart
import random


# region NPCs
floatjelly_hp = 30
floatjelly_ce = 40
FloatJelly = NPC(
    name="Float Jelly",
    level=1,
    hp=floatjelly_hp,
    max_hp=floatjelly_hp,
    ce=floatjelly_ce,
    max_ce=floatjelly_ce,
    speed=10,
    strength=40,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    techniques=["FloatJelly"],
    quantity=random.randrange(3,8),
    body_parts={"head" : BodyPart(name="head", hp=floatjelly_hp, ce=0, max_hp=floatjelly_hp, max_ce=0)}
)

bugfly_hp = 20
bugfly_ce =50
BugFly = NPC(
    name="Bug Fly",
    level=1,
    hp=bugfly_hp,
    max_hp=bugfly_hp,
    ce=bugfly_ce,
    max_ce=bugfly_ce,
    speed=50,
    strength=20,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    is_flying=True,
    techniques=["BugFly"],
    quantity=random.randrange(2,8),
    body_parts={"head" : BodyPart(name="head", hp=bugfly_hp, ce=0, max_hp=bugfly_hp, max_ce=0)}

)

batmouth_hp = 40
batmouth_ce = 60
BatMouth = NPC(
    name="Bat Mouth",
    level=1,
    hp=batmouth_hp,
    max_hp=batmouth_hp,
    ce=batmouth_ce,
    max_ce=batmouth_ce,
    speed=20,
    strength=30,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    techniques=["Bat Mouth"],
    quantity=random.randrange(2,5),
    body_parts={"head" : BodyPart(name="head", hp=batmouth_hp, ce=0, max_hp=batmouth_hp, max_ce=0)}
)



barehand_hp = 150
barehand_ce = 200
BareHand = NPC(
    name="Bare Hand",
    level=10,
    hp=barehand_hp,
    max_hp=barehand_hp,
    ce=barehand_ce,
    max_ce=barehand_ce,
    speed=100,
    strength=100,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['Bare Hand'],
    quantity=1,
    body_parts= {"head" : BodyPart(name="head", hp=barehand_hp * 50 // 100, ce=0, max_hp=barehand_hp * 50 // 100, max_ce=0),
                  "hand_1" : BodyPart(name="hand", hp=barehand_hp * 17 // 100, ce=0, max_hp=barehand_hp * 17 // 100, max_ce=0), 
                  "hand_2" : BodyPart(name="hand", hp=barehand_hp * 17 // 100, ce=0, max_hp=barehand_hp * 17 // 100, max_ce=0), 
                  "hand_3" : BodyPart(name="hand", hp=barehand_hp * 16 // 100, ce=0, max_hp=barehand_hp * 16 // 100, max_ce=0)}
)


furrpede_hp = 200
furrpede_ce = 200
Furrpede = NPC(
    name="Furrpede",
    level=10,
    hp=furrpede_hp,
    max_hp=furrpede_hp,
    ce=furrpede_ce,
    max_ce=furrpede_ce,
    speed=50,
    strength=150,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['Furrpede'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=furrpede_hp * 20 // 100, ce=0, max_hp=furrpede_hp * 20 // 100, max_ce=0),
         "body" : BodyPart(name="body", hp=furrpede_hp * 50 // 100, ce=0, max_hp=furrpede_hp * 50 // 100, max_ce=0),
         "hands" : BodyPart(name="hands", hp=furrpede_ce * 30 // 100, ce=0, max_hp= furrpede_ce * 30 // 100, max_ce=0)
         }
)


onewisemonkey_hp = 250
onewisemonkey_ce = 200
OneWiseMonkey = NPC(
    name="One Wise Monkey",
    level=10,
    hp=onewisemonkey_hp,
    max_hp=onewisemonkey_hp,
    ce=onewisemonkey_ce,
    max_ce=onewisemonkey_ce,
    speed=60,
    strength=150,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['OneWiseMonkey'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=onewisemonkey_hp * 50 // 100, ce=0, max_hp=onewisemonkey_hp * 30 // 100, max_ce=0),
        "arms" : BodyPart(name="arms", hp=onewisemonkey_hp * 25 // 100, ce=0, max_hp=onewisemonkey_hp * 25 // 100, max_ce=0),
        "legs" : BodyPart(name="legs", hp=onewisemonkey_hp * 25 // 100, ce=0, max_hp=onewisemonkey_hp * 25 // 100, max_ce=0)        
         }
)

stinkaspore_hp = 350
stinkaspore_ce = 350
Stinkaspore = NPC(
    name="Stinkaspore",
    level=20,
    hp=stinkaspore_hp,
    max_hp=stinkaspore_hp,
    ce=stinkaspore_ce,
    max_ce=stinkaspore_ce,
    speed=150,
    strength=250,
    grade=3,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=20,
    cgp_reward=2,
    techniques=['Stinkaspore'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=stinkaspore_hp * 20 // 100, ce=0, max_hp=stinkaspore_hp * 20 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=stinkaspore_hp * 50 // 100, ce=0, max_hp=stinkaspore_hp * 50 // 100, max_ce=0),
        "stingers" : BodyPart(name="stingers", hp=stinkaspore_hp * 30 // 100, ce=0, max_hp=stinkaspore_hp * 30 // 100, max_ce=0)
    }
)


primate_hp = 400
primate_ce = 300
Primate = NPC(
    name="Primate",
    level=20,
    hp=primate_hp,
    max_hp=primate_hp,
    ce=primate_ce,
    max_ce=primate_ce,
    speed=250,
    strength=300,
    grade=3,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=20,
    cgp_reward=2,
    techniques=['Primate'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 20 // 100, max_ce = 0),
        "body" : BodyPart(name="body", hp=primate_hp * 50 // 100, ce=0, max_hp=primate_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0)
    }
)


orbmaster_hp = 400
orbmaster_ce = 500
Orbmaster = NPC(
    name="Orbmaster",
    level=40,
    hp=orbmaster_hp,
    max_hp=orbmaster_hp,
    ce=orbmaster_ce,
    max_ce=orbmaster_ce,
    speed=300,
    strength=200,
    grade=4,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Orbmaster'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=orbmaster_hp * 50 // 100, ce=0, max_hp=orbmaster_hp * 50 // 100, max_ce= 0),
        "arm_1" : BodyPart(name="left arm", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0)
    }
)


electrocharge_hp = 500
electrocharge_ce = 700
Electrocharge = NPC(
    name="Electrocharge",
    level=40,
    hp=electrocharge_hp,
    max_hp=electrocharge_hp,
    ce=electrocharge_ce,
    max_ce=electrocharge_ce,
    speed=400,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Electrocharge'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=electrocharge_hp * 50 // 100, ce=0, max_hp=electrocharge_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0)  
    }
)

fingerbearer_hp = 1000
fingerbearer_ce= 1000
Fingerbearer= NPC(
    name="Fingerbearer",
    level=40,
    hp=fingerbearer_hp,
    max_hp=fingerbearer_hp,
    ce=fingerbearer_ce,
    max_ce=fingerbearer_ce,
    speed=650,
    strength=650,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=60,
    cgp_reward=2,
    techniques=['Fingerbearer'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=fingerbearer_hp * 50 // 100, ce=0, max_hp=fingerbearer_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0)  
    }
)


dis_flame_hp = 1500
dis_flame_ce = 1500
DisasterFlame = NPC(
    name="Disaster Flame",
    level=50,
    hp=dis_flame_hp,
    max_hp=dis_flame_hp,
    ce=dis_flame_ce,
    max_ce=dis_flame_ce,
    speed=1500,
    strength=1500,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=80,
    cgp_reward=2,
    techniques=['DisasterFlame'],
    quantity=1,
    body_parts= {
"head" : BodyPart(name="head", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"body" : BodyPart(name="body", hp=dis_flame_hp * 50 // 100, ce=0, max_hp=dis_flame_hp * 50 // 100, max_ce=0),
"arm_1" : BodyPart(name="left arm", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"arm_2" : BodyPart(name="right arm", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"leg_1" : BodyPart(name="left leg", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"leg_2" : BodyPart(name="right leg", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0)
    }
)




nature_hp = 2000
nature_ce = 1200
Nature = NPC(
    name="Nature Spirit",
    level=50,
    hp=nature_hp,
    max_hp=nature_hp,
    ce=nature_ce,
    max_ce=nature_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=80,
    cgp_reward=2,
    techniques=['Nature'],
    quantity=1,
    body_parts= {
"head" : BodyPart(name="head", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"body" : BodyPart(name="body", hp=nature_hp * 50 // 100, ce=0, max_hp=nature_hp * 50 // 100, max_ce=0),
"arm_1" : BodyPart(name="left arm", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"arm_2" : BodyPart(name="right arm", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"leg_1" : BodyPart(name="left leg", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"leg_2" : BodyPart(name="right leg", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
    }
)


tide_hp = 1200
tide_ce = 1000
TideCurse = NPC(
name="Disaster Tides",
level=50,
hp=tide_hp,
max_hp=tide_hp,
ce=tide_ce,
max_ce=tide_ce,
speed=800,
strength=800,
grade=5,
player_type="NPC",
playerclass="Curse",
xp_reward=80,
cgp_reward=2,
techniques=['TideCurse'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=tide_hp * 17 // 100, ce=0, max_hp=tide_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=tide_hp * 50 // 100, ce=0, max_hp=tide_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=tide_hp * 16 // 100, ce=0, max_hp=tide_hp * 16 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=tide_hp * 16 // 100, ce=0, max_hp=tide_hp * 17 // 100, max_ce=0)
    }
)



femhito_hp = 2000
femhito_ce = 1500
Femhito = NPC(
    name="Femhito",
    level=50,
    hp=femhito_hp,
    max_hp=femhito_hp,
    ce=femhito_ce,
    max_ce=femhito_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=100,
    cgp_reward=2,
    techniques=['Femhito'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=femhito_hp * 17 // 100, ce=0, max_hp=femhito_hp * 17 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=femhito_hp * 50 // 100, ce=0, max_hp=femhito_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=femhito_hp * 16 // 100, ce=0, max_hp=femhito_hp * 16 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=femhito_hp * 17 // 100, ce=0, max_hp=femhito_hp * 17 // 100, max_ce=0)
        }
)


brute_hp = 1000
brute_ce= 500
Brute = NPC(
    name="Brute Curse",
    level=30,
    hp=brute_hp,
    max_hp=brute_hp,
    ce=brute_ce,
    max_ce=brute_ce,
    speed=600,
    strength=900,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=50,
    cgp_reward=2,
    techniques=['Fist of Destruction'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=brute_hp * 50 // 100, ce=0, max_hp=brute_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0)
        }
)

witch_hp = 900
witch_ce = 600
Witch = NPC(
    name="Witch Curse",
    level=20,
    hp=witch_hp,
    max_hp=witch_hp,
    ce=witch_ce,
    max_ce=witch_ce,
    speed=500,
    strength=400,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=30,
    cgp_reward=2,
    techniques=['Curse Magic'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=witch_hp * 50 // 100, ce=0, max_hp=witch_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0)
    }
)


cultist_hp = 1000
cultist_ce = 500

Cultist = NPC(
    name="Cultist Curse",
    level=30,
    hp=cultist_hp,
    max_hp=cultist_hp,
    ce=cultist_ce,
    max_ce=cultist_ce,
    speed=600,
    strength=600,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Binding Chains'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=cultist_hp * 50 // 100, ce=0, max_hp=cultist_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0)
    }
)


merfolk_hp = 1000
merfolk_ce = 800
Merfolk = NPC(
    name="Merfolk Curse",
    level=30,
    hp=merfolk_hp,
    max_hp=merfolk_hp,
    ce=merfolk_ce,
    max_ce=merfolk_ce,
    speed=600,
    strength=500,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Depths Call'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=merfolk_hp * 50 // 100, ce=0, max_hp=merfolk_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0)
    }
)

toji_hp = 3000
toji_ce = 0
Toji = NPC(
    name="Toji",
    level=50,
    hp=toji_hp,
    max_hp = toji_hp,
    ce=toji_ce,
    max_ce=toji_ce,
    speed=2000,
    strength=2000,
    grade=5,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Heavenly Restriction: 0'],
    quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=toji_hp * 50 // 100, ce=0, max_hp=toji_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0)
    }
)


reggie_hp = 800
reggie_ce = 500
Reggie = NPC(
    name="Reggie",
    level=30,
    hp=reggie_hp,
    max_hp=reggie_hp,
    ce=reggie_ce,
    max_ce=reggie_ce,
    speed=400,
    strength=600,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=60,
    cgp_reward=5,
    techniques=['Contract Recreation'],
    quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=reggie_hp * 50 // 100, ce=0, max_hp=reggie_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=reggie_hp    * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0)
    }
)

uro_hp = 1000
uro_ce = 800
Uro = NPC(
    name="Uro",
    level=40,
    hp=uro_hp,
    max_hp=uro_hp,
    ce=uro_ce,
    max_ce=uro_ce,
    speed=500,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Sky Manipulation'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=uro_hp * 50 // 100, ce=0, max_hp=uro_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=uro_hp *  10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0)
    })

takaba_hp = 900
takaba_ce = 700
Takaba = NPC(
    name="Takaba",
    level=40,
    hp=takaba_hp,
    max_hp=takaba_hp,
    ce=takaba_ce,
    max_ce=takaba_ce,
    speed=400,
    strength=400,
grade=5,
player_type="NPC",
playerclass="Sorcerer",
xp_reward=80,
cgp_reward=5,
techniques=['Comedian'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=takaba_hp * 50 // 100, ce=0, max_hp=takaba_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0)
}
)

ryu_hp = 1000
ryu_ce = 800
Ryu = NPC(
name="Ryu",
level=40,
hp=ryu_hp,
max_hp=ryu_hp,
ce=ryu_ce,
max_ce=ryu_ce,
speed=700,
strength=700,
grade=4,
player_type="NPC",
playerclass="Sorcerer",
xp_reward=80,
cgp_reward=5,
techniques=['Energy Discharge'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=ryu_hp * 50 // 100, ce=0, max_hp=ryu_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0)
}
)


kashima_hp = 2000
kashima_ce = 1500
Kashima = NPC(
    name="Kashima",
    level=80,
    hp=kashima_hp,
    max_hp=kashima_hp,
    ce=kashima_ce,
    max_ce=kashima_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Mythic Beast Amber'],
    quantity=1,
    body_parts= {
    "head" : BodyPart(name="head", hp=kashima_hp * 10 // 100, ce=0, max_hp = kashima_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=kashima_hp * 50 // 100, ce=0, max_hp=kashima_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=kashima_hp *  10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0)
}
)
    

higgy_hp = 600
higgy_ce = 600
Higuruma = NPC(
    name="Higuruma",
    level=40,
    hp=higgy_hp,
    max_hp=higgy_hp,
    ce=higgy_ce,
    max_ce=higgy_ce,
    speed=300,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=60,
    cgp_reward=5,
    techniques=['Deadly Sentence'],
    quantity=1,
    body_parts= { 
    "head" : BodyPart(name="head", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=higgy_hp * 50 // 100, ce=0, max_hp=higgy_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0)
}
)

three_finger_hp = 1500
three_finger_ce = 1500
ThreeFinger = NPC(
    name="Three Finger King",
    level=30,
    hp=three_finger_hp,
    max_hp=three_finger_hp,
    ce=three_finger_ce,
    max_ce=three_finger_ce,
    speed=1500,
    strength=1500,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Shrine'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=three_finger_hp * 50 // 100, ce=0, max_hp=three_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0)
    }
)



fifteen_finger_hp = 3000
fifteen_finger_ce = 3000

FifteenFinger = NPC(
    name="Fifteen Finger King",
    level=50,
    hp=fifteen_finger_hp,
    max_hp=fifteen_finger_hp,
    ce=fifteen_finger_ce,
    max_ce=fifteen_finger_ce,
    speed=2000,
    strength=2000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Shrine', "Ten Shadows"],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=fifteen_finger_hp * 50 // 100, ce=0, max_hp=fifteen_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0)
    }
)

twenty_finger_hp = 4000
twenty_finger_ce = 4000

TwentyFinger = NPC(
    name="King Of Curses",
    level=100,
    hp=twenty_finger_hp,
    max_hp=twenty_finger_hp,
    ce=twenty_finger_ce,
    max_ce=twenty_finger_ce,
    speed=4500,
    strength=4500,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=200,
    cgp_reward=5,
    techniques=['Shrine', "Ten Shadows"],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=twenty_finger_hp * 50 // 100, ce=0, max_hp=twenty_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0)
    }
)

kenny_hp = 2500
kenny_ce = 2500

Kenny = NPC(
    name="Kenny",
    level=60,
    hp=kenny_hp,
    max_hp=kenny_hp,
    ce=kenny_ce,
    max_ce=kenny_ce,
    strength=2000,
    speed=2000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Cursed Spirit Manipulation', 'Anti-Gravity System', 'Body Hop'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=kenny_hp * 50 // 100, ce=0, max_hp=kenny_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0)
    }
)

uraume_hp = 2000
uraume_ce = 2000
Uraume = NPC(
    name="Uraume",
    level=60,
    hp=uraume_hp,
    max_hp=uraume_hp,
    ce=uraume_ce,
    max_ce=uraume_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Freeze'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=uraume_hp * 50 // 100, ce=0, max_hp=uraume_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0)
    }
)


NPC_enemy_list = [
    FloatJelly,
    BatMouth,
    BugFly,
    Furrpede,
    OneWiseMonkey,
    BareHand,
    Stinkaspore,
    Primate,
    Orbmaster,
    Electrocharge,
    Fingerbearer,
    DisasterFlame,
    Nature,
    TideCurse,
    Femhito,
    Brute,
    Witch,
    Cultist,
    Merfolk,
    Toji,
    Reggie,
    Uro,
    Ryu,
    Kashima,
    Higuruma,
    ThreeFinger,
    FifteenFinger,
    TwentyFinger,
    Kenny,
    Uraume
    
]

for npc in NPC_enemy_list:
    print(f"{npc.name} - HP: {npc.hp}, CE: {npc.ce}, Speed: {npc.speed}, Strength: {npc.strength}, Grade: {npc.grade}, Techniques: {', '.join(npc.techniques)}")

# endregion


# region Shikigami NPCs
DivineDog = NPC(
    name="Divine Dog",
    level=0,
    hp=600,
    max_hp=600,
    ce=600,
    max_ce=600,
    speed=400,
    strength=400,
    grade=3,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=20,
    cgp_reward=0,
    techniques=['Divine Dog'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=500 * 50 // 100, ce=0, max_hp=500 * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0)
    }
)

RabbitEscape = NPC(
    name="Rabbit Escape",
    level=0,
    hp=100,
    max_hp=100,
    ce=100,
    max_ce=100,
    speed=200,
    strength=100,
    grade=3,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=10,
    cgp_reward=0,
    techniques=['Rabbit Escape'],
    quantity=1,
body_parts= {
    "body" : BodyPart(name="body", hp=100 * 100 // 100, ce=0, max_hp=100 * 100 // 100, max_ce=0)
})


Toad = NPC(
    name="Toad",
    level=0,
    hp=200,
    max_hp=200,
    ce=100,
    max_ce=100,
    speed=150,
    strength=150,
grade=3,
player_type="NPC",
playerclass="Shikigami",
xp_reward=15,
cgp_reward=0,
techniques=['Toad'],
quantity=1,
body_parts= {
    "body" : BodyPart(name="body", hp=200 * 100 // 100, ce=0, max_hp=200 * 100 // 100, max_ce=0)
}
)


Nue = NPC(
    name="Nue",
    level=0,
    hp=400,
    max_hp=400,
    ce=300,
    max_ce=300,
    speed=300,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=30,
    cgp_reward=0,
    techniques=['Nue'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=400 * 10 // 100, ce=0, max_hp=400 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=400 * 50 // 100, ce=0, max_hp=400 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=400 * 10 // 100, ce=0, max_hp=400 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=400 * 10 // 100, ce=0, max_hp=400 * 10 // 100, max_ce=0),
        "wing_1" : BodyPart(name="left wing", hp=400 * 10 // 100, ce=0, max_hp=400 * 10 // 100, max_ce=0),
        "wing_2" : BodyPart(name="right wing", hp=400 * 10 // 100, ce=0, max_hp=400 * 10 // 100, max_ce=0)
    })

Elephant = NPC(
    name="Max Elephant",
    level=0,
    hp=1000,
    max_hp=1000,
    ce=500,
    max_ce=500,
    speed=400,
    strength=1000,
    techniques=['Elephant'],
    grade=1,
player_type="NPC",
playerclass="Shikigami",
xp_reward=50,
cgp_reward=0,
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=1000 * 50 // 100, ce=0, max_hp=1000 * 50 // 100, max_ce=0),
    "leg_1" : BodyPart(name="front left", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="front right", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
    "leg_3" : BodyPart(name="back left", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
    "leg_4" : BodyPart(name="back right", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0)
}
)


Ox = NPC(
    name="Piercing Ox",
level=0,
hp=600,
max_hp=600,
ce=400,
max_ce=400,
speed=700,
strength=700,
grade=4,
player_type="NPC",
playerclass="Shikigami",
xp_reward=40,
cgp_reward=0,
techniques=['Piercing Ox'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=600 * 10 // 100, ce=0, max_hp=600 * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=600 * 50 // 100, ce=0, max_hp=600 * 50 // 100, max_ce=0),
    "leg_1" : BodyPart(name="front left", hp=600 * 10 // 100, ce=0, max_hp=600 * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="front right", hp=600 * 10 // 100, ce=0, max_hp=600 * 10 // 100, max_ce=0),
    "leg_3" : BodyPart(name="back left", hp=600 * 10 // 100, ce=0, max_hp=600 * 10 // 100, max_ce=0),
    "leg_4" : BodyPart(name="back right", hp=600 * 10 // 100, ce=0, max_hp=600 * 10 // 100, max_ce=0)
}
)

Tiger = NPC(
    name="Roaring Tiger",
    level=0,
    hp=800,
    max_hp=800,
    ce=900,
    max_ce=900,
    speed=900,
    strength=1000,
    grade=4,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=50,
    cgp_reward=0,
    techniques=['Roaring Tiger'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=800 * 10 // 100, ce=0, max_hp=800 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=800 * 50 // 100, ce=0, max_hp=800 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=800 * 10 // 100, ce=0, max_hp=800 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=800 * 10 // 100, ce=0, max_hp=800 * 10 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=800 * 10 // 100, ce=0, max_hp=800 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=800 * 10 // 100, ce=0, max_hp=800 * 10 // 100, max_ce=0)
    }
)


RoundDeer = NPC(
    name="Round Deer",
    level=0,
    hp=500,
    max_hp=500,
    ce=300,
    max_ce=300,
    speed=300,
    strength=300,
    grade=3,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=20,
    cgp_reward=0,
    techniques=['Round Deer'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=500 * 50 // 100, ce=0, max_hp=500 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=500 * 10 // 100, ce=0, max_hp=500 * 10 // 100, max_ce=0)
    }
)

Mahoraga = NPC(
    name="Mahoraga",
    level=0,
    hp=5000,
    max_hp=5000,
    ce=5000,
    max_ce=5000,
    speed=5000,
    strength=5000,
    grade=5,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=200,
    cgp_reward=0,
    techniques=['Mahoraga'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=5000 * 10 // 100, ce=0, max_hp=5000 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=5000 * 50 // 100, ce=0, max_hp=5000 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=5000 * 10 // 100, ce=0, max_hp=5000 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=5000 * 10 // 100, ce=0, max_hp=5000 * 10 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=5000 * 10 // 100, ce=0, max_hp=5000 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=5000 * 10 // 100, ce=0, max_hp=5000 * 10 // 100, max_ce=0)
    }
)

Rika = NPC(
    name="Rika",
    level=0,
    hp=3000,
    max_hp=3000,
    ce=2000,
    max_ce=2000,
    speed=3000,
    strength=2000,
    grade=5,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=150,
    cgp_reward=0,
    techniques=['Rika'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=3000 * 10 // 100, ce=0, max_hp=3000 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=3000 * 50 // 100, ce=0, max_hp=3000 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=3000 * 10 // 100, ce=0, max_hp=3000 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=3000 * 10 // 100, ce=0, max_hp=3000 * 10 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=3000 * 10 // 100, ce=0, max_hp=3000 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=3000 * 10 // 100, ce=0, max_hp=3000 * 10 // 100, max_ce=0)
    }
)



Garuda = NPC(
    name="Garuda",
    level=0,
    hp=1000,
    max_hp=1000,
    ce=1000,
    max_ce=1000,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Shikigami",
    xp_reward=100,
    cgp_reward=0,
    techniques=['Garuda'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=1000 * 50 // 100, ce=0, max_hp=1000 * 50 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=1000 * 10 // 100, ce=0, max_hp=1000 * 10 // 100, max_ce=0)
    }
)


# endregion