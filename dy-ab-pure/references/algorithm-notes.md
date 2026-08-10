# Douyin a_bogus Pure Python Notes

本文件记录抖音 Web BDMS `a_bogus` 纯 Python 纯算链路。目标是让最终请求脚本不依赖 `iv8`、`jsdom`、浏览器、Node.js 或 BDMS runtime。

## VM 函数对应关系

- `id130`：Base64 变体编码函数，按传入 alphabet 名称选择字符表。
- `id142`：UA sign wrapper，生成 3 字节 key 后调用 `id280`，再由 `id130(s3)` 编码。
- `id146`：两字节 pair 打包，掺入 16-bit random。
- `id147`：`slot86` 打包，底层调用 `id146`。
- `id148`：`slot90_source` 每 3 字节一组打包，掺入随机 byte。
- `id150`：`a_bogus` 主字段组装函数。
- `id280`：BDMS stream transform，KSA 初始 state 为 `[255,254,...,0]`。

## Digest

SM3 初始 IV：

```text
7380166f 4914b2b9 172442d7 da8a0600 a96f30bc 163138aa e38dee4d b0fb0e4e
```

字段公式：

```python
slot18 = sm3_digest(sm3_digest(query + "dhzx"))
slot19 = sm3_digest(sm3_digest("" + "dhzx"))
slot21 = sm3_digest(sign_value)
```

注意：trace 中 `text` 可能截断，验证 `slot18` 时必须用完整 query 或完整 char codes。

## sign_value

`sign_value = id130(id280(ua.strip(), key), "s3")`

```python
key = [cursor_value // 256, cursor_value % 256, mode_value % 256]
```

默认观察值：

- `cursor_value = 1`
- `mode_value = 14`
- `SIGN_ALPHABET = "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe"`

## slot77

`slot77` 是下列环境字段拼接的 UTF-8 bytes：

```text
innerWidth|innerHeight|outerWidth|outerHeight|screen.availWidth|screen.availHeight|screen.width|screen.height|navigator.platform
```

示例：

```text
1920|969|1920|1040|1920|1040|1920|1080|Win32
```

这是显式指纹输入，不是运行时环境依赖。

## slot82

```python
slot82 = list((str((timestamp_ms + 3) & 255) + ",").encode("utf-8"))
```

长度可能是 2、3、4 字节，取决于 `(timestamp_ms + 3) & 255` 的十进制位数。

## slot87

`slot87` 不是只 XOR 50 个字段，还要 XOR 已打包的 `slot86` 8 字节。

```python
slot87 = xor(packed_slot86 + selected_50_fields)
```

## slot90_source 字段顺序

```python
order = [34, 44, 56, 61, 73, 29, 70, 45, 35, 49, 38, 66, 51, 68, 28, 48, 64, 47, 30, 71, 26, 55, 31, 69, 59, 40, 62, 63, 27, 72, 41, 74, 57, 52, 42, 39, 33, 67, 53, 43, 65, 46, 36, 24, 60, 32, 79, 80, 84, 85]
slot90_source = [fields[i] for i in order] + slot77 + slot82 + [slot87]
```

## Random

固定 trace 复现时传入：

- `prefix_random`
- `slot86_random`
- `slot90_random`
- `random_tick`
- `parent_start_ms`
- `vendor_tick`

真实请求时可以默认生成：

- prefix: `int(random.random() * 65535)`
- slot90: 每组 `int(random.random() * 1000) & 255`
- random_tick: `int(random.random() * 40) + browser_offset`
- slot86 第二段：由 `id144/id145` 的随机和权限字段分布生成

## 验证标准

- 固定 trace 样本：最终 `a_bogus` 必须逐字节匹配。
- 默认随机样本：`a_bogus` 长度通常为 192，shape 匹配 `[A-Za-z0-9+/=_-]{180,200}`。
- 请求 URL：`parse_qs(url).get("a_bogus")` 能取回生成值。
