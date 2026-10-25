# Medieval Madness capability evidence

ROM: mm_109b. Map: upstream mm_109 at f0c422099f0b50b69bfdf6d071a6653a8b25a6fd.
The same-ROM map names alone do not qualify any other table or revision.

| Input | Source | Current evidence | Submission status |
|---|---|---|---|
| Four player scores | Five-byte BCD, offsets 5792/5798/5804/5810 | Real attract snapshot; four distinct seats and large values tested offline in actual VBScript | No live-game upload |
| Player count | Offset 5901 | Attract observed; synthetic lifecycle tests | Gameplay unqualified |
| Current player / ball | Offsets 946/947 | Attract observed; synthetic transitions | Gameplay unqualified |
| Game-over flag | Offset 135 | Boot and attract transitions observed | Final-bonus timing unqualified |
| Extra balls / extra balls this ball | Offsets 948/949 | Upstream mapped, not live-qualified | Not emitted |
| Credits / free-play / configured balls | Upstream game_state fields | Map discovery only | Legacy entry route does not expose a dedicated credits field in inspected clients |
| Castle, trolls, multiballs, wizard modes | Require verified current-game RAM/lamps/switch evidence | No validated mode adapter yet | Not emitted |
| Historic high scores / audits / champions | Upstream map sections | Historical/cumulative fields | Not substituted for live events |

Inspected donor clients send current player scores, ball/player and a game_modes
string. The common queue currently emits scores and ball/player, not modes;
see [implemented protocol and open questions](protocol.md). Mode strings are not proof that every SDK 2.x feature
exists in this older protocol. No achievements are invented from score jumps,
ball counts, physical switch closures, or historical audit values.

Offline synthetic inputs used during diagnostics must never be uploaded. The
current common pilot embeds a false network flag and zero catalog ID. Normal
play could not be focused through the unavailable computer-use connection;
attract capture did not confirm accepted coin/start input. Saved ROM state was
restored after those tests. Full-game, extra-ball, multiplayer, tilt, reset and
final-bonus verification remains necessary.
