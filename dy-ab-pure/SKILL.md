---
name: dy-ab-pure
description: >-
  抖音 Web BDMS `a_bogus` 纯 Python 纯算技能。适合用户明确要求“抖音 a_bogus 纯算”“不依赖 iv8/jsdom/浏览器/JS 环境”“把 BDMS/a_bogus 全流程还原成 Python requests 脚本”“基于已还原的 pure_abogus.py 生成/维护请求脚本”。本 skill 固定处理 douyin.com `aweme/v1/web/*` BDMS 1.0.1.19 风格链路：SM3 digest、UA 加密 sign_value、slot 字段组装、slot86/slot90 bit-pack、RC4-like transform、动态 alphabet Base64。不要用于：从零定位签名入口（转 camoufox-js-reverse）、只要 iv8 喂入截出请求脚本（转 iv8-web-reverse）、只要浏览器 hook snippet（转 browser-hook-snippets）、AST 解混淆（转 ast-deobfuscate）、通用 Node/jsdom 补环境（转 env-patch）、非抖音或非 a_bogus 的完整协议恢复（转 web-protocol-recovery）。
argument-hint: "[抖音接口URL/现有纯算项目路径/需要生成的Python请求脚本]"
compatibility: "Python 3 + requests；最终代码不得依赖 iv8、jsdom、浏览器或 Node.js"
---

# dy-ab-pure

本 skill 用于把抖音 Web BDMS `a_bogus` 生成链路落地为纯 Python 纯算和 `requests` 请求脚本。最终业务代码只能依赖 Python 标准库、`requests` 和本地纯 Python 算法文件；`iv8`、浏览器、hook、trace 只能作为逆向验证材料，不能进入最终生成路径。

## 启动检查

激活后先说明本次目标属于哪一类：

- 维护已有 `pure_abogus.py` / `douyin_aweme_post_pure.py`。
- 从已知 BDMS 版本和 trace 材料补齐纯算字段。
- 生成一个自包含的 `requests` 请求脚本。
- 只解释/校验某个字段来源。

如果用户只是要“找入口”“hook XHR”“用 iv8 跑通”，不要使用本 skill，按 frontmatter 的转交规则处理。

🔴 CHECKPOINT：写入或覆盖 `pure_abogus.py`、请求脚本或 `js_reverse_cache/` 验证材料前，先声明目标类型、目标文件路径、输入材料来源和最终运行时依赖；只要依赖里出现 JS runtime 或浏览器，就停止本 skill 路线。

## 核心约束

- 最终请求脚本不得 `import iv8`、`jsdom`、`playwright`、`camoufox`、`selenium` 或任何 JS runtime。
- 最终请求脚本不得从旧的 iv8 喂入截出脚本导入常量或 helper，因为 import 可能触发环境依赖。
- 环境指纹字段可以作为显式参数传入，例如 `WINDOW_INFO`，但不能在运行时启动浏览器读取。
- Cookie 可以来自手工字符串或 `js_reverse_cache/douyin_cookie.txt`，但不要写死到 skill 仓库。
- 动态材料和验证产物写入当前工作区 `js_reverse_cache/`，不要写入本 skill 目录。
- 保留固定随机参数入口以复现 trace，同时提供默认随机生成路径用于真实请求。

## 已还原算法地图

按这条链路生成：

1. `query`：接口参数用 `urllib.parse.urlencode(params, safe="*")`，不包含 `a_bogus`。
2. `sign_value`：`id142(cursor, mode, ua)`，构造 key `[cursor//256, cursor%256, mode%256]`，对 `ua.strip()` 做 BDMS stream transform，再用 `SIGN_ALPHABET` 编码。
3. Digest：
   - `slot18 = SM3(SM3(query + "dhzx"))`
   - `slot19 = SM3(SM3("" + "dhzx"))`
   - `slot21 = SM3(sign_value)`
4. 字段组装：按函数 150 的字段表生成 `fields[24..87]`。
5. `slot77`：`innerWidth|innerHeight|outerWidth|outerHeight|screen.availWidth|screen.availHeight|screen.width|screen.height|navigator.platform` 的 UTF-8 bytes。
6. `slot82`：`str((timestamp_ms + 3) & 255) + ","` 的 UTF-8 bytes。
7. `slot86`：`[1,0,1,0]` 经 `bdms_pack4()` 打包。
8. `slot87`：XOR 已打包 `slot86` 和 slot90 字段顺序里的 50 个字段。
9. `slot90_source`：50 个字段 + `slot77` + `slot82` + `slot87`。
10. `slot90`：`slot90_source` 经 `bdms_pack3_chunks()` 打包。
11. `payload = prefix4 + bdms_stream_transform(slot86 + slot90, key=b"\xd3")`。
12. `a_bogus = encode_abogus_payload(payload, ABOGUS_ALPHABET)`。

关键 alphabet：

- `ABOGUS_ALPHABET = "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe"`
- `SIGN_ALPHABET = "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe"`

## 实现步骤

1. 在当前工作区查找是否已有 `pure_abogus.py`。
2. 如果没有，按 `references/algorithm-notes.md` 创建纯算法文件，或从 `scripts/pure_abogus_template.py` 改造。
3. 生成请求脚本时必须自包含站点常量、headers、cookie 读取、`build_params()` 和响应打印；不要从 iv8 脚本导入。
4. `WINDOW_INFO` 是显式环境参数，不是运行时环境依赖；默认可用 trace 值，但要说明可按真实浏览器样本替换。
5. 给 `generate_abogus()` 同时保留两种模式：
   - 固定随机材料：用于复现 trace，验证 `match=True`。
   - 默认随机材料：用于真实请求，生成合法 shape。
6. 校验时至少跑：
   - `python pure_abogus.py` 或等价 roundtrip 验证。
   - 固定 trace 样本复现：`match=True`。
   - 纯请求 URL 构造：`len(a_bogus)==192` 且 URL 中 `a_bogus` 可解析。

## 失败模式

| 触发条件 | 处理动作 | 兜底 |
|---|---|---|
| 当前目录没有 `pure_abogus.py` 且用户未要求新建 | 先说明可从模板创建纯算法文件 | 未确认前只做字段解释，不写文件 |
| 固定 trace 复现不是 `match=True` | 停止真实请求生成，回查 digest、slot77、slot82、slot86/90 和 alphabet | 保留失败样本到 `js_reverse_cache/`，不声称纯算可用 |
| `a_bogus` 长度不是 192 或 URL 不可解析 | 停止接口请求，先修 payload 打包或编码层 | 只输出本地验证报告，不生成业务采集脚本 |
| 真实请求被拒绝但本地 shape 正确 | 检查 Cookie、UA、`WINDOW_INFO` 和同 session 首跳 | 不把浏览器运行时加入最终脚本；必要时转 `camoufox-js-reverse` 重新取证 |
| 用户要求从 iv8 喂入脚本导入 helper | 拒绝导入并改为复制纯算法必要常量 | 如果无法拆出纯算，转 `iv8-web-reverse` |
| 目标不是抖音 Web `a_bogus` / BDMS 1.0.1.19 风格 | 停止套用本算法地图 | 转 `web-protocol-recovery` 或入口定位 skill |

🔴 CHECKPOINT：只有本地三项校验全部通过后，才生成或更新真实请求脚本；任一校验失败就停在诊断报告。

## 请求脚本要求

自包含脚本应包含：

- `START_PAGE`、`PAGE_COUNT`、`PAGE_SIZE`、`SEC_USER_ID`、`UA`、`PAGE_URL`、`API_URL`。
- `MANUAL_COOKIE = ""` 和 `COOKIE_PATH = CACHE_DIR / "douyin_cookie.txt"`。
- `WINDOW_INFO` 明确放在顶部。
- `build_params(page, max_cursor)`。
- `build_signed_url(params, timestamp_ms=None, rng_seed=None)`。
- `main()` 使用同一个 `requests.Session()`，先首跳页面，再请求接口。

不要：

- 不要 `from douyin_aweme_post_iv8 import ...`。
- 不要导入 `utils.iv8_silent`。
- 不要读取 BDMS JS runtime。
- 不要用浏览器抓当前环境作为运行时步骤。

## 字段解释口径

当用户质疑“这是不是环境依赖”时，按以下口径回答：

- `WINDOW_INFO`、UA、platform、screen 是 BDMS payload 里的浏览器指纹字段。
- 纯算脚本把它们当输入参数，不启动浏览器读取，因此不是 JS/浏览器运行环境依赖。
- 如果用户要更干净，可以从接口参数和配置推导部分字段，但 `innerHeight/outerHeight/availHeight` 这类值本质仍需要人为配置或来自一次真实样本。

## 参考文件

- `references/algorithm-notes.md`：本次已还原链路的字段和函数说明。
- `scripts/pure_abogus_template.py`：可复制到项目中的纯算法骨架。
