"""Strict validation around the pinned upstream decoder, not a second parser.

WPC live snapshots contain 0x3000 RAM bytes and a 46-byte PinMAME trailer.
The 0x3000 form is allowed for explicitly supplied offline RAM-only fixtures.
"""

from dataclasses import dataclass
from pathlib import Path

from third_party.pinmame_nvmaps import nvram_parser as upstream

upstream.MAPS_ROOT = str(Path(__file__).parents[1] / "maps")


def checked_value(entry, memory):
    """Decode an upstream field, rejecting missing bytes, invalid BCD and nonintegers."""
    raw = entry.get_bytes(memory)
    if raw is None:
        raise ValueError("Incomplete memory coverage")
    # Upstream intentionally coerces A-F to zero; live scores must reject it.
    if entry.entry.get("encoding") == "bcd" and any((byte >> 4) > 9 or (byte & 15) > 9 for byte in raw):
        raise ValueError("Invalid BCD score")
    value = entry.get_value(memory)
    if value is None or not isinstance(value, int):
        raise ValueError("Missing or non-integer mapped value")
    return value


def decode_field(memory, field):
    """Inspection convenience using the same upstream mapping class."""
    sparse = upstream.SparseMemory()
    sparse.update_memory(0, bytearray(memory))
    metadata = {"big_endian": True, "platform": upstream.load_platform("williams-wpc-12K")}
    return checked_value(upstream.RamMapping(field, metadata), sparse)


@dataclass(frozen=True)
class Snapshot:
    """Immutable decoded state: 1-based active seats/balls and ordered integer scores.

    Decoder supplies four score slots. Construction alone does not validate values;
    production consumers should obtain snapshots through Decoder rather than raw input.
    """

    game_over: bool
    player_count: int
    player: int
    ball: int
    scores: tuple[int, ...]


class Decoder:
    """Reusable map decoder; each decode replaces memory, never merges snapshots."""

    def __init__(self, mapping, rom):
        if rom not in mapping["_metadata"]["roms"]:
            raise ValueError("ROM revision is not covered by this map")
        if mapping["_metadata"]["platform"] != "williams-wpc-12K":
            raise ValueError("This adapter only qualifies the WPC 12K layout")
        self.parser = upstream.ParseNVRAM(mapping)
        self.fields = {
            key: self.parser.get_entry(section="game_state", key=key)
            for key in ("game_over", "player_count", "current_player", "current_ball")
        }
        # get_entry(key='scores') returns ONE slot. Preserve all four instead.
        self.scores = [
            entry for entry in self.parser.mapping if entry.section == "game_state" and entry.key == "scores"
        ]
        if any(value is None for value in self.fields.values()) or len(self.scores) != 4:
            raise ValueError("Incomplete pilot game-state mapping")

    def decode(self, memory):
        """Return an immutable Snapshot from complete bytes or raise ValueError.

        Input must be WPC RAM-only or full RAM plus PinMAME trailer. Invalid BCD,
        missing fields and inconsistent active state are rejected, not zeroed.
        """
        if len(memory) not in (0x3000, 0x302E):
            raise ValueError("Unexplained WPC snapshot length")
        # Each input is a complete snapshot. Upstream merges sparse memory, so
        # reset it to prevent a previous full dump's trailer surviving RAM-only input.
        self.parser.memory = upstream.SparseMemory()
        self.parser.set_nvram(bytearray(memory))
        values = {key: checked_value(entry, self.parser.memory) for key, entry in self.fields.items()}
        over = bool(values["game_over"])
        count, player, ball = (values[key] for key in ("player_count", "current_player", "current_ball"))
        if not 0 <= count <= 4:
            raise ValueError("Invalid player count")
        if not over and not (1 <= player <= count and 1 <= ball <= 9):
            raise ValueError("Transient or invalid active game state")
        scores = tuple(checked_value(entry, self.parser.memory) for entry in self.scores)
        if any(not 0 <= score <= 9999999999 for score in scores):
            raise ValueError("Score outside five-byte BCD range")
        return Snapshot(over, count, player, ball, scores)


def decode_snapshot(memory, mapping, rom):
    """Decode one complete snapshot with a newly validated map/ROM decoder."""
    return Decoder(mapping, rom).decode(memory)
