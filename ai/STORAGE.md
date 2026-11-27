# Storage

| What | Where | Lifetime |
|---|---|---|
| Colonies, characters, maps | **SQLite** (default, `CULLING_SQLITE`) or **DynamoDB** (`CULLING_DB=dynamodb`) | for good |
| A battle in progress | Redis `cg:battle:<server>:<battle id>` (hash: pickled state, round, last 40 log lines), saved after every round | deleted when the battle ends; 6 h TTL otherwise |
| Every character who fought, with their stats | Redis `cg:char:<server>:<user>` (hash: `record`, `stats`, `saved_at`, `last_battle`) | 30 days (a cache; the database keeps the character) |

Redis is optional for local runs (it falls back to memory with a warning). The deployment sets
`REDIS_REQUIRED=1` so the bot refuses to start without it.

## One item format for both databases
SQLite and DynamoDB hold exactly the same items (`storage.pack`), so `python -m ai.migrate` moves
a game between them without converting anything:

```
PK      SERVER#<discord server id>
SK      META | MAP | PLAYER#<discord user id>
GSI1PK  USER#<discord user id>          (players only)
GSI1SK  SERVER#<discord server id>      (players only)
name, level, alive, points              (players only: small readable copies for the index)
v       format version (1)
d       the whole object: JSON, zlib-compressed, as one binary attribute
```

SQLite: one table `items(pk, sk, gsi1pk, gsi1sk, item)` with the same primary key and a partial index
on `(gsi1pk, gsi1sk)`, `item` being the packed item above.

## Why this is cheap on DynamoDB
- **On-demand billing** (`PAY_PER_REQUEST`): a game bot's traffic is bursty and mostly idle, and
  on-demand costs nothing when nobody plays. Switch to provisioned capacity with auto scaling only
  once traffic is steady and you can see it in CloudWatch.
- **Small items**: a character is about 350 bytes packed (a nested DynamoDB map of the same data
  would be several KB, because every attribute name counts toward the size). Writes are billed per
  1 KB, so a save costs one write unit, and reads per 4 KB, so a load costs half a read unit.
- **Unchanged items are not written**: the store remembers what it last wrote, and a save that
  would write the same bytes is skipped. A colony command saves the colony, the map and every
  player, but only what actually changed reaches the database.
- **A sparse index with a small projection**: only player items carry `GSI1PK`, so colony and map
  writes cost nothing extra in the index. The index projects four small attributes, not the whole
  item, so each player write's index copy stays tiny.
- **No scans in play**: everything the game does is a `GetItem`, or a `Query` on one server's
  partition or on one user's index entries. `Scan` is only used by `ai.migrate`.
- **Live battle state stays in Redis**, never in DynamoDB: a battle saves every round, which would
  be the most expensive write pattern in the game.

Rough cost at us-east-1 on-demand prices: 1,000 player saves and 4,000 reads come to well under
one cent; storage is $0.25 per GB-month, and a thousand characters are about 0.5 MB.

Create the table with `python -m ai.migrate ... --create-table` (or `GameStore.create_table()`);
the definition is `storage.table_definition()`.

## Many battles at once
A battle never touches the database while it is being fought. Its state is in memory (and
snapshotted to Redis each round); the database is written when a command finishes and when a
fight ends (the fighters only), each write a few hundred bytes.

- **One thread per battle**, parked while it waits for players (`KOGANE_MAX_BATTLES`, default 256,
  is the ceiling on battles + commands in flight).
- **A colony is locked only while a command works on it**, never for the length of a fight. A fight
  marks its players (`ColonySession.in_battle`) and curses (`Roamer.engaged`) busy and lets go of
  the lock, so other fights and commands in the same colony carry on. Different colonies never
  wait on each other at all.
- **SQLite** is one connection in WAL mode behind a lock: writes are serialized, each takes well
  under a millisecond, and readers are not blocked. Saving a 200-player colony with nothing
  changed costs about 15 ms; after a fight only the fighters are written.

Measured on one core with players that answer instantly (the worst case): 200 fights going at once
in ONE colony finished in about 21 s, every result saved correctly, and a bystander's `/look` was
answered in about 200 ms (max 307 ms) throughout. With human players, who take seconds per turn, the
limit you meet first is Discord's rate limits, not the database.

Past one process: SQLite + the in-memory colony sessions assume a single bot process. To run
several (Discord shards), move to DynamoDB and put the colony lock and lobby state in Redis.
