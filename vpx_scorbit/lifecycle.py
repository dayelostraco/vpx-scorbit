"""Conservative pilot lifecycle: observe attract before accepting a game.

Two consistent active snapshots confirm start; two identical snapshots confirm
end. Disconnect or reset is never an
inferred completed game. Reconnect requires a fresh attract observation.
"""


class Lifecycle:
    """Offline two-snapshot reference model; the embedded VBS host uses elapsed time.

    Consumes validated immutable Snapshots and returns ordered event tuples. This
    class does not perform I/O or interpret an interrupted stream as a finished game.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Forget prior observations and require fresh attract evidence; emit no finish."""
        self.armed = False
        self.active = False
        self.previous = None
        self.previous_active = None
        self.last_scores = ()

    def feed(self, snap):
        """Return ordered (kind, value) events for a validated snapshot.

        A finish is preceded by final scores in the same result. Score/seat
        regression emits abort; callers must stop without submitting completion.
        """
        stable = snap == self.previous
        self.previous = snap
        if not self.active:
            if snap.game_over:
                self.previous_active = None
                if stable:
                    self.armed = True
                return []
            active_stable = self.previous_active is not None and self.previous_active == (
                snap.player_count,
                snap.player,
                snap.ball,
            )
            self.previous_active = (snap.player_count, snap.player, snap.ball)
            if snap.player != 1 or snap.ball != 1:
                self.armed = False
            if not self.armed or not active_stable:
                return []
            self.active = True
            self.armed = False
            self.last_scores = snap.scores[: snap.player_count]
            return [("start", None), ("scores", snap)]
        if snap.game_over:
            if not stable:
                return []
            # An unexpected loss of seats or score reset isn't a valid finish.
            if self._regressed(snap):
                self.reset()
                return [("abort", "score/player reset")]
            self.active = False
            self.armed = True
            self.last_scores = ()
            return [("scores", snap), ("finish", None)]
        if self._regressed(snap):
            self.reset()
            return [("abort", "score/player reset")]
        self.last_scores = snap.scores[: snap.player_count]
        return [("scores", snap)]

    def _regressed(self, snap):
        return snap.player_count < len(self.last_scores) or any(
            new < old for new, old in zip(snap.scores, self.last_scores, strict=False)
        )
