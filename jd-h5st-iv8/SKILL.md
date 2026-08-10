---
name: jd-h5st-iv8
description: Use ONLY for JD/Jingdong `h5st` reproduction tasks where the user wants a compact runnable Python script that uses iv8 to execute JD browser-side signing JavaScript and then replays `api.m.jd.com/api` requests with Python HTTP. Trigger for JD mobile `h5st`, `ParamsSignMain`, `js_security_v3_main.js`, `m.jd.com`, `api.m.jd.com`, or requests to adapt the bundled JD h5st case. Do not use for generic iv8 sites, non-JD signatures, browser hook snippets, sign entry location only, AST deobfuscation, Node.js env patching, captcha, Ruishu, BDMS, or full protocol recovery.
---

# JD H5st iv8

本 skill 只用于京东 / Jingdong `h5st` 案例：交付一个紧凑、可运行的 Python 主脚本，用 `iv8` 执行 JD 浏览器侧签名 bundle，再用 Python HTTP 请求真实接口。

目标输出是 PyCharm 友好的单个主 `.py` 文件，默认配套极小的 `utils/iv8_silent.py` 和 `utils/logger.py`。不要做框架、CLI、通用模板集合或非京东站点适配。

## 触发范围

使用本 skill 当用户目标包含：

- 京东 / JD / Jingdong / `m.jd.com` / `api.m.jd.com` 的 `h5st` 生成或请求复现。
- 明确提到 `ParamsSignMain`、`_$sdnmd`、`appId: "2088b"` 或 `js_security_v3_main.js`。
- 要把 bundled JD h5st 案例改造成当前工作目录下可直接运行的紧凑 Python 脚本。
- 要用 `iv8 + requests` 或 `iv8 + curl_cffi.requests` 计算 JD `h5st` 并发真实请求。
- 要把页码、pageSize、UA、`PAGE_URL`、`API_URL`、JD body 等常量写在代码顶部。

不要使用本 skill 当：

- 只想定位 JD `h5st` 入口、脚本 URL 或调用链，交给 `find-crypto-entry`。
- 不是京东 `h5st`，而是小红书、拼多多、Boss、抖音、瑞数、腾讯 TDC、验证码、challenge cookie 或 BDMS，交给对应专用 skill 或 `iv8-web-reverse`。
- 只要浏览器 DevTools hook snippet，交给 `browser-hook-snippets`。
- 要 AST 解混淆或控制流还原，交给 `ast-deobfuscate`。
- 要 Node.js 沙箱补环境，交给 `env-patch`。
- 要完整 browser-free 分层协议采集器而非紧凑 iv8 脚本，交给 `web-protocol-recovery`。

## 参考文件

写代码前按顺序读取：

- `references/jd-h5st-reverse-process.md`：JD h5st 逆向流程和关键注意点。
- `references/cases/jd-h5st.py`：原始 bundled JD 案例。
- `references/cases/js_reverse_cache/js_security_v3_main.js`：frozen JD 签名 bundle。
- `references/cases/js_reverse_cache/jd_index.html`：frozen JD 页面 HTML。

这些文件只作为 JD 案例参考。新任务下载或生成的动态素材仍写入当前工作目录的 `js_reverse_cache/`，不要写入本 skill 目录。

## 硬性约束

- 自动下载、复制或生成的运行时材料统一写入当前工作目录的 `js_reverse_cache/`。
- 真实请求链路保持同一个 HTTP session 中的 Cookie、body、body hash、`h5st`、headers 和分页参数，不混用旧值。
- 如果 body、页码、时间戳或参数参与签名，必须在翻页循环内重建 body、hash 和 `h5st`。
- 本 skill 自带 bundled 素材保持脱敏；生成用户现场脚本时，默认不截断、不摘要输出 `h5st`、URL、headers、请求体、响应字段，只有用户明确要求公开脱敏版本时才进一步清理。
- 默认不把业务响应 JSON 保存到文件，除非用户明确要求。

## JD 固定模式

核心流程：

1. 读取或准备 `jd_index.html` 和 `js_security_v3_main.js`。
2. 创建 JD mobile-like `iv8.JSContext`，至少设置 `location.href = "https://m.jd.com/"`、`origin = "https://m.jd.com"`、`host = "m.jd.com"`。
3. 注入 `MessageChannel` patch，并用 `__iv8__.wrapNative` 包装。
4. 用 `document.documentElement.innerHTML = ...` 注入 frozen HTML。
5. `ctx.eval(js_code, name="https://storage.360buyimg.com/webcontainer/main/js_security_v3_main.js")` 执行签名 bundle。
6. 对请求 `body` 做 `hashlib.sha256(body.encode("utf-8")).hexdigest()`。
7. 调用 `new window.ParamsSignMain({appId: "2088b"})._$sdnmd({appid, functionId, body: body_hash}).h5st`。
8. 将 `h5st` 放入 `params`，发送 `https://api.m.jd.com/api` 真实请求。

必要 patch：

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

## 输出规则

- 默认生成一个短主脚本，例如 `jd_h5st_iv8.py`。
- 同时生成 `utils/iv8_silent.py` 和 `utils/logger.py`。
- 主脚本顶部放可编辑常量，按需包含：`START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`UA`、`PAGE_URL`、`API_URL`、`APPID`、`FUNCTION_ID`、`SIGN_APP_ID`。
- 默认用 `requests`；如果 bundled JD 案例或目标环境需要浏览器 TLS 指纹，可用 `curl_cffi.requests`，但不要无理由引入。
- 主脚本用 `from utils.iv8_silent import import_iv8_silent` 和 `iv8 = import_iv8_silent()`。
- 主脚本用 `from utils.logger import logger`，业务输出用 `logger.info(...)`。
- `logger.py` 用 `try loguru / PrintLogger` fallback，不安装 `loguru`，不添加 `logger.remove()` / `logger.add()`。
- 不添加 `sys.stdout.reconfigure(...)`。
- 业务流程附近写短中文注释。
- 终端打印完整响应。

## 建议脚本结构

主脚本使用当前工作目录缓存规则：

```python
from pathlib import Path

WORK_DIR = Path.cwd()
CACHE_DIR = WORK_DIR / "js_reverse_cache"
CACHE_DIR.mkdir(exist_ok=True)
```

优先从当前工作目录读取用户提供的新 JD 素材；没有提供时，可以从本 skill 的 frozen 参考素材复制到 `js_reverse_cache/` 再读取。复制后的运行素材路径应在完成报告里说明。

必要 helper 只保留当前脚本用到的函数，例如：

- `read_text(path)`
- `build_body(page)`
- `build_params(page)`
- `build_environment()`
- `make_h5st(ctx, params)`
- `print_response(page, resp)`

避免类、大型 wrapper、通用下载框架和未使用能力。

## 生成脚本流程

1. 读取 `references/jd-h5st-reverse-process.md` 和 `references/cases/jd-h5st.py`。
2. 在当前工作目录创建 `js_reverse_cache/`。
3. 若用户没有提供当前 JD bundle/HTML，将 bundled `js_security_v3_main.js`、`jd_index.html` 复制到当前工作目录的 `js_reverse_cache/` 使用。
4. 写 `jd_h5st_iv8.py`、`utils/iv8_silent.py`、`utils/logger.py`。
5. 在翻页循环内构造 JD body、params、body hash 和 `h5st`。
6. 用同一个 HTTP session 发送真实请求并打印完整响应。
7. 可行时运行 `python -m py_compile jd_h5st_iv8.py utils/iv8_silent.py utils/logger.py`。
8. 如果网络和目标环境允许，再运行脚本验证 `h5st` 生成和真实请求状态码。

## 依赖

核心依赖缺失时才安装：

```bash
python -m pip install iv8 requests
```

如果明确使用 `curl_cffi.requests`：

```bash
python -m pip install curl_cffi
```

## 完成报告

完成后简短报告：

- 主脚本路径。
- `utils/iv8_silent.py` 路径。
- `utils/logger.py` 路径。
- 使用的 JD 参考案例路径：`references/cases/jd-h5st.py`。
- 控制分页或请求输入的顶部常量。
- `js_reverse_cache/` 是否创建。
- 使用的 `jd_index.html` 和 `js_security_v3_main.js` 路径。
- `h5st` 生成是否验证成功。
- 最终真实请求返回 `200` 还是实际状态码。
- 是否没有保存响应 JSON。
