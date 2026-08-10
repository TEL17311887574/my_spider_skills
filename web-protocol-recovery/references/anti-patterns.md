# Anti-Patterns

- Do not ask the user to manually inspect giant bundles if tooling can inspect them.
- Do not skip available Camoufox/CloakBrowser capability on a fresh target when browser evidence matters. If either is unavailable, continue down the chain `single fingerprint browser → js-reverse-mcp → chrome-devtools-mcp → manual samples` and record the missing capability group.
- Do not force `js-reverse` as a mandatory fresh-target gate; use it only when Camoufox/CloakBrowser are unavailable, unstable, blocked, or need second-source validation.
- Do not ignore Camoufox capabilities when environment/fingerprint/property-access evidence would materially improve proof; do not ignore CloakBrowser capabilities when CDP-native requests/initiators, request interception, SourceMaps/source, Debugger breakpoints/paused scopes, WebSocket frames, Chromium fingerprinting, Hook/JSVMP/instrumentation, cookie/storage/state, heap/artifacts, or offline signer verification would materially improve evidence; report unavailable capability instead.
- Do not jump straight to Selenium or Playwright when a direct API exists.
- Do not install broad hooks before capturing a clean baseline on verifier-gated or behavior-sensitive targets.
- Do not confuse business-layer params with wire-layer params.
- Do not trust helper names without fixed-input proof.
- Do not call browser-only behavior before checking page-specific headers or cookies.
- Do not hardcode rotating cookies before proving who writes them and how they refresh.
- Do not bury every concern in one `main.py`.
- Do not stop after one lucky success.
- Do not ship a browser automation script when the task is protocol-recoverable.
- Do not hide automation behind words like "temporary collector" or "reliable fallback".
- Do not leave final JS helpers coupled to `window`, `document`, browser storage, or manual browser state when they can be made local and deterministic.
- Do not treat a Camoufox/CloakBrowser persistent profile, CDP endpoint, exported state file, screenshot, or browser_env snapshot as a final protocol dependency.
