#!/usr/bin/env python3
"""Create compact protocol-first Python reverse projects."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


PROJECT_DIRS = [
    "config",
    "utils",
    "tests",
    "js_reverse_cache",
]


@dataclass(slots=True)
class WriteStats:
    created: int = 0
    updated: int = 0


@dataclass(frozen=True, slots=True)
class ProfileSpec:
    name: str
    summary: str
    first_moves: tuple[str, ...]
    anti_patterns: tuple[str, ...]
    list_method: str
    list_body_kind: str
    transport_field: str
    sign_field: str
    timestamp_field: str
    page_param: str
    category_param: str
    use_compact_json: bool
    sign_before_timestamp: bool


PROFILE_SPECS: dict[str, ProfileSpec] = {
    "generic": ProfileSpec(
        name="generic",
        summary="Balanced scaffold for unknown protocol targets. Start broad, prove one stable replay, then specialize.",
        first_moves=(
            "Confirm the real wire endpoint before reading giant bundles.",
            "Freeze one known-good request and one response sample.",
            "Recover sign, cookie, decode, or transport state only after the wire path is proven.",
        ),
        anti_patterns=(
            "Do not assume every hard target is only a sign problem.",
            "Do not mix bootstrap, transport, decode, and storage logic in one file.",
        ),
        list_method="GET",
        list_body_kind="query",
        transport_field="",
        sign_field="sign",
        timestamp_field="timestamp",
        page_param="page",
        category_param="category",
        use_compact_json=True,
        sign_before_timestamp=True,
    ),
    "public-envelope": ProfileSpec(
        name="public-envelope",
        summary="For public pages that still require entry-route cookies, bootstrap artifacts, and wrapped or encrypted business payloads.",
        first_moves=(
            "Hit the real public entry route once and freeze the seeded cookies.",
            "Freeze the bootstrap artifact such as a public key, config blob, nonce seed, or envelope metadata.",
            "Recover the exact payload build order: payload, compact JSON, sign, timestamp, encode or encrypt, wrapper field.",
        ),
        anti_patterns=(
            "Do not assume public list access means detail access is also public.",
            "Do not trust empty filters when the UI may be injecting category or mode state.",
        ),
        list_method="POST",
        list_body_kind="json",
        transport_field="param",
        sign_field="sign",
        timestamp_field="timeStamp",
        page_param="pageIndex",
        category_param="category",
        use_compact_json=True,
        sign_before_timestamp=True,
    ),
    "structured-transport": ProfileSpec(
        name="structured-transport",
        summary="For GraphQL, WebSocket, protobuf, msgpack, or nested envelope contracts where transport shape is the real protocol.",
        first_moves=(
            "Freeze one known-good envelope with all metadata intact.",
            "Separate transport fields from business fields before rewriting anything.",
            "Document auth, sequencing, operation names, and heartbeat or cursor rules explicitly.",
        ),
        anti_patterns=(
            "Do not flatten envelope metadata away just because the business payload looks simple.",
            "Do not treat channel names, frame types, or persisted-query hashes as optional noise.",
        ),
        list_method="POST",
        list_body_kind="json",
        transport_field="",
        sign_field="sign",
        timestamp_field="timestamp",
        page_param="page",
        category_param="channel",
        use_compact_json=False,
        sign_before_timestamp=False,
    ),
    "response-decode": ProfileSpec(
        name="response-decode",
        summary="For targets where HTTP replay is easy but the payload stays unreadable until a local decode chain is rebuilt.",
        first_moves=(
            "Freeze the raw payload before tracing any decoder.",
            "Find the first consumer of the raw payload rather than guessing from helper names.",
            "Rebuild the decode order exactly and prove it against a captured sample.",
        ),
        anti_patterns=(
            "Do not optimize parsing before the raw payload is frozen.",
            "Do not mark success when replay works but the local decode chain is still missing.",
        ),
        list_method="GET",
        list_body_kind="query",
        transport_field="",
        sign_field="sign",
        timestamp_field="timestamp",
        page_param="page",
        category_param="",
        use_compact_json=True,
        sign_before_timestamp=True,
    ),
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "reverse-job"


def normalize_content(content: str) -> str:
    text = dedent(content).lstrip("\n").rstrip()
    return f"{text}\n"


def replace_tokens(template: str, mapping: dict[str, str]) -> str:
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace(f"__{key}__", value)
    return rendered


def write_file(path: Path, content: str, force: bool, stats: WriteStats) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    if exists and not force:
        return
    path.write_text(normalize_content(content), encoding="utf-8")
    if exists:
        stats.updated += 1
    else:
        stats.created += 1


def profile_moves(spec: ProfileSpec) -> str:
    return "\n".join(f"- {line}" for line in spec.first_moves)


def profile_anti_patterns(spec: ProfileSpec) -> str:
    return "\n".join(f"- {line}" for line in spec.anti_patterns)


def build_mapping(slug: str, spec: ProfileSpec) -> dict[str, str]:
    return {
        "SLUG": slug,
        "PROFILE": spec.name,
        "PROFILE_SUMMARY": spec.summary,
        "PROFILE_FIRST_MOVES": profile_moves(spec),
        "PROFILE_ANTI_PATTERNS": profile_anti_patterns(spec),
        "LIST_METHOD": spec.list_method,
        "LIST_BODY_KIND": spec.list_body_kind,
        "TRANSPORT_FIELD": spec.transport_field,
        "SIGN_FIELD": spec.sign_field,
        "TIMESTAMP_FIELD": spec.timestamp_field,
        "PAGE_PARAM": spec.page_param,
        "CATEGORY_PARAM": spec.category_param,
        "USE_COMPACT_JSON": "True" if spec.use_compact_json else "False",
        "SIGN_BEFORE_TIMESTAMP": "True" if spec.sign_before_timestamp else "False",
        "USE_COMPACT_JSON_JSON": "true" if spec.use_compact_json else "false",
        "SIGN_BEFORE_TIMESTAMP_JSON": "true" if spec.sign_before_timestamp else "false",
    }


def project_templates() -> dict[str, str]:
    return {
        "README.md": """
            # __SLUG__

            Pure-protocol collector scaffold for Web Protocol Recovery.

            This output follows this skill's built-in compact Python protocol layout:
            root entry script, `config/` for headers/keys/local JS helpers, and
            `utils/` for request, sign, and crypto code. `js_reverse_cache/` is
            retained for required reconnaissance artifacts.

            ## Profile

            - Active profile: `__PROFILE__`
            - Summary: __PROFILE_SUMMARY__

            ## First Moves

            __PROFILE_FIRST_MOVES__

            ## Anti-Patterns

            __PROFILE_ANTI_PATTERNS__

            ## Directory

            ```text
            .
            |-- main.py
            |-- requirements.txt
            |-- config/
            |   |-- headers.json
            |   |-- keys.json
            |   `-- sign_logic.js
            |-- utils/
            |   |-- __init__.py
            |   |-- crypto.py
            |   |-- request.py
            |   `-- sign.py
            |-- tests/
            `-- js_reverse_cache/
            ```

            ## Run

            ```bash
            pip install -r requirements.txt
            python main.py --pages 1
            python -m unittest discover
            ```

            ## Notes

            - Save captured JS/WASM/font/HTML/request artifacts only under `js_reverse_cache/`.
            - Put stable headers and endpoint metadata in `config/`.
            - Keep browser tooling out of the final collector.
            - Recover one stable request before adding pagination or concurrency.
        """,
        "requirements.txt": """
            requests>=2.31.0
            # Uncomment only when the target requires it.
            # curl_cffi>=0.7.0
            # pycryptodome>=3.20.0
            # protobuf>=5.0.0
            # brotli>=1.1.0
        """,
        "main.py": """
            from __future__ import annotations

            import argparse
            import json
            import sys
            import time
            from pathlib import Path
            from typing import Any

            from utils.crypto import compact_json
            from utils.request import ProtocolClient
            from utils.sign import build_sign, run_self_check


            ROOT = Path(__file__).resolve().parent
            CONFIG_DIR = ROOT / "config"


            def _ensure_utf8_stdout() -> None:
                reconfigure = getattr(sys.stdout, "reconfigure", None)
                if callable(reconfigure):
                    reconfigure(encoding="utf-8")


            def load_json(path: Path) -> dict[str, Any]:
                with path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)


            def build_payload(config: dict[str, Any], page_index: int) -> dict[str, Any]:
                payload = dict(config.get("base_payload") or {})
                category_param = config.get("category_param") or ""
                category_value = config.get("category_value") or ""
                page_param = config.get("page_param") or ""

                if category_param and category_value:
                    payload.setdefault(category_param, category_value)
                if page_param:
                    payload[page_param] = page_index
                return payload


            def sign_input(payload: dict[str, Any], config: dict[str, Any]) -> str:
                if config.get("use_compact_json", True):
                    return compact_json(payload)
                return json.dumps(payload, ensure_ascii=False)


            def inject_runtime_fields(payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
                body = dict(payload)
                sign_field = config.get("sign_field") or ""
                timestamp_field = config.get("timestamp_field") or ""
                sign_before_timestamp = config.get("sign_before_timestamp", True)

                if sign_field and sign_before_timestamp:
                    body[sign_field] = build_sign(sign_input(payload, config), payload, context=config)

                if timestamp_field:
                    body[timestamp_field] = int(time.time() * 1000)

                if sign_field and not sign_before_timestamp:
                    body[sign_field] = build_sign(sign_input(body, config), payload, context=config)

                return body


            def build_request_body(payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
                body = inject_runtime_fields(payload, config)
                transport_field = config.get("transport_field") or ""
                if not transport_field:
                    return body
                return {transport_field: compact_json(body)}


            def build_parser() -> argparse.ArgumentParser:
                parser = argparse.ArgumentParser(description="Run protocol-first collector")
                parser.add_argument("--pages", type=int, default=1, help="Number of pages to request")
                parser.add_argument("--url", default="", help="Override config/keys.json list_url")
                return parser


            def main() -> None:
                _ensure_utf8_stdout()
                args = build_parser().parse_args()
                config = load_json(CONFIG_DIR / "keys.json")
                headers = load_json(CONFIG_DIR / "headers.json")
                list_url = args.url or config.get("list_url") or ""

                run_self_check()
                if not list_url:
                    print("list_url is empty; update config/keys.json before live replay")
                    return

                client = ProtocolClient(headers=headers, timeout=float(config.get("timeout", 20.0)))
                page_start = int(config.get("page_start", 1))

                for page_index in range(page_start, page_start + args.pages):
                    payload = build_payload(config, page_index)
                    body = build_request_body(payload, config)
                    result = client.request_json(
                        list_url,
                        method=config.get("list_method", "GET"),
                        body_kind=config.get("list_body_kind", "query"),
                        body=body,
                    )
                    print(json.dumps(result, ensure_ascii=False, indent=2))


            if __name__ == "__main__":
                main()
        """,
        "config/headers.json": """
            {
              "User-Agent": "Mozilla/5.0",
              "Accept": "application/json, text/plain, */*"
            }
        """,
        "config/keys.json": """
            {
              "profile": "__PROFILE__",
              "base_url": "",
              "entry_url": "",
              "bootstrap_url": "",
              "list_url": "",
              "list_method": "__LIST_METHOD__",
              "list_body_kind": "__LIST_BODY_KIND__",
              "transport_field": "__TRANSPORT_FIELD__",
              "sign_field": "__SIGN_FIELD__",
              "timestamp_field": "__TIMESTAMP_FIELD__",
              "page_param": "__PAGE_PARAM__",
              "category_param": "__CATEGORY_PARAM__",
              "category_value": "",
              "use_compact_json": __USE_COMPACT_JSON_JSON__,
              "sign_before_timestamp": __SIGN_BEFORE_TIMESTAMP_JSON__,
              "page_start": 1,
              "page_size": 20,
              "timeout": 20.0,
              "base_payload": {}
            }
        """,
        "config/sign_logic.js": """
            // Optional tiny local JS helper.
            // It must run locally without document, window, browser profile, or clicks.
        """,
        "js_reverse_cache/.gitkeep": "",
    }


def utils_templates() -> dict[str, str]:
    return {
        "utils/__init__.py": "",
        "utils/crypto.py": """
            from __future__ import annotations

            import base64
            import hashlib
            import json
            from typing import Any


            def compact_json(payload: dict[str, Any]) -> str:
                return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


            def md5_hex(text: str) -> str:
                return hashlib.md5(text.encode("utf-8")).hexdigest()


            def sha256_hex(text: str) -> str:
                return hashlib.sha256(text.encode("utf-8")).hexdigest()


            def b64encode_text(text: str) -> str:
                return base64.b64encode(text.encode("utf-8")).decode("ascii")
        """,
        "utils/request.py": """
            from __future__ import annotations

            import json
            from typing import Any

            import requests


            class ProtocolClient:
                def __init__(self, *, headers: dict[str, str] | None = None, timeout: float = 20.0) -> None:
                    self.session = requests.Session()
                    self.session.headers.update(headers or {})
                    self.timeout = timeout

                def request_json(
                    self,
                    url: str,
                    *,
                    method: str = "GET",
                    body_kind: str = "query",
                    body: dict[str, Any] | None = None,
                    headers: dict[str, str] | None = None,
                ) -> Any:
                    response = self.request(
                        url,
                        method=method,
                        body_kind=body_kind,
                        body=body,
                        headers=headers,
                    )
                    return response.json()

                def request_text(
                    self,
                    url: str,
                    *,
                    method: str = "GET",
                    body_kind: str = "query",
                    body: dict[str, Any] | None = None,
                    headers: dict[str, str] | None = None,
                ) -> str:
                    return self.request(
                        url,
                        method=method,
                        body_kind=body_kind,
                        body=body,
                        headers=headers,
                    ).text

                def request(
                    self,
                    url: str,
                    *,
                    method: str = "GET",
                    body_kind: str = "query",
                    body: dict[str, Any] | None = None,
                    headers: dict[str, str] | None = None,
                ) -> requests.Response:
                    request_kwargs: dict[str, Any] = {
                        "headers": headers or {},
                        "timeout": self.timeout,
                    }
                    if body_kind == "query":
                        request_kwargs["params"] = body or {}
                    elif body_kind == "json":
                        request_kwargs["json"] = body or {}
                    elif body_kind == "form":
                        request_kwargs["data"] = body or {}
                    elif body_kind == "raw":
                        request_kwargs["data"] = json.dumps(body or {}, ensure_ascii=False, separators=(",", ":"))
                    else:
                        raise RuntimeError(f"Unsupported body_kind: {body_kind}")

                    response = self.session.request(method.upper(), url, **request_kwargs)
                    response.raise_for_status()
                    return response
        """,
        "utils/sign.py": """
            from __future__ import annotations

            from typing import Any


            def run_self_check() -> None:
                # Add fixed-input assertions after the signer is recovered.
                pass


            def build_sign(
                sign_input: str,
                payload: dict[str, Any],
                *,
                context: dict[str, Any] | None = None,
            ) -> str:
                # Return the recovered sign/token value for one fixed request shape.
                _ = (sign_input, payload, context)
                return ""
        """,
    }


def test_templates() -> dict[str, str]:
    return {
        "tests/__init__.py": "",
        "tests/test_crypto.py": """
            import unittest

            from utils.crypto import compact_json, sha256_hex


            class CryptoTests(unittest.TestCase):
                def test_compact_json_has_no_spaces(self) -> None:
                    self.assertEqual(compact_json({"a": 1, "b": 2}), '{"a":1,"b":2}')

                def test_sha256_hex_known_vector(self) -> None:
                    self.assertEqual(
                        sha256_hex("abc"),
                        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                    )
        """,
        "tests/test_sign.py": """
            import unittest

            from utils.sign import build_sign, run_self_check


            class SignTests(unittest.TestCase):
                def test_run_self_check_is_callable(self) -> None:
                    run_self_check()

                def test_build_sign_defaults_to_empty_string(self) -> None:
                    self.assertEqual(build_sign("x", {"page": 1}), "")
        """,
    }


def build_templates(slug: str, spec: ProfileSpec) -> dict[str, str]:
    mapping = build_mapping(slug, spec)
    templates = {}
    templates.update(project_templates())
    templates.update(utils_templates())
    templates.update(test_templates())
    return {path: replace_tokens(content, mapping) for path, content in templates.items()}


def scaffold(root: Path, name: str, profile: str, force: bool) -> tuple[Path, WriteStats]:
    slug = slugify(name)
    project = root / slug
    stats = WriteStats()
    spec = PROFILE_SPECS[profile]

    for rel in PROJECT_DIRS:
        (project / rel).mkdir(parents=True, exist_ok=True)

    for relative_path, content in build_templates(slug, spec).items():
        write_file(project / relative_path, content, force, stats)

    return project, stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold a compact protocol-first Python project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("name", help="Project name or target slug")
    parser.add_argument("--root", default=".", help="Directory where the project will be created")
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_SPECS),
        default="generic",
        help="Template profile tuned for the target symptom family",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    project, stats = scaffold(Path(args.root).resolve(), args.name, args.profile, args.force)
    print(project)
    print(f"profile={args.profile}")
    print(f"created={stats.created} updated={stats.updated}")
    print(
        "next: fill config/keys.json, config/headers.json, utils/sign.py, "
        "utils/request.py, optional config/sign_logic.js, then run python main.py --pages 1"
    )


if __name__ == "__main__":
    main()
