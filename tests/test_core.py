import json
import unittest
from pathlib import Path

from vpx_scorbit.lifecycle import Lifecycle
from vpx_scorbit.memory import Decoder, Snapshot, decode_field, decode_snapshot
from vpx_scorbit.sdk import SDK

MAP = json.loads((Path(__file__).parents[1] / "maps/mm_109.map.json").read_text())


class CoreTests(unittest.TestCase):
    def test_large_bcd_and_invalid_digits(self):
        field = {"start": 0, "length": 5, "encoding": "bcd"}
        self.assertEqual(decode_field(bytes.fromhex("9876543210"), field), 9876543210)
        with self.assertRaises(ValueError):
            decode_field(bytes.fromhex("00a0000000"), field)
        with self.assertRaises(ValueError):
            decode_field(b"\0", field)

    def test_map_and_bounds(self):
        data = bytearray(12334)
        data[135] = 1
        data[5901] = 1
        data[5792:5797] = bytes.fromhex("0024697230")
        self.assertEqual(decode_snapshot(data, MAP, "mm_109b").scores, (24697230, 0, 0, 0))
        with self.assertRaises(ValueError):
            decode_snapshot(data, MAP, "mm_10")
        data[135] = 0
        with self.assertRaises(ValueError):
            decode_snapshot(data, MAP, "mm_109b")

    def test_late_attach_does_not_create_game(self):
        tracker = Lifecycle()
        game = Snapshot(False, 1, 1, 2, (12345,))
        self.assertEqual(tracker.feed(game), [])
        self.assertEqual(tracker.feed(game), [])

    def test_final_scores_before_finish_multiplayer(self):
        tracker = Lifecycle()
        attract = Snapshot(True, 0, 0, 0, ())
        tracker.feed(attract)
        tracker.feed(attract)
        game = Snapshot(False, 1, 1, 1, (0,))
        self.assertEqual(tracker.feed(game), [])
        self.assertEqual([e[0] for e in tracker.feed(game)], ["start", "scores"])
        game = Snapshot(False, 2, 2, 3, (100, 200))
        self.assertEqual(tracker.feed(game), [("scores", game)])
        end = Snapshot(True, 2, 0, 0, (110, 250))
        self.assertEqual(tracker.feed(end), [])
        self.assertEqual(tracker.feed(end), [("scores", end), ("finish", None)])
        self.assertEqual(tracker.feed(end), [])

    def test_reset_aborts_without_finish(self):
        tracker = Lifecycle()
        attract = Snapshot(True, 0, 0, 0, ())
        tracker.feed(attract)
        tracker.feed(attract)
        game = Snapshot(False, 1, 1, 1, (100,))
        tracker.feed(game)
        tracker.feed(game)
        self.assertEqual(tracker.feed(Snapshot(False, 1, 1, 1, (0,)))[0][0], "abort")
        self.assertFalse(tracker.active)

    def test_sdk_final_score_order(self):
        calls = []

        class FakeGame:
            def set_score(self, seat, score):
                calls.append(("score", seat, score))

            def set_game_finished(self):
                calls.append(("finish",))

        adapter = SDK.__new__(SDK)
        adapter.gs = FakeGame()
        adapter._publish = lambda *args: None
        adapter.apply([("scores", Snapshot(True, 2, 0, 0, (123, 456, 0, 0))), ("finish", None)])
        self.assertEqual(calls, [("score", 1, 123), ("score", 2, 456), ("finish",)])

    def test_start_accepts_changing_scores(self):
        tracker = Lifecycle()
        attract = Snapshot(True, 0, 0, 0, ())
        tracker.feed(attract)
        tracker.feed(attract)
        tracker.feed(Snapshot(False, 1, 1, 1, (0,)))
        events = tracker.feed(Snapshot(False, 1, 1, 1, (100,)))
        self.assertEqual(events[0][0], "start")

    def test_four_slots_and_trailer_preserved(self):
        raw = bytearray(0x302E)
        raw[135] = 1
        raw[5901] = 4
        for address, value in zip(
            (5792, 5798, 5804, 5810), ("0012345678", "0000000001", "0000900000", "9999999999"), strict=False
        ):
            raw[address : address + 5] = bytes.fromhex(value)
        raw[0x3000:] = bytes(range(46))
        decoder = Decoder(MAP, "mm_109b")
        self.assertEqual(decoder.decode(raw).scores, (12345678, 1, 900000, 9999999999))
        self.assertEqual(decoder.parser.get_dot_nv(), raw)
        raw[5810] = 0xFA
        decoder.parser.set_nvram(raw)
        # Upstream's display-oriented conversion accepts invalid BCD; wrapper doesn't.
        self.assertIsInstance(decoder.scores[3].get_value(decoder.parser.memory), int)
        with self.assertRaises(ValueError):
            decoder.decode(raw)


if __name__ == "__main__":
    unittest.main()
