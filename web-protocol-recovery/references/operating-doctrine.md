# Operating Doctrine

## Doctrine 1: Trust the wire, not the page text

- Real request paths beat page hints.
- Real headers beat visible business code.
- Real cookies beat guessed token stories.
- Real response shape beats archived notes.

## Doctrine 2: The dynamic parameter is not always a signature

The real moving part may be:

- a cookie
- a page-specific header
- a transport envelope
- a server-returned JS bootstrap
- a dynamic font
- a WebAssembly export
- a transport wrapper rewrite
- a response-side decoder
- an account-bound session contract

Do not assume every hard target is solved by hunting a `sign` function.

## Doctrine 3: Fixed-input validation beats naming

If a page helper is called `md5` or `btoa`, prove it on fixed inputs before trusting the name.

Minimum standard for suspicious helpers:

1. pick a fixed input such as `"abc"` or a captured timestamp
2. record browser output
3. record local output
4. compare intermediate values, not just final output

## Doctrine 4: Narrow exceptions stay narrow

If only one page needs a special `User-Agent`, or only one request needs a rotated cookie, encode that exception explicitly. Do not poison the entire collector with a fake "browser-only" conclusion.

## Doctrine 5: Automation is not an acceptable crutch

When stuck, do more protocol work:

- diff requests
- extract inline scripts
- run bootstrap JS locally
- port helper logic
- instantiate WASM locally
- decode fonts locally

Do not fall back to browser automation as delivery.

## Doctrine 6: Environment mismatch is evidence

When local output and live output disagree, treat the mismatch as evidence:

- compare fixed inputs
- compare side assets
- compare patched helpers
- compare environment branches

Do not hand-wave the mismatch away as "probably browser-only".

## Doctrine 7: Delivery gates outrank convenience

If the only known path still depends on live page context, the task is not done.

- a browser profile is not a protocol artifact
- a hidden refresh click is not a collector
- an unexplained decoder is not acceptable handoff

Keep reversing until the moving parts are local, explicit, and testable.

## Doctrine 8: Public does not mean unsigned

Anonymous pages still have protocol contracts.

- a public list may still require entry-route cookies
- a bootstrap endpoint may still return the key, config, or envelope seed
- list visibility does not prove detail or submit visibility

Treat anonymous access, envelope construction, and permission boundaries as separate questions.

## Doctrine 9: Stateful streams are protocol, not browser magic

If the target only becomes readable after login, pairing, or a warm-up WebSocket exchange, the session transcript is part of the protocol.

- pairing or login bootstrap is not UI fluff
- handshake outputs are protocol artifacts
- heartbeats, ack frames, counters, and reconnect rules are part of the collector

Do not collapse a stateful stream problem into a fake single-request sign story.

## Doctrine 10: Observer effect is real

Some targets get harder after you touch them.

- verifier-gated or behavior-sensitive flows may change once hooks, breakpoints, or monkey patches are installed
- capture one clean baseline request and response before invasive instrumentation
- prefer initiator stacks, request diffs, and narrow boundary hooks before broad global hooks
- if hooking changes the failure mode, treat that as evidence that your tooling is perturbing the target

Do not confuse hook-induced breakage with proof that the site is "browser-only".

## Doctrine 11: Cookie provenance beats cookie superstition

When a cookie gates replay, prove where it came from:

- `Set-Cookie` on a protocol response
- `document.cookie` from page code
- server-returned challenge or bootstrap JS
- redirect wrappers, iframes, workers, or SDK side effects
- a derived header or token that only looks like a cookie problem

Do not hardcode a rotating business cookie before proving its writer and refresh path.
