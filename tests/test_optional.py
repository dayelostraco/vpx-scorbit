"""Offline contracts for optional Python tools; never load the native SDK."""

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from vpx_scorbit import bridge
from vpx_scorbit.memory import Snapshot
from vpx_scorbit.qr import write_qr
from vpx_scorbit.sdk import SDK


class OptionalToolTests(unittest.TestCase):
    def test_qr_atomic_output_and_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "qr.png"
            write_qr("urn:offline:fixture", path)
            self.assertTrue(path.read_bytes().startswith(b"\x89PNG"))
            self.assertFalse(path.with_suffix(".tmp.png").exists())
            for bad in ("", "bad\nlink", "bad\rlink"):
                with self.assertRaises(ValueError):
                    write_qr(bad, path)

    def test_sdk_callback_lifetime_keys_and_events(self):
        module = MagicMock()
        module.__version__ = "2.0.4"
        module.create_game_state.return_value.pair_deeplink = "urn:offline:pair"
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(sys.modules, scorbit=module),
            patch("vpx_scorbit.sdk.write_qr") as render,
        ):
            root = Path(directory)
            config = {
                "device_key_path": str(root / "key"),
                "provider": "offline",
                "machine_id": 1,
                "hostname": "offline.invalid",
                "encrypted_provider_key": "fixture",
            }
            adapter = SDK(config, root)
            callbacks = module.Config.return_value
            load = callbacks.set_load_key_callback.call_args.args[0]
            save = callbacks.set_save_key_callback.call_args.args[0]
            event = callbacks.set_event_callback.call_args.args[0]
            self.assertEqual(load(), "")
            save("offline-fixture")
            self.assertEqual(load(), "offline-fixture")
            self.assertFalse((root / "key.tmp").exists())
            adapter.tick()
            render.assert_called_with("urn:offline:pair", root / "pair.png")
            ev = MagicMock()
            ev.type = module.EventType.PairingStatusChanged
            ev.get_pairing_status_changed.return_value = True
            event(ev)
            ev.type = module.EventType.PlayersUpdated
            players = {1: types.SimpleNamespace(claim_deeplink="urn:offline:claim")}
            ev.get_players_updated.return_value = players
            event(ev)
            players[1].claim_deeplink = "changed after callback"
            adapter.tick()
            self.assertTrue(adapter.paired)
            self.assertEqual(adapter.links["claim-1"], "urn:offline:claim")
            ev.type = module.EventType.PairingStatusChanged
            ev.get_pairing_status_changed.return_value = False
            event(ev)
            adapter.tick()
            self.assertEqual(adapter.links["claim-1"], "")
            ev.type = module.EventType.PlayersUpdated
            ev.get_players_updated.return_value = None
            event(ev)
            ev.type = "unknown"
            event(ev)
            adapter.tick()
            adapter.apply(
                [
                    ("start", None),
                    ("scores", Snapshot(False, 2, 2, 1, (100, 200))),
                    ("scores", Snapshot(True, 2, 0, 0, (110, 220))),
                    ("finish", None),
                ]
            )
            adapter.gs.set_active_player.assert_called_once_with(2)
            adapter.gs.set_game_finished.assert_called_once()
            with self.assertRaises(RuntimeError):
                adapter.apply([("abort", None)])
            adapter.close()
            adapter.gs.destroy.assert_called_once()
            module.__version__ = "wrong"
            with self.assertRaises(RuntimeError):
                SDK(config, root)

    def test_bridge_offline_missing_invalid_stale_and_sdk(self):
        # One bounded loop per case; clock and SDK are controlled, memory decode
        # remains real. KeyboardInterrupt exercises orderly close, not game finish.
        for case in ("missing", "invalid", "short", "stale", "valid", "sdk", "stale_active", "gap_active"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / "nvram.hex"
                raw = bytearray(0x302E)
                raw[135] = 1
                if case != "missing":
                    source.write_text("bad-hex" if case == "invalid" else ("00" if case == "short" else raw.hex()))
                if case in ("stale", "stale_active"):
                    os.utime(source, (1, 1))
                argv = ["bridge", "--runtime", str(root)]
                if case == "sdk":
                    (root / "config.json").write_text("{}")
                    argv += ["--sdk-config", str(root / "config.json")]
                tracker = MagicMock(active=case.endswith("_active"))
                tracker.feed.return_value = [("scores", Snapshot(True, 1, 0, 0, (0,)))]
                with (
                    patch.object(sys, "argv", argv),
                    patch.object(bridge.time, "sleep", side_effect=KeyboardInterrupt),
                    patch.object(bridge.time, "monotonic", side_effect=[0, 3, 3]),
                    patch.object(bridge, "Lifecycle", return_value=tracker),
                    patch("vpx_scorbit.sdk.SDK") as sdk,
                ):
                    if case.endswith("_active"):
                        # stale-active must reach the file-age branch, not gap.
                        with patch.object(
                            bridge.time, "monotonic", side_effect=[0, 0] if case == "stale_active" else [0, 3]
                        ):
                            with self.assertRaisesRegex(RuntimeError, "no finish submitted"):
                                bridge.main()
                    else:
                        bridge.main()
                    if case == "sdk":
                        sdk.return_value.apply.assert_called_once()
                        sdk.return_value.close.assert_called_once()
                    else:
                        sdk.assert_not_called()
