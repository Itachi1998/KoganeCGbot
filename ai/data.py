"""Game content.  Everything here is data; behaviour lives in effects.py."""
from __future__ import annotations

from dataclasses import dataclass, field

from .constants import (ANY_ARM, ANY_LEG, BOTH_ARMS, HEAD_REQ, TORSO_REQ, DType, Kind,
                        PClass, React, Rng, Stat, Status, Target)
from .techniques import Action as A
from .techniques import Technique, register

P, C, S = DType.PHYSICAL, DType.CURSED, DType.SOUL
fs = frozenset
DEF, BUFF, HEAL, SUMMON, DOMAIN, UTIL = (Kind.DEFENSE, Kind.BUFF, Kind.HEAL, Kind.SUMMON,
                                         Kind.DOMAIN, Kind.UTILITY)
SELF, ALL, CORPSE, CHOICE, ANY = (Target.SELF, Target.ALL_ENEMIES, Target.CORPSE,
                                  Target.CHOICE, Target.ANY)
RANGED = Rng.RANGED

# ======================================================================================
# Basic kit - every combatant
# ======================================================================================
register(Technique("basic", "Basic Combat", innate=False, copyable=False, actions=(
    A("punch", "Punch", power=8, dtype=P, sta=4, requires=ANY_ARM, tags=fs({"blunt"})),
    A("kick", "Kick", power=11, dtype=P, sta=6, requires=ANY_LEG, acc=-0.05, tags=fs({"blunt"})),
    A("weapon", "Weapon Strike", power=5, dtype=P, sta=5, requires=ANY_ARM,
      effect="weapon_strike", params={"cond": "has_weapon"}),
    A("shoot", "Shoot", dtype=P, sta=1, rng=RANGED, requires=ANY_ARM, effect="weapon_strike",
      params={"cond": "has_gun"}, desc="An ordinary bullet: no cursed energy in it."),
    A("infused_strike", "Infused Strike", power=7, dtype=P, ce=5, sta=5, requires=ANY_ARM,
      effect="weapon_strike", params={"cond": "plain_weapon"},
      desc="Pour cursed energy into an ordinary weapon as you swing it."),
    A("infused_shot", "Infused Shot", power=2, dtype=P, ce=5, sta=1, rng=RANGED, requires=ANY_ARM,
      effect="weapon_strike", params={"cond": "has_gun"}, desc="A bullet carrying cursed energy."),
    A("ce_strike", "Cursed Strike", power=13, ce=6, sta=3, requires=ANY_ARM,
      tags=fs({"blunt"}), desc="A blow reinforced with cursed energy."),
    A("dodge", "Dodge", kind=DEF, react=React.DODGE, sta=5, requires=ANY_LEG),
    A("block", "Block", kind=DEF, react=React.BLOCK, sta=4, requires=ANY_ARM,
      params={"block": 0.5}),
    A("counter", "Counter", kind=DEF, react=React.COUNTER, sta=7, requires=ANY_ARM),
    A("cover", "Summon Cover", kind=DEF, react=React.COVER, params={"hold": 99, "cond": "has_summon"},
      desc="One of your shikigami, spirits or puppets takes single blows aimed at you. Stays in "
           "force until it is destroyed or you choose another defence."),
    A("reinforce", "Reinforce Body Part", kind=DEF, react=React.REINFORCE,
      params={"max": 30}, desc="Pour cursed energy into the part being targeted."),
    # ---- answers to a domain ---------------------------------------------------------------
    A("simple_domain", "Simple Domain", kind=BUFF, target=SELF, ce=12, min_level=6, effect="anti_domain",
      params={"anti": "Simple Domain", "rounds": 3},
      desc="A small circle that neutralises a lethal sure-hit. Each sure-hit it stops wears a round "
           "off it, and it ends if you move."),
    A("basket_ward", "Hollow Wicker Basket", kind=BUFF, target=SELF, ce=10, requires=BOTH_ARMS,
      effect="anti_domain", params={"anti": "Hollow Wicker Basket", "rounds": 5, "hands": True, "cond": "ancient"},
      desc="The old anti-domain art: lasts longer, but only while both hands hold the sign - any "
           "action that needs an arm drops it."),
    A("falling_blossom", "Falling Blossom Emotion", kind=BUFF, target=SELF, ce=10, min_level=5,
      effect="falling_blossom", params={"cond": "big_three"},
      desc="Secret of the three great clans. Does not stop a sure-hit: it counters on contact, so "
           "only 35% of a sure-hit's damage lands, and anyone who strikes you by hand is struck back."),
    A("domain_amplification", "Domain Amplification", kind=BUFF, target=SELF, ce=12, min_level=9,
      effect="amplify",
      desc="Wrap yourself in an empty domain for 2 rounds: sure-hits fail on you, innate techniques "
           "that hit you come apart (30% damage, no effects), and your blows go through technique "
           "defences (Infinity, soul bodies, gag armor) - but your own innate technique cannot be "
           "used meanwhile."),
    A("rct", "Reverse Cursed Technique", kind=HEAL, target=SELF, ce=30, min_level=10,
      requires=HEAD_REQ, effect="heal", params={"frac": 0.4, "limbs": 1, "cond": "can_rct", "cd": 4},
      desc="Only those whose technique's users managed it in the source (RCT_TECHNIQUES)."),
    A("rct_brain", "Reverse Cursed Technique: Restore Technique", kind=BUFF, target=SELF, ce=25, min_level=10,
      requires=HEAD_REQ, effect="restore_technique", params={"cond": "can_restore", "ai": 58},
      desc="Heal the brain a collapsed domain has burnt out: your technique is back at once instead of in "
           "two rounds. Four times a fight; after the fourth you have one domain left in you."),
    A("rct_output", "Reverse Cursed Technique: Output", kind=HEAL, target=ANY, ce=40, min_level=12,
      requires=ANY_ARM, effect="heal_other", params={"frac": 0.3, "limbs": 1, "cond": "can_rct_out", "cd": 3},
      desc="Heal an ally. Far less efficient than healing yourself."),
)))

register(Technique("spirit_body", "Cursed Spirit Body", innate=False, copyable=False, actions=(
    A("regenerate", "Regenerate", kind=HEAL, target=SELF, ce=14, effect="heal",
      params={"frac": 0.3, "limbs": 1, "cd": 3}, desc="Cursed spirits rebuild themselves with cursed energy."),
)))

# The Six Eyes are a trait, not a technique: Limitless always has them, and the original bot gave
# copy and construction users a 1-in-2 chance of them too (see rarity.py). A player who rolled
# them carries this; the "six_eyes" flag is what the engine reads.
register(Technique("six_eyes", "Six Eyes", innate=False, copyable=False, flags=("six_eyes",),
                   desc="Every flow of cursed energy laid bare: the best efficiency and recovery there is."))

# ======================================================================================
# Innate techniques
# ======================================================================================
register(Technique("deadly_sentencing", "Deadly Sentencing", tool="gavel", desc="Hiromi Higuruma's court.", actions=(
    A("gavel", "Gavel Strike", power=16, ce=8, requires=ANY_ARM, channel=1,
      statuses=((Status.STUN, 0.2, 1, 1.0),), tags=fs({"blunt", "gavel"})),
    A("gavel_long", "Extending Gavel", power=13, ce=10, rng=RANGED, requires=ANY_ARM,
      channel=1, tags=fs({"blunt", "gavel"})),
    A("gavel_guard", "Gavel Guard", kind=DEF, react=React.BLOCK, ce=5, requires=ANY_ARM,
      params={"block": 0.7}),
    A("ds_domain", "Domain Expansion: Deadly Sentencing", kind=DOMAIN, ce=40, min_level=5,
      requires=ANY_ARM, effect="deadly_sentencing",
      desc="Opens at once - no channelling turn, no hand sign: the court is this technique's "
           "natural state. Violence is barred; Judgeman tries one opponent for a crime."),
    A("execute", "Executioner's Sword", dtype=P, requires=ANY_ARM,
      needs_status=Status.EXEC_SWORD, effect="execute", desc="Any cut kills."),
)))

register(Technique("comedian", "Comedian", desc="What Takaba is sure is funny becomes real.", actions=(
    A("joke", "Tell a Joke", kind=UTIL, ce=6, requires=HEAD_REQ, effect="comedian_joke",
      params={"ai": 30, "cond": "confident"},
      desc="The target must answer; the answer decides what the bit does. Jokes chain."),
    A("slapstick", "Slapstick", power=10, dtype=P, ce=2, sta=4, requires=ANY_ARM,
      statuses=((Status.STUN, 0.25, 1, 1.0),), tags=fs({"blunt", "gag"})),
    A("pep_talk", "Pep Talk", kind=UTIL, target=SELF, effect="pep_talk",
      params={"ai": 40, "cond": "doubting"}, desc="Regain confidence as a comedian."),
    A("pratfall", "Pratfall", kind=DEF, react=React.DODGE, sta=3, params={"dodge": 0.2},
      desc="Slip on a banana peel at exactly the right moment."),
)))

register(Technique("idle_death_gamble", "Idle Death Gamble", desc="Kinji Hakari's pachinko domain.", actions=(
    A("shutter", "Shutter Doors", power=13, ce=8, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="idg_attack", statuses=((Status.BLEED, 0.25, 2, 3.0),), tags=fs({"shutter"})),
    A("ball_barrage", "Pachinko Ball Barrage", power=9, ce=5, rng=RANGED, requires=ANY_ARM,
      channel=1, effect="idg_attack", tags=fs({"balls"})),
    A("rough_guard", "Rough Energy Guard", kind=DEF, react=React.BLOCK, ce=4,
      requires=ANY_ARM, params={"block": 0.6}),
    A("idg_domain", "Domain Expansion: Idle Death Gamble", kind=DOMAIN, target=SELF, ce=30, min_level=4,
      requires=BOTH_ARMS, channel=1, effect="idle_death_gamble", params={"cond": "no_jackpot"},
      desc="Spin for a jackpot: infinite cursed energy and automatic healing."),
)))

register(Technique("body_hop", "Body Hop", copyable=False, flags=("body_hop",),
                   desc="The user is a brain that moves between bodies.", actions=(
    A("body_hop", "Body Hop", kind=UTIL, target=CORPSE, ce=20, requires=HEAD_REQ,
      effect="body_hop", params={"ai": 45}, desc="Take a dead body and its innate technique."),
    A("barrier_pulse", "Barrier Pulse", power=13, ce=8, rng=RANGED, requires=ANY_ARM,
      channel=1, tags=fs({"barrier"})),
    A("wicker_basket", "Barrier Guard", kind=DEF, react=React.BLOCK, ce=6,
      requires=BOTH_ARMS, params={"block": 0.6}),
)))

register(Technique("copy", "Copy", copyable=False,
                   stat_mods={Stat.MAX_CE: 2.5, Stat.CE_REGEN: 1.5, Stat.EFF: 0.5},   # vast reserves, wasteful use
                   desc="Yuta Okkotsu's technique, bound to Rika.", actions=(
    A("cursed_blade", "Cursed Blade", power=15, ce=7, requires=ANY_ARM,
      tags=fs({"slash"}), desc="Slashes sever limbs more easily; Rika eats what falls."),
    A("summon_rika", "Summon Rika", kind=SUMMON, target=SELF, ce=20, requires=ANY_ARM,
      channel=1, effect="summon_rika", params={"cond": "no_rika"}),
    A("full_manifestation", "Rika: Full Manifestation", kind=UTIL, target=SELF,
      effect="full_manifestation", params={"cond": "has_rika", "ai": 45, "cd": 8},
      desc="Five rounds of access to every copied technique and Rika's energy."),
    A("rika_guard", "Rika's Guard", kind=DEF, react=React.BLOCK, ce=4,
      params={"hold": 3, "block": 0.65, "cond": "has_rika"}),
    A("mutual_love", "Domain Expansion: Authentic Mutual Love", kind=DOMAIN, ce=60, min_level=12,
      requires=ANY_ARM, channel=1, effect="mutual_love",
      desc="You choose one copied technique to fill the barrier and one enemy to turn it on: every "
           "round it strikes that one person as a sure-hit."),
)))

register(Technique("ten_shadows", "Ten Shadows Technique", desc="Shikigami drawn from shadow.", actions=(
    A("summon_shikigami", "Summon Shikigami", kind=SUMMON, target=CHOICE, ce=10,
      requires=BOTH_ARMS, channel=1, effect="summon_shikigami"),
    A("taming_ritual", "Exorcism Ritual", kind=SUMMON, target=CHOICE, ce=5,
      requires=BOTH_ARMS, effect="taming_ritual", params={"ai": 0},
      desc="Call an untamed shikigami. Defeat it without help to tame it."),
    A("merge_shikigami", "Merge Shikigami", kind=SUMMON, target=CHOICE, ce=24, min_level=6,
      requires=BOTH_ARMS, channel=1, effect="merge_shikigami"),
    A("channel_shikigami", "Channel Shikigami", kind=UTIL, target=CHOICE, ce=15,
      min_level=10, effect="channel_shikigami", params={"ai": 24},
      desc="Wear a shikigami's power yourself (Mahoraga's wheel, Max Elephant's water...)."),
    A("shadow_swarm", "Unstable Shadows: Divine Dog Swarm", power=13, ce=8, rng=RANGED, requires=ANY_ARM,
      channel=1, min_level=12, params={"cond": "dogs_tamed"}, tags=fs({"fang", "shadow"}), speed=1.5,
      desc="The Divine Dogs let go of their shape: a cluster of shadow with a long reach and a weaker bite, "
           "kept up by a steady stream of cursed energy."),
    A("shadow_step", "Shadow Step", kind=DEF, react=React.DODGE, ce=4, params={"hold": 2, "dodge": 0.3},
      desc="Sink into your own shadow. Holds 2 rounds."),
    A("shadow_clone", "Shadow Clone", kind=DEF, react=React.BLOCK, ce=5,
      params={"hold": 3, "block": 0.85, "cond": "in_garden"},
      desc="Inside Chimera Shadow Garden: a clone of shadow steps into the blow. Holds 3 rounds."),
    A("shadow_garden", "Domain Expansion: Chimera Shadow Garden", kind=DOMAIN, target=SELF, ce=40, min_level=6,
      requires=BOTH_ARMS, channel=1, effect="shadow_garden",
      desc="Incomplete: no sure-hit. While the shadows flood the field your shikigami cost nothing "
           "extra, arrive at once and strike first unanswered."),
)))

register(Technique("cursed_spirit_manipulation", "Cursed Spirit Manipulation",
                   desc="Swallow curses and command them.", actions=(
    A("cursed_swarm", "Cursed Swarm", power=11, ce=7, rng=RANGED, requires=ANY_ARM,
      channel=1, effect="cursed_swarm", tags=fs({"swarm"})),
    A("absorb", "Absorb Cursed Spirit", kind=UTIL, target=ANY, ce=5, requires=HEAD_REQ,
      effect="absorb", params={"ai": 60}),
    A("release_spirit", "Release Spirit", kind=SUMMON, target=CHOICE, ce=6,
      requires=ANY_ARM, effect="release_spirit"),
    A("maximum_uzumaki", "Maximum: Uzumaki", ce=30, rng=RANGED, requires=ANY_ARM,
      channel=1, can_chant=True, min_level=6, effect="uzumaki", params={"ai": 50, "all": True},
      tags=fs({"uzumaki"})),
    A("mini_uzumaki", "Mini Uzumaki", ce=12, rng=RANGED, requires=ANY_ARM,
      channel=1, min_level=10, effect="uzumaki", params={"ai": 28}, tags=fs({"uzumaki"})),
    A("spirit_shield", "Spirit Shield", kind=DEF, react=React.BLOCK,
      params={"block": 0.8, "cond": "has_spirits", "on_react": "spend_spirit"}),
)))

register(Technique("idle_transfiguration", "Idle Transfiguration", flags=("soul_body",),
                   desc="Mahito's soul manipulation.", actions=(
    A("soul_touch", "Idle Transfiguration", power=13, dtype=S, ce=10, requires=ANY_ARM,
      channel=1, tags=fs({"soul"}), desc="Reshapes the soul: ignores durability, lowers max HP."),
    A("body_repel", "Body Repel", power=13, ce=9, rng=RANGED, requires=TORSO_REQ, channel=1,
      tags=fs({"flesh"})),
    A("spawn_limb", "Grow Limb", kind=BUFF, target=CHOICE, effect="spawn_limb",
      params={"ai": 18}, desc="More cursed energy, stronger limb. Extra limbs extend reach."),
    A("transfigured_human", "Transfigured Human", kind=SUMMON, target=SELF, ce=8,
      requires=ANY_ARM, effect="transfigured_human"),
    A("soul_reshape", "Reshape Self", kind=HEAL, target=SELF, ce=16, effect="heal",
      params={"frac": 0.3, "limbs": 2, "cd": 3, "scar": True}),
    A("flesh_shift", "Flesh Shift", kind=DEF, react=React.DODGE, ce=4, params={"dodge": 0.2}),
    A("sep_domain", "Domain Expansion: Self-Embodiment of Perfection", kind=DOMAIN, target=SELF, ce=45,
      min_level=8, requires=HEAD_REQ, channel=1, effect="domain",
      params={"rounds": 2, "tick": "sep_tick", "name": "Self-Embodiment of Perfection"}),
    A("true_form", "Instant Spirit Body of Distorted Killing", kind=BUFF, target=SELF, ce=30, min_level=12,
      effect="true_form", params={"cond": "no_true_form", "ai": 40},
      desc="The soul's true shape: x1.8 durability, x1.5 strength, x1.2 speed for the rest of the fight."),
)))

register(Technique("blood_manipulation", "Blood Manipulation", desc="Death Painting blood arts.", actions=(
    A("piercing_blood", "Piercing Blood", power=25, ce=14, rng=RANGED, requires=BOTH_ARMS,
      channel=1, can_chant=True, tags=fs({"blood", "pierce"})),
    A("blood_edge", "Blood Edge", power=15, ce=6, requires=ANY_ARM, channel=1,
      tags=fs({"blood", "slash"}), statuses=((Status.BLEED, 0.35, 2, 3.0),)),
    A("flowing_red_scale", "Flowing Red Scale", kind=BUFF, target=SELF, ce=10,
      requires=TORSO_REQ, statuses=((Status.BOOST, 1.0, 4, 5.0),)),
    A("supernova", "Supernova", target=ALL, power=14, ce=18, rng=RANGED, requires=ANY_ARM,
      channel=1, min_level=6, tags=fs({"blood"})),
    A("rot", "Rot Technique: Decay", power=6, ce=10, rng=RANGED, requires=ANY_ARM, channel=1,
      min_level=4, statuses=((Status.POISON, 1.0, 4, 6.0),), tags=fs({"blood", "rot"})),
    A("blood_shield", "Blood Shield", kind=DEF, react=React.BLOCK, ce=6, params={"hold": 3, "block": 0.65}),
)))

register(Technique("heavenly_restriction", "Heavenly Restriction (Zero Cursed Energy)", tool="slaughter_demon",
                   copyable=False, flags=("hr_zero",),
                   stat_mods={Stat.MAX_CE: 0, Stat.CE_REGEN: 0, Stat.STR: 2.0, Stat.SPD: 1.7,
                              Stat.DUR: 1.5, Stat.PER: 1.5, Stat.MAX_STA: 1.8, Stat.MAX_HP: 1.3},
                   desc="No cursed energy at all; a body beyond human limits.", actions=(
    A("heavy_blow", "Heavy Blow", power=20, dtype=P, sta=9, requires=ANY_ARM, tags=fs({"blunt"})),
    A("flurry", "Flurry", power=9, dtype=P, sta=13, requires=BOTH_ARMS, effect="multi_hit",
      params={"hits": 3}, tags=fs({"blunt"})),
    A("reflex", "Heightened Reflexes", kind=DEF, react=React.DODGE, sta=5, requires=ANY_LEG,
      params={"dodge": 0.25}),
    A("iron_guard", "Iron Guard", kind=DEF, react=React.BLOCK, sta=5, requires=ANY_ARM,
      params={"block": 0.65}),
)))

register(Technique("puppet_manipulation", "Puppet Manipulation (Heavenly Restriction)",
                   copyable=False, flags=("hr_max",),
                   stat_mods={Stat.MAX_HP: 0.5, Stat.STR: 0.4, Stat.SPD: 0.4, Stat.DUR: 0.5,
                              Stat.MAX_CE: 2.0, Stat.CE_REGEN: 2.0, Stat.MAX_STA: 0.5},
                   desc="A frail body in a hideout; cursed energy that reaches across the country.",
                   actions=(
    A("deploy_puppet", "Deploy Puppet", kind=SUMMON, target=CHOICE, ce=15,
      effect="deploy_puppet", params={"remote_ok": True, "ai": 40}),
    A("emergency_shield", "Emergency Shield", kind=DEF, react=React.BLOCK, ce=8,
      params={"block": 0.6}),
)))

register(Technique("mythical_beast_amber", "Mythical Beast Amber", tool="conductor_staff", flags=("electric_ce",),
                   desc="Hajime Kashimo: electric cursed energy and a once-in-a-lifetime transformation.",
                   actions=(
    A("charged_strike", "Charged Strike", power=14, ce=6, sta=3, requires=ANY_ARM,
      tags=fs({"lightning", "blunt"}),
      desc="Any hit carrying your cursed energy shocks the target and leaves a charge on them."),
    A("lightning_discharge", "Lightning Discharge", power=18, ce=12, rng=RANGED, effect="discharge",
      tags=fs({"lightning"}), params={"ai": 48},
      desc="Spends the charge on a target: cannot miss, cannot be answered, hits the part you name."),
    A("static_guard", "Static Guard", kind=DEF, react=React.BLOCK, ce=4, requires=ANY_ARM,
      params={"hold": 2, "block": 0.55}),
    A("amber", "Mythical Beast Amber", kind=UTIL, target=SELF, ce=30, min_level=6, effect="amber",
      params={"cond": "no_amber"},
      desc="Extreme strength, speed, toughness and perception, plus new attacks. You die when the battle ends."),
    A("amber_soundwave", "Amber: Soundwave", target=ALL, power=20, ce=14, rng=RANGED,
      needs_status=Status.AMBER, statuses=((Status.STUN, 0.25, 1, 1.0),), tags=fs({"sound"})),
    A("amber_beam", "Amber: Electromagnetic Beam", power=34, ce=18, rng=RANGED, channel=1,
      can_chant=True, needs_status=Status.AMBER, tags=fs({"lightning", "em"})),
    A("amber_reflex", "Amber: Lightning Reflexes", kind=DEF, react=React.DODGE, sta=3,
      needs_status=Status.AMBER, params={"dodge": 0.3}),
)))

register(Technique("boogie_woogie", "Boogie Woogie",
                   desc="Aoi Todo: clap, and two things that hold cursed energy trade places.", actions=(
    A("boogie_woogie", "Boogie Woogie", kind=UTIL, target=Target.FREE, ce=6, requires=BOTH_ARMS,
      effect="boogie_woogie", params={"ai": 46},
      desc="Swap any two of: yourself, allies, enemies, imbued objects. Attacks already aimed at a "
           "place land on whoever is standing there now."),
    A("swap_strike", "Swap Strike", power=15, dtype=P, ce=6, sta=5, requires=BOTH_ARMS,
      effect="swap_strike", params={"reach": True}, tags=fs({"blunt"}),
      desc="Appear beside the target and hit before they can react. Reaches anywhere."),
    A("boogie_switch", "Boogie Woogie: Switch", kind=DEF, react=React.SWAP, ce=8, requires=BOTH_ARMS,
      params={"while_attacking": True},
      desc="When attacked, trade places with another enemy or an imbued object so it takes the hit."),
    A("brawler_guard", "Brawler's Guard", kind=DEF, react=React.BLOCK, sta=4, requires=ANY_ARM,
      params={"block": 0.6}),
)))

register(Technique("shrine", "Shrine", desc="Slashes that adjust to the target.", actions=(
    A("dismantle", "Dismantle", power=15, ce=8, rng=RANGED, requires=ANY_ARM, channel=1,
      tags=fs({"slash"})),
    A("cleave", "Cleave", power=10, ce=10, requires=ANY_ARM, channel=1, effect="cleave",
      tags=fs({"slash"}), desc="Scales with the target's toughness."),
    A("slash_parry", "Slash Parry", kind=DEF, react=React.COUNTER, ce=4, requires=ANY_ARM,
      params={"counter": 0.15}),
    A("shrine_domain", "Domain Expansion: Malevolent Shrine", kind=DOMAIN, target=SELF, ce=50, min_level=8,
      requires=BOTH_ARMS, channel=1, effect="domain",
      params={"rounds": 2, "tick": "shrine_tick", "name": "Malevolent Shrine", "open": True,
              "scope": "all", "objects": True},
      desc="No barrier, and nothing in range is spared: enemies, ALLIES and the battlefield itself are "
           "cut every round. Only you and your own shikigami are not."),
    A("spiderweb", "Spiderweb", target=ALL, power=16, ce=14, rng=RANGED, requires=ANY_ARM, channel=1,
      tags=fs({"slash"}), desc="A web of slashes through the ground under everyone."),
    A("fuga", "Divine Flame: Open", power=48, ce=40, rng=RANGED, requires=ANY_ARM, channel=1, can_chant=True,
      min_level=12, tags=fs({"fire"}), desc="The arrow of flame kept for what slashes cannot finish."),
    A("world_slash", "Dismantle: The Slash That Cuts the World", power=55, ce=45, rng=RANGED, requires=BOTH_ARMS,
      channel=1, min_level=18, effect="world_slash", params={"must_chant": True, "cond": "seen_mahoraga"},
      tags=fs({"slash"}),
      desc="Cuts space itself, so no technique's defence means anything to it. Always needs its incantation. "
           "It is learned by watching Mahoraga adapt to Infinity: a Shrine user who also holds Ten Shadows "
           "(Sukuna in a Ten Shadows vessel) gets it two rounds after the wheel finishes adapting to "
           "Limitless, and keeps it from then on."),
)))

register(Technique("disaster_flames", "Disaster Flames", desc="Volcanic cursed fire.", actions=(
    A("ember_insects", "Ember Insects", power=11, ce=8, rng=RANGED, requires=ANY_ARM,
      channel=1, statuses=((Status.BURN, 0.6, 3, 4.0),), tags=fs({"fire"})),
    A("eruption", "Eruption", power=17, ce=12, requires=ANY_ARM, channel=1,
      statuses=((Status.BURN, 0.4, 2, 4.0),), tags=fs({"fire"})),
    A("maximum_meteor", "Maximum: Meteor", target=ALL, power=24, ce=35, rng=RANGED,
      requires=BOTH_ARMS, channel=1, can_chant=True, min_level=8, tags=fs({"fire"})),
    A("flame_veil", "Flame Veil", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.55}),
    A("coffin_domain", "Domain Expansion: Coffin of the Iron Mountain", kind=DOMAIN, target=SELF, ce=45,
      min_level=8, requires=BOTH_ARMS, channel=1, effect="domain",
      params={"rounds": 2, "tick": "coffin_tick", "name": "Coffin of the Iron Mountain"}),
)))

# ======================================================================================
# Action pools for summons (not selectable as a player technique)
# ======================================================================================
# ---- more techniques from the source material -------------------------------------------------
register(Technique("limitless", "Limitless", flags=("six_eyes",),
                   desc="Satoru Gojo: infinity made real, afforded by the Six Eyes.", actions=(
    A("infinity", "Infinity", kind=BUFF, target=SELF, ce=14, min_level=4,
      statuses=((Status.INFINITY, 1.0, 3, 1.0),), params={"keep_up": True},
      desc="For 3 rounds nothing reaches you - except the owner of an open domain, a "
           "technique-cancelling tool or technique, or something that has adapted."),
    A("blue", "Cursed Technique Lapse: Blue", power=16, ce=12, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="blue", tags=fs({"attraction"}), desc="Drags the target out of cover or off high ground."),
    A("red", "Cursed Technique Reversal: Red", power=28, ce=22, rng=RANGED, requires=ANY_ARM, channel=1,
      min_level=8, tags=fs({"repulsion"})),
    A("hollow_purple", "Hollow Technique: Purple", power=80, ce=55, rng=RANGED, requires=BOTH_ARMS,
      channel=1, can_chant=True, min_level=12, tags=fs({"void"})),
    A("void_domain", "Domain Expansion: Unlimited Void", kind=DOMAIN, target=SELF, ce=60, min_level=10,
      requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 2, "tick": "void_tick", "name": "Unlimited Void", "scope": "all", "touch": True},
      desc="Everyone inside is flooded with everything at once and frozen - allies too, except "
           "whoever you are touching (one per free hand: you are asked as it opens)."),
    A("void_reinforced", "Unlimited Void: Reinforced Shell", kind=DOMAIN, target=SELF, ce=60, min_level=12,
      requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 2, "tick": "void_tick", "name": "Unlimited Void", "shell": "reinforced", "scope": "all",
              "touch": True},
      desc="The barrier's conditions swapped: nothing breaks it from outside, so an open domain gets no "
           "edge on it. Soft inside: it holds nobody in, and gives 10% to another closed barrier."),
    A("void_miniature", "Unlimited Void: Miniature Barrier", kind=DOMAIN, target=SELF, ce=80, min_level=20,
      requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 2, "tick": "void_tick", "name": "Unlimited Void", "shell": "miniature"},
      desc="Reinforced, and shrunk to the size of a ball: half again as hard to break in a clash. It closes "
           "around one enemy only - the owner of the domain it answers, else the strongest one there."),
)))

register(Technique("ratio", "Ratio Technique", tool="blunt_sword", desc="Kento Nanami: every target has a 7:3 point.", actions=(
    A("ratio_strike", "Ratio: 7:3", power=15, ce=9, requires=ANY_ARM, channel=1, effect="ratio_strike",
      tags=fs({"slash"}), desc="Forces a weak point: the target's durability counts for nothing."),
    A("collapse", "Ratio: Collapse", target=ALL, power=15, ce=22, requires=ANY_ARM, channel=1, min_level=6,
      effect="collapse", desc="The weak point is put into the surroundings. Hits everyone; levels cover."),
    A("overtime", "Binding Vow: Overtime", kind=BUFF, target=SELF, effect="overtime",
      params={"cond": "overtime_ready", "ai": 50},
      desc="From round 4: +40% output and strength for the rest of the fight."),
    A("measured_guard", "Measured Guard", kind=DEF, react=React.BLOCK, sta=4, requires=ANY_ARM,
      params={"block": 0.6}),
)))

register(Technique("cursed_speech", "Cursed Speech", desc="Toge Inumaki: words that must be obeyed.", actions=(
    A("speech_stop", "Cursed Speech: Don't Move", ce=10, rng=RANGED, requires=HEAD_REQ, effect="speech",
      params={"cmd": "stop", "strain": 6, "ai": 30}, tags=fs({"speech"}),
      desc="Cannot miss. The stronger the listener, the worse the backlash on your throat."),
    A("speech_blast", "Cursed Speech: Blast Away", power=22, ce=14, rng=RANGED, requires=HEAD_REQ,
      effect="speech", params={"cmd": "blast", "strain": 10}, tags=fs({"speech"})),
    A("speech_crush", "Cursed Speech: Get Crushed", power=34, ce=24, rng=RANGED, requires=HEAD_REQ,
      min_level=7, effect="speech", params={"cmd": "crush", "strain": 18}, tags=fs({"speech"})),
)))

register(Technique("straw_doll", "Straw Doll Technique", desc="Nobara Kugisaki: hammer, nails, effigy.", actions=(
    A("hairpin", "Hairpin", power=13, ce=7, rng=RANGED, requires=ANY_ARM, channel=1,
      statuses=((Status.NAILED, 1.0, 5, 1.0),), tags=fs({"nail"}), desc="Leaves a nail in the target."),
    A("hammer", "Hammer and Nail", power=14, dtype=P, ce=3, sta=5, requires=ANY_ARM,
      statuses=((Status.NAILED, 0.6, 5, 1.0),), tags=fs({"nail", "blunt"})),
    A("resonance", "Resonance", power=24, dtype=S, ce=14, rng=RANGED, requires=BOTH_ARMS,
      effect="resonance", params={"ai": 50}, tags=fs({"soul", "nail"}),
      desc="Strikes the soul through a nail in the target or a limb they have lost. Cannot miss."),
    A("effigy_slip", "Effigy Slip", kind=DEF, react=React.DODGE, ce=4, params={"dodge": 0.15}),
)))

register(Technique("projection_sorcery", "Projection Sorcery",
                   desc="Zen'in clan: one second cut into 24 frames.", actions=(
    A("frame_rush", "24 Frames", kind=BUFF, target=SELF, ce=10, effect="frame_rush", params={"ai": 20},
      desc="Each use adds a stack (4 at most): +3.5 speed and strength per stack, and all of them "
           "last 3 more rounds. Let them lapse and you start again from nothing."),
    A("frame_freeze", "Frame Freeze", power=12, dtype=P, ce=8, sta=4, requires=ANY_ARM,
      effect="frame_freeze", tags=fs({"blunt"}),
      desc="+2 power per stack. A touched target is frozen for a turn unless they match your speed "
           "or have the perception (14) to move by the rule. Miss, and your stacks are gone - with "
           "two or more, you freeze yourself."),
    A("frame_step", "Frame Step", kind=DEF, react=React.DODGE, ce=4, needs_status=Status.BOOST,
      params={"dodge": 0.3}),
    A("time_cell", "Domain Expansion: Time Cell Moon Palace", kind=DOMAIN, target=SELF, ce=45, min_level=12,
      requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 2, "tick": "time_cell_tick", "name": "Time Cell Moon Palace"},
      desc="The 24-frame rule applied to every cell of everyone inside: a sure-hit that freezes and tears."),
)))

register(Technique("construction", "Construction",
                   desc="Make matter out of cursed energy. A beginner manages a wall and one bullet; Yorozu "
                        "made liquid metal, living armor and a perfect sphere.", actions=(
    A("construct_wall", "Construction: Barricade", kind=UTIL, target=SELF, ce=18, requires=ANY_ARM,
      effect="construct_wall", params={"ai": 14, "cond": "no_cover"},
      desc="Build cover and get behind it."),
    A("construct_bullet", "Construction: Cursed Bullet", power=40, ce=38, rng=RANGED, requires=ANY_ARM,
      channel=1, params={"cd": 9999}, tags=fs({"bullet", "construct"}), desc="One per battle."),
    A("liquid_metal", "Construction: Liquid Metal", power=17, ce=7, rng=RANGED, requires=ANY_ARM, channel=1,
      min_level=6, tags=fs({"slash", "construct", "liquid"}),
      desc="Semi-autonomous metal on a low, steady supply of cursed energy; mid to long range. "
           "Reverse cursed energy (Round Deer) unravels it."),
    A("liquid_guard", "Liquid Metal: Autonomous Guard", kind=DEF, react=React.BLOCK, ce=3, min_level=6,
      params={"hold": 3, "block": 0.5, "while_attacking": True},
      desc="The metal moves by itself, so it guards even while you attack. Holds 3 rounds."),
    A("insect_armor", "Construction: Insect Armor", kind=DEF, react=React.BLOCK, ce=8, min_level=8,
      params={"hold": 4, "block": 0.7}, desc="Living armor. Holds 4 rounds, and powers Beetle Strike."),
    A("beetle_strike", "Insect Armor: Beetle Strike", power=28, ce=8, sta=5, requires=ANY_ARM, min_level=8,
      params={"cond": "armor_up"}, tags=fs({"blunt", "construct"}),
      desc="Only while Insect Armor is up: an insect's strength at a human's size."),
    A("true_sphere", "Construction: True Sphere", power=45, ce=40, rng=RANGED, requires=BOTH_ARMS, channel=1,
      min_level=12, effect="true_sphere", tags=fs({"sphere", "construct"}),
      desc="A perfect sphere touches at a single point: the pressure ignores durability."),
    A("threefold_affliction", "Domain Expansion: Threefold Affliction", kind=DOMAIN, target=SELF, ce=50,
      min_level=12, requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 4, "tick": "sphere_tick", "name": "Threefold Affliction"},
      desc="The True Sphere becomes a sure-hit. It takes shape, closes in, and on the third count it lands "
           "- unless something already adapted to Construction is there to break it."),
)))

register(Technique("granite_blast", "Granite Blast", stat_mods={Stat.OUT: 1.35},
                   desc="Ryu Ishigori: the highest cursed energy output there is.", actions=(
    A("granite_blast", "Granite Blast", power=30, ce=20, rng=RANGED, requires=ANY_ARM, channel=1,
      can_chant=True, tags=fs({"blast"})),
    A("energy_discharge", "Cursed Energy Discharge", target=ALL, power=14, ce=16, rng=RANGED, channel=1,
      tags=fs({"blast"})),
    A("dense_guard", "Dense Energy Guard", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.6}),
)))

register(Technique("ice_formation", "Ice Formation", desc="Uraume: cursed energy that freezes.", actions=(
    A("frost_calm", "Frost Calm", target=ALL, power=8, ce=16, rng=RANGED, channel=1,
      statuses=((Status.SLOW, 1.0, 3, 5.0), (Status.STUN, 0.2, 1, 1.0)), tags=fs({"ice"})),
    A("icefall", "Icefall", power=20, ce=12, rng=RANGED, requires=ANY_ARM, channel=1, tags=fs({"ice"})),
    A("ice_wall", "Ice Wall", kind=DEF, react=React.BLOCK, ce=6, params={"hold": 2, "block": 0.7}),
)))

register(Technique("jacobs_ladder", "Jacob's Ladder", flags=("winged",),
                   desc="Angel: a technique that extinguishes other techniques.", actions=(
    A("extinguish", "Extinguishing Light", power=14, ce=9, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="extinguish", tags=fs({"light"}),
      desc="Ignores technique defences and strips technique effects from the target."),
    A("jacobs_ladder", "Jacob's Ladder", power=38, ce=40, rng=RANGED, requires=BOTH_ARMS, channel=1,
      min_level=8, effect="extinguish", params={"must_chant": True, "seal": 3, "purge": 2.0}, tags=fs({"light"}),
      desc="Always needs its incantation. Seals the target's technique; double against cursed "
           "spirits and reincarnated sorcerers."),
    A("wing_fold", "Wings", kind=DEF, react=React.DODGE, sta=3, params={"dodge": 0.2}),
)))

register(Technique("disaster_plants", "Disaster Plants", stat_mods={Stat.DUR: 1.4},
                   desc="Hanami: the forest's grudge, in a body like ironwood.", actions=(
    A("wooden_ball", "Wooden Ball", power=19, ce=8, rng=RANGED, channel=1, tags=fs({"wood"})),
    A("root_spears", "Root Spears", power=25, ce=11, channel=1, statuses=((Status.BLEED, 0.3, 2, 3.0),),
      tags=fs({"wood"})),
    A("cursed_bud", "Cursed Bud", power=6, ce=10, rng=RANGED, channel=1,
      statuses=((Status.BUD, 1.0, 4, 8.0),), tags=fs({"wood"}),
      desc="A bud takes root and drinks 8 cursed energy a round."),
    A("flower_field", "Flower Field", kind=UTIL, target=SELF, ce=12, effect="flower_field",
      params={"ai": 22}, desc="Every enemy loses the will to hurry: slowed for 3 rounds."),
    A("bark_skin", "Bark Skin", kind=DEF, react=React.BLOCK, ce=4, params={"hold": 3, "block": 0.65}),
)))

register(Technique("disaster_tides", "Disaster Tides", desc="Dagon: the sea's grudge.", actions=(
    A("water_surge", "Water Surge", power=17, ce=10, rng=RANGED, channel=1, tags=fs({"water"})),
    A("death_swarm", "Death Swarm", target=ALL, power=11, ce=15, rng=RANGED, channel=1,
      statuses=((Status.BLEED, 0.3, 2, 3.0),), tags=fs({"swarm"})),
    A("water_veil", "Water Veil", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.6}),
    A("tides_domain", "Domain Expansion: Horizon of the Captivating Skandha", kind=DOMAIN, target=SELF, ce=45,
      min_level=8, channel=1, effect="domain",
      params={"rounds": 3, "tick": "skandha_tick", "name": "Horizon of the Captivating Skandha"}),
)))

register(Technique("shikigami_pool", "Shikigami Arts", innate=False, copyable=False, actions=(
    A("bite", "Bite", power=12, dtype=P, sta=3, tags=fs({"fang"})),
    A("thunder_dive", "Thunder Dive", power=14, ce=5, rng=RANGED,
      statuses=((Status.STUN, 0.25, 1, 1.0),), tags=fs({"lightning"})),
    A("constrict", "Constrict", power=13, dtype=P, sta=4,
      statuses=((Status.SLOW, 0.7, 2, 4.0),), tags=fs({"bind"})),
    A("tongue_bind", "Tongue Bind", power=6, dtype=P, sta=3, rng=RANGED,
      statuses=((Status.SLOW, 0.8, 2, 5.0),), tags=fs({"bind"})),
    A("water_torrent", "Water Torrent", target=ALL, power=17, ce=12, rng=RANGED,
      tags=fs({"water"})),
    A("swarm", "Rabbit Swarm", power=5, dtype=P, sta=2,
      statuses=((Status.SLOW, 0.9, 2, 6.0),), tags=fs({"swarm"})),
    A("deer_heal", "Reverse Energy Aura", kind=HEAL, target=SELF, ce=10, effect="aura_heal",
      params={"frac": 0.2, "cd": 2}),
    A("ox_charge", "Ox Charge", power=18, dtype=P, sta=8, acc=-0.1, effect="ox_charge", tags=fs({"blunt"}),
      desc="A straight line only, and stronger the longer the run: +10 power for every round since it "
           "was summoned or last charged (up to +30)."),
    A("rend", "Rend", power=17, dtype=P, sta=5, statuses=((Status.BLEED, 0.5, 2, 4.0),),
      tags=fs({"slash"})),
    A("funeral_hold", "Funeral Hold", power=8, dtype=P, sta=4, effect="funeral_hold", tags=fs({"fear"}),
      desc="Keeps hold of a victim frozen with dread so the paralysis does not lift."),
    A("sword_of_extermination", "Sword of Extermination", power=26, dtype=P, sta=6,
      tags=fs({"slash", "positive"})),
    A("rika_claw", "Rika's Claw", power=19, dtype=P, sta=4, tags=fs({"slash"})),
    A("rika_beam", "Rika's Cursed Blast", power=24, ce=20, rng=RANGED, channel=1,
      tags=fs({"blast"})),
    A("sword_option", "Sword Option", power=16, dtype=P, sta=5, tags=fs({"slash"})),
    A("ultra_cannon", "Ultra Cannon", power=28, ce=22, rng=RANGED, channel=1, can_chant=True,
      tags=fs({"blast"})),
    A("ultra_shield", "Ultra Shield", kind=DEF, react=React.BLOCK, sta=4, params={"hold": 2, "block": 0.7}),
    A("flail", "Flail", power=9, dtype=P, sta=3, tags=fs({"blunt"})),
    A("elephant_drop", "Elephant Drop", power=24, dtype=P, sta=8, acc=-0.05, effect="elephant_drop", params={"cd": 9999},
      statuses=((Status.STUN, 0.35, 1, 1.0),), tags=fs({"blunt", "crush"}),
      desc="Summoned overhead and simply let fall: it shatters whatever guard the target had set. "
           "Once each time it is summoned."),
    A("garuda_kick", "Garuda's Lash", power=24, dtype=P, sta=4, tags=fs({"blunt"})),
    A("jelly_sting", "Sting", power=8, dtype=P, sta=2, statuses=((Status.POISON, 0.8, 3, 4.0),), tags=fs({"poison"})),
    A("doll_strike", "Doll Strike", power=13, dtype=P, sta=3, tags=fs({"blunt"})),
)))

# ======================================================================================
# The rest of the canon special-grade fights
# ======================================================================================
register(Technique("star_rage", "Star Rage", stat_mods={Stat.STR: 1.8},
                   desc="Yuki Tsukumo: virtual mass, as much as she likes.", actions=(
    A("mass_strike", "Star Rage: Mass Strike", power=30, dtype=P, ce=10, sta=6, requires=ANY_ARM,
      tags=fs({"blunt", "mass"}), desc="A fist with the weight of a mountain behind it."),
    A("virtual_mass", "Virtual Mass", kind=BUFF, target=SELF, ce=12, statuses=((Status.BOOST, 1.0, 4, 10.0),)),
    A("garuda", "Summon Garuda", kind=SUMMON, target=SELF, ce=18, channel=1, effect="summon_garuda",
      params={"cond": "no_garuda"}, desc="A shikigami that carries her mass too."),
    A("mass_guard", "Mass Guard", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.7}),
    A("black_hole", "Star Rage: Black Hole", target=ALL, power=90, ce=60, rng=RANGED, channel=1, min_level=12,
      effect="black_hole", params={"ai": 0}, tags=fs({"mass"}),
      desc="All the mass at once. It takes everyone near - and her."),
)))

register(Technique("sky_manipulation", "Sky Manipulation", desc="Takako Uro: the sky is a surface she can hold.", actions=(
    A("thin_ice_breaker", "Thin Ice Breaker", power=26, ce=12, requires=ANY_ARM, channel=1, effect="unanswerable",
      tags=fs({"space"}), desc="Shatters the space the target stands in: it cannot be blocked, countered or dodged by reaction."),
    A("sky_grab", "Sky Grab", power=16, ce=8, rng=RANGED, requires=ANY_ARM, channel=1, effect="blue",
      tags=fs({"space"}), desc="Pulls the target out of cover or off high ground."),
    A("sky_fold", "Fold the Sky", kind=DEF, react=React.COUNTER, ce=6, requires=ANY_ARM,
      params={"hold": 2, "counter": 0.3, "while_attacking": True},
      desc="Bends an attack's path back along itself - even while she is attacking."),
    A("sky_domain", "Domain Expansion: Sky Manipulation", kind=DOMAIN, target=SELF, ce=45, min_level=8,
      requires=BOTH_ARMS, channel=1, effect="domain", params={"rounds": 2, "tick": "sky_tick", "name": "Uro's domain"}),
)))

register(Technique("antigravity_system", "Anti-Gravity System", desc="Kaori Itadori's technique, in Kenjaku's keeping.",
                   actions=(
    A("anti_gravity", "Anti-Gravity System", target=ALL, power=16, ce=16, rng=RANGED, channel=1,
      statuses=((Status.STUN, 0.35, 1, 1.0),), tags=fs({"gravity"}), desc="Everything nearby falls upward, then down."),
    A("gravity_press", "Gravity", power=22, ce=12, rng=RANGED, requires=ANY_ARM, channel=1,
      statuses=((Status.SLOW, 0.8, 2, 5.0),), tags=fs({"gravity"})),
    A("gravity_guard", "Gravity Well", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.6}),
    A("womb_profusion", "Domain Expansion: Womb Profusion", kind=DOMAIN, target=SELF, ce=50, min_level=10,
      requires=ANY_ARM, channel=1, effect="domain",
      params={"rounds": 3, "tick": "womb_tick", "name": "Womb Profusion", "open": True}),
)))

register(Technique("festering_life", "Festering Life", desc="Kurourushi: a plague of cockroaches with a blade.", actions=(
    A("roach_swarm", "Cockroach Swarm", target=ALL, power=13, ce=12, rng=RANGED, channel=1,
      statuses=((Status.BLEED, 0.5, 2, 4.0),), tags=fs({"swarm"})),
    A("festering_blade", "Festering Life Sword", power=24, ce=10, channel=1,
      statuses=((Status.POISON, 0.8, 4, 6.0),), tags=fs({"slash"}), desc="Lays eggs in the wound."),
    A("devour", "Devour", kind=HEAL, target=SELF, ce=10, effect="heal", params={"frac": 0.25, "cd": 3}),
    A("swarm_body", "Scatter", kind=DEF, react=React.DODGE, ce=4, params={"hold": 2, "dodge": 0.3}),
)))
register(Technique("pestilence", "Pestilence", desc="The Smallpox Deity: a coffin, a grave, and a count of three.", actions=(
    A("plague_touch", "Plague Touch", power=12, ce=8, channel=1, statuses=((Status.POISON, 1.0, 4, 7.0),),
      tags=fs({"disease"})),
    A("grave_domain", "Domain Expansion: Graveyard Domain", kind=DOMAIN, target=SELF, ce=45, min_level=8, channel=1,
      effect="domain", params={"rounds": 3, "tick": "grave_tick", "name": "Graveyard Domain"},
      desc="Everyone is shut in a coffin (stunned). Still inside on the third count: the disease takes hold."),
    A("miasma", "Miasma", kind=DEF, react=React.BLOCK, ce=4, params={"hold": 2, "block": 0.5}),
)))
register(Technique("shikigami_territory", "Shikigami Territory",
                   desc="Dhruv Lakdawalla: wherever his shikigami have passed becomes his domain.", actions=(
    A("trail_shikigami", "Trail Shikigami", kind=SUMMON, target=SELF, ce=12, channel=1, effect="summon_trail",
      desc="Two at most. Each one alive widens the territory every round (up to 6)."),
    A("territory_strike", "Territory Strike", power=12, ce=9, rng=RANGED, channel=1, effect="territory_strike",
      desc="+5 power for every point of territory."),
    A("territory_guard", "Territory Guard", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.6}),
)))
register(Technique("hakuna_laana", "Hakuna Laana", tool="black_rope", stat_mods={Stat.STR: 1.3, Stat.SPD: 1.2},
                   desc="Miguel: rhythm in the body, and a rope woven over decades.", actions=(
    A("rhythm", "Rhythm", kind=BUFF, target=SELF, ce=8, statuses=((Status.BOOST, 1.0, 4, 6.0),)),
    A("offbeat", "Off-Beat Strike", power=16, dtype=P, ce=5, sta=5, requires=ANY_ARM, effect="offbeat",
      tags=fs({"blunt"}), desc="Breaks the target's rhythm: ends their boost and slows them."),
    A("sway", "Sway", kind=DEF, react=React.DODGE, sta=4, params={"hold": 2, "dodge": 0.25}),
)))
register(Technique("sword_saint", "Sword Saint", stat_mods={Stat.STR: 1.2, Stat.SPD: 1.2, Stat.PER: 1.3},
                   desc="Daido Hagane: no technique worth the name. Give him a blade.", actions=(
    A("iai", "Iai", power=20, dtype=P, sta=7, requires=ANY_ARM, effect="iai", params={"cond": "has_weapon"},
      tags=fs({"slash"}), desc="A weapon strike with 20 power behind it instead of 5."),
    A("sword_counter", "Sen no Sen", kind=DEF, react=React.COUNTER, sta=5, requires=ANY_ARM,
      params={"hold": 2, "counter": 0.3}),
)))
register(Technique("heart_catch", "Heart Catch", desc="Larue: takes hold of a heart, and the body follows.", actions=(
    A("heart_catch", "Heart Catch", ce=10, rng=RANGED, requires=ANY_ARM, effect="heart_catch", params={"ai": 30},
      speed=3.0, desc="Cannot miss. Stuns for a round; someone two grades above you only loses their defence."),
    A("heart_grip", "Grip", power=14, ce=6, rng=RANGED, requires=ANY_ARM, channel=1),
    A("heart_guard", "Guard", kind=DEF, react=React.BLOCK, ce=4, params={"block": 0.5}),
)))
register(Technique("g_warstaff", "G Warstaff", desc="Charles Bernard: draws the future in his opponent's blood.", actions=(
    A("g_pen", "G-Pen Thrust", power=13, ce=5, requires=ANY_ARM, effect="g_pen", tags=fs({"pierce"}),
      desc="A hit that draws blood is ink."),
    A("future_sight", "Next Panel", kind=DEF, react=React.DODGE, ce=4,
      params={"hold": 3, "dodge": 0.45, "cond": "has_ink"}, desc="With ink: read what comes next. Holds 3 rounds."),
)))
register(Technique("transport", "Spatial Transport", desc="Ui Ui: here, and then there.", actions=(
    A("evacuate", "Evacuate", kind=UTIL, target=ANY, ce=12, effect="evacuate", params={"ai": 0},
      desc="Take yourself or an ally out of the fight. A closed domain still holds you."),
    A("blink_strike", "Blink Strike", power=12, dtype=P, ce=5, sta=4, requires=ANY_ARM, params={"reach": True},
      tags=fs({"blunt"})),
    A("blink", "Blink", kind=DEF, react=React.DODGE, ce=4, params={"hold": 2, "dodge": 0.3}),
)))
register(Technique("clone_technique", "Clone Technique", desc="Bayer: up to four of him, and only one is real.", actions=(
    A("split", "Split", kind=SUMMON, target=SELF, ce=8, effect="make_clone"),
    A("gang_up", "Gang Up", power=8, dtype=P, ce=4, sta=4, requires=ANY_ARM, effect="gang_up", tags=fs({"blunt"}),
      desc="+4 power for every clone standing."),
    A("clone_decoy", "Which One?", kind=DEF, react=React.DODGE, ce=3, params={"dodge": 0.2}),
)))
register(Technique("sumo", "Sumo", stat_mods={Stat.STR: 1.3, Stat.MAX_HP: 1.2},
                   desc="Rokujushi Miyo: a ring, and nothing in it but sumo.", actions=(
    A("tachiai", "Tachiai", power=18, dtype=P, ce=3, sta=7, statuses=((Status.STUN, 0.3, 1, 1.0),), tags=fs({"blunt"})),
    A("dohyo", "Dohyo", kind=UTIL, ce=12, effect="dohyo", params={"ai": 32},
      desc="Draws a ring around one opponent: their technique is sealed for 2 rounds."),
    A("shiko", "Shiko", kind=BUFF, target=SELF, ce=5, statuses=((Status.BOOST, 1.0, 3, 5.0),)),
    A("oshi", "Oshi", kind=DEF, react=React.BLOCK, sta=4, params={"block": 0.6}),
)))

# ======================================================================================
# Lower-grade techniques: what most sorcerers actually awaken with
# ======================================================================================
register(Technique("black_bird", "Black Bird Manipulation", desc="Mei Mei: crows that see for her, and die for her.", actions=(
    A("bird_strike", "Bird Strike", power=60, ce=12, rng=RANGED, channel=1, effect="bird_strike",
      params={"cond": "has_crows", "ai": 55}, speed=2.0,
      desc="A crow gives its life as a binding vow. Two crows a fight."),
    A("crow_sight", "Shared Sight", kind=BUFF, target=SELF, ce=6, effect="crow_sight", params={"cond": "no_sight"},
      desc="+5 perception for the fight."),
    A("crow_screen", "Crow Screen", kind=DEF, react=React.DODGE, ce=3, params={"dodge": 0.15}),
)))
register(Technique("contractual_recreation", "Contractual Re-creation",
                   desc="Reggie Star: receipts made real. Every recreation burns a receipt (5 + level/2 a "
                        "fight), and water ruins them.", actions=(
    A("recreate_car", "Receipt: Vehicle", power=30, dtype=P, ce=14, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="receipt", params={"cond": "has_receipts", "tons": 2}, tags=fs({"blunt"}),
      desc="Against an open Chimera Shadow Garden it is sunk into the shadow instead: weight its owner must carry."),
    A("recreate_house", "Receipt: House", power=46, dtype=P, ce=28, rng=RANGED, requires=ANY_ARM, channel=1,
      min_level=8, activation=0.7, effect="receipt", params={"cond": "has_receipts", "tons": 4}, tags=fs({"blunt"})),
    A("knife_volley", "Receipt: Knives", power=14, ce=7, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="receipt", params={"cond": "has_receipts"}, tags=fs({"slash"}), speed=1.5),
    A("receipt_net", "Receipt: Fishing Net", power=4, dtype=P, ce=6, rng=RANGED, requires=ANY_ARM, channel=1,
      effect="receipt", params={"cond": "has_receipts"}, statuses=((Status.SLOW, 1.0, 3, 7.0),), tags=fs({"bind"})),
    A("receipt_heal", "Receipt: Five-Star Inn", kind=HEAL, target=SELF, ce=12, effect="receipt",
      params={"frac": 0.25, "cd": 3, "cond": "has_receipts"}),
    A("recreated_wall", "Receipt: Wall", kind=DEF, react=React.BLOCK, ce=6,
      params={"hold": 2, "block": 0.65, "cond": "has_receipts", "on_react": "spend_receipt"}),
)))
register(Technique("cursed_chords", "Cursed Chords", desc="Yoshinobu Gakuganji: amplified sound as a weapon.", actions=(
    A("power_chord", "Power Chord", power=18, ce=9, rng=RANGED, requires=BOTH_ARMS, channel=1, tags=fs({"sound"}), speed=3.0),
    A("feedback", "Feedback", target=ALL, power=12, ce=14, rng=RANGED, requires=BOTH_ARMS, channel=1,
      statuses=((Status.STUN, 0.15, 1, 1.0),), tags=fs({"sound"}), speed=3.0),
    A("sound_wall", "Wall of Sound", kind=DEF, react=React.BLOCK, ce=5, params={"hold": 2, "block": 0.6}),
)))
register(Technique("blazing_courage", "Blazing Courage", desc="Ogi Zen'in: a blade wrapped in flame.", actions=(
    A("flame_blade", "Flame Blade", power=20, ce=9, requires=ANY_ARM, channel=1,
      statuses=((Status.BURN, 0.5, 3, 4.0),), tags=fs({"fire", "slash"})),
    A("fire_scales", "Fire Scales", target=ALL, power=12, ce=14, rng=RANGED, channel=1,
      statuses=((Status.BURN, 0.4, 2, 4.0),), tags=fs({"fire"})),
    A("ember_parry", "Ember Parry", kind=DEF, react=React.BLOCK, ce=5, requires=ANY_ARM, params={"block": 0.6}),
)))
register(Technique("corpse_creation", "Cursed Corpse Creation", desc="Masamichi Yaga: dolls with cores of their own.", actions=(
    A("create_corpse", "Animate Cursed Corpse", kind=SUMMON, target=SELF, ce=14, requires=ANY_ARM, channel=1,
      effect="create_corpse", desc="Each doll carries its own cursed energy. Three at most."),
    A("doll_rush", "Doll Rush", power=12, ce=8, rng=RANGED, channel=1, tags=fs({"blunt"})),
    A("doll_guard", "Stuffed Guard", kind=DEF, react=React.BLOCK, ce=4, params={"block": 0.55}),
)))
register(Technique("solo_forbidden_area", "Solo Forbidden Area", desc="Utahime Iori: a ritual that amplifies everyone on her side.",
                   actions=(
    A("ritual_dance", "Ritual Dance", kind=UTIL, target=SELF, ce=20, channel=1, effect="forbidden_area",
      params={"must_chant": True, "cond": "no_ritual", "ai": 45},
      desc="Song and dance, so it lands next round: +40% cursed energy output for every ally, for the fight."),
    A("ofuda", "Warding Tag", power=10, ce=6, rng=RANGED, requires=ANY_ARM, channel=1, tags=fs({"seal"})),
    A("ritual_ward", "Ritual Ward", kind=DEF, react=React.BLOCK, ce=4, params={"block": 0.5}),
)))
register(Technique("paralyzing_gaze", "Paralyzing Gaze", desc="Ranta Zen'in: an eye that holds what it looks at.", actions=(
    A("gaze", "Paralyzing Gaze", ce=10, rng=RANGED, requires=HEAD_REQ, effect="gaze", params={"ai": 28}, speed=3.0,
      desc="Cannot miss. Holding someone stronger than you damages the eye."),
    A("clan_blade", "Clan Blade", power=12, ce=4, requires=ANY_ARM, tags=fs({"slash"})),
    A("averted", "Avert", kind=DEF, react=React.DODGE, ce=3, params={"dodge": 0.1}),
)))
register(Technique("tool_manipulation", "Tool Manipulation", flags=("winged",),
                   desc="Momo Nishimiya: a broom to ride and wind to throw.", actions=(
    A("wind_scythe", "Wind Scythe", power=13, ce=7, rng=RANGED, requires=ANY_ARM, channel=1, tags=fs({"wind", "slash"}),
      speed=1.5),
    A("broom_ram", "Broom Ram", power=12, dtype=P, ce=3, sta=5, tags=fs({"blunt"})),
    A("aerial_evasion", "Aerial Evasion", kind=DEF, react=React.DODGE, sta=3, params={"dodge": 0.2}),
)))
register(Technique("abrupt_mutation", "Abrupt Mutation (Three Cores)", flags=("cores",),
                   desc="Panda: a cursed corpse with three cores. Two can be lost.", actions=(
    A("drumming_beat", "Gorilla Mode: Drumming Beat", power=20, dtype=P, ce=8, sta=6, requires=ANY_ARM, min_level=4,
      effect="unanswerable", tags=fs({"blunt"}), desc="The impact goes through a guard."),
    A("core_shift", "Core Shift", kind=BUFF, target=SELF, ce=6, statuses=((Status.BOOST, 1.0, 3, 5.0),)),
    A("panda_guard", "Padded Guard", kind=DEF, react=React.BLOCK, sta=4, requires=ANY_ARM, params={"block": 0.6}),
)))
register(Technique("explosive_flesh", "Explosive Flesh", desc="Iori Hazenoki: teeth and eyes that go off like grenades.",
                   actions=(
    A("tooth_bomb", "Tooth Bomb", power=16, ce=6, rng=RANGED, requires=HEAD_REQ, channel=1, effect="flesh_bomb",
      params={"price": 3}, tags=fs({"blast"}),
      desc="Costs you 3 HP from the head; the teeth grow back at the start of the next round for 15 cursed energy."),
    A("eye_bomb", "Eye Bomb", power=32, ce=10, rng=RANGED, requires=HEAD_REQ, channel=1, min_level=5,
      effect="flesh_bomb", params={"price": 12}, tags=fs({"blast"}),
      desc="Costs you 12 HP from the head; the eye grows back at the start of the next round for 60 cursed energy."),
    A("blast_step", "Blast Step", kind=DEF, react=React.DODGE, ce=3, params={"dodge": 0.15}),
)))
register(Technique("seance", "Seance Technique", desc="Granny Ogami: a dead fighter's body, worn for a while.", actions=(
    A("seance", "Seance", kind=UTIL, target=CORPSE, ce=15, requires=HEAD_REQ, effect="seance", params={"ai": 50},
      desc="Take on the strength, speed and durability of a corpse for the rest of the fight."),
    A("spirit_bullet", "Spirit Bullet", power=16, ce=6, rng=RANGED, requires=ANY_ARM, channel=1),
    A("beads_guard", "Prayer Beads", kind=DEF, react=React.BLOCK, ce=4, params={"block": 0.5}),
)))
register(Technique("inverse", "Inverse", flags=("inverse",),
                   desc="Jiro Awasaka: strong blows land weak on him, weak blows land strong.", actions=(
    A("inverse_palm", "Inverse Palm", power=18, ce=8, requires=ANY_ARM, channel=1),
    A("inverse_guard", "Brace", kind=DEF, react=React.BLOCK, sta=4, params={"block": 0.5}),
)))
register(Technique("auspicious_beasts", "Auspicious Beasts Summon", desc="Takuma Ino: four beasts called through a mask.",
                   actions=(
    A("kaichi", "Kaichi", power=15, ce=8, rng=RANGED, channel=1, acc=0.2, desc="A horn that follows its target."),
    A("reiki", "Reiki", kind=BUFF, target=SELF, ce=6, statuses=((Status.BOOST, 1.0, 3, 4.0),)),
    A("kirin", "Kirin", kind=HEAL, target=SELF, ce=10, effect="heal", params={"frac": 0.2, "cd": 3}),
    A("ryu", "Ryu", power=26, ce=16, rng=RANGED, channel=1, min_level=6),
    A("mask_step", "Sidestep", kind=DEF, react=React.DODGE, sta=3, params={"dodge": 0.15}),
)))
register(Technique("love_rendezvous", "Love Rendezvous", desc="Kirara Hoshi: stars that decide who may approach whom.",
                   actions=(
    A("southern_cross", "Southern Cross", ce=10, rng=RANGED, channel=1,
      statuses=((Status.SLOW, 1.0, 3, 6.0), (Status.STUN, 0.3, 1, 1.0)), power=4, tags=fs({"star"})),
    A("star_shot", "Star Shot", power=12, ce=7, rng=RANGED, channel=1, tags=fs({"star"})),
    A("star_repel", "Repel", kind=DEF, react=React.DODGE, ce=4, params={"hold": 2, "dodge": 0.3}),
)))
register(Technique("moon_dregs", "Moon Dregs", desc="Junpei Yoshino: a jellyfish shikigami full of poison.", actions=(
    A("summon_jellyfish", "Summon Moon Dregs", kind=SUMMON, target=SELF, ce=40, channel=1, effect="summon_jellyfish",
      params={"cond": "no_jellyfish"},
      desc="The jellyfish is made of your cursed energy and lives on it: 40 to form it, and while it is out "
           "your cursed energy does not come back. So how many you can form in a fight is how much you have, "
           "and its body is 10 HP plus 40% of your maximum cursed energy. One at a time."),
    A("poison_tentacle", "Poison Tentacle", power=8, ce=6, rng=RANGED, channel=1,
      statuses=((Status.POISON, 0.8, 3, 4.0),), tags=fs({"poison"})),
    A("jelly_shield", "Jelly Shield", kind=DEF, react=React.BLOCK, ce=4, params={"block": 0.5}),
)))
register(Technique("new_shadow_style", "New Shadow Style", desc="A school, not a birthright: the sword, and a simple domain.",
                   actions=(
    A("batto", "Batto: Evening Moon Draw", power=16, ce=4, sta=6, requires=ANY_ARM, acc=0.1, tags=fs({"slash"})),
    A("batto_counter", "Simple Domain: Auto-Counter", kind=DEF, react=React.COUNTER, ce=4, requires=ANY_ARM,
      params={"hold": 2, "counter": 0.25}),
)))
register(Technique("miracles", "Miracles", flags=("miracles",),
                   desc="Haruta Shigemo: small miracles saved up, spent when he should have died. Two a fight.", actions=(
    A("lucky_strike", "Lucky Strike", power=12, ce=4, requires=ANY_ARM),
    A("fluke", "Fluke", kind=DEF, react=React.DODGE, ce=3, params={"dodge": 0.25}),
)))
register(Technique("divergent_fist", "Divergent Fist", stat_mods={Stat.STR: 1.3, Stat.SPD: 1.2},
                   desc="No technique at all: a body out of proportion and a punch that lands twice.", actions=(
    A("divergent_fist", "Divergent Fist", power=11, ce=5, sta=4, requires=ANY_ARM, effect="multi_hit",
      params={"hits": 2}, tags=fs({"blunt"})),
    A("manji_kick", "Manji Kick", power=14, dtype=P, ce=3, sta=6, requires=ANY_LEG, tags=fs({"blunt"})),
    A("reflexes", "Superhuman Reflexes", kind=DEF, react=React.DODGE, sta=4, requires=ANY_LEG, params={"dodge": 0.2}),
)))
register(Technique("hair_manipulation", "Hair Manipulation", desc="Remi: hair wound into a scorpion's tail.", actions=(
    A("scorpion_hair", "Scorpion Hair", power=10, ce=4, tags=fs({"pierce"})),
    A("hair_bind", "Hair Bind", power=5, ce=5, rng=RANGED, channel=1, statuses=((Status.SLOW, 0.7, 2, 4.0),)),
    A("hair_veil", "Hair Veil", kind=DEF, react=React.BLOCK, ce=3, params={"block": 0.45}),
)))
register(Technique("sugar_craft", "Sugar Manipulation", desc="Rin Amai: spun sugar, harder than it sounds.", actions=(
    A("sugar_shards", "Sugar Shards", power=8, ce=4, rng=RANGED, channel=1),
    A("candy_shell", "Candy Shell", kind=DEF, react=React.BLOCK, ce=3, params={"block": 0.45}),
)))


@dataclass(frozen=True)
class ShikigamiDef:
    key: str
    name: str
    hp: float
    str_: float
    spd: float
    dur: float
    per: float
    cost: int
    traits: tuple = ()
    actions: tuple = ()


SHIKIGAMI = {s.key: s for s in (
    ShikigamiDef("divine_dogs", "Divine Dogs", 60, 12, 14, 6, 12, 6, ("tracker",), ("bite",)),
    ShikigamiDef("nue", "Nue", 50, 10, 16, 5, 9, 8, ("flight", "lightning"), ("thunder_dive",)),
    ShikigamiDef("great_serpent", "Great Serpent", 70, 14, 9, 8, 7, 9, ("bind",), ("constrict", "bite")),
    ShikigamiDef("toad", "Toad", 40, 7, 9, 6, 7, 5, ("tongue",), ("tongue_bind",)),
    ShikigamiDef("max_elephant", "Max Elephant", 110, 16, 5, 12, 6, 16, ("water",), ("elephant_drop", "water_torrent", "flail")),
    ShikigamiDef("rabbit_escape", "Rabbit Escape", 25, 4, 15, 2, 6, 4, ("swarm",), ("swarm",)),
    ShikigamiDef("round_deer", "Round Deer", 80, 9, 10, 9, 9, 12, ("rct",), ("deer_heal", "flail")),
    ShikigamiDef("piercing_ox", "Piercing Ox", 90, 18, 11, 10, 6, 12, ("charge",), ("ox_charge",)),
    # Its technique was never shown in the source; this one is built from fan ideas: it cannot be
    # seen, touching it paralyses with dread, and other shikigami arrive unannounced beside it.
    ShikigamiDef("tiger_funeral", "Tiger Funeral", 85, 17, 13, 9, 9, 12, ("unseen", "fear"),
                 ("rend", "funeral_hold")),
    ShikigamiDef("mahoraga", "Eight-Handled Sword Divergent Sila Divine General Mahoraga",
                 320, 30, 16, 20, 14, 40, ("adapt", "positive_blade"), ("sword_of_extermination", "flail")),
)}
SHIKI_ORDER = list(SHIKIGAMI)
MERGE_NAMES = {frozenset(("nue", "toad")): "Well's Unknown Abyss",
               frozenset(("nue", "great_serpent")): "Merged Beast Agito"}


# ======================================================================================
# Order of resolution.  activation = how far into the round before it can be let go
# (default: 0.5 if channelled, else 0); speed = technique speed, for everything that is not a
# melee blow (default 1).  See Battle.timing.
# ======================================================================================
TIMING = {
    # lightning and sound are the fastest things on the field
    "lightning_discharge": dict(speed=4.0), "amber_beam": dict(speed=3.0), "thunder_dive": dict(speed=2.0),
    "amber_soundwave": dict(speed=3.0), "speech_stop": dict(speed=3.0), "speech_blast": dict(speed=3.0),
    "speech_crush": dict(speed=3.0), "resonance": dict(speed=5.0), "shoot": dict(speed=4.0),
    "infused_shot": dict(speed=4.0), "construct_bullet": dict(speed=3.0), "boogie_woogie": dict(speed=4.0),
    # fast projectiles
    "piercing_blood": dict(speed=2.5), "granite_blast": dict(speed=2.0), "dismantle": dict(speed=1.8),
    "red": dict(speed=1.5), "hairpin": dict(speed=1.5), "ball_barrage": dict(speed=1.5),
    "energy_discharge": dict(speed=1.5), "ultra_cannon": dict(speed=1.5, activation=0.7),
    "supernova": dict(speed=1.3), "blue": dict(speed=1.2), "shutter": dict(speed=1.2), "rika_beam": dict(speed=1.2),
    # heavy, slow, or needing more time to build
    "hollow_purple": dict(speed=1.2, activation=0.9), "maximum_meteor": dict(speed=0.6, activation=0.9),
    "maximum_uzumaki": dict(speed=0.8, activation=0.7), "cursed_swarm": dict(speed=0.8),
    "ember_insects": dict(speed=0.9), "frost_calm": dict(speed=0.8), "water_torrent": dict(speed=0.8),
    "death_swarm": dict(speed=0.8), "jacobs_ladder": dict(speed=1.5, activation=0.7),
    # quick stances and the court
    "fuga": dict(speed=1.5, activation=0.7), "world_slash": dict(speed=2.0, activation=0.7),
    "black_hole": dict(speed=1.0, activation=0.9), "thin_ice_breaker": dict(speed=1.0),
    "recreate_house": dict(speed=0.8, activation=0.7), "true_sphere": dict(speed=1.5, activation=0.9),
    "infinity": dict(speed=2.0), "simple_domain": dict(speed=2.0), "domain_amplification": dict(speed=2.0),
    "falling_blossom": dict(speed=2.0), "ds_domain": dict(speed=3.0), "frame_rush": dict(speed=2.0),
}


# ======================================================================================
# Technique grades.  Not balanced on purpose: see constants.TIER_POWER (rarity is in rarity.py).
# ======================================================================================
_G = {5: ["limitless", "shrine", "copy", "cursed_spirit_manipulation", "ten_shadows", "idle_transfiguration",
          "body_hop", "idle_death_gamble", "mythical_beast_amber", "jacobs_ladder", "heavenly_restriction",
          "disaster_flames", "disaster_plants", "disaster_tides", "comedian", "star_rage", "sky_manipulation",
          "granite_blast", "festering_life", "pestilence", "construction"],
      4: ["shikigami_territory", "hakuna_laana", "sword_saint", "deadly_sentencing", "blood_manipulation", "boogie_woogie", "ratio", "projection_sorcery", "ice_formation",
          "antigravity_system", "black_bird", "contractual_recreation", "cursed_chords", "blazing_courage",
          "corpse_creation"],
      3: ["puppet_manipulation", "cursed_speech", "solo_forbidden_area", "paralyzing_gaze", "heart_catch"],
      2: ["straw_doll", "tool_manipulation", "abrupt_mutation", "explosive_flesh", "seance", "inverse",
          "auspicious_beasts", "love_rendezvous", "g_warstaff", "transport", "clone_technique", "sumo"],
      1: ["moon_dregs", "new_shadow_style", "miracles", "divergent_fist"],
      0: ["hair_manipulation", "sugar_craft"]}
TECH_GRADE = {key: grade for grade, keys in _G.items() for key in keys}

# Reverse cursed technique is not a matter of level: these are the techniques whose users healed
# themselves with it in the source (Gojo, Sukuna, Yuta, Kenjaku, Uraume, Yuki, Higuruma, Yuji).
RCT_TECHNIQUES = {"limitless", "shrine", "copy", "body_hop", "ice_formation", "star_rage",
                  "deadly_sentencing", "divergent_fist"}
RCT_OUTPUT_TECHNIQUES = {"shrine", "copy"}             # healing someone else is rarer still (Sukuna, Yuta)


def _apply_timing() -> None:
    from dataclasses import replace
    from .techniques import TECHNIQUES
    for tech in list(TECHNIQUES.values()):
        acts = tuple(replace(a, **TIMING[a.key]) if a.key in TIMING else a for a in tech.actions)
        grade = TECH_GRADE.get(tech.key, tech.grade)
        if grade != tech.grade or any(x is not y for x, y in zip(acts, tech.actions)):
            register(replace(tech, actions=acts, grade=grade))


_apply_timing()

# ======================================================================================
# Perception unlocks (players only; NPCs are already trained). Every technique's first move, its
# first attack and its defences are free; everything else needs perception - more for heavier moves - and a
# reincarnated sorcerer's perception counts +6 (constants.REINCARNATED_PER_BONUS), so an awakened
# sorcerer has far more to unlock. PER_OVERRIDE sets a requirement by hand.
# ======================================================================================
PER_BY_KIND = {Kind.ATTACK: 12, Kind.BUFF: 13, Kind.UTILITY: 13, Kind.SUMMON: 13, Kind.HEAL: 13,
               Kind.DOMAIN: 18, Kind.DEFENSE: 0}
PER_BY_LEVEL = ((18, 12), (12, 8), (10, 6), (6, 3))     # unlock level -> extra perception
PER_OVERRIDE: dict = {}                                  # action key -> perception


def perception_needed(tech, act) -> int:
    if act.key in PER_OVERRIDE:
        return PER_OVERRIDE[act.key]
    if act.react is not None or act.kind == Kind.DEFENSE:
        return 0
    first = next((a for a in tech.actions if a.kind == Kind.ATTACK), None)
    if (first is not None and act.key == first.key) or (tech.actions and act.key == tech.actions[0].key):
        return 0
    extra = next((e for lv, e in PER_BY_LEVEL if act.min_level >= lv), 0)
    return PER_BY_KIND.get(act.kind, 10) + extra


def _apply_perception() -> None:
    from dataclasses import replace
    from .techniques import TECHNIQUES
    for tech in list(TECHNIQUES.values()):
        if not tech.innate:
            continue
        acts = tuple(replace(a, min_per=perception_needed(tech, a)) for a in tech.actions)
        register(replace(tech, actions=acts))


_apply_perception()

# ======================================================================================
# Comedian material (original gags)
# ======================================================================================
@dataclass(frozen=True)
class JokeOption:
    text: str          # what the target says
    outcome: str       # bonk | stun | heal | fizzle | none | backfire
    result: str        # what happens


@dataclass(frozen=True)
class Joke:
    setup: str
    options: tuple


JOKES = (
    Joke("Knock knock!", (
        JokeOption("Who's there?", "bonk",
                   '"Domain." "Domain who?" "Do-main-tain eye contact while this pan falls on you!" '
                   "A brass pan drops out of the sky."),
        JokeOption("...", "none", "Silence. Somewhere a tumbleweed rolls past."),
        JokeOption("(snort despite yourself)", "heal",
                   "The laugh feeds him. His injuries rewind like a cartoon run backwards."))),
    Joke("I asked a Grade 4 curse for directions. Know what it said?", (
        JokeOption("What did it say?", "stun",
                   '"Boo." A ghost of few words. The sheer weakness of it leaves you reeling.'),
        JokeOption("Don't care.", "none", "He waits for a laugh that is not coming."),
        JokeOption("That's terrible!", "fizzle",
                   '"You were supposed to say BOO!" A paper fan smacks your hands and your '
                   "gathered energy scatters."))),
    Joke("Be my straight man: I'm quitting comedy to become a domain.", (
        JokeOption("You can't BECOME a domain!", "bonk",
                   '"Why not? I already have nobody inside!" The retort lands like a falling stage light.'),
        JokeOption("Good. Quit.", "backfire", "That one stings. His shoulders drop."),
        JokeOption("(stare blankly)", "none", "The bit dies on the pavement."))),
    Joke("My cursed technique is so secret even I don't know what it is!", (
        JokeOption("Then how do you use it?", "heal",
                   '"By accident! Like this!" A first-aid kit bounces off his head and patches him up.'),
        JokeOption("That's a confession, not a joke.", "none", "He opens his mouth. Closes it."),
        JokeOption("(reluctant chuckle)", "stun",
                   "You laughed. The bit has you now; you can't move until the punchline ends."))),
    Joke("Pick a card, any card!", (
        JokeOption("(pick one)", "fizzle",
                   "It's a parking ticket made out to you. Your concentration goes with it."),
        JokeOption("I'm not playing.", "none", "He shuffles sadly."),
        JokeOption("(pick two)", "bonk",
                   '"Cheater!" A whistle blows and a red card the size of a door flattens you.'))),
    Joke("What's the difference between you and a vending machine?", (
        JokeOption("What?", "bonk",
                   '"The vending machine takes a hit better!" One lands on you to prove it.'),
        JokeOption("I'm worth more points.", "none", "He blinks. That was a better line than his."),
        JokeOption("(laugh)", "heal", "He soaks up the laugh and stands a little taller."))),
)


# ======================================================================================
# Items / cursed tools (bought with culling game points)
# ======================================================================================
@dataclass(frozen=True)
class Item:
    key: str
    name: str
    slot: str                 # weapon | armor (cursed tools unless mundane) | object | supply
    cost: int                 # shop price; for things the shop never stocks, the reference price
    power: float = 0.0
    dtype: DType = P
    tags: frozenset = frozenset()
    flags: tuple = ()         # mundane = holds no cursed energy; signature = comes with a technique
    params: dict = field(default_factory=dict)
    desc: str = ""
    shop: bool = True         # stocked by the colony's shop

    @property
    def mundane(self) -> bool:
        return "mundane" in self.flags or self.slot == "supply"

    @property
    def kind(self) -> str:
        if self.mundane:
            return "ordinary item"
        return "cursed object" if self.slot == "object" else f"cursed tool: {self.slot}"


_ARMS = (2, 3)                # Part.L_ARM, Part.R_ARM
ITEMS = {i.key: i for i in (
    # ---- cursed tools: weapons -------------------------------------------------------------
    Item("slaughter_demon", "Slaughter Demon", "weapon", 3, power=7, tags=fs({"slash"}),
         desc="A plain cursed blade."),
    Item("playful_cloud", "Playful Cloud", "weapon", 25, power=10, tags=fs({"blunt"}),
         params={"str_scale": 0.9}, desc="Three-section staff; hits as hard as its wielder."),
    Item("black_rope", "Black Rope", "weapon", 28, power=7, tags=fs({"bind"}), flags=("disrupt", "nullify", "signature"),
         desc="Woven to disturb cursed energy: a hit breaks whatever the target is channelling.", shop=False),
    Item("dragon_bone", "Dragon-Bone", "weapon", 30, power=9, tags=fs({"slash"}), params={"ramp": 2},
         desc="Stores the energy of every clash: each hit adds 2 power for the fight (up to +12)."),
    Item("split_soul_katana", "Split Soul Katana", "weapon", 40, power=10, dtype=S,
         tags=fs({"slash", "soul"}), flags=("soul_strike",), desc="Cuts the soul; durability is ignored."),
    # Never in the shop: carried by the Sorcerer Killer and taken only from his body.
    Item("inverted_spear", "Inverted Spear of Heaven", "weapon", 40, power=9, tags=fs({"slash"}),
         flags=("nullify", "disrupt"), shop=False,
         desc="Cancels techniques: ignores technique defences, breaks channelling."),
    Item("inventory_curse", "Inventory Curse", "object", 35, flags=("kept",), shop=False,
         desc="A curse that swallows weapons and coughs them up on demand. Not consumed: while you "
              "carry it you can change cursed tools anywhere, mid-fight. The Sorcerer Killer's."),
    # ---- cursed tools that come with a technique (never in the shop) -----------------------
    Item("blunt_sword", "Wrapped Blunt Sword", "weapon", 10, power=10, tags=fs({"blunt"}),
         flags=("signature",), shop=False,
         desc="Comes with the Ratio Technique: a 7:3 strike made with it hits 4 harder."),
    Item("gavel", "Judge's Gavel", "weapon", 12, power=8, tags=fs({"blunt", "gavel"}),
         flags=("signature",), shop=False, params={"stun": 0.2},
         desc="Comes with Deadly Sentencing. A solid hit may stun."),
    Item("conductor_staff", "Conductor Staff", "weapon", 14, power=8, tags=fs({"blunt"}),
         flags=("signature", "conductor"), shop=False,
         desc="Comes with Mythical Beast Amber: in the hands of someone with electric cursed "
              "energy, every blow from it shocks and leaves a charge."),
    # ---- cursed tools: armor ---------------------------------------------------------------
    Item("cursed_gauntlets", "Cursed Gauntlets", "armor", 18,
         params={"parts": _ARMS, "guard": 0.35, "fist": 4, "dur": 1},
         desc="Arms take 35% less damage; bare-handed strikes hit 4 harder; +1 durability."),
    Item("cursed_greaves", "Cursed Greaves", "armor", 14,
         params={"parts": (4, 5), "guard": 0.35, "kick": 4, "dur": 1},
         desc="Legs take 35% less damage; kicks hit 4 harder; +1 durability."),
    # ---- cursed objects (single use) -------------------------------------------------------
    Item("cursed_relic", "Cursed Relic", "object", 3, params={"ce": 35},
         desc="Remains steeped in cursed energy. Consume in battle: +35 cursed energy."),
    # Never in the shop: cut out of a Finger Bearer, or taken from whoever was carrying one.
    Item("sukuna_finger", "Sukuna's Finger", "object", 30, shop=False,
         desc="Eat it (`item sukuna_finger` in a fight, `eat` on the map). If your body can cage it, "
              "Sukuna's cursed energy amplifies everything you do, for good: +10% output and strength and "
              "+25 cursed energy per finger. If it cannot, Sukuna takes the body and you are gone."),
    # ---- ordinary things found lying around the colony (never in the shop) -----------------
    # They hold no cursed energy: used as they are they cannot hurt a curse, and a sorcerer
    # killed with one comes back as a curse. Pour cursed energy in (Infused Strike / Shot).
    Item("bat", "Baseball Bat", "weapon", 0, power=6, tags=fs({"blunt"}), flags=("mundane",), shop=False,
         desc="Ordinary. No cursed energy."),
    Item("knife", "Kitchen Knife", "weapon", 0, power=5, tags=fs({"slash"}), flags=("mundane",), shop=False,
         desc="Ordinary. No cursed energy."),
    Item("sword", "Plain Katana", "weapon", 0, power=8, tags=fs({"slash"}), flags=("mundane",), shop=False,
         desc="Ordinary steel. No cursed energy."),
    Item("gun", "Handgun", "weapon", 0, power=15, tags=fs({"bullet"}), flags=("mundane", "ranged"), shop=False,
         params={"ammo": 6}, desc="Ordinary. Six rounds a fight; `shoot`. No cursed energy."),
    Item("bandage", "Bandages", "supply", 0, params={"heal": 30}, shop=False,
         desc="Ordinary. Stops bleeding and closes wounds for 30 HP; cannot regrow anything."),
)}

# ======================================================================================
# Classes
# ======================================================================================
_S = Stat
CLASS_BASE = {
    PClass.SORCERER: {_S.MAX_HP: 100, _S.MAX_CE: 60, _S.MAX_STA: 60, _S.STR: 10, _S.SPD: 10,
                      _S.DUR: 8, _S.PER: 8, _S.OUT: 10, _S.CE_REGEN: 4, _S.STA_REGEN: 5, _S.EFF: 0},
    PClass.REINCARNATED: {_S.MAX_HP: 110, _S.MAX_CE: 80, _S.MAX_STA: 60, _S.STR: 11, _S.SPD: 10,
                          _S.DUR: 9, _S.PER: 10, _S.OUT: 12, _S.CE_REGEN: 5, _S.STA_REGEN: 5, _S.EFF: 10},
    PClass.CURSED_SPIRIT: {_S.MAX_HP: 120, _S.MAX_CE: 120, _S.MAX_STA: 40, _S.STR: 11, _S.SPD: 9,
                           _S.DUR: 9, _S.PER: 7, _S.OUT: 11, _S.CE_REGEN: 8, _S.STA_REGEN: 3, _S.EFF: 5},
    PClass.MUTANT: {_S.MAX_HP: 115, _S.MAX_CE: 90, _S.MAX_STA: 70, _S.STR: 12, _S.SPD: 11,
                    _S.DUR: 10, _S.PER: 9, _S.OUT: 11, _S.CE_REGEN: 5, _S.STA_REGEN: 5, _S.EFF: 5},
}

PLAYABLE = {
    PClass.SORCERER: ["deadly_sentencing", "comedian", "idle_death_gamble", "copy",
                      "ten_shadows", "cursed_spirit_manipulation", "heavenly_restriction",
                      "puppet_manipulation", "boogie_woogie", "limitless", "ratio", "cursed_speech",
                      "straw_doll", "projection_sorcery", "construction",
                      "star_rage", "black_bird", "cursed_chords", "blazing_courage", "corpse_creation",
                      "solo_forbidden_area", "paralyzing_gaze", "tool_manipulation", "abrupt_mutation",
                      "seance", "inverse", "auspicious_beasts", "love_rendezvous", "moon_dregs",
                      "new_shadow_style", "miracles", "divergent_fist", "hair_manipulation", "sugar_craft",
                      "hakuna_laana", "heart_catch", "g_warstaff", "transport", "clone_technique"],
    PClass.REINCARNATED: ["body_hop", "shrine", "ten_shadows", "cursed_spirit_manipulation",
                          "deadly_sentencing", "idle_death_gamble", "mythical_beast_amber",
                          "granite_blast", "ice_formation", "jacobs_ladder",
                          "sky_manipulation", "antigravity_system", "contractual_recreation", "explosive_flesh",
                          "shikigami_territory", "sword_saint", "sumo"],
    PClass.CURSED_SPIRIT: ["idle_transfiguration", "disaster_flames", "disaster_plants", "disaster_tides",
                           "festering_life", "pestilence"],
    PClass.MUTANT: ["blood_manipulation"],
}
DEATH_PAINTINGS = ["Choso", "Eso", "Kechizu"] + [f"Death Painting No. {n}" for n in range(4, 10)] + ["The Tenth"]
