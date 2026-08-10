# 瑞数证据识别 Checklist

在决定触发 `rs-reverse` 之前，先确认页面是否真的是瑞数/Ruishu/Rivers Security。

## 确认标准（满足任意 2 项即可确认）

### Cookie 层

| 证据 | 示例 |
|------|------|
| Cookie 名称含 `S` / `T` / `P` 后缀 + 随机串前缀 | `6HZbKHDjIEcgS`, `S6J51OuUjLieT`, `kbfJdf1eP` |
| Cookie 值明显为 base64 + 分隔符 | `xxx...*` 结尾，中间含 `*` |
| 同一 session 有两个以上动态 cookie | `xxxS` + `xxxT` 或 `xxxS` + `xxxP` |

### HTML/响应层

| 证据 | 位置 |
|------|------|
| `<script` 带 `r="m"` 属性 | `<script src="xxx.js" r="m"></script>` |
| `<meta` 带 `r="m"` 属性 | `<meta r="m" http-equiv="..." content="...">` |
| HTTP 状态码 `412` / `403` + body 含 `$_ts` | 首次请求返回 412 |
| HTTP 状态码 `202` + body 含内联 JS | 业务请求返回 202 |

### JS/运行时层

| 证据 | 关键词 |
|------|--------|
| 全局变量 `$_ts` | `$_ts.nsd`, `$_ts.cd`, `$_ts.l__` |
| 全局变量 `r2mKa` | (瑞数 5/6 常用) |
| `hasDebug` 属性 | 在 `$_ts` 或 `window` 上 |
| 内联 JS 解密 `document.cookie` 写入 | 在 `<script r="m">` 块内 |

## 排除标准（以下情况 NOT 瑞数）

1. **Cookie 名称不含 S/T/P 后缀** — 即使有 412 也可能是其他 WAF
2. **`$_ts` 不是瑞数全局变量而是业务变量** — 确认是否来自 `window.$_ts`
3. **403/412 但没有 `<script r="m">`** — 可能是 Cloudflare / Akamai 等其他防护
4. **JS challenge 但状态码是 200（非 202/412）** — 可能不是瑞数机制

## 判断后的路由

| 判断结果 | 下一步 |
|----------|--------|
| 明确瑞数 + 仅需骨架/缓存/proxy 观察 | → `rs-reverse` |
| 明确瑞数 + 需要完整 Node VM 补环境 | → `env-patch` |
| 明确瑞数 + 后缀请求可用性/iv8 跑通 | → `iv8-web-reverse` |
| 不确定是否瑞数 | → `camoufox-js-reverse` 先定位确认 |
| 不是瑞数 | → `camoufox-js-reverse` / `env-patch` |
