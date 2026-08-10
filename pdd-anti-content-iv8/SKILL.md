---
name: pdd-anti-content-iv8
description: Use ONLY for Pinduoduo / 拼多多 / PDD PC `anti_content` reproduction tasks where the user wants a compact runnable Python script using iv8 to execute Pinduoduo browser-side webpack JavaScript and replay real requests with Python requests. Trigger for `anti_content`, `apiv2.pinduoduo.com`, `www.pinduoduo.com`, `query_tf_goods_info`, `api/server/_stm`, webpack module `fbeZ`, or `messagePackSync()`. Do not use for generic iv8 sites, JD h5st, XHS, Boss, BDMS/a_bogus, Ruishu, captcha/TDC, only locating entry points, browser hook snippets, AST deobfuscation, or Node.js environment patching.
---

# PDD Anti Content iv8

本 skill 只用于拼多多 PC 站 `anti_content` 复现：用 `iv8` 加载拼多多当前 Next.js / webpack chunk，捕获 `__webpack_require__`，调用内部混淆模块生成 `anti_content`，再用 Python `requests` 请求真实接口。

不要把其他网站案例、通用 iv8 案例或非 PDD 工作流混入本 skill。

## 适用场景

使用本 skill 当用户目标包含：

- 拼多多 / PDD / Pinduoduo PC 页面接口复现。
- 需要生成查询参数 `anti_content`。
- 目标包含 `www.pinduoduo.com` 或 `apiv2.pinduoduo.com`。
- 目标接口类似 `https://apiv2.pinduoduo.com/api/gindex/tf/query_tf_goods_info`。
- 需要请求 `https://apiv2.pinduoduo.com/api/server/_stm` 获取 `server_time`。
- 已知或怀疑入口是 webpack 模块 `fbeZ` 和 `new fbeZ({serverTime}).messagePackSync()`。
- 用户要求交付可运行的 `Python + iv8 + requests` 脚本。

不要使用本 skill 当：

- 只是要找 `anti_content` 入口、脚本 URL 或调用链，还不需要复现脚本：交给 `find-crypto-entry`。
- 只是要浏览器 hook 脚本：交给 `browser-hook-snippets`。
- 目标是通用 iv8 复现但不是拼多多：交给 `iv8-web-reverse` 或对应专用 skill。
- 目标是 AST 解混淆：交给 `ast-deobfuscate`。
- 目标是在 Node.js 中补环境跑通：交给 `env-patch`。
- 目标是京东 `h5st`、小红书 `X-s`、Boss 直聘 `__zp_stoken__`、BDMS/a_bogus、瑞数或验证码/TDC。

## 参考文件

- `references/cases/signatures/pdd-anti-content.py`：唯一 bundled case，拼多多 PC 分类页 `anti_content` 复现脚本。
- `references/reverse-process/signatures/pdd-anti-content-reverse-process.md`：逆向流程说明，适配前先读。

## 核心流程

1. 用同一个 `requests.Session` 请求拼多多 PC 分类页，例如 `https://www.pinduoduo.com/home/girlclothes/`。
2. 保存当前 HTML 到当前工作目录 `js_reverse_cache/`。
3. 从 HTML 提取当前 Next.js / webpack script URL。
4. 下载当前 `subject.js`、`_app.js`、webpack runtime 和 commons chunk 到当前工作目录 `js_reverse_cache/`。
5. 请求 `https://apiv2.pinduoduo.com/api/server/_stm`，读取 `server_time`。
6. 创建 PC 浏览器态 `iv8.JSContext`，补 `location`、`navigator`、`screen`、`window` 等基础环境。
7. 按页面顺序 `ctx.eval(...)` 下载到的 webpack chunk。
8. 通过 `window.webpackJsonp.push(...)` 注入小 chunk，捕获 `__webpack_require__` 到 `window.__pdd_require__`。
9. 调用 `window.__pdd_require__('fbeZ')` 获取模块。
10. 执行 `new fbeZ({serverTime}).messagePackSync()`，推进 microtask/timer，得到 `anti_content`。
11. 把 `anti_content` 放进业务 API query params，用同一个 session 发真实请求。
12. 翻页或每次请求前重新获取 `server_time` 并重新生成 `anti_content`。

## 输出规则

- 默认在当前工作目录生成一个紧凑主 `.py` 脚本。
- 自动下载的 HTML、JS chunk、临时材料都写到当前工作目录的 `js_reverse_cache/`。
- 不要把运行时下载到的新 chunk 写回 skill 目录。
- 顶部放可编辑常量，例如 `START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`TF_ID`、`UA`、`PAGE_URL`、`STM_URL`、`API_URL`。
- 默认使用 `requests.Session`，保持 Cookie、headers、server time 和 `anti_content` 在同一请求链路中一致。
- 默认打印完整响应，不脱敏、不截断 `anti_content`、Cookie、URL、响应字段；只有用户明确要求公开脱敏版本时才处理。
- 可行时运行 `python -m py_compile <script.py>` 验证语法。

## 实现要点

- 不能硬编码静态 chunk hash；必须从当前页面 HTML 重新发现并下载 webpack 资源。
- `anti_content` 长度通常较长，生成后至少检查非空且长度合理。
- 如果 `fbeZ` 不存在，优先重新检查当前 chunk 加载顺序和页面是否变化。
- 如果 promise 未完成，推进 `__iv8__.eventLoop.drainMicrotasks()`、`drain()` 和少量 `sleep(...)`。
- 如果业务 API 失败，优先确认 `server_time`、`TF_ID`、`referer/origin`、UA 和 `anti_content` 是否同一轮生成。

## 案例适配

适配新拼多多接口时，先读：

1. `references/reverse-process/signatures/pdd-anti-content-reverse-process.md`
2. `references/cases/signatures/pdd-anti-content.py`

然后只替换当前目标所需的页面 URL、接口 URL、业务 params、分页参数和 headers。不要复制其他站点逻辑。
