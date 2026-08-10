# Output Contract

After each meaningful phase, emit short structured reporting instead of vague prose.

Always return:

- which target family won the startup triage and why
- what `chrome-devtools` proved about the site flow
- what `cloakbrowser-reverse-mcp` proved through CDP/network/initiator, interception, source/SourceMap, debugger/breakpoints, WebSocket, environment/fingerprint, Hook/JSVMP/instrumentation, cookie/storage/state, heap/artifact, or offline signer evidence
- whether `js-reverse` fallback was needed; if used, what it proved as second-source validation
- what the real endpoint is
- what the real moving parts are
- whether observer-effect risk showed up and how it was controlled
- what the cookie provenance is when cookies mattered
- what was misleading
- what was verified with fixed inputs
- what the final protocol path is
- how the Python collector and JS helper are split
- confirmation that the final runtime is fully browser-free
- confirmation that CloakBrowser and any CDP/browser state were used only for reconnaissance, not final replay
- where the collector and sample output were saved
- what still looks unstable, if anything

Use the headings from `references/report-templates.md` when possible.
