---
name: iv8-ruishu-reverse
description: >-
  瑞数/Ruishu/Rivers Security 的 Python + iv8 请求可用性复现专项 skill。仅在已有明确瑞数证据（如 $_ts、r2mKa、meta[r=m]、Cookie S/T/P、hasDebug、瑞数/Rivers 412/403）且用户目标是用紧凑 Python 主脚本通过 iv8 执行页面 JS 生成 cookie、捕获 XHR URL 后缀/header/cookieHeader，再用同一个 requests.Session 回放真实请求时触发。不要用于瑞数固定 Node 项目骨架、首跳材料缓存或最小 proxy 观察（交给 rs-reverse），也不要用于瑞数深度算法、r2mKa 字节码、URL suffix AST 研究、普通 sign/token 入口定位或通用 Node.js 补环境。
---

# iv8 Ruishu Reverse

本 skill 是从 `iv8-web-reverse` 中单独拆出的瑞数专项路线：交付一个可运行、紧凑、PyCharm 友好的 Python 主脚本，用 `iv8` 执行瑞数页面/运行时 JS，再用 Python `requests` 发真实 HTTP 请求。

默认仍生成极小 `utils/iv8_silent.py` 和 `utils/logger.py`。不要把它扩展成框架、CLI、通用模板集合或瑞数字节码研究工程。

## 硬性约束

- 自动下载或生成的目标站点动态材料统一写入当前工作目录的 `js_reverse_cache/`，不存在则先创建。
- 不要把新任务的动态素材写入本 skill 目录、`iv8-web-reverse` 目录或任何 `references/cases/`。
- 同一条验证链路必须使用同一个 `requests.Session` 的首跳 Cookie、挑战 HTML、动态 JS、iv8 生成 cookie、XHR 后缀/header、业务参数、时间戳和最终回放请求；不要混用旧值。
- 默认原样输出和保存逆向复现必需字段，不脱敏、不截断 cookie、token、header、sign、URL、请求体、响应字段或 suffix。只有用户明确要求公开脱敏版本时才处理。
- 如果目标转成瑞数算法深挖、r2mKa 字节码、URL suffix AST、session49、child[29]/child[40] 或 VM opcode 工具链，停止本 skill 路线。

## 参考来源

本 skill 复用 `iv8-web-reverse` 已验证的 iv8 API 规则和瑞数案例。执行任务时先读取这些文件：

- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/example-taxonomy.md`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/script-writing-rules.md`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/reverse-process/index.md`

瑞数最近案例优先读取：

- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/reverse-process/js-challenges/chinatax-ruishu-reverse-process.md`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/cases/js-challenges/chinatax-ruishu.py`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/reverse-process/js-challenges/customs-ruishu-reverse-process.md`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/cases/js-challenges/customs-ruishu.py`

需要 iv8 API 写法时，再读：

- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/api-inventory.md`
- `C:/Users/86153/.config/opencode/skills/iv8-web-reverse/references/api-examples/README.md`

## 触发范围

使用本 skill 当：

- 用户明确说瑞数、Ruishu、Rivers Security、瑞数 4/5/6、Rivers 动态安全防护，并且要求 `Python + iv8 + requests` 跑通请求。
- `412` / `403` challenge 有明确瑞数证据：`$_ts`、`$_ts.nsd`、`$_ts.cd`、`$_ts.l__`、`r2mKa`、`meta[r=m]`、Cookie `S/T/P` 或 `hasDebug`，且用户目标是 iv8 runtime reproduction。
- `rs-reverse` 的 Node 骨架、首跳材料或最小 proxy 观察已经不足以跑通请求，需要转为 iv8 页面执行或 `netLog` 捕获后缀/header/cookieHeader。
- 目标请求可用性依赖浏览器态触发 XHR/fetch 后得到最终 URL、动态后缀、请求 header 或 cookieHeader。
- 用户要求页码、关键词、pageSize、UA、URL 写在 Python 顶部常量中，并由脚本循环翻页请求。

不要使用本 skill 当：

- 只是创建或维护瑞数固定 Node 项目结构、缓存首跳材料、运行基础 Node cookie/runtime 检查、创建最小 proxy 模板。交给 `rs-reverse`。
- 只是定位 sign/token/header/cookie 写入点、脚本 URL、函数入口或调用链。交给 `find-crypto-entry`。
- 只是需要浏览器 DevTools hook snippet。交给 `browser-hook-snippets`。
- 任务是通用 Node.js 补环境。交给 `env-patch`。
- 任务是 AST 解混淆、控制流还原、字符串数组还原。交给 `ast-deobfuscate`。
- 任务是瑞数深度算法、r2mKa 字节码、URL suffix AST 或 VM opcode 研究。本 skill 不接管。
- 目标不是紧凑 iv8 脚本，而是完整分层协议恢复、多层加密、响应解密或传输包装。交给 `web-protocol-recovery`。

## 输出规则

- 默认生成一个短主 `.py` 脚本，同时生成 `utils/iv8_silent.py` 和 `utils/logger.py`。
- 顶部放可编辑常量，按需包含：`START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`KEYWORD`、`UA`、`PAGE_URL`、`API_URL`。
- 默认使用 `requests`；只有目标确实需要浏览器 TLS 指纹或参考案例已经使用时才用 `curl_cffi.requests`。
- 主脚本用 `from utils.iv8_silent import import_iv8_silent` 和 `iv8 = import_iv8_silent()` 静默导入 `iv8`。
- 主脚本用 `from utils.logger import logger`，业务输出用 `logger.info(...)`。
- 不添加 `logger.remove()` / `logger.add()`。
- 不添加 `sys.stdout.reconfigure(...)`。
- 业务流程附近写短中文注释。
- 终端打印完整响应。
- 默认不保存业务响应 JSON，除非用户明确要求。

## 工作流程

1. 确认瑞数证据和目标业务请求，记录首跳 URL、业务 API、UA、Referer、必要 Cookie 和请求体。
2. 读取 `iv8-web-reverse` 的 `script-writing-rules.md`，使用 `WORK_DIR = Path.cwd()` 和 `CACHE_DIR = WORK_DIR / "js_reverse_cache"` 规则。
3. 读取 `reverse-process/index.md`，优先选择 `chinatax-ruishu` 或 `customs-ruishu` 作为最近参考。
4. 用同一个 `requests.Session` 发送首跳请求，保存挑战 HTML、响应 headers、首跳 cookies 到 `js_reverse_cache/`。
5. 提取 `meta[r=m]`、`$_ts` inline/bootstrap、runner JS URL 或外链保护脚本；用同 session 和同 headers 下载 JS 并保存。
6. 创建 `iv8.JSContext(environment=..., config={"timezone": "Asia/Shanghai"})`，环境中的 `location`、`navigator.userAgent`、`document.cookie` 必须和首跳/session 一致。
7. 生命周期重要时优先使用 `__iv8__.page.load(snapshot)`；只有案例明确需要手工执行脚本时才手动设置 DOM 并按顺序 `ctx.eval(...)`。
8. 有 timer、promise、XHR 或 load 事件时，推进 `__iv8__.eventLoop.sleep(...)`、`drainMicrotasks()` 或 `drain()`。
9. 如果目标只需要 cookie，读取 `document.cookie` 并更新同一个 session 的 cookie jar。
10. 如果目标需要 URL 后缀/header/cookieHeader，在 iv8 内触发目标 XHR/fetch，从 `__iv8__.netLog.entries` 读取最终 URL、headers、cookieHeader 和 body 元数据。
11. 用 Python `requests` 回放捕获到的最终请求，保持 method、headers、cookieHeader、body、params 和 Referer 一致。
12. 如果翻页、关键词、timestamp 或 body 影响 suffix/header，必须在循环内重新触发 iv8 生成，不要复用上一页结果。
13. 可行时运行 `python -m py_compile <script.py> utils/iv8_silent.py utils/logger.py`。
14. 网络、Cookie、账号和目标环境允许时，再运行脚本验证 iv8 生成链路和真实请求状态码。

## 常见瑞数模式

### 两阶段 Cookie

1. 首跳拿到挑战 HTML、基础 Cookie 和 runner JS。
2. iv8 加载页面 snapshot 或按案例顺序执行 inline/bootstrap/runner。
3. 推进事件循环后读取 `document.cookie`。
4. 更新同 session cookie jar。
5. 用更新后的 cookie 重放业务请求。

### Cookie + XHR 后缀

1. 完成两阶段 Cookie。
2. 在 iv8 中构造和浏览器一致的 XHR/fetch 请求。
3. 从 `__iv8__.netLog.entries[-1]` 或匹配 URL 的 entry 中取最终 URL、header 和 cookieHeader。
4. 用 Python 回放最终 URL。

### Header / CookieHeader 重放

1. 不要只把 `document.cookie` 合并进 session 后盲发。
2. 参考 `netLog` 中的 `cookieHeader` 和 headers，必要时显式设置 `Cookie` 请求头。
3. 保持同一条链路里的 Referer、Origin、Content-Type、Accept、UA 和 body 一致。

## 依赖

核心依赖缺失时才安装：

```bash
python -m pip install iv8 requests
```

`loguru` 是可选依赖。除非用户明确要求，不安装。

## 完成报告

完成后简短报告：

- 脚本路径。
- `utils/iv8_silent.py` 路径。
- `utils/logger.py` 路径。
- 使用了哪个瑞数 bundled case 作为最近参考。
- 哪些顶部常量控制分页或请求输入。
- `js_reverse_cache/` 是否创建。
- 挑战 HTML、动态 JS、临时 runtime、netLog 样本或报告保存路径。
- iv8 cookie、URL 后缀、header 或 cookieHeader 生成是否验证成功。
- 最终真实请求返回 `200` 还是实际状态码。
- 是否没有保存响应 JSON。
