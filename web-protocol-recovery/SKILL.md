---
name: web-protocol-recovery
description: >-
  把 hostile web client 还原成 browser-free 的纯协议 Python 采集器。适合“帮我恢复这个接口的协议链路”“把签名/cookie/挑战/WASM/字体解码/传输包装还原成 Python 脚本”“需要端到端协议回放，不依赖浏览器”。触发信号：用户给了目标页面 URL、API URL、请求样本、Cookie 样本、JS 片段、sign/token 样本、抓包、WebSocket/GraphQL/protobuf 传输或响应加密/字体混淆，且最终目标是一个脱离浏览器的 Python 采集器。侦察阶段优先最大化 `Camoufox + CloakBrowser`：Camoufox 负责反检测环境/指纹采样与属性访问证据，CloakBrowser 负责 CDP 原生网络/initiator、请求拦截、脚本源码/SourceMap、Debugger/断点/paused scope、WebSocket、Hook/JSVMP/源码插桩、cookie/storage/state、heap/artifact 和离线 signer 验证；不可用时按 `js-reverse-mcp`、`chrome-devtools-mcp` 顺序降级。不要用于：只要单个 hook 脚本（转 browser-hook-snippets）、只定位签名入口（转 camoufox-js-reverse）、通用 Node.js 补环境（转 env-patch）、整文件 AST 解混淆（转 ast-deobfuscate）、Python+iv8 请求脚本（转 iv8-web-reverse）、瑞数项目骨架（转 rs-reverse）。
argument-hint: "[目标页面 URL 或 API URL]"
compatibility: "需要 Python 3 + requests；侦察首选 Camoufox + CloakBrowser；可降级 js-reverse/chrome-devtools"
---

# Web Protocol Recovery

## Role

把 hostile web client 还原成稳定的纯协议采集器。

本 skill 不是浏览器自动化 skill。本 skill 是协议恢复 skill。

默认姿态：

1. 每个新目标优先以 `Camoufox + CloakBrowser` 双指纹浏览器起步做证据收集；Camoufox 做环境/指纹采样，CloakBrowser 做 CDP/源码/断点/网络证据；不可用时按 `js-reverse-mcp`、`chrome-devtools-mcp` 降级
2. 找到真实请求
3. 识别真正的动态状态
4. 离线重建这些状态
5. 交付脱离浏览器的 Python 采集器，只在必要时保留极小本地 JS 参数 helper

## 触发边界

### 应该触发

- 用户给了目标页面/API URL/请求样本/Cookie 样本/JS 片段/sign 样本/抓包，且目标是端到端协议恢复
- 需要还原多层交织的协议链路：签名 + bootstrap + Cookie + WASM + 字体解码 + 传输包装
- 请求能发出但响应体需要解码/解密/字形映射
- 目标涉及 GraphQL/WebSocket/protobuf/msgpack 等结构化传输
- 需要把已验证的浏览器 JS 链路转化为离线 Python 采集器

### 不要触发，转交对应 skill

- 只要一段浏览器 hook 脚本观察行为 → `browser-hook-snippets`
- 只定位 sign/token/header 的脚本 URL、函数名、调用链 → `camoufox-js-reverse`
- 已有 JS 入口、要在 Node.js 沙箱里补环境跑通 → `env-patch`
- 整文件 AST 解混淆、控制流还原 → `ast-deobfuscate`
- 明确要紧凑 Python + iv8 执行浏览器 JS 并翻页请求 → `iv8-web-reverse`
- 瑞数/Ruishu/Rivers 固定项目骨架、首跳缓存、最小 proxy 观察 → `rs-reverse`
- 纯标准 UI 自动化或页面操作录制

### 本 skill 与其他 skill 的层级关系

```
任务范围：整个 hostile web client 的协议恢复
├── 子问题：入口在哪？→ camoufox-js-reverse
├── 子问题：混淆文件太大 → ast-deobfuscate
├── 子问题：需要补环境跑 → env-patch
├── 子问题：要用 iv8 跑 → iv8-web-reverse
└── 子问题：是瑞数 → rs-reverse
```

本 skill 负责 **端到端协议链路**，其他 skill 解决链路中的**单点问题**。当用户的目标已缩小到单点问题时，转交对应 skill。

## Non-Negotiables

- 最终交付必须是纯协议：原始 HTTP + 本地签名/解码/bootstrap helper
- 每个新目标必须先经可用浏览器/调试 MCP 基线分析再写最终采集器，首选 `Camoufox + CloakBrowser`，降级顺序为单可用指纹浏览器 → `js-reverse-mcp` → `chrome-devtools-mcp` → 手工样本
- 逆向 MCP 分工：Camoufox 负责反检测环境/指纹和属性访问证据；CloakBrowser 负责 CDP 原生网络/initiator、源码/SourceMap、断点/paused scope、WebSocket、Hook/JSVMP、cookie/storage/state、heap/artifact 和离线 signer 验证等证据；降级时必须记录缺失能力和替代证据
- 不把 Playwright/Selenium/CDP 页面驱动作为最终方案
- 最终交付在浏览器外运行：Python 采集器 + 仅在 Python 移植不划算时保留极小本地 JS/WASM helper
- JS helper 必须能在本地运行，不依赖 `document`/`window`/人工点击/浏览器 profile
- 浏览器工具只做侦察和证据收集，不作为最终采集器的隐藏依赖
- 自动化被禁止作为最终答案、兜底答案或伪装成"临时"交付路径
- 先恢复一次稳定请求，再谈分页、并发和规模化
- 每个结论必须有 artifact 支撑：请求样本、固定输入 helper 输出、cookie/header、回放证据
- 所有侦察过程中下载的 JS/WASM/字体/HTML/抓包样本等动态素材统一写入当前工作目录的 `js_reverse_cache/`（不存在则先创建），不污染工作区根目录
- 在一个执行回路里坚持下去，直到达成协议交付或遇到真正的外部阻塞

## Startup Gate

每个 fresh target 开始前，先完成四项检查：

1. **环境与工具检查**：本地可用时运行 `scripts/check_reverse_env.py`；会话内确认 Camoufox、CloakBrowser、js-reverse、chrome-devtools 是否可用。优先级顺序：startup triage → Camoufox 环境/指纹证据 + CloakBrowser CDP 全能力证据 → request diff → helper 固定输入验证 → 必要时 js-reverse fallback → 必要时 chrome-devtools 基础降级 → 离线执行 → 本地协议回放。任一工具被封阻或未配置时，明确报告缺失能力和替代证据。只有所有浏览器/调试 MCP 都不可用且用户没有样本时才停止侦察。
2. **缓存目录检查**：确认当前工作目录下存在 `js_reverse_cache/`，不存在则创建；后续所有下载的 JS/WASM/字体/HTML/抓包样本均写入该目录
3. **目标家族分类**：先读 `references/startup-triage-playbook.md`，将目标分类为 `signer-gated` / `verifier-gated` / `decode-gated` / `session-gated`
4. **交付意图声明**：明确最终交付形态——纯 Python / Python+极小 JS helper / Python+极小 WASM helper / Python+本地 bootstrap executor；明确拒绝浏览器驱动回放

规则：startup gate 不完整，就说明目标还没被理解；分类在新证据后变化时，重新声明 gate。

🔴 CHECKPOINT：在开始 Phase 1 之前，先把四项检查结果、目标家族和最终交付形态写清楚；缺一项就停，不进入后续分析。

## What This Skill Optimizes For

- 协议优先的逆向工程
- Python 优先的交付
- 离线再现动态状态
- 可复用的采集器而非一次性幸运请求
- 可跨目标迁移的通用方法论

## 家族症状

以下任一症状出现，目标即属于同一家族类：

- 页面代码提到一个接口但线路上用另一个
- 业务代码构建 `token`/`sign`/`m`，但传输 wrapper 在发送前改写
- 传输是 GraphQL/WebSocket/protobuf/msgpack 等结构化信封
- 标准 helper（`md5`/`btoa`/`sha1`）输出不标准
- 首个请求返回 JS/cookie/偏移量/字体文件而非业务数据
- 页面公开但 bootstrap 端点返回密钥/config blob/nonce seed
- 只有某一页失败
- API 返回字符串/提示/字形/字体而非最终数值
- 响应体被编码/压缩/protobuf/msgpack/分层包装
- 同一请求成功一次后就死掉
- 存在长连接 WebSocket（auth/ack/heartbeat/reconnect 帧必须保序）
- 媒体元数据与数据解密需不同密钥

详见 `references/startup-triage-playbook.md`。

## Operating Doctrine

11 条核心原则，详见 `references/operating-doctrine.md`。

速记版：
1. 信线路，不信页面文字
2. 动态参数不一定是签名（可能是 cookie/header/传输信封/WASM/字体/响应解码链/会话状态）
3. 固定输入验证胜过信任函数名
4. 窄异常就窄处理，不污染整个采集器
5. 自动化不是可接受的拐杖
6. 环境差异是证据，不是"浏览器专属"的借口
7. 交付门禁高于便利性
8. 公开不等于无签名
9. 有状态流是协议不是浏览器魔法
10. 观察者效应是真实的——先取干净基线再上 hook
11. Cookie 出处比猜 Cookie 重要——证明谁写的、怎么刷新

## Universal Reverse Loop

完整五阶段流程见 `references/universal-reverse-loop.md`。

| 阶段 | 目标 | 关键动作 |
|------|------|---------|
| Phase 0 | 指纹化 | 读 `startup-triage-playbook.md`，分类目标，选择最小验证路径 |
| Phase 1 | 确认真实请求路径 | 跟跳转链、区分假接口/真实接口/包装层、映射 bootstrap/列表/详情/提交链路 |
| Phase 2 | 分类动态字段 | 区分静态 header、旋转 cookie、时间戳、nonce、签名体、传输信封、响应解码链 |
| Phase 3 | 定位突变点 | 从传输 wrapper → bootstrap 脚本 → helper 函数 → WASM 导出 → server 挑战 JS 逐层查找 |
| Phase 4 | 离线重建 | 纯 Python > Python+极小 JS > Python+极小 WASM > Python+本地 bootstrap executor |
| Phase 5 | 重复性验证 | 同逻辑成功 2-3 次、分页前进、动态状态正确再生 |

## Pattern Atlas

按症状路由到对应 reference，不要在 SKILL.md 中展开全文：

| Pattern | 症状 | 路由 |
|---------|------|------|
| A: 假接口 | 页面代码一个接口，线路上另一个 | `transport-wrapper-playbook.md` |
| B: 假参数 | 业务层构建 `token`，线路上发 `m` | `transport-wrapper-playbook.md` |
| C: 标准函数被 patch | `md5`/`btoa` 输出不标准 | `patched-helper-playbook.md` |
| D: 首次响应是 bootstrap | 首个请求返回 JS/cookie/偏移量 | `server-js-cookie-bootstrap-playbook.md` |
| E: 单页异常 | 只有某一页失败 | `page-specific-exception-playbook.md` |
| F: 响应需解码 | 返回 gibberish/字形/二进制帧 | `response-decode-playbook.md` |
| G: WASM 侧资源 | 细微 .wasm 文件携带完整签名状态 | `side-asset-bootstrap-playbook.md` |
| H: 动态字体 | 数值显示为字形/无意义文本 | `response-decode-playbook.md` |
| I: Verifier 门控 | 需要验证/挑战步骤后才放行 | `verifier-replay-playbook.md` |
| J: 响应编码/分层 | 原始 payload 需要解码链 | `response-decode-playbook.md` |
| K: 结构化传输 | GraphQL/WebSocket/protobuf 信封 | `structured-transport-playbook.md` |
| L: 公开页面+引导信封 | 公开页面但仍需密钥/config 引导 | `public-bootstrap-envelope-playbook.md` |
| M: 有状态 WebSocket | 登录/配对/心跳/会话密钥/媒体解密 | `stateful-stream-e2ee-playbook.md` |

## Failure Modes

| 触发条件 | 处理动作 | 兜底 |
|---|---|---|
| 真实接口和页面代码不一致 | 先锁定线路，再回到对应 Pattern 继续分析 | 记录 decoy/real request 差异，不直接写最终采集器 |
| 浏览器/调试工具缺失 | 记录缺失能力和可用降级链 | 只有所有浏览器/调试 MCP 都不可用且用户没有样本时才停止 |
| cookie/header/sign 只能在浏览器里稳定 | 先证明谁写的、怎么刷新、何时过期 | 若无法离线重建，停在局部 helper，不伪装成纯协议交付 |
| 响应需要解码或分层包装 | 先分离解码链，再做协议重建 | 不把未解码 payload 直接塞进最终请求脚本 |
| 单页失败或会话流失 | 走单页异常或会话合同 reference | 如果仍然不稳定，保留最小可复现样本，不扩到全站 |
| 仍然依赖浏览器自动化 | 回退到 browser-free 目标定义 | 停止交付最终方案，继续逆向直到可离线重建 |

## Reproduction Decision Tree

选择交付路径：

1. 纯 Python（当所有逻辑已恢复）
2. Python + 极小 JS helper（签名逻辑精确在 JS 且移植风险大）
3. Python + 极小 WASM helper（参数来自 WASM 导出）
4. Python + 本地 bootstrap executor（服务器返回 JS 播种 cookie/token）
5. 停住继续逆向（当剩余路径是浏览器自动化时）

永不选择：浏览器驱动回放、"我的浏览器 profile 里能跑"、页面驱动的提交。

🔴 CHECKPOINT：在选择交付路径前，明确写出“纯 Python / Python+helper / 停住继续逆向”三选一，并说明为什么浏览器自动化不在最终方案里。

## Bundled Scripts

- `scripts/check_reverse_env.py`：快速检查本地逆向环境
- `scripts/crypto_fingerprint.py`：指纹化可疑摘要/Base64/自定义字母表输出
- `scripts/protocol_diff.py`：对比请求/响应样本、找出有意义的差异
- `scripts/scaffold_reverse_project.py`：生成当前 skill 内置的 compact Python protocol 项目骨架

## 实现要点

详见 `references/implementation-rules.md`。核心规则：
- 模块分离（header/cookie/signer/pagination/output 分模块）
- 固定输入自检先行再发真实流量
- JS helper 只做参数恢复，Python 掌管 HTTP/分页/重试/存储
- 项目产物目录默认使用当前 skill 内置的 compact Python protocol 规范：`main.py`、`requirements.txt`、`config/`、`utils/`、`README.md`；额外保留 `js_reverse_cache/` 存放侦察素材，测试/验证脚本放入 `tests/`
- 启动引导 artifact（密钥/config/nonce）作为一等输入
- Cookie 出处验证后方可缓存

## Reference Router

按症状路由：

| 场景 | Reference |
|------|-----------|
| 新目标、不做分类不敢动 | `references/startup-triage-playbook.md` |
| 最短端到端执行地图 | `references/workflow-overview.md` |
| 工具选择与下一步路由 | `references/tool-playbook.md` |
| CloakBrowser MCP 全量能力路由 | `references/cloakbrowser-mcp-playbook.md` |
| 阶段报告与交接结构 | `references/report-templates.md` |
| 验证 skill 未退化 | `references/official-self-test-task-suite.md` |
| Cookie 阻塞重放 | `references/cookie-provenance-playbook.md` |
| 签名/helper 输出可疑 | `references/crypto-patterns.md` |
| 打包代码/字符串表 | `references/obfuscation-guide.md` |
| 运行时验证比静态快 | `references/hook-techniques.md` |
| 页面让工具不稳定 | `references/anti-debug-playbook.md` |
| 本地执行偏离真实执行 | `references/environment-patch-playbook.md` |
| 重定向/wrapper 导致差异 | `references/env-diff-playbook.md` |
| 自定义 VM/字节码解释器 | `references/jsvmp-analysis-playbook.md` |
| GraphQL/WS/protobuf/msgpack | `references/structured-transport-playbook.md` |
| 登录/配对/会话密钥/媒体解密 | `references/stateful-stream-e2ee-playbook.md` |
| 响应需本地解码 | `references/response-decode-playbook.md` |
| 公开页面+引导信封 | `references/public-bootstrap-envelope-playbook.md` |
| 判断当前路径是否可交付 | `references/delivery-gate-playbook.md` |
| 内联脚本/eval/老旧 hash | `references/offline-inline-deob-playbook.md` |
| 页面与线路不一致 | `references/decoy-and-real-request-playbook.md` |
| 传输 wrapper 改写 | `references/transport-wrapper-playbook.md` |
| helper 名字标准输出不标准 | `references/patched-helper-playbook.md` |
| 单页异常 | `references/page-specific-exception-playbook.md` |
| 结果/提交是账号绑定 | `references/session-contract-playbook.md` |
| .wasm/侧脚本/字体播种状态 | `references/side-asset-bootstrap-playbook.md` |
| 端点返回可执行 JS 播种 cookie | `references/server-js-cookie-bootstrap-playbook.md` |
| captcha/一次性验证 | `references/verifier-replay-playbook.md` |
| 回放接近但不稳定 | `references/troubleshooting-playbook.md` |

Implementation Rules → `references/implementation-rules.md`
Verification Gates → `references/verification-gates.md`
Output Contract → `references/output-contract.md`
Skill Validation → `references/skill-validation.md`
Anti-Patterns → `references/anti-patterns.md`
Experience Deposition → `references/experience-deposition.md`

## Deliverables

完整验证清单见 `references/verification-gates.md`，输出报告模板见 `references/output-contract.md`。完成时用户应拿到：

- 真实接口路径
- 动态状态分类结论
- 关键固定输入/输出验证样本
- Python 采集器 + 必要时极小 JS/WASM helper
- 原始请求/响应样本
- 可重复成功的回放逻辑

## Bottom Line

当网站看起来"browser-only"时，不要慌也不要自动化。先问三个问题：

1. 真实请求是什么
2. 真实动态状态是什么
3. 这些状态能否本地重建

大多数看起来"browser-only"的目标，答完这三个问题就塌缩了。
