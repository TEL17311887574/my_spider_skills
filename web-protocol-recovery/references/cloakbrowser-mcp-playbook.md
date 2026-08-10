# CloakBrowser MCP Playbook

Use `cloakbrowser-reverse-mcp` as the primary Chromium/CDP reverse reconnaissance plane for protocol recovery. Pair it with Camoufox when anti-detection environment sampling or engine-level property access evidence matters. CloakBrowser can collect CDP-native evidence, survive hostile fingerprinting better than a normal browser, and expose low-level network, source, debugger, WebSocket, hook, JSVMP, state, artifact, and offline verification evidence. It must never become the final collector.

All saved artifacts from this MCP must go under `js_reverse_cache/`: scripts, source maps, HTML, WASM, fonts, heap snapshots, screenshots, exported state, request samples, response samples, and trace logs.

## Startup Policy

- Run `cloakbrowser-reverse-mcp_check_environment` when the MCP is available.
- Use `cloakbrowser-reverse-mcp_launch_browser` only for reconnaissance, not final collection.
- Treat `Camoufox + CloakBrowser` as the preferred dual reconnaissance stack on fresh targets when both are available. Use Camoufox for anti-detection environment/fingerprint evidence and property access; use CloakBrowser for CDP-native network, initiators, source, debugger, WebSocket, hooks, JSVMP, state, artifacts, and signer verification. A fixed sample baseline still comes from one selected browser context; the other tool supplies corroborating evidence.
- If only one fingerprint browser is available, use it as the single baseline and record the missing capability group. If both are unavailable, degrade to `js-reverse-mcp`; if that is also unavailable, degrade to `chrome-devtools-mcp`; if all browser tools are unavailable, proceed only from user-provided samples and report missing dynamic evidence.
- Prefer a clean context for baseline captures. Avoid persistent profile state unless the target is explicitly session-bound and the session contract is part of the evidence.
- Use `cloakbrowser-reverse-mcp_reset_browser_state` before a fresh target when previous hooks, routes, cookies, or captures could pollute the sample.
- Use `cloakbrowser-reverse-mcp_close_browser` after collection when long-lived browser state would confuse the next target.
- Do not run `cloakbrowser-reverse-mcp_update_browser_binary` unless the user requested maintenance or the current binary is the blocker. Report `cloakbrowser-reverse-mcp_browser_binary_info` and `cloakbrowser-reverse-mcp_check_browser_update` first.

## Capability Map

### Environment, Browser, And Page Lifecycle

- `cloakbrowser-reverse-mcp_check_environment`: verify MCP dependencies and local browser state.
- `cloakbrowser-reverse-mcp_browser_binary_info`: inspect the installed CloakBrowser binary.
- `cloakbrowser-reverse-mcp_check_browser_update`: check whether a newer binary exists.
- `cloakbrowser-reverse-mcp_update_browser_binary`: update the local browser binary when explicitly chosen.
- `cloakbrowser-reverse-mcp_launch_browser`: launch the stealth browser with locale, proxy, WebRTC blocking, viewport, fingerprint seed, humanization, and CDP enabled.
- `cloakbrowser-reverse-mcp_get_page_info`: record URL, title, viewport, and CDP endpoint.
- `cloakbrowser-reverse-mcp_navigate`: navigate with optional hook presets and response-chain capture.
- `cloakbrowser-reverse-mcp_reload`: reload while preserving init scripts.
- `cloakbrowser-reverse-mcp_wait_for`: wait for selectors or URL substrings.
- `cloakbrowser-reverse-mcp_click`, `cloakbrowser-reverse-mcp_type_text`, `cloakbrowser-reverse-mcp_human_scroll`: perform minimal UI actions needed to reveal protocol traffic.
- `cloakbrowser-reverse-mcp_take_screenshot` and `cloakbrowser-reverse-mcp_capture_screenshot_cdp`: save visual evidence when the page state or gate matters.
- `cloakbrowser-reverse-mcp_close_browser`: release the browser.

Use these only to reach and document the protocol boundary. Do not build final logic around UI clicks, profile state, or browser timers.

### HTTP Network Evidence

- `cloakbrowser-reverse-mcp_network_capture`: start, stop, clear, or inspect request capture; enable body capture only when needed.
- `cloakbrowser-reverse-mcp_list_network_requests`: list captured requests by URL, domain, method, resource type, or status.
- `cloakbrowser-reverse-mcp_get_network_request`: inspect one Playwright-side request with headers and optional body.
- `cloakbrowser-reverse-mcp_list_cdp_network_requests`: list CDP-native requests with initiator metadata.
- `cloakbrowser-reverse-mcp_get_cdp_network_request`: inspect one CDP request and optional response body.
- `cloakbrowser-reverse-mcp_get_request_initiator`: get the best available initiator for one captured request.
- `cloakbrowser-reverse-mcp_get_cdp_request_initiator`: get Chromium's native `Network.Initiator` for one CDP request id.
- `cloakbrowser-reverse-mcp_intercept_request`: log, block, modify, or mock matching requests for narrow proof only.

Protocol rule: capture one clean baseline before adding interception. If interception changes behavior, remove it and treat the change as observer-effect evidence.

### Scripts, Source, And Source Maps

- `cloakbrowser-reverse-mcp_scripts`: list, get, or save loaded page scripts.
- `cloakbrowser-reverse-mcp_search_code`: search loaded scripts by substring.
- `cloakbrowser-reverse-mcp_list_cdp_scripts`: enumerate Debugger-domain scripts.
- `cloakbrowser-reverse-mcp_get_cdp_script_source`: get full source for a CDP script id.
- `cloakbrowser-reverse-mcp_get_cdp_source`: read a small source slice by script id or URL.
- `cloakbrowser-reverse-mcp_save_cdp_script_source`: save a full CDP script source under `js_reverse_cache/`.
- `cloakbrowser-reverse-mcp_search_cdp_sources`: search CDP scripts by string or regex.
- `cloakbrowser-reverse-mcp_list_source_maps`: list scripts advertising source maps.
- `cloakbrowser-reverse-mcp_get_source_map`: fetch and summarize a source map.
- `cloakbrowser-reverse-mcp_get_source_map_source`: retrieve one original source from a source map.

Use source maps to shrink the problem before deobfuscation. If the work becomes whole-file AST restoration, hand off that subproblem to `ast-deobfuscate`.

### Debugger And Breakpoints

- `cloakbrowser-reverse-mcp_cdp_enable_debugger`: enable Runtime and Debugger domains.
- `cloakbrowser-reverse-mcp_cdp_status`: inspect CDP endpoint, script count, and pause state.
- `cloakbrowser-reverse-mcp_get_cdp_endpoint`: record the local CDP endpoint as evidence, not as a final dependency.
- `cloakbrowser-reverse-mcp_break_on_xhr`: pause on XHR/Fetch URL substrings.
- `cloakbrowser-reverse-mcp_remove_xhr_breakpoint`: remove an XHR/Fetch breakpoint.
- `cloakbrowser-reverse-mcp_set_breakpoint_on_text`: search code text and set a breakpoint.
- `cloakbrowser-reverse-mcp_set_cdp_breakpoint`: set a breakpoint by script id or URL and line/column.
- `cloakbrowser-reverse-mcp_list_cdp_breakpoints`: list breakpoints set by this MCP.
- `cloakbrowser-reverse-mcp_remove_cdp_breakpoint`: remove one or all CDP breakpoints.
- `cloakbrowser-reverse-mcp_get_paused_info`: inspect paused call stack and scopes.
- `cloakbrowser-reverse-mcp_evaluate_on_paused`: evaluate in a paused frame.
- `cloakbrowser-reverse-mcp_step_debugger`: step over, into, or out.
- `cloakbrowser-reverse-mcp_resume_debugger`: resume JavaScript execution.
- `cloakbrowser-reverse-mcp_set_cdp_skip_all_pauses`: ignore debugger statements or breakpoints when anti-debug code interferes.

Use breakpoints to prove exact pre-sign strings, keys, IVs, payloads, and wrapper mutations. Remove them immediately after extracting fixed samples.

### Runtime Evaluation, Hooks, And Instrumentation

- `cloakbrowser-reverse-mcp_evaluate_js`: execute page-context JavaScript expressions.
- `cloakbrowser-reverse-mcp_hook_function`: trace or intercept a function path such as `JSON.stringify`, `fetch`, or a known signer.
- `cloakbrowser-reverse-mcp_inject_hook_preset`: install preset hooks for XHR, fetch, crypto, WebSocket, debugger bypass, cookie, or runtime probing.
- `cloakbrowser-reverse-mcp_hook_jsvmp_interpreter`: install page-level JSVMP runtime probes.
- `cloakbrowser-reverse-mcp_instrumentation`: source-level script instrumentation through route rewriting, log retrieval, reload, status, and stop.
- `cloakbrowser-reverse-mcp_remove_hooks`: clear persistent hook registrations.
- `cloakbrowser-reverse-mcp_get_console_logs`: collect console evidence emitted by hooks or the page.
- `cloakbrowser-reverse-mcp_verify_signer_offline`: run candidate signer code against captured fixed samples inside the page context.

Use runtime hooks only after a clean baseline and initiator evidence exist. Favor `verify_signer_offline` for fixed-input proof before porting to Python.

### WebSocket And Stateful Stream Evidence

- `cloakbrowser-reverse-mcp_websocket_capture`: enable, clear, or inspect CDP WebSocket capture.
- `cloakbrowser-reverse-mcp_list_websockets`: list captured WebSocket connections.
- `cloakbrowser-reverse-mcp_get_websocket_connection`: inspect one connection, handshake metadata, and recent messages.
- `cloakbrowser-reverse-mcp_get_websocket_messages`: list, filter, inspect, or group WebSocket messages by payload shape.

For stateful streams, save a full transcript before interpreting payload semantics. Preserve auth, ack, heartbeat, reconnect, counter, and key-derivation order.

### Cookies, Storage, State, And Fingerprint Evidence

- `cloakbrowser-reverse-mcp_cookies`: get, set, or delete cookies.
- `cloakbrowser-reverse-mcp_get_storage`: read localStorage or sessionStorage.
- `cloakbrowser-reverse-mcp_export_state`: export cookies and storage to an artifact.
- `cloakbrowser-reverse-mcp_import_state`: import a prior Playwright storage state for controlled reproduction.
- `cloakbrowser-reverse-mcp_compare_env`: collect browser fingerprint values.
- `cloakbrowser-reverse-mcp_list_trace_files` and `cloakbrowser-reverse-mcp_query_trace_file`: inspect historical trace files when available.
- `cloakbrowser-reverse-mcp_trace_property_access`: documented non-Camoufox compatibility surface. CloakBrowser does not expose Camoufox-style engine-level property tracing, so do not rely on it for invisible property access evidence.

Cookie rule: use these tools to prove who writes or refreshes cookies. Do not hardcode rotating cookies into the final collector without provenance.

### Heap, Memory, And Heavy Artifacts

- `cloakbrowser-reverse-mcp_capture_heap_snapshot`: save a Chrome heap snapshot under `js_reverse_cache/` when runtime object graphs are the only practical evidence.
- `cloakbrowser-reverse-mcp_capture_screenshot_cdp` and `cloakbrowser-reverse-mcp_take_screenshot`: preserve gate or UI-state evidence when it explains why a request exists, without treating screenshots as protocol state.
- `cloakbrowser-reverse-mcp_list_trace_files` and `cloakbrowser-reverse-mcp_query_trace_file`: inspect saved trace artifacts if they exist.
- `cloakbrowser-reverse-mcp_trace_property_access`: record the limitation that CloakBrowser has no Camoufox-style engine-level property tracing; use `compare_env`, hooks, and source evidence instead.

Use heap snapshots sparingly. Prefer request, source, and fixed-input artifacts first.

## Decision Routes

- Need a second source of truth for real endpoints: use CDP network list/detail plus initiators.
- Need to prove the request was changed on the wire: use request diffs, CDP initiators, `break_on_xhr`, then narrow `intercept_request` or hooks only after the clean baseline.
- Need exact mutation logic: use text breakpoints, paused-frame evaluation, then fixed-input signer verification.
- Need original source: use source-map listing and source retrieval before saving bundles.
- Need hostile-page survivability: try Camoufox and CloakBrowser as complementary planes; Camoufox for environment/property survivability, CloakBrowser for controlled Chromium fingerprint and CDP evidence. Block WebRTC when relevant and capture clean evidence before hooks.
- Need WebSocket protocol: enable WebSocket capture, group messages, inspect one frame per group, then rebuild transcript order locally.
- Need cookie/session provenance: capture cookie writes, storage, exported state, and request diffs, then localize refresh logic.
- Need JSVMP evidence: use source-level instrumentation or runtime probes narrowly, then distill fixed inputs/outputs.
- Need environment or fingerprint proof: prefer Camoufox `compare_env` + `trace_property_access`; use CloakBrowser `compare_env`, source reads, narrow hooks, and fixed-input tests as Chromium/CDP evidence. Do not claim invisible engine-level property trace from CloakBrowser because it does not expose Camoufox-style trace.
- Need heavy runtime object evidence: use heap snapshots only after request/source/debugger evidence cannot answer the question.
- Need a fallback evidence plane: use `js-reverse` only after recording why Camoufox/CloakBrowser evidence is unavailable or insufficient; use `chrome-devtools` only after js-reverse is unavailable or insufficient.

## Delivery Boundary

CloakBrowser evidence can justify the Python collector, but the final collector cannot depend on CloakBrowser, CDP, persistent browser profiles, UI actions, screenshots, or browser-side storage. If the only remaining path is browser-driven replay, stop and continue reverse engineering rather than shipping automation.
