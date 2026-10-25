"""Read staged VPX telemetry, defaulting to an offline event monitor."""

import argparse
import json
import time
from pathlib import Path

from .lifecycle import Lifecycle
from .memory import Decoder


def main():
    """Poll complete telemetry files offline unless --sdk-config explicitly enables SDK I/O.

    Ignore transient invalid samples; a stale active stream raises without finish.
    Keyboard interrupt closes the optional SDK without manufacturing a completed game.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--map", type=Path, default=Path(__file__).parents[1] / "maps/mm_109.map.json")
    ap.add_argument("--rom", default="mm_109b")
    ap.add_argument("--sdk-config", type=Path, help="Explicit opt-in to authenticated SDK networking")
    args = ap.parse_args()
    mapping = json.loads(args.map.read_text())
    decoder = Decoder(mapping, args.rom)
    tracker = Lifecycle()
    sdk = None
    if args.sdk_config:
        from .sdk import SDK

        sdk = SDK(json.loads(args.sdk_config.read_text()), args.runtime)
    stamp = None
    last_seen = time.monotonic()
    try:
        while True:
            if time.monotonic() - last_seen > 2:
                if tracker.active:
                    raise RuntimeError("Telemetry disconnected during game; no finish submitted")
                tracker.reset()
            source = args.runtime / "nvram.hex"
            try:
                stat = source.stat()
                if time.time() - stat.st_mtime > 2:
                    if tracker.active:
                        raise RuntimeError("Telemetry disconnected during game; no finish submitted")
                    tracker.reset()
                    time.sleep(0.2)
                    continue
                if stat.st_mtime_ns != stamp:
                    raw = bytes.fromhex(source.read_text())
                    if len(raw) != 0x302E:
                        raise ValueError("Expected complete live WPC handler image")
                    snapshot = decoder.decode(raw)
                    events = tracker.feed(snapshot)
                    if sdk:
                        sdk.apply(events)
                    for kind, value in events:
                        print(kind, value, flush=True)
                    stamp = stat.st_mtime_ns
                    last_seen = time.monotonic()
            except FileNotFoundError:
                pass  # Writer publishes by rename; retry the brief publication gap.
            except ValueError:
                # ROM boot/reset can expose zero or inconsistent fields. Never
                # feed them to the lifecycle; an ongoing invalid stream times out.
                pass
            if sdk:
                sdk.tick()
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        if sdk:
            sdk.close()


if __name__ == "__main__":
    main()
