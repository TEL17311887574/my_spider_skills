# Universal Reverse Loop (Full Phases)

## Phase 0: Fingerprint before deep work

Classify the target before reading giant bundles:

- decoy endpoint vs real endpoint
- wrapper rewrite vs visible param
- patched helper vs standard helper
- signer-gated vs verifier-gated vs decode-gated vs session-gated
- bootstrap asset vs direct data API
- plain JSON vs GraphQL vs WebSocket vs binary envelope
- single-shot replay vs stateful session with pairing, auth, or warm-up frames
- direct response vs encoded response vs glyph-mapped response
- page-specific exception vs whole-flow exception
- session-bound vs anonymous
- clean-baseline-first vs trace-first vs decode-first vs transcript-first
- rotating-cookie provenance known vs unknown
- JSVMP or heavy obfuscation vs normal packed bundle

Goal: choose the smallest next proof and the least destructive first instrument, not the biggest code dump.

## Phase 1: Identify the true request path

- follow redirects
- inspect wrapper pages and compatibility pages
- separate visible page routes from real wire routes
- map bootstrap requests, list requests, detail requests, submission requests, and risk-control requests
- detect whether one endpoint serves both bootstrap and final data in separate phases

Deliverable for this phase: one confirmed request that is definitely on the real business path.

## Phase 2: Classify the moving parts

For the real request, classify each changing field:

- static header
- rotating header
- static cookie
- rotating cookie
- timestamp
- nonce or random fragment
- signed body or query
- transport envelope, operation name, or message type
- compressed or binary response format
- decode key, glyph map, or response-side transform
- encrypted response
- page-specific exception
- account-bound session dependency
- bootstrap artifact dependency
- login or pairing bootstrap artifact
- session key schedule or exported secret material
- heartbeat, ack, counter, or message-tag state
- media-key derivation or side-channel download secret

Goal: separate what must be reproduced from what is just noise.

## Phase 3: Locate the canonical mutation point

Look in this order:

1. transport wrappers such as `$.ajaxSetup`, `beforeSend`, fetch wrappers, interceptors
2. bootstrap side scripts and inline payloads
3. page-exposed helper functions
4. WebAssembly exports
5. server-returned JS challenges
6. response-side refresh fields that seed the next request
7. handshake transcripts, frame serializers, binary node encoders, protobuf parsers, or session key schedules

Rule: the canonical mutation point is where the wire payload actually changes, not where the business code first creates a placeholder.

## Phase 4: Rebuild the moving parts offline

Choose the cheapest valid offline shape:

1. pure Python
2. Python plus isolated JS signer
3. Python plus minimal local JS or WASM helper
4. Python plus local challenge bootstrap executor
5. Python plus local font decoder

Never add browser automation to the final path.

## Phase 5: Prove repeatability

Do not call it solved until:

- the same logic succeeds at least 2 to 3 times
- pagination advances correctly
- final fields are complete
- dynamic state regenerates correctly
- account-bound constraints are documented
