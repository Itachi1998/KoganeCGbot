"""Copy the whole game from one storage backend to another. Items are byte-for-byte the same format.

    python -m ai.migrate --from sqlite:culling.db --to dynamodb:CullingGame --create-table
    python -m ai.migrate --from json:culling_save.json --to sqlite:culling.db
    python -m ai.migrate --from dynamodb:CullingGame --to sqlite:backup.db       (a backup)

AWS credentials and region come from the usual places (instance role, AWS_REGION...).
"""
from __future__ import annotations

import argparse

from .storage import GameStore


def open_store(spec: str) -> GameStore:
    kind, _, where = spec.partition(":")
    if kind == "sqlite":
        return GameStore(backend="sqlite", sqlite_path=where or "culling.db")
    if kind == "json":
        return GameStore(backend="json", local_path=where or "culling_save.json")
    if kind == "dynamodb":
        store = GameStore(backend="dynamodb", table=where or "CullingGame")
        if store.kind != "dynamodb":
            raise SystemExit("Could not reach DynamoDB (see the message above).")
        return store
    raise SystemExit(f"unknown backend {kind!r}: use sqlite:, json: or dynamodb:")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--create-table", action="store_true", help="create the DynamoDB table first")
    args = ap.parse_args(argv)
    if args.create_table:
        kind, _, name = args.dst.partition(":")
        if kind != "dynamodb":
            raise SystemExit("--create-table is for a dynamodb: destination")
        import boto3
        from .storage import table_definition
        client = boto3.client("dynamodb")
        client.create_table(**table_definition(name or "CullingGame"))
        client.get_waiter("table_exists").wait(TableName=name or "CullingGame")
        print(f"Created table {name or 'CullingGame'}.")
    src, dst = open_store(args.src), open_store(args.dst)
    n = 0
    for item in src.raw_items():
        dst.put_raw(item)
        n += 1
    print(f"Copied {n} item(s) from {src.backend} to {dst.backend}.")


if __name__ == "__main__":
    main()
