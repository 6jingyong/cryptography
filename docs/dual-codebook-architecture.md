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


---

## V15/V16：locator 使用稳定 label canonicalize

第二码本进一步写成：

\[
F=\{(\ell_i,v_i)\}
\]

其中 `label` 来自公开结构，`value` 才是预共享模式的一部分。

因此：

```text
figure/table reorder
    -> recover public labels
    -> canonical sort
    -> compare locator values
```

而不是把 figure 的当前顺序直接当协议位置。

当前 benchmark 中：

- naive ordered matcher 在随机重排下 median rank ≈ 4066 / 10k；
- canonical labeled matcher 在同样 25% erasure + 10% substitution 下 median rank = 1。

在 1M synthetic candidates 上，12-ary × 16 labeled positions、25% erasure 时，Top-20=96.7%、Top-100=100%（30 seeds）。

如果允许 50% labeled positions 完全缺失：

- 12-ary × 24：Top-100=100%；
- 12-ary × 32：Top-20=100%。

所以 locator 的主要冗余预算应针对 **erasure / label loss**，而不是 figure 顺序。
