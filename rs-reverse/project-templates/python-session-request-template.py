import json
import re
import subprocess
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


# Copy this template into the target Ruishu project root as main.py before use.
# It expects rs_reverse.js and mod.js to be in BASE_DIR.
# It does not overwrite the root challenge_payload_*.js files; those are manual
# environment-detection samples maintained by the user.
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "js_reverse_cache"

# === Replace these for the target site ===
TARGET_URL = "https://example.com/replace-me"
API_URL = ""  # Optional business API for layered verification.
API_METHOD = "POST"
API_PARAMS = None
API_JSON = None
API_DATA = None

REQUEST_TIMEOUT = 20
NODE_TIMEOUT = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
API_HEADERS = {}

session = requests.Session()


def make_cache_run_dir(final_url):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(final_url or TARGET_URL)
    host = re.sub(r"[^A-Za-z0-9_.-]+", "_", parsed.netloc or "target")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    digest = sha1(f"{final_url or TARGET_URL}|{stamp}".encode("utf-8")).hexdigest()[:8]
    run_dir = CACHE_DIR / f"{stamp}_{host}_{digest}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "latest.txt").write_text(str(run_dir), encoding="utf-8")
    return run_dir


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def decode_utf8_response(response):
    return response.content.decode("utf-8", errors="ignore")


def cache_first_request(run_dir, response, first_html, runner_url, runner_response, payload_bootstrap, payload_runner):
    (run_dir / "first_response.html").write_text(first_html, encoding="utf-8", errors="ignore")
    (run_dir / "challenge_payload_bootstrap.js").write_text(payload_bootstrap, encoding="utf-8")
    (run_dir / "challenge_payload_runner.js").write_text(payload_runner, encoding="utf-8", errors="ignore")
    (run_dir / "runner_url.txt").write_text(runner_url, encoding="utf-8")
    write_json(run_dir / "metadata.json", {
        "target_url": TARGET_URL,
        "first_status": response.status_code,
        "first_final_url": response.url,
        "runner_url": runner_url,
        "runner_status": runner_response.status_code,
        "cookies_after_first_request": session.cookies.get_dict(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })


def extract_challenge_scripts(html):
    """Extract inline $_ts bootstrap and external r='m'/r2mKa runner from the first response."""
    payload_bootstrap = ""
    for script_body in re.findall(r"<script\b[^>]*>([\s\S]*?)</script>", html, flags=re.I):
        if "$_ts.cd" in script_body or "$_ts.nsd" in script_body:
            payload_bootstrap = script_body.strip()
            break

    runner_src = ""
    script_tags = re.findall(r"<script\b[^>]*>", html, flags=re.I)
    for script_tag in script_tags:
        src_match = re.search(r"\bsrc=['\"]([^'\"]+)['\"]", script_tag, flags=re.I)
        if not src_match:
            continue
        src = src_match.group(1)
        if "r='m'" in script_tag or 'r="m"' in script_tag or "r2m" in src or "/fpq" in src:
            runner_src = src
            break

    if not runner_src and len(script_tags) >= 2:
        src_match = re.search(r"\bsrc=['\"]([^'\"]+)['\"]", script_tags[1], flags=re.I)
        if src_match:
            runner_src = src_match.group(1)

    if not payload_bootstrap or not runner_src:
        raise RuntimeError(f"未提取到瑞数内联脚本或外链脚本，响应片段:\n{html[:1000]}")
    return payload_bootstrap, runner_src


def first_request():
    """First hop: keep Set-Cookie S/O/acw_tc in the same requests.Session."""
    response = session.get(TARGET_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    first_html = decode_utf8_response(response)
    payload_bootstrap, runner_src = extract_challenge_scripts(first_html)
    runner_url = urljoin(response.url or TARGET_URL, runner_src)
    runner_response = session.get(runner_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    payload_runner = decode_utf8_response(runner_response)
    cache_run_dir = make_cache_run_dir(response.url or TARGET_URL)
    cache_first_request(cache_run_dir, response, first_html, runner_url, runner_response, payload_bootstrap, payload_runner)

    print("first status ->", response.status_code)
    print("first final url ->", response.url)
    print("first cookies ->", session.cookies.get_dict())
    print("runner url ->", runner_url)
    print("cache dir ->", cache_run_dir)
    return payload_bootstrap, payload_runner, cache_run_dir


def replace_placeholder(template, placeholder, payload):
    tokens = (
        f"'{placeholder}';",
        f'"{placeholder}";',
        f"'{placeholder}'",
        f'"{placeholder}"',
    )
    for token in tokens:
        if token in template:
            return template.replace(token, payload)
    raise RuntimeError(f"rs_reverse.js 缺少占位符: {placeholder}")


def patch_runtime_require_paths(js_code):
    mod_path = (BASE_DIR / "mod.js").as_posix()
    return re.sub(r"require\((['\"])\./mod\1\)", f"require({json.dumps(mod_path)})", js_code, count=1)


def build_rs_reverse_runtime(payload_bootstrap, payload_runner, cache_run_dir):
    template_path = BASE_DIR / "rs_reverse.js"
    template = template_path.read_text(encoding="utf-8")
    js_code = replace_placeholder(template, "challenge_payload_bootstrap", payload_bootstrap)
    js_code = replace_placeholder(js_code, "challenge_payload_runner", payload_runner)
    js_code = patch_runtime_require_paths(js_code)

    runtime_path = cache_run_dir / "rs_reverse_runtime.js"
    runtime_path.write_text(js_code, encoding="utf-8")
    return runtime_path


def _to_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value


def parse_generated_cookie(output):
    path_matches = re.findall(r"([A-Za-z0-9_]+)=([^;\s]+);\s*path=/", output, flags=re.I)
    if path_matches:
        return path_matches[-1]

    ignored_prefixes = ("方法：", "document.", "script.", "div.", "meta.")
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line or line.startswith(ignored_prefixes):
            continue
        for part in reversed(line.split(";")):
            part = part.strip()
            if "=" not in part:
                continue
            name, value = part.split("=", 1)
            name, value = name.strip(), value.strip()
            if re.fullmatch(r"[A-Za-z0-9_]+", name) and value:
                return name, value
    raise RuntimeError(f"未从 Node 输出解析到瑞数 Cookie:\n{output[-2000:]}")


def run_node_get_cookie(runtime_path):
    try:
        result = subprocess.run(
            ["node", str(runtime_path)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=NODE_TIMEOUT,
            check=False,
        )
        output = result.stdout + "\n" + result.stderr
        if result.returncode != 0 and "=" not in output:
            raise RuntimeError(f"Node 执行失败({result.returncode}):\n{output[-2000:]}")
    except subprocess.TimeoutExpired as exc:
        output = _to_text(exc.stdout) + "\n" + _to_text(exc.stderr)
        print("node timeout -> try parsing cookie from partial output")

    name, value = parse_generated_cookie(output)
    return name, value, output


def second_request(payload_bootstrap, payload_runner, cache_run_dir):
    """Run rs_reverse.js through Node, then update Cookie T/P back to the same session."""
    runtime_path = build_rs_reverse_runtime(payload_bootstrap, payload_runner, cache_run_dir)
    cookie_name, cookie_value, node_output = run_node_get_cookie(runtime_path)
    session.cookies.update({cookie_name: cookie_value})
    (cache_run_dir / "node_output.txt").write_text(node_output, encoding="utf-8", errors="ignore")
    write_json(cache_run_dir / "cookies_after_node.json", session.cookies.get_dict())

    print("generated cookie ->", cookie_name, cookie_value[:32])
    print("session cookies ->", session.cookies.get_dict())
    return cookie_name, cookie_value, node_output


def home_check():
    response = session.get(TARGET_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    print("home check ->", response.status_code, response.url)
    return response


def request_api():
    if not API_URL:
        return None

    method = API_METHOD.upper()
    headers = {**HEADERS, **API_HEADERS}
    kwargs = {"headers": headers, "timeout": REQUEST_TIMEOUT}
    if method == "GET":
        kwargs["params"] = API_PARAMS
    else:
        if API_JSON is not None:
            kwargs["json"] = API_JSON
        elif API_DATA is not None:
            kwargs["data"] = API_DATA
        elif API_PARAMS is not None:
            kwargs["data"] = API_PARAMS

    response = session.request(method, API_URL, **kwargs)
    print("api check ->", response.status_code, response.text[:300])
    return response


def main():
    payload_bootstrap, payload_runner, cache_run_dir = first_request()
    second_request(payload_bootstrap, payload_runner, cache_run_dir)
    home_check()
    request_api()


if __name__ == "__main__":
    main()
