# Architecture

This file documents the env-patch skill architecture and runtime behavior.

## What This Is

An OpenCode skill for JS reverse-engineering sandbox environment patching (JS逆向沙箱补环境). Given an obfuscated JS file, it automates the cycle of: execute → diagnose missing browser APIs → patch environment → repeat until the script runs successfully.

This is a **skill directory** (not an npm project). It is self-contained with no external dependencies. At runtime, `$SKILL_DIR` resolves to the skill's installation path.

## Key Commands

```bash
# First diagnosis (no env modules)
node $SKILL_DIR/scripts/env-diagnose.js <target.js>

# Diagnosis with env modules
node $SKILL_DIR/scripts/env-diagnose.js --env bom/navigator.js,bom/crypto.js,dom/document.js <target.js>

# Multiple --env flags also work
node $SKILL_DIR/scripts/env-diagnose.js --env bom/navigator.js --env dom/document.js <target.js>

# Options: --timeout <ms> (default 60000), --quiet/-q
```

env-diagnose.js outputs JSON to stdout with: `success`, `error`, `undefinedPaths`, `stats`, `consoleOutput`.

## Architecture

### Core Loading Chain

`env-diagnose.js` creates a Node.js `vm` sandbox and loads modules in this order:

1. **`core/ProxyMonitor.js`** — Always loaded. Provides `watch()` (Proxy wrapper that logs all property access), `safefunction()` (makes functions appear native via toString), `makeFunction()`, and `__ProxyMonitor__` global for log access.

2. **`core/ProxyEnv.js`** — Loaded **only when no `--env` modules are specified**. Creates basic proxy-wrapped browser globals (document, navigator, location, etc.) with `configurable: false`. When env modules are specified, this is skipped to avoid conflicts.

3. **User-specified env modules** — Loaded in the order given via `--env`. Paths are relative to `env/` directory.

4. **Target script** — Executed last. ProxyMonitor logs are cleared before this step so only the target's accesses are captured.

### Env Module Categories

All modules are IIFEs with `'use strict'`. They use `watch()` from ProxyMonitor and `Object.defineProperty` to set globals.

- **`bom/`** — Browser Object Model: navigator, location, screen, storage, window properties, crypto, performance, console, observers
- **`dom/`** — DOM: event classes, document (largest module ~103KB with full Element/Node hierarchy), elements (HTML element subclasses)
- **`webapi/`** — Web APIs: fetch, XMLHttpRequest, Blob/File/FormData, URL/URLSearchParams, network monitoring
- **`encoding/`** — atob/btoa (already built into env-diagnose.js), TextEncoder/TextDecoder
- **`timer/`** — setTimeout/setInterval with ID management (env-diagnose.js has basic stubs)
- **`ai-generated/`** — Custom patches for properties not covered by existing modules. Filename format: `<object>-<property>.js`

### Critical Loading Order Rules

Module dependency order within `--env` matters. See `references/loading-order.md` for the full standard order. Key constraints:
- `dom/elements.js` **must** come after `dom/document.js` (depends on Element base class)
- `webapi/network.js` **must** come after `webapi/xhr.js` and `webapi/fetch.js`
- `dom/event.js` should come before `dom/document.js`
- BOM modules generally go before DOM modules

### Module Selection Algorithm

1. Collect `undefinedPaths` from diagnose output
2. Extract prefix (before first `.`) from each path
3. Match prefix to module using `references/env-modules.md` mapping table
4. Manually order modules per `references/loading-order.md`
5. Manually add dependencies (e.g., `dom/elements.js` requires `dom/document.js`)

`env-diagnose.js` does not sort modules or expand dependencies. It loads exactly the modules supplied via `--env`, in the supplied order.

### Key Design Decisions

- `success: true` from env-diagnose.js only means the script loaded without throwing — it does NOT mean the target functionality (signing, encryption) works. Functional verification requires a project-local runner, preferably under `js_reverse_cache/env/run.js`.
- The sandbox's `window`/`self`/`global`/`globalThis` all point to the same sandbox object.
- env-diagnose.js provides built-in stubs for: console, setTimeout/setInterval, atob/btoa, and a minimal XMLHttpRequest.
- ProxyMonitor filters its own `[ProxyMonitor]` prefixed logs from consoleOutput to avoid noise.

## Writing Custom Patches

When an undefinedPath has no matching module, create a target-specific patch in the current workspace, not in the installed skill directory:

```javascript
// js_reverse_cache/env/ai-generated/<object>-<property>.js
(() => {
    'use strict';
    Object.defineProperty(window, 'someProperty', {
        value: /* reasonable browser default */,
        writable: false,
        configurable: true,
        enumerable: true
    });
})();
```

Then load it explicitly in the next diagnosis:

```bash
node $SKILL_DIR/scripts/env-diagnose.js --env bom/navigator.js,js_reverse_cache/env/ai-generated/<object>-<property>.js <target.js>
```

`patch-loader.js` is only a management helper for injected file contents; `env-diagnose.js` does not automatically scan `env/ai-generated/` or any project-local `js_reverse_cache/env/ai-generated/` directory.
