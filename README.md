# cryptography

一个关于**结构化数值数据如何承载、检索和恢复离散信息**的 synthetic benchmark 项目。

> 这个仓库研究的是：  
> **当一组公开数值数据本来就有自己的宏观规律、噪声、量化和多表结构时，还能否在不破坏这些规律的前提下，稳定加入可恢复的离散状态？**
>
> 当前只使用 synthetic / mock 数据做实验，不用于真实科研造假，也不提供真实 secrets / model weights 的隐蔽传输工作流。

---

# Quick Start：先亲眼跑一次

第一次看这个项目，推荐先不要跑完整 benchmark：

```bash
python -m pip install -r requirements.txt
python demo.py
```

`demo.py` 会自动完成：

```text
synthetic payload
-> adaptive-q numeric package
-> structural locator
-> reject a decoy
-> decode the published package
-> SHA-256 PASS
```

并生成：

```text
demo_output/curve_before_after.svg
demo_output/demo_manifest_summary.json
demo_output/demo_summary.json
```

Quick demo 使用缩小的 calibration，只用于理解流程；正式结果仍以 `src/` / `results/` 中的 benchmark 为准。

更详细步骤见 [`docs/quick-start.md`](docs/quick-start.md)。

---

# 30 秒理解这个项目

```text
原始 payload
    ↓
把 bit 变成 q-ary 状态
    ↓
把这些状态放进“不影响宏观曲线”的自由方向
    ↓
得到一组可正常发布的数值表格
    ↓
接收端先用“第二本码本”从很多候选里找出可能的目标
    ↓
再按“第一本码本”尝试解码
    ↓
最后用严格校验判断对错
```

所以它不是“一张图里藏一串 bit”这么简单，而更像：

\[
\boxed{
\text{numeric carrier}
+
\text{locator}
+
\text{decoder}
+
\text{verifier}
}
\]

---

# 为什么需要两本码本？

因为“找到目标”和“读懂目标”是两件不同的事。

## Codebook A：解释码本

它告诉 decoder：

> 这张表应该怎样解释？

例如：

```text
family = periodic
transform = identity
q = 16
ECC = q-ary Hamming
publication mode = guarded
```

它决定真正的解码方式。

## Codebook B：定位码本

它不负责解码，只负责回答：

> 在很多候选 package 里，哪些值得先试？

例如一个 package 的结构可能是：

```text
affine/q8
affine/q16
periodic/q8
periodic/q16
gaussian/q16
...
```

这组结构本身就可以形成一个短指纹。

如果 Top-20 里有多个候选，也没关系：

```text
candidate A -> decode -> reject
candidate B -> decode -> reject
candidate C -> decode -> accept
```

因此：

\[
\boxed{
\text{locator 允许误召回，verifier 才负责最终真假}
}
\]

---

# 数值层是怎么工作的？

一条曲线通常有自己的宏观规律。

我们把它写成：

\[
z=B(x)\beta+U(x)c
\]

其中：

- \(B(x)\beta\)：负责“这条曲线看起来还是原来的曲线”；
- \(U(x)c\)：负责承载离散状态。

例如周期曲线可以保护：

\[
1,\sin \omega x,\cos \omega x,\sin 2\omega x,\cos 2\omega x
\]

然后只在这些方向的正交补空间中调整 carrier。

对于 Gaussian peak，还可以先进入：

\[
z=\log y
\]

再做同样的事情。

---

# q 是什么？

q 表示每个离散 symbol 有多少种状态。

目前主要研究：

\[
q\in\{8,16,32\}
\]

对应：

- q=8：3 bit / symbol
- q=16：4 bit / symbol
- q=32：5 bit / symbol

q 越大，容量越高，但需要更大的数值间隔，所以现在由每张 table 自己选择 q。

---

# adaptive-q

当前逻辑可以概括成：

```text
非常平滑 / 精度高     -> q=8
允许约 1% residual   -> q=16
允许约 2.5~3%        -> q=32
```

这不是理论常数，而是当前 synthetic benchmark 的 operating point。

---

# 为什么还要 ECC？

因为公开数据可能经历：

- rounding；
- re-quantization；
- 数值噪声；
- 个别 symbol 判错。

当前使用 q-ary Hamming：

\[
[q+1,q-1,3]_q
\]

并保留一个 information symbol 作为 shaping freedom。

shaping 的目的不是增加 payload，而是在多个合法 codeword 中选择结构代价更低的那个。

---

# 为什么容量单位是 package？

一个 package 可以包含：

- 多张 table；
- 每张 table 多个 y-series；
- 每张 table 不同 q；
- 不同 transform；
- 不同 publication mode。

所以总容量更接近：

\[
C_{package}
=
\sum_{tables}
\sum_{series}
N_{ij}R_{ij}
-
L(metadata)
\]

---

# 目前跑到什么程度？

## V10：大 package

已经实际跑通：

- synthetic payload：23.4 MB
- 100 tables
- 64 y-series / table
- 2.275M published rows
- 82.286 bit/row
- SHA-256 exact recovery

## V12：adaptive-q

同一 128 KiB synthetic payload：

| mode | exact | rows | gross bit/value | net bit/row |
|---|:---:|---:|---:|---:|
| fixed q=8 | yes | 43,776 | 1.497 | 22.646 |
| adaptive q | yes | 27,760 | 2.361 | 35.705 |

adaptive-q 让 net bit/row 提升约 57.7%。

## V16：第二本码本 / locator

在 1,000,000 个 synthetic candidates 中：

| fingerprint | erasure | P(Top-20) | P(Top-100) |
|---|---:|---:|---:|
| 12-ary × 16 | 25% | 96.7% | 100% |
| 12-ary × 24 | 50% | 90.0% | 100% |
| 12-ary × 32 | 50% | 100% | 100% |

结论：

> 第二本码本不需要唯一定位，只需要让目标高概率进入 Top-K。

## V17：发布流程鲁棒性

现在已经区分：

### Natural invariant

不需要额外 metadata。

例如 Gaussian/log mode 下：

\[
y'=ay
\]

仍然可以直接恢复。

### Canonicalizable

只要保留公开 schema，就可以恢复：

- 行重排；
- 列重排；
- table split / merge；
- 已知单位换算。

### Precision-destructive

真正危险的是二次量化。

当前实验中：

- 2 decimal places：exact
- 1 decimal place：fail
- 4 significant digits：exact
- 3 significant digits：fail

通过加大 symbol spacing，可以换取更强 publication robustness。

---

# 一个完整例子

假设有一个 12-table synthetic package：

```text
table 01 -> affine / q8
table 02 -> affine / q16
table 03 -> affine / q32
table 04 -> periodic / q8
table 05 -> periodic / q16
table 06 -> periodic / q32
table 07 -> saturation / q8
table 08 -> saturation / q16
table 09 -> saturation / q32
table 10 -> gaussian / q8
table 11 -> gaussian / q16
table 12 -> gaussian / q32
```

那么：

1. `family + q` 可以形成 locator fingerprint；
2. 每张 table 内部再根据 Codebook A 解码；
3. 如果 table 顺序被打乱，只要 table identity 还在，就先 canonicalize；
4. 如果少几张 table，locator 把它当 erasure；
5. 如果误召回了错误 package，最终 verifier 会拒绝。

这就是当前完整协议。

---

# 当前主线代码

```text
src/adaptive_q_package_v12.py
src/dual_codebook_pipeline_v14.py
src/locator_erasure_scaling_v16.py
src/publication_robustness_v17.py
```

说明文档：

```text
docs/how-it-works.md
docs/theory-framework.md
docs/dual-codebook-architecture.md
docs/publication-pipeline.md
docs/validation-plan.md
```

---

# 完整实例：从 12 行配置到一个 mock paper package

如果 Quick Start 只告诉你“协议能跑”，完整实例则回答：

> **我给工具什么？它最后给我什么？**

输入只是一个很小的 JSON：

```json
{
  "payload_bytes": 8192,
  "channels_per_table": 8,
  "locator": {
    "candidate_count": 1000,
    "near_decoys": 20,
    "shared_structure_fraction": 0.5,
    "target_substitutions": 1
  }
}
```

运行：

```bash
python examples/generate_mock_paper.py \
  --config examples/mock-paper-config.json \
  --out-dir mock_paper_output
```

内部发生的事情只有三层：

```text
WRITE   synthetic payload -> adaptive-q numeric package
FIND    structural fingerprint -> Top-K candidates
VERIFY  decoder + strict integrity -> ACCEPT / REJECT
```

最后得到：

```text
mock_paper_output/
├── README.md
├── paper.md
├── manifest_readable.json
├── verification.json
├── figures/
│   ├── figure_1_periodic_before_after.svg
│   ├── figure_2_adaptive_q_schedule.svg
│   └── figure_3_locator_verifier.svg
├── data/
│   ├── periodic_table_sample.csv
│   └── gaussian_table_sample.csv
└── carrier/
    ├── published_adaptive_q_v12.npz
    ├── manifest_adaptive_q_v12.json
    └── adaptive_q_v12_results.json
```

其中 `paper.md` 只是展示层；真正权威的是：

```text
published numeric package
+ manifest
-> decoder
-> verification.json
```

完整说明见：

```text
docs/mock-paper-example.md
skills/synthetic-paper-benchmark/SKILL.md
```

所有 mock-paper 产物必须保留：

```text
MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS
```

这不是装饰标签，而是 Skill 的硬约束。

---

# 当前真正还没解决的问题

现在最重要的问题已经不是“还能不能再塞更多 bit”，而是：

\[
\boxed{
\text{加入 carrier 后，residual 是否仍然像原本的数据生成机制？}
}
\]

下一阶段会显式建立：

\[
y=f(x)+\epsilon
\]

其中 \(\epsilon\) 分别是：

- iid Gaussian；
- heteroscedastic；
- AR(1)；
- batch drift；
- sparse outlier mixture。

然后测试：

> 在保持 residual model 合理的条件下，最大 q / publication guard 到底是多少？

---

# 边界

本仓库只研究 synthetic / mock benchmark：

- 不制造真实科研证据；
- 不把真实 secrets / model weights 做成隐蔽传输工具；
- 不把 detector 失败解释成“绝对不可检测”；
- 不把理论组合数直接当有效容量；
- locator 只在 synthetic corpus 中验证。

## License

MIT
