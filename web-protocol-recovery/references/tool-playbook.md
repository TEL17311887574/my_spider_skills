# Tool playbook

Use this file as the fast map from reverse-engineering task to tool choice.

## Preferred order

1. Capture one clean baseline request.
2. Find the real request.
3. Trace the initiator.
4. Diff the moving fields.
5. Add the narrowest runtime proof that still preserves the sample.
6. Reproduce one stable request.
7. Scale collection only after the first request is repeatable.

Prefer clean baselines, initiator stacks, and narrow proofs over broad hooks. Prefer focused source reads over loading giant bundles into context.

## Recon and network capture

### Unified Browser Recon Fallback

Use this order for fresh targets and tool failures:

1. `Camoufox + CloakBrowser`: Camoufox for anti-detection environment/fingerprint evidence and property access; CloakBrowser for CDP-native network, initiators, source, SourceMap, debugger, WebSocket, hooks, JSVMP, state, and offline signer evidence.
2. Single fingerprint browser: if only Camoufox or CloakBrowser is available, use that source as the baseline and record missing capability groups.
3. `js-reverse-mcp`: first fallback when both fingerprint browsers are unavailable, blocked, or unstable.
4. `chrome-devtools-mcp`: second fallback when js-reverse is unavailable.
5. Manual samples: only user-provided HAR/HTML/JS/Cookie/header samples when all browser tools are unavailable.

Do not mix cookies, UA, storage, screen, or request evidence from different browser contexts into one fixed sample. Other tools may provide cross-checks, but the final proof chain needs one baseline source.

### `camoufox-reverse-mcp`

- `check_environment`, `launch_browser`, `navigate`, `reload`, `get_page_info`: start and document the anti-detection browser baseline.
- `compare_env`, `trace_property_access`, `cookies`, `get_storage`, `export_state`: preserve environment, fingerprint, cookie, storage, and actual-property-access evidence.
- `network_capture`, `list_network_requests`, `get_network_request`, `get_request_initiator`: collect request evidence when Camoufox is the survivable browser plane.
- `scripts`, `search_code`, `hook_function`, `inject_hook_preset`, `hook_jsvmp_interpreter`, `instrumentation`: collect runtime proof when the target is sensitive to Chromium/CDP or when engine-level fingerprint trace matters.

Use Camoufox when hostile fingerprinting, environment branches, canvas/WebGL/audio/timing, or JSVMP property reads are the main uncertainty. Camoufox remains reconnaissance only; the final collector must be browser-free.

### `chrome-devtools`

- `navigate_page` / `new_page`: open the page when UI flow evidence matters
- `take_snapshot`: inspect page structure fast
- `wait_for`: wait on target text while triggering filters, search, or pagination
- `list_network_requests` and `get_network_request`: second source of truth when UI flow matters
- `take_screenshot`: capture evidence for hidden panels, captcha gates, or lazy regions

Use browser DevTools when DOM state matters and higher-priority tools are unavailable. Use Camoufox for fingerprint survivability and CloakBrowser for CDP-native runtime evidence.

### `cloakbrowser-reverse-mcp`

Tool names in this section are shorthand for `cloakbrowser-reverse-mcp_*` calls unless the full prefix is shown.

- `check_environment`, `browser_binary_info`, `launch_browser`, `navigate`, `reload`, `wait_for`, `get_page_info`: start and document a stealth CDP-enabled reconnaissance browser.
- `network_capture`, `list_network_requests`, `get_network_request`, `list_cdp_network_requests`, `get_cdp_network_request`: capture Playwright-side and CDP-native request/response evidence.
- `get_request_initiator`, `get_cdp_request_initiator`, `break_on_xhr`: identify request initiators and stop at XHR/Fetch boundaries when wrapper mutation is suspected.
- `intercept_request`: log, block, modify, or mock a narrow request only after clean baseline evidence exists.
- `scripts`, `search_code`, `list_cdp_scripts`, `search_cdp_sources`, `get_cdp_source`, `get_cdp_script_source`, `save_cdp_script_source`: inspect and preserve the smallest useful script evidence.
- `list_source_maps`, `get_source_map`, `get_source_map_source`: recover original source when source maps exist.
- `cdp_enable_debugger`, `cdp_status`, `set_breakpoint_on_text`, `set_cdp_breakpoint`, `get_paused_info`, `evaluate_on_paused`, `step_debugger`, `resume_debugger`, `set_cdp_skip_all_pauses`: prove pre-sign strings, keys, payload mutations, and anti-debug behavior at the breakpoint.
- `websocket_capture`, `list_websockets`, `get_websocket_connection`, `get_websocket_messages`: capture, group, and preserve WebSocket handshakes and frames.
- `compare_env`, `cookies`, `get_storage`, `export_state`, `import_state`: prove environment, cookie, storage, and session-state provenance without making browser state a final dependency.
- `hook_function`, `inject_hook_preset`, `instrumentation`, `hook_jsvmp_interpreter`, `remove_hooks`, `get_console_logs`: add narrow runtime, crypto, XHR/fetch, cookie, WebSocket, debugger-bypass, and JSVMP proof after a clean baseline exists.
- `verify_signer_offline`: verify a candidate signer against captured fixed samples before porting it.
- `capture_heap_snapshot`, `take_screenshot`, `capture_screenshot_cdp`, `list_trace_files`, `query_trace_file`, `trace_property_access`: preserve heavy/runtime artifacts only when normal request, source, or fixed-input evidence is insufficient; note that CloakBrowser has no Camoufox-style engine trace.

Use CloakBrowser as the primary CDP reverse plane for JavaScript runtime evidence, CDP-native network/initiators, request interception, hooks, stealth Chromium fingerprinting, SourceMap/source access, WebSocket capture, debugger control, JSVMP instrumentation, cookie/storage/session state proof, heap/artifacts, and offline signer verification. Pair with Camoufox when engine-level fingerprint/property evidence matters. See `references/cloakbrowser-mcp-playbook.md` for the full capability map. CloakBrowser remains reconnaissance only; the final collector must be browser-free.

### `js-reverse` fallback

Tool names in this section are shorthand for `js-reverse-mcp_*` calls.

- Use only when both Camoufox and CloakBrowser are unavailable, unstable, blocked by the target, or when a second runtime evidence source is needed.
- `new_page` / `navigate_page`: open the target and follow the real landing URL.
- `list_network_requests(reqid=...)` and `get_request_initiator`: cross-check chosen requests and caller stacks.
- `list_scripts`, `search_in_sources`, `get_script_source`, `save_script_source`: cross-check source locations.
- `break_on_xhr`, `set_breakpoint_on_text`, `get_paused_info`, `evaluate_script(frameIndex=...)`: fallback debugger proof.
- `get_websocket_messages(analyze=true)`: fallback WebSocket grouping.

Use browser DevTools when DOM state matters and higher-priority tools are unavailable. Use Camoufox when hostile fingerprint survivability or property access matters. Use CloakBrowser when JavaScript runtime, request initiators, hooks, CDP evidence, or SourceMap/debugger proof matters. Use `js-reverse` only as fallback/second-source validation.

## Static JS analysis

- CloakBrowser `list_cdp_scripts` or `scripts`: enumerate candidate bundles
- CloakBrowser `search_cdp_sources` or `search_code`: search keywords across all loaded sources
- CloakBrowser `get_cdp_source`: inspect the exact function neighborhood
- CloakBrowser `save_cdp_script_source`: dump a full bundle locally when a file is too large to inspect in slices

Fallback recipes when you wanted a missing helper:

- no `find_in_script`: use CloakBrowser `search_cdp_sources`, then `get_cdp_source`
- no automatic code summary: read the initiator stack first, then the smallest source slice around the mutation point
- no automatic crypto detector: search helper names, compare fixed inputs, and route to `references/crypto-patterns.md`
- no automatic deobfuscator: use CloakBrowser `search_cdp_sources`, `save_cdp_script_source`, and `references/obfuscation-guide.md`
- no Chrome DevTools source map view: use CloakBrowser `list_source_maps`, `get_source_map`, and `get_source_map_source`
- no stable CloakBrowser debugger: use `js-reverse` only as fallback; otherwise prefer CloakBrowser `cdp_enable_debugger`, `set_breakpoint_on_text`, `get_paused_info`, and `evaluate_on_paused`

Keyword packs:

- request path: `"/api/"`, `"graphql"`, `"fetch("`, `"axios"`, `"XMLHttpRequest"`
- signer: `"sign"`, `"token"`, `"nonce"`, `"timestamp"`, `"trace"`, `"x-sign"`, `"beforeSend"`, `"ajaxSetup"`, `"requestId"`
- crypto: `"md5"`, `"sha"`, `"hmac"`, `"aes"`, `"rsa"`, `"crypto.subtle"`
- environment: `"navigator"`, `"canvas"`, `"webgl"`, `"performance"`, `"webdriver"`

## Dynamic validation

Start with a clean baseline. Then use initiator stacks and request diffs. Add runtime proofs only after you know why you are instrumenting.

### Baseline-first proof flow

1. capture one clean request and response pair
2. use CloakBrowser `get_request_initiator` or `get_cdp_request_initiator` to jump from the request to the caller stack
3. use CloakBrowser `search_cdp_sources`, `get_cdp_source`, and source-map tools to inspect the smallest relevant code region
4. use CloakBrowser `hook_function` or `inject_hook_preset` when a named helper is stable enough to trace without poisoning the target
5. use CloakBrowser `break_on_xhr` when you need to stop at the exact request boundary
6. use CloakBrowser `instrumentation` or `hook_jsvmp_interpreter` only for narrow JSVMP/runtime proof that you can justify
7. use Camoufox environment/property evidence when environment mismatch remains unexplained
8. use `js-reverse` only if Camoufox/CloakBrowser evidence is unavailable, unstable, or needs a second-source check
9. fall back to `chrome-devtools` only when js-reverse is unavailable or DOM evidence is sufficient
10. if the target is verifier-gated or behavior-sensitive, remove invasive instrumentation and recapture a clean baseline the moment behavior changes

### Breakpoint tools

- CloakBrowser `set_breakpoint_on_text`: best when the bundle is minified
- CloakBrowser `get_paused_info`: inspect locals and scope
- CloakBrowser `evaluate_on_paused`: print the exact pre-sign string, key, iv, or payload in the paused call frame
- CloakBrowser `resume_debugger`: resume execution after inspection
- CloakBrowser `step_debugger`: only after you already know why you are pausing

## Session and environment handling

- Camoufox `compare_env` / `trace_property_access`: prove environment values and actual JS-visible property reads when fingerprint mismatch is suspected
- CloakBrowser `evaluate_js`: inspect `document.cookie`, storage values, bootstrap globals, or runtime helper outputs
- CloakBrowser `hook_function`, `inject_hook_preset`, and `instrumentation`: patch or observe a narrow environment branch before the page script runs
- CloakBrowser `save_cdp_script_source`: preserve suspicious bundles for offline diffing when environment mismatch remains unclear
- CloakBrowser `compare_env`, `cookies`, `get_storage`, `export_state`, `import_state`: preserve environment and state evidence without treating browser state as final collector state

## Failure routing

- `403`, `412`, `429`: compare headers, cookies, sign freshness, and request pacing
- business error with normal `200`: compare payload assembly order and timestamp precision
- decrypt failure after a successful `200`: verify whether the runtime key/iv is transformed through a helper such as digit-pair-to-char before AES is applied
- empty data: verify pagination, filters, referer, login state, and cursor evolution
- occasional success: inspect one-time tokens, session refresh, or concurrent request coupling
- first request works but immediate replay fails: compare cookie mutation, in-memory timestamp slots, and whether a page refresh function must run before every request
- response gibberish: search for decrypt path, compression, protobuf, or msgpack
- hooked page fails but clean page works: suspect observer effect, remove invasive hooks, and recapture the baseline before deeper tracing

## Local helper scripts

Use the bundled local scripts when they are faster than re-deriving the same mechanics:

- `scripts/check_reverse_env.py`: confirm the local reverse stack quickly
- `scripts/crypto_fingerprint.py`: classify suspicious digest or alphabet outputs
- `scripts/protocol_diff.py`: compare captured requests or responses and surface the meaningful deltas
- `scripts/scaffold_reverse_project.py`: start a clean Python-first collector layout
