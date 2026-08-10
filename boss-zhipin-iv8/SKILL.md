---
name: boss-zhipin-iv8
description: Use ONLY for Boss Zhipin / BOSS 直聘 / zhipin.com iv8 reproduction tasks where the user wants a compact runnable Python script that handles `__zp_stoken__`, `__zp_sseed__`, `__zp_sname__`, `__zp_sts__`, `code=37`, `security-js/{name}.js`, `new window.ABC().z(seed, ts)`, or real job-list API replay with Python requests. Do not use for generic iv8 sites, JD h5st, XHS, PDD, BDMS, Ruishu, captcha/TDC, only locating token entry points, browser hook snippets, AST deobfuscation, or Node.js environment patching.
---

# Boss Zhipin iv8

本 skill 是从 `iv8-web-reverse` 收窄出来的 Boss 直聘专用版本，只用于交付一个可运行的紧凑 Python 脚本：用 `iv8` 执行 Boss 直聘安全 JS 生成 `__zp_stoken__`，再用 Python `requests` 重放 `www.zhipin.com` 真实接口。

默认目标是 PyCharm 友好的短主 `.py` 文件，可配套 `utils/iv8_silent.py` 和 `utils/logger.py`，不是通用 iv8 框架，也不是多站点案例库。

## 触发范围

使用本 skill 当用户目标包含：

- Boss 直聘、BOSS直聘、zhipin、`www.zhipin.com`、`wapi/zpgeek/search/joblist.json`。
- 需要用 Python + iv8 + requests 跑 Boss 直聘职位搜索、职位列表、翻页接口。
- API 返回 `code=37`，响应内有 `zpData.seed`、`zpData.name`、`zpData.ts`。
- 需要下载 `https://www.zhipin.com/web/common/security-js/{name}.js` 并计算 `__zp_stoken__`。
- 需要复现 `encodeURIComponent((new window.ABC).z(seed, ts))`。
- 需要刷新同一 session 里的 `__zp_stoken__`、`__zp_sseed__`、`__zp_sname__`、`__zp_sts__` 后重试 API。
- 用户要求关键词、城市、页码、pageSize、UA、Cookie 写在代码顶部。

不要使用本 skill 当：

- 目标不是 Boss 直聘 / zhipin.com。交给通用 `iv8-web-reverse` 或其他更窄 skill。
- 只定位 token 入口、脚本 URL 或调用链，不要求写 iv8 请求脚本。交给 `find-crypto-entry`。
- 只要浏览器 DevTools hook snippet。交给 `browser-hook-snippets`。
- 要 AST 解混淆、字符串数组还原、控制流平坦化。交给 `ast-deobfuscate`。
- 要 Node.js 补环境而不是 Python + iv8。交给 `env-patch`。
- 是 JD `h5st`、小红书 `X-s`、拼多多 `anti_content`、BDMS/a_bogus、瑞数、腾讯 TDC 或验证码任务。

## 参考文件

优先读取这些文件：

- `references/reverse-process/browser-tokens/zhipin-stoken-reverse-process.md`：Boss `__zp_stoken__` 逆向和复现步骤。
- `references/cases/browser-tokens/zhipin-stoken.py`：已验证的 Boss 直聘 iv8 + requests 案例。
- `references/script-writing-rules.md`：紧凑脚本、`utils/iv8_silent.py`、`utils/logger.py`、`js_reverse_cache/` 写法规则。
- `references/api-inventory.md`：iv8 API 索引。
- `references/api-examples/dom_pageload.py`：`__iv8__.page.load` 和外链脚本加载。
- `references/api-examples/event_loop.py`：`__iv8__.eventLoop.sleep(...)`。
- `references/api-examples/environment_fingerprint.py`：构造 `location`、`navigator`、`screen`、`canvas` 环境。
- `references/cases/js_reverse_cache/zhipin-stoken/`：Boss frozen 样本，仅作参考；新任务素材仍写当前工作目录 `js_reverse_cache/`。

## 固定复现流程

1. 用同一个 `requests.Session` 初始化用户提供或现场抓到的 Boss Cookie。
2. 请求目标 Boss API，例如 `https://www.zhipin.com/wapi/zpgeek/search/joblist.json`。
3. 如果响应不是 `code=37`，直接打印完整响应并继续翻页。
4. 如果响应是 `code=37`，读取 `zpData.seed`、`zpData.name`、`zpData.ts`。
5. 用同一个 session 下载 `https://www.zhipin.com/web/common/security-js/{name}.js`，保存到当前工作目录 `js_reverse_cache/`。
6. 构造 `security-check.html?seed=...&name=...&ts=...&callbackUrl=&srcReferer=...` 的 iv8 browser environment。
7. 构造包含安全 JS `<script src="..."></script>` 的 HTML snapshot，并用 `window.__iv8__.page.load(...)` 加载。
8. 推进事件循环，例如 `window.__iv8__.eventLoop.sleep(100)`。
9. 执行 `encodeURIComponent((new window.ABC).z(seed, ts))` 得到新的 `__zp_stoken__`。
10. 在同一个 session cookie jar 中按名称替换旧值，不要叠加第二个同名 Cookie。
11. 同步更新 `__zp_sseed__`、`__zp_sname__`、`__zp_sts__`。
12. 用同一个 headers、body、session 重试原 API。

## Boss 关键细节

- `seed`、`name`、`ts` 必须来自同一次 `code=37` 响应，不能混用旧值。
- `__zp_stoken__` 要用 `encodeURIComponent(...)` 后的值写入 Cookie。
- 旧 `__zp_stoken__` 必须从 session jar 中清掉或按名称覆盖，避免同名 Cookie 冲突。
- `referer` 应指向当前搜索页，例如 `/web/geek/jobs?query=...&city=...`。
- `origin` 固定为 `https://www.zhipin.com`。
- `x-requested-with: XMLHttpRequest` 通常需要保留。
- `page`、`pageSize`、`query`、`city` 放在顶部常量或构造函数里，翻页时每页重新构造请求体。
- Boss 安全 JS 依赖浏览器环境时，优先最小补 `location`、`navigator`、`screen`、`window.origin`、`devicePixelRatio` 和 canvas fingerprint。

## 输出规则

- 默认生成一个短主 `.py` 脚本，同时生成 `utils/iv8_silent.py` 和 `utils/logger.py`。
- 顶部放可编辑常量：`START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`KEYWORD`、`CITY_CODE`、`UA`、`PAGE_URL`、`API_URL`、`COOKIES`。
- 自动下载或生成的安全 JS、临时 HTML、token 样本统一保存到当前工作目录 `js_reverse_cache/`。
- 默认使用 `requests`，不要无故改用 `curl_cffi.requests`。
- 业务输出用 `logger.info(...)`，打印完整响应，不默认截断。
- 不添加 CLI 参数解析、大型类、通用框架或无关站点逻辑。
- 不默认保存完整业务响应 JSON；除非用户明确要求保存。

## 验证

至少运行语法校验：

```bash
python -m py_compile <script.py> utils/iv8_silent.py utils/logger.py
```

如果网络、Cookie、账号和目标环境允许，再运行脚本并报告：

- 是否命中 `code=37`。
- 是否下载到 `security-js/{name}.js`。
- iv8 是否生成非空 `__zp_stoken__`。
- 重试后的 HTTP 状态码和业务 `code`。
- `js_reverse_cache/` 内保存的动态素材路径。

## 完成报告

完成后简短报告：

- 主脚本路径。
- `utils/iv8_silent.py` 和 `utils/logger.py` 路径。
- 使用的 Boss 参考案例路径。
- 可编辑常量有哪些。
- `js_reverse_cache/` 是否创建，以及保存了哪些 Boss 动态素材。
- 语法校验和实际请求验证结果。
