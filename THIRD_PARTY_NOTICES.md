# Third-party notices

The root MIT license covers original project code and documentation. It does
not replace the licenses of included upstream files or externally installed
dependencies. Preserve upstream notices when adapting or distributing them.

We gratefully acknowledge Tom Collins and the memory-map/parser contributors,
the Scorbit team at Spinner Systems and its contributors, the Visual Pinball and
PinMAME communities, and the authors of the existing table integrations studied
during development. See the [README acknowledgments](README.md#acknowledgments-and-upstream-projects)
for their projects and the specific roles they play here.

| Component | Source/provenance | Terms and location |
|---|---|---|
| ROM map and platform data | [Tom Collins and contributors](https://github.com/tomlogic/pinball-memory-maps), commit `f0c422099f0b50b69bfdf6d071a6653a8b25a6fd` | ODbL / DbCL; `maps/LICENSE-ODbL.md`, `maps/LICENSE-DbCL` |
| Python NVRAM parser | [Tom Collins](https://github.com/tomlogic/py-pinmame-nvmaps), commit `4a8d77c39badb8fd893672238b90b541ed056581` | LGPL-3.0-or-later; original headers and `third_party/pinmame_nvmaps/LICENSE` retained |
| Optional Scorbit SDK wrapper | [Scorbit SDK](https://github.com/scorbit-io/scorbit_sdk), Spinner Systems, Inc. (DBA Scorbit) and contributors; Python dependency `scorbit==2.0.4` | Upstream MIT; fetched separately, native SDK not bundled |
| Other Python dependencies | `requirements.txt` | Installed separately; retain their own distribution notices |
| Legacy sToken / sQRCode / QRView helpers | External existing-table tooling; `packaging/helpers.lock.json` records observed hashes | Not included. Redistribution terms must be confirmed before a helper package is published |

The generated decoder is derived from map data; retain the map provenance and
licenses with generated integration material. The map audit is a discovery
report, not a list of supported Scorbit tables.

No ROMs, VPX tables, helper executables, native SDK library, private keys, device
tokens or account state are distributed in this source repository. The Scorbit
VPX plugin ([upstream repository](https://github.com/scorbit-io/vpx-scorbit-plugin))
is a separately licensed upstream project; its GPL-3.0 license is
distinct from the SDK's MIT license. This project does not bundle its source.
