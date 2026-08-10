---
name: xhs-homefeed-iv8
description: Use ONLY for Xiaohongshu / 小红书 / XHS PC request-signing reproduction tasks where the user wants a compact runnable Python script using iv8 to initialize `signV2Init()`, expose `window.mnsv2`, generate `X-s`, `X-t`, and `X-S-Common`, then replay real requests with Python requests. Trigger for `www.xiaohongshu.com`, `edith.xiaohongshu.com`, `/api/sns/web/v1/homefeed`, `signV2Init`, `window.mnsv2`, `X-s`, `X-S-Common`, `a1`, `b1`, `dsllt`, `_dsl`, or XHS browser seed signing. Do not use for generic iv8 sites, PDD anti_content, Douyin BDMS/a_bogus, JD h5st, Boss stoken, Ruishu, captcha/TDC, only locating entry points, browser hook snippets, AST deobfuscation, or Node.js environment patching.
---

# XHS Homefeed iv8

本 skill 只用于小红书 / Xiaohongshu / XHS PC 请求签名复现：用 `iv8` 初始化 `signV2Init()`，得到 `window.mnsv2`，根据请求 payload 和浏览器 seed 生成 `X-s`、`X-t`、`X-S-Common`，再用 Python `requests` 发送真实请求。

不要把其他网站案例、通用 iv8 案例或非小红书签名工作流混入本 skill。

## 适用场景

使用本 skill 当用户目标包含：

- 小红书 / XHS / Xiaohongshu PC 接口复现。
- 目标域名包含 `www.xiaohongshu.com` 或 `edith.xiaohongshu.com`。
- API 类似 `https://edith.xiaohongshu.com/api/sns/web/v1/homefeed`。
- 需要生成请求头 `X-s`、`X-t`、`X-S-Common`。
- 已知或怀疑入口是 `signV2Init()` / `window.mnsv2`。
- 签名依赖 Cookie / localStorage seed，例如 `a1`、`b1`、`b1b1`、`dsllt`、`dsl`、`sc`。
- 用户要求交付可运行的 `Python + iv8 + requests` 脚本。

不要使用本 skill 当：

- 只是要定位 `X-s` / `X-S-Common` 入口、脚本 URL 或调用链，还不需要复现脚本：交给 `find-crypto-entry`。
- 只是要浏览器 hook 脚本：交给 `browser-hook-snippets`。
- 目标是通用 iv8 复现但不是小红书：交给 `iv8-web-reverse` 或对应专用 skill。
- 目标是 AST 解混淆：交给 `ast-deobfuscate`。
- 目标是在 Node.js 中补环境跑通：交给 `env-patch`。
- 目标是拼多多 `anti_content`、抖音 BDMS/a_bogus、京东 `h5st`、Boss 直聘 `__zp_stoken__`、瑞数或验证码/TDC。

## 参考文件

- `references/cases/signatures/xhs-homefeed.py`：唯一 bundled case，小红书 PC homefeed 生成 `X-s` / `X-S-Common` 并请求真实接口。
- `references/reverse-process/signatures/xhs-homefeed-reverse-process.md`：逆向流程说明，适配前先读。
- `references/cases/js_reverse_cache/xhs-homefeed/signV2Init_function.json`：frozen `signV2Init()` 源码。
- `references/cases/js_reverse_cache/xhs-homefeed/xhs_header_sign.js`：封装 `window.mnsv2(...)` 的 header 生成 helper。
- `references/cases/js_reverse_cache/xhs-homefeed/runtime_seed.sample.json`：运行所需 Cookie/localStorage seed 结构样例，不包含账号私密值。

## 核心流程

1. 读取 bundled `runtime_seed.sample.json`，按需合并用户提供的登录 Cookie 或浏览器 seed。
2. 构造小红书 PC 页面态 `iv8.JSContext`，补 `location`、`navigator`、`screen`、`window`、DOM、storage、performance 等基础环境。
3. 加载 `signV2Init_function.json` 中的 `src` 并执行 `signV2Init()`。
4. 校验 `typeof window.mnsv2 === "function"`。
5. 加载 `xhs_header_sign.js`，获得 `generateHeaders(payload, seed)`。
6. 构造业务 payload，注意 JSON 字段顺序和紧凑序列化会参与 `X-s`。
7. 通过 `ctx.expose(...)` 传入 `{payload, seed}`。
8. 调用 `generateHeaders(...)` 得到 `X-s`、`X-t`、`X-S-Common` 和调试用 `X-S-Common-Object`。
9. 构造 Python 请求 headers，合并签名头，用同一个 `requests.Session` 携带 Cookie 请求接口。
10. 每页或每次请求都重新构造 payload 并重新生成签名 headers。

## 输出规则

- 默认在当前工作目录生成一个紧凑主 `.py` 脚本。
- 运行时下载或生成的临时材料写到当前工作目录的 `js_reverse_cache/`。
- 不要把真实账号 Cookie、localStorage seed、响应 JSON 或一次性调试报告写回 skill 目录。
- 顶部放可编辑常量，例如 `START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`CATEGORY`、`UA`、`PAGE_URL`、`API_URL`、`API_PATH`、`LOGIN_COOKIES`。
- 默认使用 `requests.Session`，保持 Cookie、payload、seed 和签名 headers 同轮一致。
- 默认打印完整响应，不脱敏、不截断签名头、Cookie、响应字段；只有用户明确要求公开脱敏版本时才处理。
- 可行时运行 `python -m py_compile <script.py>` 验证语法。

## 实现要点

- `X-s` 依赖 body serialization，POST body 应使用 `json.dumps(payload, separators=(",", ":"), ensure_ascii=False)`。
- `a1` Cookie 和 localStorage seed 必须与目标请求会话一致。
- `signV2Init()` 不是仅由 `api/sec/v1/ds` 直接导出；案例使用 frozen page bundle module 源码恢复 `window.mnsv2`。
- 如果 `window.mnsv2` 初始化失败，优先检查 `signV2Init_function.json`、DOM/storage bootstrap 和 iv8 执行错误。
- 如果接口返回风控或签名失败，优先确认 `a1`、`b1`、`dsllt/_dsl`、payload 字段顺序、`API_PATH`、UA、referer/origin 是否一致。

## 案例适配

适配新小红书接口时，先读：

1. `references/reverse-process/signatures/xhs-homefeed-reverse-process.md`
2. `references/cases/signatures/xhs-homefeed.py`

然后只替换当前目标所需的页面 URL、API URL、API path、payload、headers、Cookie/localStorage seed 和分页逻辑。不要复制其他站点逻辑。
