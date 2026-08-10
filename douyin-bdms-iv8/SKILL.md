---
name: douyin-bdms-iv8
description: Use ONLY for Douyin / 抖音 / ByteDance BDMS iv8 reproduction tasks where the user wants a compact runnable Python script that initializes `window.bdms`, triggers a protected XHR/fetch in iv8, reads the rewritten URL or request metadata from `__iv8__.netLog.entries`, and replays the real request with Python requests. Trigger for `www.douyin.com`, `www-hj.douyin.com`, `aweme/v1`, `aweme/v2`, `BDMS`, `window.bdms.init`, `a_bogus`-style rewritten URLs, or Douyin XHR URL signing. Do not use for generic iv8 sites, PDD anti_content, JD h5st, XHS headers, Boss stoken, Ruishu, captcha/TDC, only locating entry points, browser hook snippets, AST deobfuscation, or Node.js environment patching.
---

# Douyin BDMS iv8

本 skill 只用于抖音 / ByteDance BDMS 风格请求复现：在 `iv8` 中初始化 `window.bdms`，触发受保护 XHR，让 BDMS runtime 改写 URL 或请求元数据，再从 `__iv8__.netLog.entries` 读取最终请求并用 Python `requests` 重放。

不要把其他网站案例、通用 iv8 案例或非抖音 BDMS 工作流混入本 skill。

## 适用场景

使用本 skill 当用户目标包含：

- 抖音 / Douyin / ByteDance Web 请求复现。
- 目标域名包含 `www.douyin.com` 或 `www-hj.douyin.com`。
- API 路径类似 `/aweme/v1/`、`/aweme/v2/`、`/webcast/`、`/live/`、`/ecom/`。
- 需要加载 BDMS runtime 并调用 `window.bdms.init({...})`。
- JS SDK hook XHR/fetch 后改写 URL，最终 URL 需要从 `__iv8__.netLog.entries` 读取。
- 目标描述为 `a_bogus` 风格参数、BDMS URL signing、XHR URL rewrite 或动态后缀。
- 用户要求交付可运行的 `Python + iv8 + requests` 脚本。

不要使用本 skill 当：

- 只是要定位 `a_bogus` / BDMS 入口、脚本 URL 或调用链，还不需要复现脚本：交给 `find-crypto-entry`。
- 只是要浏览器 hook 脚本：交给 `browser-hook-snippets`。
- 目标是通用 iv8 复现但不是抖音 BDMS：交给 `iv8-web-reverse` 或对应专用 skill。
- 目标是 AST 解混淆：交给 `ast-deobfuscate`。
- 目标是在 Node.js 中补环境跑通：交给 `env-patch`。
- 目标是拼多多 `anti_content`、京东 `h5st`、小红书 `X-s`、Boss 直聘 `__zp_stoken__`、瑞数或验证码/TDC。

## 参考文件

- `references/cases/network-hook-signing/douyin-bdms.py`：唯一 bundled case，抖音 BDMS runtime hook XHR 并从 `netLog` 读取改写 URL。
- `references/reverse-process/network-hook-signing/douyin-bdms-reverse-process.md`：逆向流程说明，适配前先读。
- `references/cases/js_reverse_cache/bdms_1.0.1.19.js`：案例依赖的 frozen BDMS runtime。

## 核心流程

1. 读取本 skill 自带的 `bdms_1.0.1.19.js`。
2. 创建抖音页面态 `iv8.JSContext`，补 `location`、`navigator`、必要的 `window` 字段。
3. 如 runtime 需要，使用 `__iv8__.wrapNative` patch `MessageChannel`。
4. `ctx.eval(...)` 执行 BDMS runtime。
5. 调用 `window.bdms.init({...})`，配置 `aid`、`pageId`、`paths`、`boe`、`ddrt`、`ic` 等参数。
6. 在 iv8 中构造目标 API 的 `XMLHttpRequest` 或 fetch。
7. 读取 `window.__iv8__.netLog.entries`，以其中最终 URL、headers、cookie metadata 为准。
8. 把 netLog 中的最终请求交给 Python `requests` 重放。
9. 保存 netLog 到当前工作目录 `js_reverse_cache/`，便于检查 URL 改写结果。

## 输出规则

- 默认在当前工作目录生成一个紧凑主 `.py` 脚本。
- 运行时 netLog、临时材料写到当前工作目录的 `js_reverse_cache/`。
- 不要把运行时抓到的新请求、Cookie 或响应写回 skill 目录。
- 顶部放可编辑常量，例如 `VIDEO_URL`、`API_URL`、`AWEME_ID`、`UA`、`COOKIES`、`BDMS_PATHS`。
- 默认使用 `requests.Session` 或 `requests.get/post`，保持 headers、cookies 和 netLog 捕获的最终 URL 一致。
- 默认打印完整响应，不脱敏、不截断 URL、Cookie、headers、响应字段；只有用户明确要求公开脱敏版本时才处理。
- 可行时运行 `python -m py_compile <script.py>` 验证语法。

## 实现要点

- `netLog` 是最终请求的事实来源，不要手工猜测或重写 BDMS 生成的 URL 参数。
- `window.bdms.init(...)` 的 `paths` 必须覆盖目标 API 路径，否则 XHR 不会被改写。
- 如果 `netLog.entries` 为空，优先检查 XHR URL 是否匹配 `paths`，以及 BDMS runtime 是否成功初始化。
- 如果 runtime 报 `MessageChannel` 或异步相关错误，先加入案例中的 `MessageChannel` shim。
- 如果真实请求失败，优先确认 Cookie、UA、referer/origin、API host 和 netLog 捕获 URL 是否来自同一轮运行。

## 案例适配

适配新抖音接口时，先读：

1. `references/reverse-process/network-hook-signing/douyin-bdms-reverse-process.md`
2. `references/cases/network-hook-signing/douyin-bdms.py`

然后只替换当前目标所需的页面 URL、API URL、query params、headers、cookies 和 `window.bdms.init` 的 path 配置。不要复制其他站点逻辑。
