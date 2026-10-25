"""SDK 2.0.4 adapter. Requires a matching native library and provider config.

No bundled example credentials, network calls at import, or remote controls.
This adapter must be validated against a real SDK before production use.
"""

import os
import queue
from pathlib import Path

from .qr import write_qr


class SDK:
    """Experimental native SDK owner with queued callbacks and private file output.

    Construction needs provisioned config and a matching native library. The
    runtime directory and key path must be caller-owned and outside publication.
    Offline tests replace the SDK; they do not qualify native/service behavior.
    """

    def __init__(self, config, runtime):
        import scorbit

        if scorbit.__version__ != "2.0.4":
            raise RuntimeError("Expected Scorbit SDK 2.0.4")
        self.module = scorbit
        self.runtime = Path(runtime)
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.events = queue.SimpleQueue()
        self.links = {}
        self.paired = False
        # A previous bridge run's images do not establish current auth/claims.
        for name in ("pair", "claim-1", "claim-2", "claim-3", "claim-4"):
            self._publish(name, "")
        key_path = Path(config["device_key_path"])
        key_path.parent.mkdir(parents=True, exist_ok=True)

        def save_key(key):
            temp = key_path.with_suffix(".tmp")
            temp.write_text(key, encoding="utf-8")
            os.replace(temp, key_path)

        def event(ev):
            # Copy callback data; native event pointers expire after callback.
            if ev.type == scorbit.EventType.PairingStatusChanged:
                self.events.put(("paired", ev.get_pairing_status_changed()))
            elif ev.type == scorbit.EventType.PlayersUpdated:
                players = ev.get_players_updated() or {}
                self.events.put(("players", {n: p.claim_deeplink for n, p in players.items()}))

        c = scorbit.Config()
        c.set_provider(config["provider"])
        c.set_machine_id(int(config["machine_id"]))
        c.set_hostname(config["hostname"])
        c.set_game_code_version("vpx-scorbit-0.1.0")
        c.set_encrypted_key(config["encrypted_provider_key"])
        c.set_load_key_callback(lambda: key_path.read_text(encoding="utf-8") if key_path.exists() else "")
        c.set_save_key_callback(save_key)
        c.set_event_callback(event)
        self.config = c  # Retain callback references for the entire SDK lifetime.
        self.gs = scorbit.create_game_state(c)

    def apply(self, events):
        """Apply ordered lifecycle events; callers must provide final scores before finish.

        Finishing can commit immediately. Abort raises instead of submitting a
        completed game. This method can perform SDK/network operations.
        """
        for kind, value in events:
            if kind == "start":
                self.gs.set_game_started(self.module.GameStartOrigin.StartButton)
            elif kind == "scores":
                for seat, score in enumerate(value.scores[: value.player_count], 1):
                    self.gs.set_score(seat, score)
                if not value.game_over:
                    self.gs.set_active_player(value.player)
                    self.gs.set_current_ball(value.ball)
            elif kind == "finish":
                # This commits immediately: final scores must precede it.
                self.gs.set_game_finished()
                for seat in range(1, 5):
                    self._publish(f"claim-{seat}", "")
            elif kind == "abort":
                raise RuntimeError("ROM reset detected; stop without submitting a completed game")

    def tick(self):
        """Commit SDK state, drain copied callback data and refresh private QR images."""
        self.gs.commit()
        while not self.events.empty():
            kind, value = self.events.get()
            if kind == "paired":
                self.paired = bool(value)
                if not self.paired:
                    for seat in range(1, 5):
                        self._publish(f"claim-{seat}", "")
            else:
                for seat in range(1, 5):
                    self._publish(f"claim-{seat}", value.get(seat, ""))
        self._publish("pair", "" if self.paired else self.gs.pair_deeplink)

    def _publish(self, name, link):
        if self.links.get(name) == link:
            return
        path = self.runtime / (name + ".png")
        if link:
            write_qr(link, path)
        else:
            path.unlink(missing_ok=True)
        self.links[name] = link

    def close(self):
        """Destroy the owned SDK state; do not synthesize a game-finished event."""
        self.gs.destroy()
