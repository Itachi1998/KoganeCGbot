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
* characters and colonies are saved to `culling_save.json` (set `CULLING_SAVE` to move it), or to
  DynamoDB when `CULLING_DYNAMO=1`; live battles snapshot to Redis when `REDIS_URL` is reachable
* the command-line version still works: `python -c "from ai.cli import main; main([])"`
### Commands
* `/create` (spin for class and technique, at the original odds), `/profile`, `/delete`, `/mod`
* colony: `/look` `/map` `/me` `/go` `/wait` `/rest` `/search` `/interact` `/heal` `/medic` `/treat`
  `/use` `/equip` `/unequip` `/shop` `/buy` `/sell` `/market` `/fingers` `/eat` `/rules` `/addrule`
  `/give` `/pvp` `/transfer` `/scouts` `/puppets` `/players`, or any command typed with `/do` (`,c`)
* `/lobby create`: **fights need a lobby**. Outside one you can move and do everything else, but no
  curse or player can attack you. In a lobby: **Hunt** the curses at the owner's node and **PvP** (Team A
  vs Team B) are real and saved; **Spar** is practice and saves nothing. Ambushes play in the lobby thread.
* `/learn create|colony|battle|lobby`
* in a fight, press **Open controls** when the bot pings you
### Character creation
* `ai/rarity.py` keeps the original bot's class odds (Sorcerer / Curse / Reincarnate), every
  technique's rarity number, the `weight_system` roll and the Six Eyes chance. The engine's newer
  techniques are in the roll too, rarity by grade (special grade = legend).
* `ai/oldstats.py` rolls the original stats (HP, CE, Strength, Speed, class and technique boosts).
  Players see those numbers; in a fight they scale the engine's stats against an average roll.
### Perception check
Attacked while committed to a move with no defence set? With perception 16+ you are asked: keep
your move and take the hit, or drop it and switch to a defence, which comes up in time with a
chance shown on the button (`SWITCH_*` in `ai/constants.py`).
