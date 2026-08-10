# Verification Gates

Do not mark complete until all relevant gates pass:

- startup gate completed and updated if the target classification changed
- request path confirmed
- moving parts classified
- target family classified and initial routing recorded
- canonical mutation point identified
- first-pass `chrome-devtools` evidence captured for the target
- first-pass preferred reverse MCP evidence captured for the target: CloakBrowser when available, otherwise js-reverse fallback
- CloakBrowser capability coverage recorded when used: CDP-native network/initiator, request interception, source/SourceMap, Debugger/breakpoints/paused scope, WebSocket, environment/fingerprint, Hook/JSVMP/instrumentation, cookie/storage/state, heap/artifacts, and offline signer verification
- `js-reverse` fallback evidence captured when CloakBrowser is unavailable, unstable, blocked, or needs second-source validation; otherwise fallback status recorded as not needed
- clean baseline captured before invasive tooling when the target is verifier-gated or behavior-sensitive
- helper outputs verified on fixed inputs
- structured transport rules documented when the target is not plain JSON
- response decode steps are local and repeatable when the payload is not directly readable
- fixed-sample checks exist for local decoders when decode is part of the contract
- bootstrap artifact replay confirmed when public routes still require key, config, cookie, or wrapper seeding
- cookie provenance proven when rotating cookies gate replay
- login or pairing bootstrap replay confirmed when the target needs a warm session before business traffic
- key schedule or session-secret derivation verified on captured samples when the stream is encrypted
- heartbeat, ack, counter, or message-tag rules documented when the stream is stateful
- raw frame parsing and business decode proven on at least one exact captured frame
- media-key derivation documented when file download or decryption uses separate secrets
- live replay succeeds repeatedly
- pagination or cursor advance confirmed
- account-bound constraints documented
- list-versus-detail permission boundaries documented when access levels differ
- page-specific exceptions documented
- final Python collector runs without browser automation or browser profiles
- final JS helper, if any, runs locally without browser automation or DOM dependence
- final delivery does not depend on CloakBrowser, CDP endpoints, persistent profiles, or browser-side storage
- output saved in the requested format
