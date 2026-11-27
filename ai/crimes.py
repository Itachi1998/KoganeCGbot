"""Compact per-player criminal record for Judgeman.

Every breakable object, building entry and kill a player makes is appended here.  The log
is a fixed-size numpy ring buffer of packed uint32 events plus lifetime counters, so a
player's whole history serialises to 274 bytes no matter how long they have played:

    bits 28-31  crime code        bits 16-27  reference (object / node / victim id)
    bits  0-15  colony day

That blob is stored as one binary attribute on the player's DynamoDB item.
"""
from __future__ import annotations

from enum import IntEnum

import numpy as np


class Crime(IntEnum):
    VANDALISM = 0      # broke a map object
    TRESPASS = 1       # entered a building
    THEFT = 2          # looted an object
    ASSAULT = 3        # attacked a player first
    MURDER = 4         # killed a player


#            label shown in court                      severity (3 = death penalty)
CRIME_INFO = {
    Crime.VANDALISM: ("destruction of property", 1),
    Crime.TRESPASS: ("unlawful entry into a building", 1),
    Crime.THEFT: ("theft", 1),
    Crime.ASSAULT: ("assault", 2),
    Crime.MURDER: ("murder", 3),
}
# Charges Judgeman can invent when the record is clean (or simply because it feels like it).
FABRICATED = (
    ("loitering near a barrier with intent", 1),
    ("gambling in a pachinko parlour while under age", 1),
    ("operating a cursed tool without a licence", 1),
    ("aggravated assault on a vending machine", 2),
    ("mass murder in Shibuya", 3),
)

N_CODES = 8
CAP = 64


class CrimeLog:
    __slots__ = ("counts", "events", "head", "size")

    def __init__(self):
        self.counts = np.zeros(N_CODES, dtype=np.uint16)
        self.events = np.zeros(CAP, dtype=np.uint32)
        self.head = 0
        self.size = 0

    def add(self, code: Crime, ref: int = 0, day: int = 0) -> None:
        packed = (int(code) & 0xF) << 28 | (int(ref) & 0xFFF) << 16 | (int(day) & 0xFFFF)
        self.events[self.head] = packed
        self.head = (self.head + 1) % CAP
        self.size = min(self.size + 1, CAP)
        if self.counts[int(code)] < np.iinfo(np.uint16).max:
            self.counts[int(code)] += 1

    @staticmethod
    def unpack(packed: int) -> tuple[Crime, int, int]:
        packed = int(packed)
        return Crime(packed >> 28 & 0xF), packed >> 16 & 0xFFF, packed & 0xFFFF

    def recent(self) -> list[tuple[Crime, int, int]]:
        """Newest first."""
        idx = (self.head - 1 - np.arange(self.size)) % CAP
        return [self.unpack(e) for e in self.events[idx]]

    @property
    def total(self) -> int:
        return int(self.counts.sum())

    def pick(self, rng: np.random.Generator, heavier: bool = False):
        """A random recorded event; with ``heavier`` the gravest kind on record."""
        ev = self.recent()
        if not ev:
            return None
        if heavier:
            worst = max(CRIME_INFO[c][1] for c, _, _ in ev)
            ev = [e for e in ev if CRIME_INFO[e[0]][1] == worst]
        return ev[int(rng.integers(len(ev)))]

    def to_bytes(self) -> bytes:
        return (self.counts.tobytes() + bytes([self.head, self.size]) + self.events.tobytes())

    @classmethod
    def from_bytes(cls, blob: bytes | None) -> "CrimeLog":
        log = cls()
        if blob:
            blob = bytes(blob)
            n = N_CODES * 2
            log.counts = np.frombuffer(blob[:n], dtype=np.uint16).copy()
            log.head, log.size = blob[n], blob[n + 1]
            log.events = np.frombuffer(blob[n + 2:], dtype=np.uint32).copy()
        return log

    def summary(self) -> str:
        parts = [f"{CRIME_INFO[Crime(i)][0]} x{int(c)}" for i, c in enumerate(self.counts[:len(Crime)]) if c]
        return ", ".join(parts) or "clean record"
