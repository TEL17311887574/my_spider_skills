# 瑞数实物数据形态参考

本文档用占位示例展示瑞数各阶段数据的**结构**，不是真实 token。用于辅助模型理解从 HTML → runner → cookie → 回放的字段关系。

## meta 标签

瑞数 challenge 页面特征 `meta[r=m]`，内含加密 payload：

```html
<meta content="xxxxxxxxxxxx" r="m">
<script src="/.../R3XbLZD4.js" r="m"></script>
<script src="/..." r="m"></script>
```

提取规则：`<meta content="..." r=m>` 或 `<script src="..." r=m>`

## $_ts 命名空间

首跳 HTML 内联 `<script>` 或 runner JS 中的核心变量：

```js
var $_ts = window.$_ts || {};
$_ts.nsd = [3,0,0,0,0,0,1];        // 位标志数组
$_ts.cd = "_ts_cd_value";           // challenge data
$_ts.l__ = ["_ts_loaded___"];       // 加载追踪
$_ts.meta = { content: "..." };     // meta 标签内容
$_ts.r2mKa = function(){...};       // 核心 runner 函数
```

## Cookie 形态

瑞数两阶段 cookie 典型命名：

| 域名前缀 | cookie 名 | 说明 |
|---|---|---|
| 首跳/第一阶段 | `6HZbKHDjIEcgS` | challenge seed cookie |
| 首跳/第一阶段 | `__jsluid_s` | 设备标识 cookie |
| 首跳/第一阶段 | `hasDebug` | 调试标记 |
| 二跳/第二阶段 | `6HZbKHDjIEcgT` | 验证通过 cookie（`r2mKa` 生成） |
| 二跳/第二阶段 | `6HZbKHDjIEcgP` | 额外标记（部分站点） |

## 首跳 HTTP 响应形态

```text
HTTP/1.1 412 Precondition Failed
Set-Cookie: 6HZbKHDjIEcgS=abc123...; Path=/
Set-Cookie: __jsluid_s=def456...; Path=/
Content-Type: text/html

<html>
<head><meta content="encrypted_payload_here" r="m"></head>
<body>
<script type="text/javascript" src="/....js?d=20230918" r="m"></script>
</body>
</html>
```

## runner JS URL 形态

```
https://domain.com/.../R3XbLZD4.js?d=20230918
```

路径固定模式：`/` + 不定层目录 + `/` + 随机 8-10 字符 `.js` + `?d=YYYYMMDD`

## Node 本地 runner 输出

`main.js` 加载 `mod.js` + `challenge_payload_bootstrap.js` + `challenge_payload_runner.js` 后的预期输出：

```text
[mod] navigator.userAgent accessed: Mozilla/5.0 ...
[mod] document.cookie set: 6HZbKHDjIEcgT=xyz789; path=/; domain=.example.com
[mod] window.location.href read: https://example.com/page
document.cookie = "6HZbKHDjIEcgS=abc123; 6HZbKHDjIEcgT=xyz789"
```

## netLog 条目形态（iv8 侧）

瑞数 runtime 在 iv8 中创建 XHR 后的 netLog 输出：

```json
{
  "url": "https://api.example.com/data?page=1&_rsc=abc123&_sign=xyz789",
  "method": "GET",
  "headers": {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://domain.com/page"
  },
  "cookieHeader": "6HZbKHDjIEcgS=abc123; 6HZbKHDjIEcgT=xyz789"
}
```

## 同 session 回放规则

1. `requests.Session` 先收首跳 `Set-Cookie`（S/LUID）
2. Node 用同一 session 下载 runner JS
3. Node 生成 T/P cookie 后写回同一 session jar
4. 用同一 session 发业务请求
5. 不要混用旧 cookie、旧 runtime 或旧 suffix
