# 双码本架构说明

## 一句话版本

当前系统不是“一本密码本把信息藏进一张图”，而是：

```text
Codebook A：告诉 decoder 如何解释一个 package
Codebook B：告诉 receiver 哪些 package 值得尝试
Verifier：最后决定候选是真是假
```

第二本码本只负责 locator，因此允许误召回。

---

## Codebook A — interpretation

对象：

```text
table
  -> macro family
  -> transform
  -> protected basis B
  -> adaptive q
  -> q-ary Hamming
  -> shaping
  -> publication transform
```

典型 manifest 字段：

```json
{
  "family": "periodic",
  "transform": "identity",
  "q": 16,
  "delta": 0.04,
  "points_per_block": 22,
  "channels": 16
}
```

原则：

- compact；
- deterministic；
- decoder 不访问原始 unencoded curve；
- metadata 成本必须计入净容量。

---

## Codebook B — locator

对象不是 payload bit，而是 package 结构：

```text
(family, q, transform, coarse layout, ...)
```

例如：

```text
affine/q8
affine/q16
affine/q32
periodic/q8
periodic/q16
periodic/q32
...
```

receiver 只需要知道一个短结构 pattern。

候选 ranking 可以使用：

\[
S(F,G)=\frac1L\sum_i1[F_i=G_i]
\]

也可以以后使用 weighted similarity / missing-position distance。

Codebook B 不要求：

- 唯一命中；
- 低 false positive；
- 直接解码 payload。

它只要求目标高概率进入 Top-K。

---

## Strict verifier

错误候选允许被下载、解析和尝试。

最终 accept 可以要求：

1. decoder 输出格式正确；
2. length / version 一致；
3. keyed integrity tag 正确；
4. synthetic benchmark 中 payload hash 一致。

所以系统天然容忍：

```text
retrieve wrong -> reject -> retrieve next
```

评价重点应该是：

\[
E[\text{verification attempts}]
\]

而不是单独最小化 retrieval FPR。

---

## V14 synthetic result

在 10,000 个 candidate、20% target fingerprint corruption、1% near-decoys
且 near-decoy 复制 50% 结构位置时：

`q-only`：

- Top-20：58.0%
- Top-100：83.5%
- mean attempts：99.8

joint `(family,q)`：

- Top-20：93.5%
- Top-50：98.5%
- Top-100：98.5%
- mean attempts：5.6

结论：

> 第二本码本应优先描述联合结构，不必承担最终认证职责。
