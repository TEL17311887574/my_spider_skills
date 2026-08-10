# Skill Validation

When modifying this skill itself, validate against the official self-test suite before calling the edit complete.

Pass conditions:

- the route stays protocol-first
- every fresh target begins with the best available browser evidence plane: `Camoufox + CloakBrowser` reconnaissance stack preferred, one selected browser context per fixed sample baseline, single fingerprint browser fallback, then `js-reverse-mcp`, then `chrome-devtools-mcp`, then manual samples
- Camoufox availability is checked for environment/fingerprint/property-access evidence; `cloakbrowser-reverse-mcp` availability is checked and, when available, its full relevant capability groups are supported through `references/cloakbrowser-mcp-playbook.md`: CDP-native network/initiator, interception, source/SourceMap, Debugger, WebSocket, Chromium environment/fingerprint, Hook/JSVMP/instrumentation, cookie/storage/state, heap/artifacts, and offline signer verification
- `js-reverse` and `chrome-devtools` are treated as fallback or second-source validation, not as mandatory fresh-target gates
- final delivery never depends on browser automation
- final delivery is Python collector first, with JS limited to local parameter restoration only
- minimal missing evidence is requested instead of broad homework for the user
- the chosen references match the real symptom instead of generic cargo-cult loading
- output reports the real endpoint, real moving parts, and proof artifacts
- structured transport, decode chains, stateful sessions, and delivery gates are handled correctly when present
