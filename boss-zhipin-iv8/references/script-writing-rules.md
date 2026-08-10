# 脚本写作规则

生成目标站脚本时使用本文件。默认输出一个可直接运行的紧凑主 `.py` 文件；可附带 `utils/iv8_silent.py` 和 `utils/logger.py` 这种最小公共 helper，不做框架、CLI 或通用工程。

## 默认骨架

顶部放可编辑常量和缓存目录。`js_reverse_cache/` 必须位于当前运行工作目录，用于保存动态 JS、挑战 HTML、临时 runtime、样本和运行报告。

skill 自带真实案例的本地 JS/HTML 素材放在 `references/cases/js_reverse_cache/`。新任务下载到的素材仍必须写入当前运行工作目录的 `js_reverse_cache/`，不要写回 skill 目录。只有用户明确要求“沉淀为案例 / 回写到 skill / 新增 bundled case”时，才按 `references/case-ingestion-rules.md` 把最小 frozen 素材复制到 `references/cases/js_reverse_cache/<site-slug>/`。默认保留原始字段，不脱敏、不截断；只有用户明确要求公开脱敏版本时才清理。

读取 bundled case 时，先读 `references/reverse-process/index.md`。如果该索引里有对应条目，就先读对应 `references/reverse-process/<category>/<site-slug>-reverse-process.md`，再读 case `.py`；如果没有对应逆向过程文档，就直接读 case `.py`。新增 bundled case 时默认补一份同名 `*-reverse-process.md`，除非该案例只是纯代码格式调整且没有独立逆向流程。

创建新任务基础模板时，默认创建 `utils/iv8_silent.py` 和 `utils/logger.py`，主脚本只导入 `import_iv8_silent()` 和 `logger`；不要在每个主脚本里重复粘贴 iv8 banner 静默代码或 loguru fallback 代码，除非用户明确要求单文件交付。

```python
# pyright: reportMissingImports=false
import json
import sys
import time
import urllib.parse
from pathlib import Path

import requests

from utils.iv8_silent import import_iv8_silent
from utils.logger import logger

iv8 = import_iv8_silent()


START_PAGE = 1
PAGE_COUNT = 1
PAGE_SIZE = 10
KEYWORD = ""
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
PAGE_URL = "https://example.com/page"
API_URL = "https://example.com/api"

WORK_DIR = Path.cwd()
CACHE_DIR = WORK_DIR / "js_reverse_cache"
CACHE_DIR.mkdir(exist_ok=True)
```

不要添加 `sys.stdout.reconfigure(...)`。PyCharm 输出不需要它，而且可能破坏嵌入控制台。

## `utils/iv8_silent.py`

基础模板默认创建该文件，用于去除 `import iv8` 时打印的 banner。该 helper 只放通用静默导入能力，不放目标站 URL、Cookie、签名逻辑或动态素材。

```python
import contextlib
import importlib
import io
import os
import sys


@contextlib.contextmanager
def silent_import():
    sys.stdout.flush()
    sys.stderr.flush()
    stdout = sys.__stdout__ or sys.stdout
    stderr = sys.__stderr__ or sys.stderr
    saved_stdout = os.dup(stdout.fileno())
    saved_stderr = os.dup(stderr.fileno())
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, stdout.fileno())
        os.dup2(devnull, stderr.fileno())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield
    finally:
        os.dup2(saved_stdout, stdout.fileno())
        os.dup2(saved_stderr, stderr.fileno())
        os.close(saved_stdout)
        os.close(saved_stderr)
        os.close(devnull)


def import_iv8_silent():
    with silent_import():
        return importlib.import_module("iv8")
```

## `utils/logger.py`

基础模板默认创建该文件，用于统一 `loguru` 可选导入和 fallback 输出。不要在主脚本重复粘贴这段逻辑，不要添加 `logger.remove()` / `logger.add()`。

```python
import sys

try:
    from loguru import logger
except ImportError:
    class PrintLogger:
        @staticmethod
        def info(message, *args):
            if args:
                message = message.format(*args)
            out = getattr(sys.stdout, "buffer", None)
            if out:
                out.write((message + "\n").encode("utf-8", errors="replace"))
                out.flush()
            else:
                print(message)

    logger = PrintLogger()
```

## 缓存规则

所有自动下载或生成的目标站动态素材都写入 `CACHE_DIR`：

- challenge HTML，例如 `CACHE_DIR / "challenge.html"`。
- 下载到的保护 JS，例如 `CACHE_DIR / "rs_source_code.js"`。
- 临时 runtime JS，例如 `CACHE_DIR / "runtime_sign.js"`。
- XHR/netLog 样本，例如 `CACHE_DIR / "netlog.json"`，仅在用户明确要保存样本时保存。
- 运行报告，例如 `CACHE_DIR / "run_report.txt"`，仅在确有必要时保存。

默认不保存业务响应 JSON，不创建 `artifacts/`。

默认原样打印和保存逆向复现所需字段，不脱敏、不截断 cookie、Authorization、token、storage、header、sign、URL、请求体、响应字段、telemetry 或最终 suffix。只有用户明确要求“脱敏 / 截断 / 只打印摘要 / 公开发布版本”时，才输出裁剪或清理后的版本。

案例回写是显式例外：先在当前工作目录完成复现和验证，再只复制最小可复用素材到 skill 的 `references/cases/js_reverse_cache/<site-slug>/`。默认不清理真实案例字段；如果用户要求公开脱敏版本，再按 `references/case-ingestion-rules.md` 清理。不要默认把运行报告、完整响应 JSON 或一次性抓包大文件写入 skill，除非用户明确要求保存。

```python
def save_text(name, text):
    path = CACHE_DIR / name
    path.write_text(text, encoding="utf-8", errors="ignore")
    return path
```

如果需要按站点或时间分目录：

```python
RUN_DIR = CACHE_DIR / time.strftime("%Y%m%d_%H%M%S")
RUN_DIR.mkdir(exist_ok=True)
```

## 常用小函数

只添加当前脚本用得上的 helper。

### 打印完整响应

```python
def print_response(page, resp):
    try:
        text = json.dumps(resp.json(), ensure_ascii=False)
    except ValueError:
        text = resp.text
    logger.info("page={} status={} full response:\n{}", page, resp.status_code, text)
```

### 从 URL 构造 iv8 environment

```python
def build_environment(page_url):
    parsed = urllib.parse.urlparse(page_url)
    return {
        "location": {
            "href": page_url,
            "origin": f"{parsed.scheme}://{parsed.netloc}",
            "protocol": f"{parsed.scheme}:",
            "host": parsed.netloc,
            "hostname": parsed.hostname or "",
            "port": str(parsed.port or ""),
            "pathname": parsed.path or "/",
            "search": f"?{parsed.query}" if parsed.query else "",
            "hash": f"#{parsed.fragment}" if parsed.fragment else "",
        },
        "navigator": {
            "userAgent": UA,
            "platform": "Win32",
            "language": "zh-CN",
            "languages": ["zh-CN", "zh", "en"],
            "webdriver": False,
        },
    }
```

### Cookie 合并

```python
def update_session_cookies(session, cookie_text):
    cookies = {}
    for part in (cookie_text or "").split(";"):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        cookies[key] = value
    if cookies:
        session.cookies.update(cookies)
    return cookies
```

### MessageChannel patch

仅当目标案例或目标 JS 确实需要时添加。

```python
MESSAGE_CHANNEL_PATCH = """
window.MessageChannel = __iv8__.wrapNative(function() {
    const port1 = { onmessage: null };
    const port2 = { onmessage: null };
    port1.postMessage = function(data) {
        if (port2.onmessage) setTimeout(() => port2.onmessage({data}), 0);
    };
    port2.postMessage = function(data) {
        if (port1.onmessage) setTimeout(() => port1.onmessage({data}), 0);
    };
    return { port1, port2 };
}, 'MessageChannel');
"""
```

## 翻页规则

使用顶部常量控制翻页。

```python
for page in range(START_PAGE, START_PAGE + PAGE_COUNT):
    params = build_params(page)
    headers = build_headers(params)
    resp = session.get(API_URL, params=params, headers=headers, timeout=30)
    print_response(page, resp)
```

如果 params/body/timestamp 参与签名，每一页都必须在循环里重新构造 params/body/timestamp/sign。

## Challenge Cookie 模式

适用于保护页必须在 iv8 中执行的场景。

```python
def run_snapshot_cookie(page_url, html, resources, headers=None):
    environment = build_environment(page_url)
    snapshot = {
        "baseURL": page_url,
        "html": html,
        "headers": headers or [],
        "resources": resources,
    }
    with iv8.JSContext(environment=environment, config={"timezone": "Asia/Shanghai"}) as ctx:
        ctx.expose(snapshot, "snapshot")
        ctx.eval("window.__iv8__.page.load(window.__iv8__.data.snapshot)")
        ctx.eval("window.__iv8__.eventLoop.sleep(100)")
        cookie_text = ctx.eval("document.cookie")
        if not cookie_text:
            cookie_text = ctx.eval("""
                var entries = window.__iv8__.netLog.entries;
                entries.length ? (entries[entries.length - 1].cookieHeader || '') : '';
            """)
        return cookie_text
```

保护源码保存到缓存目录：

```python
rs_path = save_text("rs_source_code.js", js_code)
logger.info("rs source saved = {}", rs_path)
```

## XHR Hook / 动态 URL 模式

适用于 JS SDK 改写 XHR URL 或 headers 的场景。

```python
def capture_xhr_entry(environment, js_code, init_code, api_url, params, method="GET", body=None):
    query = urllib.parse.urlencode(params, safe="*")
    request_url = f"{api_url}?{query}" if query else api_url
    with iv8.JSContext(environment=environment, config={"timezone": "Asia/Shanghai"}) as ctx:
        ctx.eval(MESSAGE_CHANNEL_PATCH)
        ctx.eval(js_code)
        if init_code:
            ctx.eval(init_code)
        entry = ctx.eval(f"""
            var xhr = new XMLHttpRequest();
            xhr.open({json.dumps(method)}, {json.dumps(request_url)}, true);
            xhr.setRequestHeader('Content-Type', 'application/json, text/plain, */*');
            xhr.send({json.dumps(body) if body is not None else 'null'});
            window.__iv8__.eventLoop.sleep(100);
            var entries = window.__iv8__.netLog.entries;
            entries[entries.length - 1];
        """, to_py=True)
    if not entry:
        raise RuntimeError("iv8 netLog did not capture the protected XHR")
    return entry
```

Python 重放时使用捕获到的 `url`、可选 `headers`、准确 body 序列化和 cookie。

## Runtime Sign 模式

适用于已知对象/函数直接返回 sign/header/token 的场景。

```python
def run_sign(js_code, call_code, page_url=PAGE_URL, page_html=""):
    with iv8.JSContext(environment=build_environment(page_url), config={"timezone": "Asia/Shanghai"}) as ctx:
        ctx.eval(MESSAGE_CHANNEL_PATCH)
        if page_html:
            ctx.eval(f"document.documentElement.innerHTML = {json.dumps(page_html)}")
        ctx.eval(js_code)
        return ctx.eval(call_code, to_py=True)
```

`call_code` 应返回字符串或 dict，便于 Python 合并进 params、headers、cookies 或 body。

## 可信输入模式

适用于 TDC 或行为采集。

```javascript
const st = window.__iv8__;
const input = st.input;
const handle = document.body || document.documentElement;

input.dispatchPointerEvent({
    type: "pointerdown",
    target: handle,
    pointerId: 1,
    pointerType: "mouse",
    isPrimary: true,
    clientX: 50,
    clientY: 400,
    button: 0,
    buttons: 1
});

st.eventLoop.sleep(16);

input.dispatchPointerEvent({
    type: "pointerup",
    target: document,
    pointerId: 1,
    pointerType: "mouse",
    isPrimary: true,
    clientX: 300,
    clientY: 400,
    button: 0,
    buttons: 0
});
```

完整轨迹循环见 `references/cases/captcha/tencent-tdc-slider.py`。

## 依赖

默认最小导入：

```python
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

from utils.iv8_silent import import_iv8_silent
from utils.logger import logger
```

按需添加：

- `hashlib`：MD5/SHA 签名。
- `cv2`、`numpy`、`urllib3`：TDC 图像匹配和 TLS warning 处理。
- `curl_cffi.requests`：目标确实需要浏览器 TLS 指纹时使用。

核心依赖缺失且用户允许安装时，只安装缺失核心包：

```bash
python -m pip install iv8 requests
```

`loguru` 是可选依赖，不默认安装。

## 验证

至少做语法校验：

```bash
python -m py_compile your_script.py
python -m py_compile utils/iv8_silent.py
python -m py_compile utils/logger.py
```

如果网络、Cookie、账号和目标环境允许，再运行脚本。报告 HTTP 状态码，以及 iv8 是否返回了非空 cookie/sign/header/token/URL。
