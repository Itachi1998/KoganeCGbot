from classes import Technique, Domain, Barrier

AntiGravity = {
    "name": "Anti-Gravity",
    "attack" :{
        "lapse": Technique(
            name="Curse Technique Lapse Push Away",
            cost=50,
            description="Repels targets using anti-gravity force",
            technique_type="projectile",
            strength=500,
            activation_speed=1,
            aoe=5,
            grade=2,
            travel_speed=1000,
            effects={"stun" : 1, 'sure-hit' : True},
        ),
        "reversal": Technique(
            name="Cursed Technique Reversal Gravity Slam",
            cost=2500,
            description="Slams enemies down with gravity",
            technique_type="projectile",
            strength=1000,
            activation_speed=2,
            aoe=5,
            grade=3,
            travel_speed=2000,
            effects={"stun" : 2}
        )
    },
    "defense" : {
        "lapse": Technique(
            name="Anti-Gravity Repel",
            cost=75,
            description="Repels an incoming attack/attacker with anti-gravity force",
            technique_type="counter",
            strength=700,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=1000,
            effects={"stun" : 1}
        ),
        "reversal" : Technique(
            name="Anti-Gravity Slam Counter",
            cost=2500,
            description="Counters an attack by slamming the attack/attacker into the ground with gravity",
            technique_type="counter",
            strength=1000,
            activation_speed=2,
            aoe=5,
            grade=5,
            travel_speed=2000,
            effects={"stun" : 2}
        )
    },
    "barriers" : {
        # "Gravity Well": Barrier(
        #     name="Gravity Well",
        #     cost=150,
        #     activation_speed=3,
        #     strength=400,
        #     duration=20,
        #     cooldown=10,
        #     aoe=10,
        #     effects={"gravity_manipulation": True},
        #     buffs={},
        #     debuffs={"movement_speed": -50, "jump_disabled": True}
        # )
    },
    "rarity" : 15
}

WiseMonkey = {
    "name": "Wise Monkey",
    "attack" : {
        "lapse": Technique(
            name="Wise Monkey: Hear no evil",
            cost=40,
            description="Melee attack aimed at opponents eardrums to disorient",
            technique_type="melee",
            strength=100,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=100,
            effects={"stun" : 1}
        )
    },
    "defense" : {
            "lapse": Technique(
            name="Wise Monkey: See no evil",
            cost=80,
            description="Turns invisible to avoid attacks and gain perception advantage",
            technique_type="dodge",
            strength=150,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=200,
            effects={"debuff" : {"perception" : -10}, "duration": 2}
        )
    },
    "barriers" : {},
    "rarity" : 0
}

AuspiciousBeastSummon = {
    "name" : "Seance Technique: Auspicious Beast Summon",
    "attack" : {
        "kaichi" : Technique(
            name="Auspicious Beast One: Kaichi",
            cost=25,
            description="Summons a small projectile that homes in on enemies",
            technique_type="projectile",
            strength=200,
            activation_speed=3,
            aoe=2,
            grade=1,
            travel_speed=500,
            requirements={"head" : True, "equipped" : "headcover"}),
        "ryu" : Technique(
            name="Auspicious Beast Four: Ryu",
            cost=100,
            description="Summons a large dragon from the users hands that attacks in a straight line, dealing heavy damage to anything in its path",
            technique_type="projectile",
            strength=500,
            activation_speed=1,
            aoe=5,
            grade=3,
            travel_speed=700,
            requirements={"hand" : True, "equipped" : "headcover"}
        )

    },
    "defense" : {
        "reiki" : Technique(
            name="Auspicious Beast Two: Reiki",
            cost=50,
            description="User channels spiritual energy into water to buff movements and attacks",
            technique_type="block",
            strength=300,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            requirements={"hand" : True, "equipped" : "headcover"},
            effects = {"buffs" : {"durability" : 50, "speed" : 50}, "duration" : 2}
        ),
         "kirin" : Technique(
            name="Auspicious Beast Three: Kirin",
            cost=50,
            description="Buffs the users pain tolerance and strength for a short time",
            technique_type="buff",
            strength=300,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            requirements={"head" : True, "equipped" : "headcover"},
            effects={"buff" : {"durability" : 100, "speed" : 100}, "debuff" : {"hp" : -10}, "duration" : 2})
    },
    "barriers" : {},
    "rarity" : 30
}

BareHand = {
    "name" : "Bare Hand",
    "attack" : {
        "Hand Slap": Technique(
            name="Hand Slap",
            cost=30,
            description="Basic hand strike with cursed energy",
            technique_type="melee",
            strength=200,
            activation_speed=2,
            aoe=1,
            grade=1,
            travel_speed=100
        ),
        "Multi-Hand Barrage": Technique(
            name="Multi-Hand Barrage",
            cost=80,
            description="Multiple floating hands attack in succession",
            technique_type="melee",
            strength=150,
            activation_speed=3,
            aoe=2,
            grade=2,
            travel_speed=400,
            effects={"multi_hit": 4, "combo": True}
        )
    },
    "defense" : {
        "Hand Block": Technique(
            name="Hand Block",
            cost=25,
            description="Uses floating hands to block attacks",
            technique_type="block",
            strength=100,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            effects={"damage_reduction": 0.4}
        )
    },
    "barriers" : {},
    "rarity" : 0
}


BirdManip = {
    "name" : "Crow Manipulation",
    "attack" : {
        "Crow Swarm": Technique(
            name="Crow Swarm",
            cost=60,
            description="Summons a swarm of cursed crows to attack",
            technique_type="projectile",
            strength=250,
            activation_speed=2,
            aoe=5,
            grade=2,
            travel_speed=800,
            effects={"swarm_attack": True, "blinding": True}
        ),
        "Falcon Dive": Technique(
            name="Falcon Dive",
            cost=80,
            description="Summons a large falcon for a diving attack",
            technique_type="projectile",
            strength=400,
            activation_speed=3,
            aoe=2,
            grade=3,
            travel_speed=1200,
            effects={"aerial_attack": True, "knockdown": True}
        )
    },
    "defense" : {
        "Bird Shield": Technique(
            name="Bird Shield",
            cost=45,
            description="Birds form a protective formation",
            technique_type="guard",
            strength=150,
            activation_speed=1,
            aoe=3,
            grade=2,
            travel_speed=600,
            effects={"projectile_deflection": True}
        )
    },
    "barriers" : {},
    "rarity" : 40
}

BloodManip = {
    "name" : "Blood Manipulation",
    "attack" : {
        "Blood Edge": Technique(
            name="Blood Edge",
            cost=70,
            description="Creates sharp blood projectiles",
            technique_type="projectile",
            strength=350,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=900,
            effects={"piercing": True, "bleeding": 3}
        ),
        "Crimson Binding": Technique(
            name="Crimson Binding",
            cost=90,
            description="Blood coils to bind and crush enemies",
            technique_type="projectile",
            strength=300,
            activation_speed=3,
            aoe=2,
            grade=3,
            travel_speed=600,
            effects={"binding": True, "crushing_damage": True}
        ),
        "Blood Meteorite": Technique(
            name="Blood Meteorite",
            cost=150,
            description="Compresses blood into a devastating projectile",
            technique_type="projectile",
            strength=800,
            activation_speed=4,
            aoe=8,
            grade=4,
            travel_speed=1500,
            effects={"explosive": True, "area_damage": True}
        )
    },
    "defense" : {
        "Blood Armor": Technique(
            name="Blood Armor",
            cost=80,
            description="Hardens blood into protective armor",
            technique_type="enhancement",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"defense_boost": 200, "duration": 30}
        )
    },
    "barriers" : {},
    "rarity" : 20
}

BodyHop = {
    "name" : "Body Hop",
    "attack" : {
        "Possession Strike": Technique(
            name="Possession Strike",
            cost=100,
            description="Temporarily possesses enemy to attack their allies",
            technique_type="special",
            strength=0,
            activation_speed=3,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"possession": True, "mind_control": 2, "confuse": True}
        ),
        "Soul Swap": Technique(
            name="Soul Swap",
            cost=200,
            description="Swaps consciousness with target temporarily",
            technique_type="special",
            strength=0,
            activation_speed=5,
            aoe=1,
            grade=5,
            travel_speed=0,
            effects={"body_swap": True, "duration": 10}
        )
    },
    "defense" : {
        "Escape Vessel": Technique(
            name="Escape Vessel",
            cost=80,
            description="Hops to another body when in danger",
            technique_type="escape",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"emergency_escape": True, "requires_target": True}
        )
    },
    "barriers" : {},
    "rarity" : 30
}

BoogieWoogie = {
    "name" : "Boogie Woogie",
    "attack" : {
        "Position Swap Attack": Technique(
            name="Position Swap Attack",
            cost=50,
            description="Swaps positions with target for surprise attack",
            technique_type="special",
            strength=300,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"position_swap": True, "surprise_attack": True}
        ),
        "Clapping Combo": Technique(
            name="Clapping Combo",
            cost=75,
            description="Rapid position swaps through clapping for combo attacks",
            technique_type="special",
            strength=200,
            activation_speed=2,
            aoe=3,
            grade=3,
            travel_speed=0,
            effects={"multi_swap": 3, "combo_multiplier": 1.5}
        )
    },
    "defense" : {
        "Evasive Swap": Technique(
            name="Evasive Swap",
            cost=40,
            description="Swaps position to avoid incoming attacks",
            technique_type="dodge",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"instant_dodge": True, "position_swap": True}
        )
    },
    "barriers" : {},
    "rarity" : 15
}

BugFly = {
    "name" : "Bug Fly",
    "attack" : {
        "Swarm Dive": Technique(
            name="Swarm Dive",
            cost=40,
            description="Flying bug attacks with speed advantage",
            technique_type="melee",
            strength=180,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=800,
            effects={"flying_advantage": True, "speed_boost": 50}
        ),
        "Bug Bite": Technique(
            name="Bug Bite",
            cost=30,
            description="Quick venomous bite attack",
            technique_type="melee",
            strength=150,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            effects={"poison": 2, "quick_strike": True}
        )
    },
    "defense" : {
        "Evasive Flight": Technique(
            name="Evasive Flight",
            cost=25,
            description="Uses high-speed flight to evade attacks",
            technique_type="dodge",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=900,
            effects={"aerial_dodge": True, "speed_boost": 100}
        )
    },
    "barriers" : {},
    "rarity" : 20
}


Charger = {
    "name" : "Electro Charge",
    "attack" : {
        "Lightning Bolt": Technique(
            name="Lightning Bolt",
            cost=80,
            description="Fires concentrated electrical energy",
            technique_type="projectile",
            strength=400,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=1500,
            effects={"electrical": True, "stun": 1, "chain_lightning": 2}
        ),
        "Electro Field": Technique(
            name="Electro Field",
            cost=120,
            description="Creates an area of electrical damage",
            technique_type="area",
            strength=300,
            activation_speed=3,
            aoe=8,
            grade=3,
            travel_speed=0,
            effects={"area_damage": True, "continuous": 5, "paralysis": True}
        )
    },
    "defense" : {
        "Static Shield": Technique(
            name="Static Shield",
            cost=60,
            description="Electrical barrier that shocks attackers",
            technique_type="counter",
            strength=200,
            activation_speed=2,
            aoe=2,
            grade=2,
            travel_speed=0,
            effects={"reflect_damage": 150, "stun_attacker": True}
        )
    },
    "barriers" : {
        "Tesla Dome": Barrier(
            name="Tesla Dome",
            cost=180,
            activation_speed=4,
            strength=500,
            duration=25,
            cooldown=12,
            aoe=15,
            effects={"electrical_field": True, "damage_over_time": True},
            buffs={},
            debuffs={"movement_speed": -30, "stun_chance": 0.3}
        )
    },
    "rarity" : 20
}

Ced = {
    "name" : "Curse Energy Discharge",
    "attack" : {
        "Energy Burst": Technique(
            name="Energy Burst",
            cost=60,
            description="Releases raw cursed energy in all directions",
            technique_type="area",
            strength=250,
            activation_speed=2,
            aoe=6,
            grade=2,
            travel_speed=800,
            effects={"knockback": 3, "energy_drain": 20}
        ),
        "Focused Discharge": Technique(
            name="Focused Discharge",
            cost=100,
            description="Concentrates cursed energy into a powerful beam",
            technique_type="projectile",
            strength=500,
            activation_speed=3,
            aoe=1,
            grade=3,
            travel_speed=1200,
            effects={"armor_piercing": True, "burn": 3}
        )
    },
    "defense" : {
        "Energy Absorption": Technique(
            name="Energy Absorption",
            cost=50,
            description="Absorbs incoming cursed energy attacks",
            technique_type="counter",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"absorb_energy": True, "heal_from_energy": 0.5}
        )
    },
    "barriers" : {},
    "rarity" : 20
}


Comedian = {
    "name" : "Comedian's Vow",
    "attack" : {
        "Punchline": Technique(
            name="Punchline",
            cost=150,
            description="Reality-warping gag technique with unpredictable effects",
            technique_type="special",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=5,
            travel_speed=0,
            binding_vows={"comedic_rule": True, "audience_dependent": True},
            effects={"reality_warp": True, "unpredictable": True, "instant_kill_chance": 0.1}
        ),
        "Setup": Technique(
            name="Setup",
            cost=80,
            description="Creates comedic setup for devastating punchline",
            technique_type="support",
            strength=0,
            activation_speed=2,
            aoe=3,
            grade=4,
            travel_speed=0,
            effects={"setup_bonus": True, "next_attack_enhanced": 300}
        )
    },
    "defense" : {
        "Comedy Relief": Technique(
            name="Comedy Relief",
            cost=100,
            description="Uses humor to defuse dangerous situations",
            technique_type="special",
            strength=0,
            activation_speed=1,
            aoe=5,
            grade=4,
            travel_speed=0,
            effects={"situation_defusal": True, "reset_combat": True}
        )
    },
    "barriers" : {},
    "rarity" : 5
}

Construction = {
    "name" : "Construction",
    "attack" : {
        "Construct Weapon": Technique(
            name="Construct Weapon",
            cost=80,
            description="Creates weapons from cursed energy and materials",
            technique_type="summon",
            strength=350,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"weapon_creation": True, "duration": 60}
        ),
        "Construction Barrage": Technique(
            name="Construction Barrage",
            cost=120,
            description="Rapidly constructs and launches multiple objects",
            technique_type="projectile",
            strength=250,
            activation_speed=3,
            aoe=5,
            grade=3,
            travel_speed=1000,
            effects={"multi_projectile": 6, "construction_speed": True}
        )
    },
    "defense" : {
        "Construct Shield": Technique(
            name="Construct Shield",
            cost=60,
            description="Builds protective barriers from available materials",
            technique_type="guard",
            strength=400,
            activation_speed=2,
            aoe=3,
            grade=2,
            travel_speed=0,
            effects={"material_dependent": True, "reinforced": True}
        )
    },
    "barriers" : {
        "Construction Site": Barrier(
            name="Construction Site",
            cost=200,
            activation_speed=5,
            strength=600,
            duration=120,
            cooldown=20,
            aoe=20,
            effects={"construction_boost": True, "material_abundance": True},
            buffs={"construction_speed": 100, "durability": 200},
            debuffs={}
        )
    },
    "rarity" : 15
}

ContRec = {
    "name" : "Contract Recreation",
    "attack" : {
        "Binding Contract": Technique(
            name="Binding Contract",
            cost=100,
            description="Forces enemy into a binding magical contract",
            technique_type="special",
            strength=0,
            activation_speed=3,
            aoe=1,
            grade=4,
            travel_speed=0,
            binding_vows={"contract_enforcement": True},
            effects={"binding": True, "rule_enforcement": True}
        ),
        "Penalty Clause": Technique(
            name="Penalty Clause",
            cost=150,
            description="Activates contract penalties for rule violations",
            technique_type="special",
            strength=800,
            activation_speed=1,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"contract_required": True, "penalty_damage": True}
        )
    },
    "defense" : {
        "Protective Clause": Technique(
            name="Protective Clause",
            cost=80,
            description="Contract protects from specific attack types",
            technique_type="guard",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"conditional_immunity": True, "contract_dependent": True}
        )
    },
    "barriers" : {},
    "rarity" : 20
}


Copy = {
    "name" : "Copy",
    "attack" : {
        "Mimicry": Technique(
            name="Mimicry",
            cost=100,
            description="Copies and uses an opponent's last technique",
            technique_type="special",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"copy_last_technique": True, "one_time_use": True}
        ),
        "Perfect Copy": Technique(
            name="Perfect Copy",
            cost=200,
            description="Creates an exact copy of any witnessed technique",
            technique_type="special",
            strength=0,
            activation_speed=4,
            aoe=1,
            grade=5,
            travel_speed=0,
            binding_vows={"perfect_mimicry": True},
            effects={"exact_replication": True, "requires_observation": True}
        )
    },
    "defense" : {
        "Defensive Copy": Technique(
            name="Defensive Copy",
            cost=80,
            description="Copies defensive techniques from opponents",
            technique_type="counter",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"copy_defense": True, "immediate_use": True}
        )
    },
    "barriers" : {},
    "rarity" : 5
}

CursedSpeech = {
    "name" : "Cursed Speech",
    "attack" : {
        "Blast Away": Technique(
            name="Blast Away",
            cost=80,
            description="Commanding word that forcefully repels targets",
            technique_type="projectile",
            strength=400,
            activation_speed=1,
            aoe=5,
            grade=3,
            travel_speed=1500,
            effects={"knockback": 10, "throat_damage_self": 10}
        ),
        "Don't Move": Technique(
            name="Don't Move",
            cost=60,
            description="Paralyzes target with commanding speech",
            technique_type="special",
            strength=0,
            activation_speed=1,
            aoe=3,
            grade=2,
            travel_speed=0,
            effects={"paralysis": 3, "throat_damage_self": 5}
        ),
        "Explode": Technique(
            name="Explode",
            cost=200,
            description="Forces target to violently explode with cursed speech",
            technique_type="special",
            strength=1000,
            activation_speed=2,
            aoe=1,
            grade=5,
            travel_speed=0,
            effects={"instant_kill_chance": 0.8, "throat_damage_self": 50}
        )
    },
    "defense" : {
        "Sleep": Technique(
            name="Sleep",
            cost=40,
            description="Forces attackers to fall asleep",
            technique_type="counter",
            strength=0,
            activation_speed=1,
            aoe=2,
            grade=2,
            travel_speed=0,
            effects={"sleep": 5, "throat_damage_self": 8}
        )
    },
    "barriers" : {},
    "rarity" : 30
}


CurseSpiritManip = {
    "name" : "Curse Spirit Manipulation",
    "attack" : {
        "Spirit Command": Technique(
            name="Spirit Command",
            cost=120,
            description="Commands absorbed curse spirits to attack",
            technique_type="summon",
            strength=500,
            activation_speed=2,
            aoe=3,
            grade=4,
            travel_speed=600,
            summons=["Controlled Curse"],
            effects={"requires_absorbed_spirit": True, "variable_strength": True}
        ),
        "Spirit Fusion": Technique(
            name="Spirit Fusion",
            cost=200,
            description="Fuses multiple curse spirits for devastating attack",
            technique_type="special",
            strength=800,
            activation_speed=4,
            aoe=8,
            grade=5,
            travel_speed=800,
            effects={"requires_multiple_spirits": True, "fusion_power": True}
        ),
        "Maximum: Uzumaki": Technique(
            name="Maximum: Uzumaki",
            cost=400,
            description="Ultimate technique using thousands of curses",
            technique_type="projectile",
            strength=2000,
            activation_speed=5,
            aoe=15,
            grade=5,
            travel_speed=2000,
            binding_vows={"maximum_output": True},
            effects={"thousands_of_curses": True, "devastating": True}
        )
    },
    "defense" : {
        "Spirit Shield": Technique(
            name="Spirit Shield",
            cost=80,
            description="Uses absorbed spirits as protective barrier",
            technique_type="guard",
            strength=400,
            activation_speed=1,
            aoe=2,
            grade=3,
            travel_speed=0,
            effects={"spirit_consumption": 1, "adaptive_defense": True}
        )
    },
    "barriers" : {},
    "rarity" : 5
}

Flames = {
    "name" : "Disaster Flames",
    "attack" : {
        "Ember": Technique(
            name="Ember",
            cost=60,
            description="Small but intense flame projectile",
            technique_type="projectile",
            strength=300,
            activation_speed=1,
            aoe=2,
            grade=2,
            travel_speed=800,
            effects={"burn": 5, "ignite": True}
        ),
        "Flame Arrow": Technique(
            name="Flame Arrow",
            cost=100,
            description="Concentrated fire attack with piercing power",
            technique_type="projectile",
            strength=500,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=1200,
            effects={"armor_piercing": True, "burn": 8}
        ),
        "Maximum: Meteor": Technique(
            name="Maximum: Meteor",
            cost=300,
            description="Devastating meteor-like flame attack",
            technique_type="projectile",
            strength=1200,
            activation_speed=4,
            aoe=20,
            grade=5,
            travel_speed=1500,
            binding_vows={"maximum_output": True},
            effects={"explosive": True, "area_burn": 10, "devastating": True}
        )
    },
    "defense" : {
        "Flame Barrier": Technique(
            name="Flame Barrier",
            cost=80,
            description="Wall of flames that burns attackers",
            technique_type="guard",
            strength=300,
            activation_speed=2,
            aoe=5,
            grade=3,
            travel_speed=0,
            effects={"continuous_damage": 20, "burn_attackers": True}
        )
    },
    "barriers" : {
        "Ring of Fire": Barrier(
            name="Ring of Fire",
            cost=200,
            activation_speed=3,
            strength=400,
            duration=30,
            cooldown=15,
            aoe=12,
            effects={"fire_wall": True, "continuous_burn": True},
            buffs={},
            debuffs={"burn_damage": 15}
        )
    },
    "rarity" : 5
}

Tides = {
    "name" : "Disaster Tides",
    "attack" : {
        "Water Jet": Technique(
            name="Water Jet",
            cost=70,
            description="High-pressure water attack",
            technique_type="projectile",
            strength=350,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=1000,
            effects={"piercing": True, "knockback": 5}
        ),
        "Tidal Wave": Technique(
            name="Tidal Wave",
            cost=150,
            description="Massive wave that overwhelms the battlefield",
            technique_type="area",
            strength=400,
            activation_speed=4,
            aoe=15,
            grade=4,
            travel_speed=600,
            effects={"knockdown": True, "flooding": 30}
        ),
        "Maximum: Tsunami": Technique(
            name="Maximum: Tsunami",
            cost=350,
            description="Devastating tsunami-level water attack",
            technique_type="area",
            strength=1000,
            activation_speed=5,
            aoe=30,
            grade=5,
            travel_speed=800,
            binding_vows={"maximum_output": True},
            effects={"area_devastation": True, "drowning": True}
        )
    },
    "defense" : {
        "Water Shield": Technique(
            name="Water Shield",
            cost=60,
            description="Protective water barrier that absorbs impacts",
            technique_type="guard",
            strength=250,
            activation_speed=1,
            aoe=3,
            grade=2,
            travel_speed=0,
            effects={"impact_absorption": True, "adaptive": True}
        )
    },
    "barriers" : {},
    "rarity" : 20
}

Explosive = {
    "name" : "Explosive Flesh",
    "attack" : {
        "Body Bomb": Technique(
            name="Body Bomb",
            cost=100,
            description="Explosive body parts deal area damage",
            technique_type="melee",
            strength=500,
            activation_speed=2,
            aoe=6,
            grade=3,
            travel_speed=0,
            effects={"explosive": True, "self_damage": 50, "area_damage": True}
        ),
        "Remote Detonation": Technique(
            name="Remote Detonation",
            cost=80,
            description="Detonates previously placed explosive flesh",
            technique_type="special",
            strength=400,
            activation_speed=1,
            aoe=8,
            grade=3,
            travel_speed=0,
            effects={"requires_placement": True, "delayed_explosion": True}
        )
    },
    "defense" : {
        "Explosive Counter": Technique(
            name="Explosive Counter",
            cost=70,
            description="Explosive retaliation when attacked",
            technique_type="counter",
            strength=300,
            activation_speed=1,
            aoe=4,
            grade=2,
            travel_speed=0,
            effects={"automatic_trigger": True, "self_damage": 20}
        )
    },
    "barriers" : {},
    "rarity" : 20
}


Fingerbearer = {
    "name" : "Fingerbearer",
    "attack" : {
        "Finger Beam": Technique(
            name="Finger Beam",
            cost=120,
            description="Fires concentrated cursed energy from finger",
            technique_type="projectile",
            strength=600,
            activation_speed=2,
            aoe=1,
            grade=4,
            travel_speed=1800,
            effects={"piercing": True, "high_damage": True}
        ),
        "Finger Crush": Technique(
            name="Finger Crush",
            cost=100,
            description="Devastating finger strike that can crush bones",
            technique_type="melee",
            strength=700,
            activation_speed=3,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"bone_crushing": True, "devastating": True}
        )
    },
    "defense" : {
        "Finger Shield": Technique(
            name="Finger Shield",
            cost=80,
            description="Uses fingers to deflect and block attacks",
            technique_type="guard",
            strength=500,
            activation_speed=2,
            aoe=2,
            grade=3,
            travel_speed=0,
            effects={"multi_directional_block": True}
        )
    },
    "barriers" : {},
    "rarity" : 20
}


FloatJelly = {
    "name" : "Float Jellyfish",
    "attack" : {
        "Jellyfish Sting": Technique(
            name="Jellyfish Sting",
            cost=25,
            description="Floating jellyfish attack with toxic sting",
            technique_type="melee",
            strength=150,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=300,
            effects={"poison": 3, "floating": True}
        ),
        "Toxic Cloud": Technique(
            name="Toxic Cloud",
            cost=40,
            description="Releases poisonous cloud around jellyfish",
            technique_type="area",
            strength=100,
            activation_speed=2,
            aoe=4,
            grade=1,
            travel_speed=0,
            effects={"poison_cloud": 5, "area_denial": True}
        )
    },
    "defense" : {
        "Float Away": Technique(
            name="Float Away",
            cost=20,
            description="Uses buoyancy to evade attacks",
            technique_type="dodge",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=400,
            effects={"floating_evasion": True}
        )
    },
    "barriers" : {},
    "rarity" : 0,
}


BatMouth = {
    "name" : "Bat Mouth",
    "attack" : {
        "Sonic Screech": Technique(
            name="Sonic Screech",
            cost=35,
            description="High-frequency sound attack that stuns",
            technique_type="projectile",
            strength=180,
            activation_speed=1,
            aoe=6,
            grade=1,
            travel_speed=1100,
            effects={"sonic": True, "stun": 2, "disorientation": True}
        ),
        "Bite": Technique(
            name="Bite",
            cost=30,
            description="Powerful jaw attack with crushing force",
            technique_type="melee",
            strength=200,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            effects={"crushing": True, "bleeding": 2}
        )
    },
    "defense" : {
        "Wing Shield": Technique(
            name="Wing Shield",
            cost=25,
            description="Uses wings to deflect incoming attacks",
            technique_type="guard",
            strength=100,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            effects={"deflection": True}
        )
    },
    "barriers" : {},
    "rarity" : 0,
}

FurrPede = {
    "name" : "Furry Centipede",
    "attack" : {
        "Multi-Leg Strike": Technique(
            name="Multi-Leg Strike",
            cost=50,
            description="Rapid strikes using multiple legs",
            technique_type="melee",
            strength=180,
            activation_speed=2,
            aoe=2,
            grade=1,
            travel_speed=0,
            effects={"multi_hit": 6, "overwhelming": True}
        ),
        "Venomous Bite": Technique(
            name="Venomous Bite",
            cost=40,
            description="Poisonous bite that weakens the target",
            technique_type="melee",
            strength=160,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"poison": 5, "strength_drain": 20}
        )
    },
    "defense" : {
        "Coiled Defense": Technique(
            name="Coiled Defense",
            cost=35,
            description="Coils up to reduce damage from attacks",
            technique_type="guard",
            strength=150,
            activation_speed=1,
            aoe=1,
            grade=1,
            travel_speed=0,
            effects={"damage_reduction": 0.4, "defensive_posture": True}
        )
    },
    "barriers" : {},
    "rarity" : 0
}

PuppetManip = {
    "name" : "Puppet Manipulation",
    "attack" : {
        "Puppet Strike": Technique(
            name="Puppet Strike",
            cost=60,
            description="Controls puppet to attack from multiple angles",
            technique_type="melee",
            strength=300,
            activation_speed=2,
            aoe=2,
            grade=2,
            travel_speed=500,
            effects={"multi_angle_attack": True, "unpredictable": True}
        ),
        "Mass Puppet Control": Technique(
            name="Mass Puppet Control",
            cost=150,
            description="Controls multiple puppets simultaneously",
            technique_type="summon",
            strength=250,
            activation_speed=4,
            aoe=5,
            grade=3,
            travel_speed=400,
            summons=["Combat Puppet", "Combat Puppet", "Combat Puppet"],
            effects={"swarm_tactics": True, "overwhelming_numbers": True}
        )
    },
    "defense" : {
        "Puppet Shield": Technique(
            name="Puppet Shield",
            cost=50,
            description="Uses puppet as protective barrier",
            technique_type="guard",
            strength=200,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"puppet_sacrifice": True, "damage_absorption": True}
        )
    },
    "barriers" : {},
    "rarity" : 15
}

HR_Zero = {
    "name" : "Heavenly Restriction: Zero",
    "attack" : {
        "Physical Dominance": Technique(
            name="Physical Dominance",
            cost=0,
            description="Pure physical power without cursed energy",
            technique_type="melee",
            strength=800,
            activation_speed=1,
            aoe=1,
            grade=5,
            travel_speed=0,
            effects={"no_cursed_energy": True, "pure_physical": True, "enhanced_strength": 500}
        ),
        "Superhuman Speed": Technique(
            name="Superhuman Speed",
            cost=0,
            description="Incredible speed beyond normal human limits",
            technique_type="melee",
            strength=400,
            activation_speed=0,
            aoe=2,
            grade=4,
            travel_speed=3000,
            effects={"superhuman_speed": True, "multiple_strikes": 5}
        )
    },
    "defense" : {
        "Enhanced Reflexes": Technique(
            name="Enhanced Reflexes",
            cost=0,
            description="Supernatural reflexes for dodging",
            technique_type="dodge",
            strength=0,
            activation_speed=0,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"perfect_reflexes": True, "precognition": True}
        )
    },
    "barriers" : {},
    "rarity" : 2
}

IceManip = {
    "name" : "Ice Manipulation",
    "attack" : {
        "Ice Shard": Technique(
            name="Ice Shard",
            cost=50,
            description="Launches sharp ice projectiles",
            technique_type="projectile",
            strength=280,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=1000,
            effects={"piercing": True, "freeze_chance": 0.3}
        ),
        "Frost Nova": Technique(
            name="Frost Nova",
            cost=100,
            description="Explodes ice outward in all directions",
            technique_type="area",
            strength=350,
            activation_speed=3,
            aoe=8,
            grade=3,
            travel_speed=600,
            effects={"area_freeze": 5, "slowing": True}
        ),
        "Absolute Zero": Technique(
            name="Absolute Zero",
            cost=250,
            description="Creates a field of absolute cold",
            technique_type="area",
            strength=800,
            activation_speed=5,
            aoe=12,
            grade=5,
            travel_speed=0,
            binding_vows={"temperature_manipulation": True},
            effects={"instant_freeze": True, "lethal_cold": True}
        )
    },
    "defense" : {
        "Ice Armor": Technique(
            name="Ice Armor",
            cost=70,
            description="Covers body in protective ice",
            technique_type="enhancement",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"defense_boost": 150, "cold_resistance": True}
        )
    },
    "barriers" : {
        "Ice Wall": Barrier(
            name="Ice Wall",
            cost=120,
            activation_speed=3,
            strength=400,
            duration=45,
            cooldown=10,
            aoe=8,
            effects={"ice_barrier": True, "slowing_aura": True},
            buffs={},
            debuffs={"movement_speed": -40}
        )
    },
    "rarity" : 20
}

IdleTran = {
    "name" : "Idle Transformation",
    "attack" : {
        "Soul Manipulation": Technique(
            name="Soul Manipulation",
            cost=120,
            description="Directly manipulates the shape of target's soul",
            technique_type="special",
            strength=800,
            activation_speed=2,
            aoe=1,
            grade=5,
            travel_speed=0,
            effects={"soul_damage": True, "transformation": True, "instant_kill_chance": 0.6}
        ),
        "Body Transfiguration": Technique(
            name="Body Transfiguration",
            cost=100,
            description="Transforms own body parts for combat advantage",
            technique_type="enhancement",
            strength=300,
            activation_speed=1,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"self_transformation": True, "adaptability": True}
        )
    },
    "defense" : {
        "Adaptive Form": Technique(
            name="Adaptive Form",
            cost=80,
            description="Changes body to resist specific damage types",
            technique_type="guard",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"damage_adaptation": True, "resistance_boost": 0.5}
        )
    },
    "barriers" : {},
    "rarity" : 2
}

Limitless = {
    "name" : "Limitless",
    "attack" : {
        "Blue": Technique(
            name="Blue",
            cost=100,
            description="Creates attractive force through negative space",
            technique_type="projectile",
            strength=400,
            activation_speed=2,
            aoe=5,
            grade=4,
            travel_speed=1200,
            effects={"attraction": True, "spatial_manipulation": True}
        ),
        "Red": Technique(
            name="Red",
            cost=150,
            description="Repulsive force through reversal technique",
            technique_type="projectile",
            strength=600,
            activation_speed=3,
            aoe=8,
            grade=4,
            travel_speed=1500,
            effects={"repulsion": True, "devastating": True}
        ),
        "Purple": Technique(
            name="Purple",
            cost=300,
            description="Virtual mass that erases everything in its path",
            technique_type="projectile",
            strength=1500,
            activation_speed=4,
            aoe=3,
            grade=5,
            travel_speed=2000,
            binding_vows={"imaginary_mass": True},
            effects={"existence_erasure": True, "unstoppable": True}
        )
    },
    "defense" : {
        "Infinity": Technique(
            name="Infinity",
            cost=50,
            description="Infinite space barrier that slows approaching attacks",
            technique_type="guard",
            strength=0,
            activation_speed=0,
            aoe=1,
            grade=5,
            travel_speed=0,
            effects={"infinite_defense": True, "automatic": True, "Six_Eyes_required": True}
        )
    },
    "barriers" : {
        "Unlimited Void": Domain(
            name="Unlimited Void",
            cost=1000,
            grade=5,
            activation_speed=8,
            open=False,
            sure_hit="Information Overload",
            lethal=False,
            aoe=25,
            duration=0.2,
            vows={"instant_victory": True, "perfect_information": True}
        )
    },
    "rarity" : 2
}


mba = {
    "name" : "Mythic Beast Amber",
    "attack" : {
        "Amber Entrapment": Technique(
            name="Amber Entrapment",
            cost=100,
            description="Encases target in hardening amber",
            technique_type="projectile",
            strength=300,
            activation_speed=3,
            aoe=2,
            grade=3,
            travel_speed=500,
            effects={"binding": True, "hardening": 5, "suffocation": True}
        ),
        "Beast Resurrection": Technique(
            name="Beast Resurrection",
            cost=200,
            description="Revives ancient beasts trapped in amber",
            technique_type="summon",
            strength=600,
            activation_speed=5,
            aoe=1,
            grade=4,
            travel_speed=0,
            summons=["Ancient Beast"],
            effects={"prehistoric_power": True, "ancient_wisdom": True}
        )
    },
    "defense" : {
        "Amber Shield": Technique(
            name="Amber Shield",
            cost=80,
            description="Creates protective amber barrier",
            technique_type="guard",
            strength=350,
            activation_speed=2,
            aoe=2,
            grade=3,
            travel_speed=0,
            effects={"hardening_over_time": True, "reflective": True}
        )
    },
    "barriers" : {},
    "rarity" : 10
}

NaturesWrath = {
    "name" : "Nature's Wrath",
    "attack" : {
        "Thorn Barrage": Technique(
            name="Thorn Barrage",
            cost=70,
            description="Launches volleys of razor-sharp thorns",
            technique_type="projectile",
            strength=320,
            activation_speed=2,
            aoe=4,
            grade=2,
            travel_speed=900,
            effects={"multi_hit": 8, "bleeding": 3, "natural": True}
        ),
        "Forest Fury": Technique(
            name="Forest Fury",
            cost=150,
            description="Summons wrathful forest spirits to attack",
            technique_type="summon",
            strength=450,
            activation_speed=4,
            aoe=6,
            grade=3,
            travel_speed=600,
            summons=["Forest Spirit", "Forest Spirit"],
            effects={"natural_alliance": True, "area_control": True}
        ),
        "Gaia's Judgment": Technique(
            name="Gaia's Judgment",
            cost=300,
            description="Channels the earth's fury for massive damage",
            technique_type="area",
            strength=900,
            activation_speed=6,
            aoe=20,
            grade=4,
            travel_speed=0,
            binding_vows={"nature_connection": True},
            effects={"earth_shaking": True, "primal_power": True}
        )
    },
    "defense" : {
        "Bark Skin": Technique(
            name="Bark Skin",
            cost=60,
            description="Hardens skin like tree bark for protection",
            technique_type="enhancement",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"defense_boost": 200, "natural_armor": True}
        )
    },
    "barriers" : {
        "Living Forest": Barrier(
            name="Living Forest",
            cost=250,
            activation_speed=5,
            strength=500,
            duration=90,
            cooldown=25,
            aoe=25,
            effects={"nature_healing": True, "enemy_hindering": True},
            buffs={"nature_boost": 100, "healing_over_time": 10},
            debuffs={"movement_speed": -50}
        )
    },
    "rarity" : 25
}

OrbMaster = {
    "name" : "Orb Mastery",
    "attack" : {
        "Energy Orb": Technique(
            name="Energy Orb",
            cost=60,
            description="Launches floating energy orbs that track targets",
            technique_type="projectile",
            strength=300,
            activation_speed=2,
            aoe=1,
            grade=2,
            travel_speed=700,
            effects={"tracking": True, "homing": True, "energy_based": True}
        ),
        "Orbital Strike": Technique(
            name="Orbital Strike",
            cost=120,
            description="Commands multiple orbs to converge on target",
            technique_type="projectile",
            strength=400,
            activation_speed=3,
            aoe=3,
            grade=3,
            travel_speed=1000,
            effects={"multi_orb": 5, "convergence": True, "devastating": True}
        ),
        "Orb Constellation": Technique(
            name="Orb Constellation",
            cost=200,
            description="Creates a formation of orbs for sustained assault",
            technique_type="area",
            strength=350,
            activation_speed=4,
            aoe=10,
            grade=4,
            travel_speed=500,
            effects={"sustained_fire": 10, "formation_tactics": True, "area_denial": True}
        )
    },
    "defense" : {
        "Orb Shield": Technique(
            name="Orb Shield",
            cost=80,
            description="Orbs orbit around user for protection",
            technique_type="guard",
            strength=250,
            activation_speed=2,
            aoe=2,
            grade=3,
            travel_speed=0,
            effects={"orbital_defense": True, "360_protection": True}
        )
    },
    "barriers" : {},
    "rarity" : 50
}

primate = {
    "name" : "Primate",
    "attack" : {
        "Primal Rage": Technique(
            name="Primal Rage",
            cost=80,
            description="Unleashes primitive fury in berserker attacks",
            technique_type="melee",
            strength=400,
            activation_speed=2,
            aoe=2,
            grade=2,
            travel_speed=0,
            effects={"berserker": True, "strength_boost": 100, "wild": True}
        ),
        "Alpha Dominance": Technique(
            name="Alpha Dominance",
            cost=120,
            description="Asserts dominance to intimidate and weaken foes",
            technique_type="special",
            strength=200,
            activation_speed=1,
            aoe=5,
            grade=3,
            travel_speed=0,
            effects={"intimidation": True, "enemy_debuff": 50, "pack_leader": True}
        )
    },
    "defense" : {
        "Pack Instincts": Technique(
            name="Pack Instincts",
            cost=60,
            description="Natural pack instincts enhance evasion",
            technique_type="dodge",
            strength=0,
            activation_speed=1,
            aoe=1,
            grade=2,
            travel_speed=0,
            effects={"pack_bonus": True, "instinctive_dodge": True}
        )
    },
    "barriers" : {},
    "rarity" : 0
}

projection = {
    "name" : "Projection Sorcery", 
    "attack" : {
        "Frame Acceleration": Technique(
            name="Frame Acceleration",
            cost=80,
            description="Moves at predetermined frames for incredible speed",
            technique_type="melee",
            strength=350,
            activation_speed=1,
            aoe=1,
            grade=3,
            travel_speed=2000,
            effects={"frame_based": True, "speed_boost": 200, "predetermined_path": True}
        ),
        "24 Frame Rule": Technique(
            name="24 Frame Rule",
            cost=150,
            description="Forces target to move in preset frames or freeze",
            technique_type="special",
            strength=0,
            activation_speed=2,
            aoe=3,
            grade=4,
            travel_speed=0,
            effects={"frame_lock": True, "movement_control": True, "freeze_penalty": True}
        )
    },
    "defense" : {
        "Frame Perfect": Technique(
            name="Frame Perfect",
            cost=60,
            description="Perfect timing to avoid attacks",
            technique_type="dodge",
            strength=0,
            activation_speed=0,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"perfect_timing": True, "frame_advantage": True}
        )
    },
    "barriers" : {},
    "rarity" : 15
}


shrine = {"name" : "Shrine",
          "attack" : {
              "Dismantle": Technique(
                  name="Dismantle",
                  cost=80,
                  description="Invisible slashing attack that cuts through anything",
                  technique_type="projectile",
                  strength=500,
                  activation_speed=1,
                  aoe=1,
                  grade=4,
                  travel_speed=2000,
                  effects={"invisible": True, "slashing": True, "armor_piercing": True}
              ),
              "Cleave": Technique(
                  name="Cleave",
                  cost=100,
                  description="Adjustable slashing attack that adapts to target",
                  technique_type="projectile",
                  strength=600,
                  activation_speed=1,
                  aoe=1,
                  grade=4,
                  travel_speed=2000,
                  effects={"adaptive_damage": True, "slashing": True, "cursed_energy_based": True}
              ),
              "Fire Arrow": Technique(
                  name="Fire Arrow",
                  cost=200,
                  description="Devastating fire technique with massive range",
                  technique_type="projectile",
                  strength=1000,
                  activation_speed=4,
                  aoe=20,
                  grade=5,
                  travel_speed=1800,
                  binding_vows={"flame_technique": True},
                  effects={"area_devastation": True, "burn": 10}
              )
          },
          "defense" : {},
          "barriers" : {
              "Malevolent Shrine": Domain(
                  name="Malevolent Shrine",
                  cost=800,
                  grade=5,
                  activation_speed=7,
                  open=True,
                  sure_hit="Dismantle & Cleave",
                  lethal=True,
                  aoe=200,
                  duration=60,
                  vows={"open_domain": True, "inescapable": True}
              )
          },
          "rarity" : 10
          }


sky_manipulation = {
    "name" : "Sky Manipulation",
    "attack" : {
        "Lightning Strike": Technique(
            name="Lightning Strike",
            cost=90,
            description="Calls down lightning from the sky",
            technique_type="projectile",
            strength=500,
            activation_speed=3,
            aoe=2,
            grade=3,
            travel_speed=2000,
            effects={"lightning": True, "stun": 3, "from_above": True}
        ),
        "Wind Blade": Technique(
            name="Wind Blade",
            cost=70,
            description="Compressed air creates invisible cutting attacks",
            technique_type="projectile",
            strength=350,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=1500,
            effects={"invisible": True, "slashing": True, "wind_based": True}
        ),
        "Tornado": Technique(
            name="Tornado",
            cost=200,
            description="Creates a devastating whirlwind",
            technique_type="area",
            strength=600,
            activation_speed=5,
            aoe=15,
            grade=4,
            travel_speed=800,
            effects={"area_control": True, "knockback": 10, "continuous": 8}
        )
    },
    "defense" : {
        "Wind Barrier": Technique(
            name="Wind Barrier",
            cost=60,
            description="Wind currents deflect incoming attacks",
            technique_type="guard",
            strength=200,
            activation_speed=1,
            aoe=3,
            grade=2,
            travel_speed=0,
            effects={"projectile_deflection": True, "wind_shield": True}
        )
    },
    "barriers" : {
        "Storm Domain": Barrier(
            name="Storm Domain",
            cost=300,
            activation_speed=6,
            strength=600,
            duration=60,
            cooldown=20,
            aoe=30,
            effects={"weather_control": True, "lightning_field": True},
            buffs={"sky_mastery": 150},
            debuffs={"visibility": -70, "movement_hindered": True}
        )
    },
    "rarity" : 20
}

star = {
    "name" : "Star Rage",
    "attack" : {
        "Stellar Burst": Technique(
            name="Stellar Burst",
            cost=100,
            description="Explosive energy attack mimicking stellar radiation",
            technique_type="projectile",
            strength=450,
            activation_speed=3,
            aoe=6,
            grade=3,
            travel_speed=1200,
            effects={"radiation": 5, "explosive": True, "stellar": True}
        ),
        "Supernova": Technique(
            name="Supernova",
            cost=250,
            description="Devastating explosion with stellar power",
            technique_type="area",
            strength=800,
            activation_speed=5,
            aoe=20,
            grade=4,
            travel_speed=0,
            binding_vows={"stellar_energy": True},
            effects={"massive_explosion": True, "radiation_field": 10, "devastating": True}
        ),
        "Star Fall": Technique(
            name="Star Fall",
            cost=150,
            description="Rains down stellar projectiles from above",
            technique_type="projectile",
            strength=350,
            activation_speed=4,
            aoe=10,
            grade=3,
            travel_speed=1000,
            effects={"from_above": True, "multi_hit": 12, "stellar_rain": True}
        )
    },
    "defense" : {
        "Stellar Shield": Technique(
            name="Stellar Shield",
            cost=80,
            description="Creates protective barrier of stellar energy",
            technique_type="guard",
            strength=300,
            activation_speed=2,
            aoe=2,
            grade=3,
            travel_speed=0,
            effects={"energy_absorption": True, "stellar_protection": True}
        )
    },
    "barriers" : {},
    "rarity" : 15
}

stink = {
    "name" : "Stinkaspore",
    "attack" : {
        "Toxic Spores": Technique(
            name="Toxic Spores",
            cost=50,
            description="Releases poisonous spores that weaken enemies",
            technique_type="area",
            strength=200,
            activation_speed=2,
            aoe=8,
            grade=1,
            travel_speed=300,
            effects={"poison": 8, "weakness": 5, "spore_cloud": True}
        ),
        "Stench Blast": Technique(
            name="Stench Blast",
            cost=70,
            description="Overwhelming stench that causes nausea and confusion",
            technique_type="projectile",
            strength=180,
            activation_speed=1,
            aoe=5,
            grade=2,
            travel_speed=600,
            effects={"nausea": 6, "confusion": 4, "overwhelming_stench": True}
        ),
        "Spore Explosion": Technique(
            name="Spore Explosion",
            cost=120,
            description="Explosive release of concentrated toxic spores",
            technique_type="area",
            strength=350,
            activation_speed=3,
            aoe=12,
            grade=3,
            travel_speed=0,
            effects={"explosive": True, "poison_field": 15, "area_denial": True}
        )
    },
    "defense" : {
        "Spore Shield": Technique(
            name="Spore Shield",
            cost=40,
            description="Protective cloud of spores around the user",
            technique_type="guard",
            strength=150,
            activation_speed=1,
            aoe=3,
            grade=1,
            travel_speed=0,
            effects={"passive_poison": 3, "concealment": True}
        )
    },
    "barriers" : {},
    "rarity" : 0
}


straw = {
    "name" : "Straw Doll",
    "attack" : {
        "Voodoo Strike": Technique(
            name="Voodoo Strike",
            cost=80,
            description="Damages target through sympathetic magic",
            technique_type="special",
            strength=400,
            activation_speed=3,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"sympathetic_damage": True, "requires_hair_or_blood": True, "distance_independent": True}
        ),
        "Binding Curse": Technique(
            name="Binding Curse",
            cost=100,
            description="Binds target using cursed straw doll",
            technique_type="special",
            strength=0,
            activation_speed=4,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"paralysis": 10, "requires_connection": True}
        )
    },
    "defense" : {
        "Deflection Doll": Technique(
            name="Deflection Doll",
            cost=60,
            description="Transfers incoming damage to straw doll",
            technique_type="guard",
            strength=0,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=0,
            effects={"damage_transfer": True, "one_time_use": True}
        )
    },
    "barriers" : {},
    "rarity" : 30
}


ten = {
    "name" : "Ten Shadows",
    "attack" : {
        "Divine Dogs": Technique(
            name="Divine Dogs",
            cost=80,
            description="Summons twin divine dogs to attack",
            technique_type="summon",
            strength=300,
            activation_speed=2,
            aoe=2,
            grade=3,
            travel_speed=700,
            summons=["Divine Dog White", "Divine Dog Black"],
            effects={"pack_hunting": True, "loyalty": True}
        ),
        "Nue": Technique(
            name="Nue",
            cost=120,
            description="Summons the flying electric beast Nue",
            technique_type="summon",
            strength=400,
            activation_speed=3,
            aoe=3,
            grade=4,
            travel_speed=1000,
            summons=["Nue"],
            effects={"flight": True, "electrical": True}
        ),
        "Mahoraga": Technique(
            name="Mahoraga",
            cost=500,
            description="Summons the ultimate shikigami with adaptation",
            technique_type="summon",
            strength=2000,
            activation_speed=8,
            aoe=1,
            grade=5,
            travel_speed=800,
            summons=["Mahoraga"],
            binding_vows={"death_gamble": True},
            effects={"adaptation": True, "untameable": True, "devastating": True}
        )
    },
    "defense" : {
        "Great Serpent": Technique(
            name="Great Serpent",
            cost=100,
            description="Summons protective serpent shikigami",
            technique_type="summon",
            strength=200,
            activation_speed=2,
            aoe=1,
            grade=3,
            travel_speed=0,
            summons=["Great Serpent"],
            effects={"binding": True, "protection": True}
        )
    },
    "barriers" : {},
    "rarity" : 5
}

deadly = {
    "name" : "Deadly Sentencing",
    "attack" : {
        "Confiscation": Technique(
            name="Confiscation",
            cost=150,
            description="Removes target's cursed technique temporarily",
            technique_type="special",
            strength=0,
            activation_speed=3,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"technique_removal": True, "duration": 60}
        ),
        "Executioner's Swing": Technique(
            name="Executioner's Swing",
            cost=200,
            description="Devastating attack that ignores most defenses",
            technique_type="melee",
            strength=1000,
            activation_speed=4,
            aoe=1,
            grade=5,
            travel_speed=0,
            binding_vows={"execution_vow": True},
            effects={"defense_piercing": True, "execution": True}
        )
    },
    "defense" : {
        "Judgment Shield": Technique(
            name="Judgment Shield",
            cost=100,
            description="Protective barrier based on moral judgment",
            technique_type="guard",
            strength=500,
            activation_speed=2,
            aoe=1,
            grade=4,
            travel_speed=0,
            effects={"moral_based": True, "variable_strength": True}
        )
    },
    "barriers" : {},
    "rarity" : 15
}




