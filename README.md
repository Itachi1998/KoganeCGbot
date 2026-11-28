# KOGANE CULLING GAMES
## THE DISCORD CULLING GAMES BOT
### How to run:
* create a python virtual environment with `python -m venv venv`
* do a `pip install -r requirements.txt`
* run `python models.py` to create the database with tables
* run `python main.py`
* in discord, run the `,sync` command to sync all commands for the bot (must be bot owner)
* in discord, run the `,colony` command to populate the database with colony data
### created by Loud and Codes

## The new engine (`ai/`) and its Discord bot (`ai/bot/`)
`ai/` is the round-based battle engine with colonies, roaming curses and saved characters.
`ai/bot/` puts it on Discord with the same look as the original cogs.
### How to run:
* `pip install -r requirements.txt`
* set `DISCORD_TOKEN` to the bot's token, then run `python -m ai.bot`
* in discord, run `,sync` (bot owner) to push the slash commands
* characters and colonies are saved to SQLite (`culling.db`, or `CULLING_SQLITE`), or to DynamoDB
  with `CULLING_DB=dynamodb`; both hold the same items, and `python -m ai.migrate` copies between them
  (see `ai/STORAGE.md`). Redis (`REDIS_URL`) holds live battles and post-battle character snapshots.
* **From a local terminal, token in AWS (SSM / Secrets Manager):** see `deploy/LOCAL.md` - `deploy/run_local.sh`
* **On a server (EC2):** see `deploy/EC2.md` - `docker compose -f deploy/docker-compose.yml up -d --build`
* the command-line version still works: `python -c "from ai.cli import main; main([])"`
### Commands
* `/create` (spin for class and technique, at the original odds), `/profile`, `/delete`, `/mod`
* colony: `/look` `/map` `/me` `/go` `/wait` `/rest` `/search` `/interact` `/heal` `/medic` `/treat`
  `/use` `/equip` `/unequip` `/shop` `/buy` `/sell` `/market` `/fingers` `/eat` `/rules` `/addrule`
  `/give` `/pvp` `/transfer` `/scouts` `/puppets` `/players`, or any command typed with `/do` (`,c`)
* `/lobby create`: **fights need a lobby**. Outside one you can move and do everything else, but no
  curse or player can attack you. In a lobby: **Hunt** the curses at the owner's node and **PvP** (Team A
  vs Team B) are real and saved; **Spar** is practice and saves nothing. Ambushes play in the lobby thread.
  Sides: Team A, Team B, Team C and the Field (every one for themselves). `/lobby create private:True`
  makes an invite-only lobby (`/lobby invite`) for PvP only; curses never find its members.
* `/leaderboard [global]` (needs the Open Score Board rule), `/market global`, `/sell ... global_market:True`
* `/learn create|colony|battle|lobby`
* in a fight, press **Open controls** when the bot pings you
### Character creation
* `ai/rarity.py` keeps the original bot's class odds (Sorcerer / Curse / Reincarnate), every
  technique's rarity number, the `weight_system` roll and the Six Eyes chance. The engine's newer
  techniques are in the roll too, rarity by grade (special grade = legend).
* `ai/oldstats.py` rolls the original stats (HP, CE, Strength, Speed, class and technique boosts).
  Players see those numbers; in a fight they scale the engine's stats against an average roll.
### Skill points
+10 per level-up up to level 10, +5 after (`/skills`, `/upgrade`): CE efficiency, physical speed,
physical strength (close-range moves), perception, soul perception (needed to harm Idle
Transfiguration), domain refinement, navigation. Most technique moves need perception to unlock;
a reincarnated sorcerer's counts +6, so awakened sorcerers have much more to unlock. Details in
`ai/skills.py` and `ai/data.py` (`perception_needed`).
### Curses coming back
Grade 4 to Grade 1 curses re-form far away the moment they die. Special-grade curses return after
24 h, Finger Bearers 48 h, the Sorcerer Killer 72 h and Sukuna 7 days - bearers and Sukuna only while
fewer than 20 fingers are in play (`RESPAWN_HOURS` in `ai/world.py`).
### Battle feed
One message per stretch of rounds, edited as the fight goes; a new one starts at Discord's 4000
character limit (about 9 rounds of a 1v1, 6 of a 2v2, 4 of a three-team fight).
### Domains
Every domain takes in who it does in the manga (`constants.Tier`, set per domain in `ai/data.py`):
* **one target** - Deadly Sentencing, Graveyard Domain, Authentic Mutual Love, a miniature barrier.
  Everyone else is shut OUTSIDE the barrier: nothing crosses it until it falls.
* **every enemy** - most domains.
* **everyone its user is not touching** - Unlimited Void (allies too; Gojo holds one ally per free hand).
* **everyone and everything in range** - Malevolent Shrine, alone: allies and the battlefield are cut.
* **no sure-hit** - Chimera Shadow Garden (incomplete).
### Binding vows
`vow` in a fight (or the vow menu in the battle controls). A vow moves numbers around:
* **domain** (reach, sure-hit output, clash strength, rounds, cost, barrier): Widened / Condensed /
  Pinpoint Domain trade reach for output along one target < every enemy < the domain's own tier;
  Inverted Barrier makes it strong from outside instead of from inside; Brief, Lasting, Lavish.
* **technique** (output, strength, tool, cost, activation time): Overcharge, Measured Output, Quick
  Hands, Deliberate Form, and the bindings (Bound Arm, Iron Stance, Revealing One's Hand...).
* **release**: Snap Release lets the next channelled technique go at once with no gathering, weaker,
  and the same technique owes a chant next round. Oath of Incantation is permanent: once a fight the
  first technique goes at once and stronger, and every other technique must be chanted for good.
* **Sukuna's, from the Shinjuku Showdown** (any player who has the technique can swear them; the roaming
  Sukuna swears them himself when the fight calls for it, and the permanent ones stay with him):
  * *barrierless Malevolent Shrine* - his domain as it comes: no barrier, everything in range, and it
    reaches round an ordinary barrier in a clash. *Condensed / Pinpoint Domain* are his range-for-output
    re-sets against Gojo (output now also counts in the clash).
  * *Skipped Rite* (`vow skipped_rite <technique>`, permanent) - one technique loosed once with no
    gathering, chant or sign; for ever after it needs its whole rite: always chanted, always seen coming,
    never hurried by a vow again. His vow on the slash that cuts the world.
  * *Furnace Covenant* (permanent; he always has it) - the flame arrow may not be used on several
    opponents outside his own domain; inside it, everything Malevolent Shrine has cut is dust that the
    flame sets off on all the domain takes in (`FURNACE_*` in `ai/constants.py`).
  * *Sealed Barrier* - a barrierless domain closed: the blast is half again as strong, and the domain
    loses its reach round other barriers.
  * *Ninety-Nine Seconds* - when the brain can bear no more domains (burnt out and healed four times),
    one more, a round shorter, and the last.
New vows are data: `vows.trade(key, name, desc, technique={...}, domain={...})`.
### Deadly Sentencing: confiscation
A guilty verdict takes ONE thing the defendant is wielding, picked at random: one of their innate
techniques (the others stay usable) or the cursed tool in their hand (unequipped for the rest of the
fight, kept in the bag). With neither, their cursed energy. A sentenced defendant is not tried again.
### Rabbit Escape
While Rabbit Escape is out (or channelled), its side is hidden behind the rabbits: enemies lose
`RABBIT_VEIL` perception reading it, so gathered energy and committed techniques go unseen and nobody
gets the perception-check window against its attacks; shikigami summoned behind it arrive unannounced;
escaping the fight is `RABBIT_FLEE` likelier. The Six Eyes see through it. Kill the rabbits to end it.
### Perception check
Attacked while committed to a move with no defence set? With perception 16+ you are asked: keep
your move and take the hit, or drop it and switch to a defence, which comes up in time with a
chance shown on the button (`SWITCH_*` in `ai/constants.py`).
