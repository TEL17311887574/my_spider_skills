---
name: rs-reverse
description: >-
  瑞数/Ruishu/Rivers Security 轻量项目骨架 skill。仅在有明确瑞数证据（如 $_ts.nsd/cd/l__、r2mKa、meta[r=m]、Cookie S/T/P、hasDebug、瑞数/Rivers 412/403）且任务目标是创建或维护固定本地项目结构、把首跳挑战材料缓存到 js_reverse_cache/、运行基础 Node cookie/runtime 检查、或使用最小浏览器 proxy 模板观察环境读取时触发。  不要用于瑞数深度算法/字节码研究、重型浏览器补环境、普通 sign/token 定位或 Python + iv8 请求脚本。
argument-hint: "[瑞数目标页面 URL 或缓存目录]"
compatibility: "需要 Node.js + 基础 jsdom；可选 Python requests"
---

# RS Reverse Skill

本 skill 已精简为瑞数轻量项目骨架 skill，只保留固定项目结构、`js_reverse_cache/` 缓存规则、基础 Node runtime 检查，以及最小浏览器环境 proxy 观察模板。

本 skill 不提供、不引导以下路线：瑞数深度算法/字节码研究、重型浏览器补环境、URL suffix AST 研究。

## 硬性约束

- 自动采集或下载得到的目标站点动态材料、挑战源码、session 样本、临时 runtime 文件、运行报告和分析记录，统一写入当前工作区的 `js_reverse_cache/`。
- 如果当前工作区没有 `js_reverse_cache/`，先创建它。
- 不要把目标站点动态素材写入本 skill 目录。
- 固定瑞数项目结构必须保留，不能被通用 demo 结构替代。
- 根目录 `challenge_payload_bootstrap.js` 和 `challenge_payload_runner.js` 是用户手动维护的固定样本，用于本地环境观察和缺失环境定位；除非用户明确要求，不要覆盖它们。
- `rs_reverse.js` 只放占位符模板，不写入真实动态挑战源码；真实 runtime 源码只写入 `js_reverse_cache/<run>/rs_reverse_runtime.js` 这类临时文件。
- 同一条验证链路必须使用同 session 的首跳 Cookie、挑战 payload、Node 生成 Cookie、业务参数/sign/timestamp 和回放请求；不要混用旧 Cookie、旧 runtime、旧 suffix 或旧签名。
- 不要因为浏览器网络里出现 suffix 就默认复用 suffix。本精简 skill 不做 suffix 研究或生成；如果请求可用性依赖 suffix，转交 `iv8-web-reverse`。

🔴 CHECKPOINT：创建、覆盖或运行任何固定项目文件前，先确认三件事：已命中瑞数证据、任务目标属于轻量骨架范围、根目录 `challenge_payload_*` 是否允许保留或覆盖。任一项不明确就停住询问。

## 材料采集来源

- 本 skill 默认不启动完整浏览器侦察；优先处理用户提供或当前请求得到的 HTML、Cookie、外链 JS、挑战源码和本地 Node runtime 输出。
- 需要页面侧证据时，启动 `js-reverse-mcp` 采集首跳 HTML、Cookie、script URL、请求/响应、console 日志或最小 proxy 观察结果。不可用时按 `chrome-devtools-mcp` → 用户手工样本降级。被目标站风控拦截（412/403/验证码）时，说明需要反检测能力，转交 `camoufox-js-reverse`。
- 所有采集材料必须写入当前工作区的 `js_reverse_cache/`，并记录来源 URL、时间、Cookie/session 关联关系。
- 如果需求升级为脚本入口定位、调用链、断点调试或普通 sign/header 来源分析，停止本 skill 路线并转交对应 skill。

## 固定项目结构

当用户要把瑞数材料、Cookie 检查或本地环境观察落到项目中时，使用以下根目录结构：

```text
challenge_payload_bootstrap.js  # 用户手动固定的 $_ts inline/bootstrap 样本；自动采集不要覆盖
challenge_payload_runner.js     # 用户手动固定的 mainjs/r2mKa runner 样本；自动采集不要覆盖
mod.js                          # 最小浏览器 proxy / logging 模板
main.js                         # 本地 runner：require mod/bootstrap/runner 后输出 document.cookie
main.py                         # 首跳采集 + 临时 runtime 执行 + 同 session 回放
rs_reverse.js                   # 只含占位符的 runtime 模板
js_reverse_cache/               # 自动缓存：源码、样本、临时 runtime、报告
```

本 skill 提供的模板文件：

- `project-templates/minimal-proxy-env-template.js`：创建 `mod.js` 的默认起点。
- `project-templates/rs-runtime-placeholder-template.js`：创建 `rs_reverse.js` 的占位符模板。
- `project-templates/node-cookie-runner-template.js`：创建 `main.js` 的本地 runner 模板。
- `project-templates/python-session-request-template.py`：创建 `main.py` 的首跳/session/runtime 模板。

根目录 `challenge_payload_*` 文件由用户手动维护。自动采集流程只把新鲜材料写入 `js_reverse_cache/<run>/`，再基于缓存材料构造临时 runtime 文件。

🔴 CHECKPOINT：如果固定项目文件已存在，只列出“保留 / 创建缺失 / 用户明确要求覆盖”三类动作，不默认覆盖已有文件。

## 触发范围

使用本 skill 当：

- 用户明确说瑞数、Ruishu、Rivers Security、瑞数 4/5/6 或 Rivers 动态安全防护，并且目标是固定项目结构、首跳材料缓存、基础 Node runner 或最小 proxy 观察。
- `412` / `403` challenge 有明确瑞数证据：`$_ts`、`$_ts.nsd`、`$_ts.cd`、`$_ts.l__`、`r2mKa`、`meta[r=m]`、Cookie `S/T/P` 或 `hasDebug`。
- 用户要创建或修复固定本地瑞数项目结构。
- 用户要把首跳 challenge HTML / 外链 JS 缓存到 `js_reverse_cache/`，且不覆盖根目录 payload 文件。
- 用户要一个基础 Node runner，加载 `mod.js`、`challenge_payload_bootstrap.js`、`challenge_payload_runner.js`，观察 `document.cookie` 或缺失环境读取。
- 用户要最小 proxy 版浏览器环境观察模板。

不要使用本 skill 当：

- 用户要瑞数算法链深挖、r2mKa 字节码反汇编、URL suffix AST、session49、child[29]/child[40] 或 VM opcode 工具链。
- 用户要完整浏览器级补环境、重型 DOM/事件模型模拟，或其它偏重型的本地 runtime 复现。
- 任务是普通 `sign`、`token`、`x-sign`、动态 header 或业务参数入口定位。交给 `camoufox-js-reverse`。
- 任务只是要可粘贴的浏览器 hook snippet 来观察 cookie/fetch/xhr/header。交给 `browser-hook-snippets`。
- 任务是非瑞数浏览器 JS 的通用 Node.js 补环境。交给 `env-patch`。
- 任务是通用 AST 解混淆。交给 `ast-deobfuscate`。
- 用户明确要紧凑 `Python + iv8 + requests`、iv8 翻页请求，或通过浏览器式页面执行解决 suffix 请求可用性。交给 `iv8-web-reverse`。
- 页面只有普通 403/412，但没有瑞数证据。需要确认防护脚本、入口或调用链时交给 `camoufox-js-reverse`。
- 目标超出瑞数骨架范围、涉及多层协议交织（瑞数之外还有签名/解码/传输层），交给 `web-protocol-recovery`。

跨 skill 的阶段协议见 `references/js-reverse-workflow.md`。本 skill 主要覆盖瑞数轻量项目骨架的 Observe/Capture 阶段：固定项目结构、首跳材料缓存和最小本地 runtime 检查。

## 跨 skill 交接

- 未确认瑞数，且目标是参数/header/cookie 来源定位：交给 `camoufox-js-reverse`。
- 只要 DevTools 临时观察 hook：交给 `browser-hook-snippets`。
- 通用 Node.js / VM 补环境：交给 `env-patch`。
- 单个混淆文件结构化还原：交给 `ast-deobfuscate`。
- 紧凑 Python + iv8 runtime 复现或请求可用性：交给 `iv8-web-reverse`。

## 失败与转交表

| 触发条件 | 处理动作 | 兜底 |
|---|---|---|
| 未确认瑞数证据 | 先按 `references/ruishu-evidence-checklist.md` 查 Cookie/HTML/JS 三层证据 | 仍无证据时转 `camoufox-js-reverse` 做入口定位 |
| 需要覆盖 `challenge_payload_bootstrap.js` 或 `challenge_payload_runner.js` | 先展示文件路径和覆盖理由 | 未获确认时只写入 `js_reverse_cache/<run>/` |
| Node runtime 不生成 Cookie | 记录缺失环境读取和当前缓存 run | 若只是环境缺口，继续最小 proxy；若变成重型补环境，转 `env-patch` |
| 回放失败原因是 suffix 或高保真页面执行 | 停止本 skill 路线 | 转 `iv8-web-reverse`，不要在本 skill 内研究 suffix |
| 回放失败原因是业务 sign/header/timestamp | 保留瑞数 artifact，停止扩展骨架 | 转 `camoufox-js-reverse` 定位业务参数 |
| 目标要求 r2mKa 字节码、URL suffix AST 或深度算法 | 拒绝进入本 skill 实现 | 只给范围说明，不新增工具链 |

## 任务状态块

仅当任务需要多步执行、跨会话续做或会产出本地工件时，先输出一个简短状态块；简单问答、目录检查、轻量 review 或用户明确只要结论时不要强制输出。

```text
Complexity: L3
Current stage:
Why this stage now:
Read now:
Required artifact:
Exit condition:
```

阶段含义：

- `locate`：确认瑞数证据、首跳页面、runner 脚本、可见 cookie 和目标业务请求。
- `scaffold`：创建或修复固定项目结构和模板文件。
- `runtime`：用同 session 缓存材料构造临时 runtime，并运行本地 Node 检查。
- `validation`：同 session 回放检查和 artifact/report 清理。

## 工作流程

1. 从页面 HTML、Cookie、script 标签或网络响应确认瑞数证据。
2. 确保当前工作区存在 `js_reverse_cache/`。
3. 如果固定项目文件缺失，只从 `project-templates/` 创建缺失文件。
4. 不覆盖根目录 `challenge_payload_bootstrap.js` 或 `challenge_payload_runner.js`，除非用户明确要求。
5. 把首跳 HTML、首跳 Cookie、runner URL、runner JS 写入带时间戳的 `js_reverse_cache/<run>/` 目录。
6. 基于根目录 `rs_reverse.js` 的占位符，在缓存 run 目录里生成临时 `rs_reverse_runtime.js`。
7. 只运行临时 runtime，不把真实挑战源码写回 `rs_reverse.js`。
8. 如果 Node 输出中能解析到生成 Cookie，写回同一个 Python `requests.Session`。
9. 用同一个 session 回放页面或业务请求。
10. 如果失败原因是业务参数、sign 或 timestamp，离开本 skill 修业务逻辑。
11. 如果失败需要 suffix 生成或高保真页面执行，停止本 skill 路线并转交 `iv8-web-reverse`。

🔴 CHECKPOINT：进入 `validation` 前，报告同 session 材料是否齐全；缺首跳 Cookie、挑战 payload、临时 runtime 或回放目标中的任一项，就不做成功性结论。

## 最小浏览器 Proxy 模板

本 skill 只保留一个浏览器环境辅助：基础 proxy/logging 模板，用来观察目标瑞数 JS 在本地运行时读取、写入或调用了哪些浏览器全局对象。

用 `project-templates/minimal-proxy-env-template.js` 创建 `mod.js`。

不要在本 skill 内把 `mod.js` 扩展成完整浏览器框架。如果目标需要大量 DOM、navigator、canvas、WebGL、Worker、crypto 或 XHR 仿真，根据交付目标转交 `env-patch` 或 `iv8-web-reverse`。

## 已移除范围

- 瑞数算法深挖和 r2mKa 字节码研究。
- 重型浏览器补环境或完整 DOM/事件模型模拟。
- URL suffix AST 研究和相关工具链。

本精简 skill 只用于项目骨架、同 session 材料缓存、最小本地 runtime 检查和 proxy 环境观察。

## 参考文件

1. `references/ruishu-evidence-checklist.md`：瑞数证据识别 checklist，含 Cookie/HTML/JS 三层确认标准和排除条件，以及判断后的路由表。
2. `references/js-reverse-workflow.md`：跨 skill 阶段协议。本 skill 覆盖瑞数轻量骨架的 Observe/Capture 阶段。
3. `references/data-shapes.md`：瑞数实物数据形态参考，含 meta 标签、$_ts 命名空间、Cookie 形态、payload 结构示例。

## 完成报告

完成后简短报告：

- 触达的项目根目录。
- 是否创建了 `js_reverse_cache/`。
- 创建或保留了哪些固定项目文件。
- 根目录 `challenge_payload_*` 是否保持未覆盖。
- 如果发生采集，缓存 run 目录路径是什么。
- 本地 Node runtime 是否生成 cookie，或卡在哪个缺失环境读取。
- 是否尝试了同 session 回放，以及观察到的 HTTP 状态码。
