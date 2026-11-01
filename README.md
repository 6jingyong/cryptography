# cryptography

一个研究**合成结构化数据中的可控自由度、纠错、package-level multiplexing、检索/验证与发布流程鲁棒性**的开放实验仓库。

> 当前仓库只做 **synthetic / mock benchmark**。不用于伪造真实科研证据，也不提供真实 secrets / model weights 的隐蔽传输工作流。

## 当前架构

```text
synthetic payload
    ↓
Codebook A：解释规则
    ↓
protected subspace + adaptive q + q-ary ECC + shaping
    ↓
published numeric package
    ↓
public canonicalization schema
    ↓
Codebook B：labeled structural fingerprint，只负责 locator
    ↓
Top-K candidates
    ↓
strict decode / integrity verification
    ↓
accept / reject
```

现在明确区分：

\[
\text{recognizability}
\neq
\text{interpretability}
\neq
\text{verified recovery}
\]

Codebook B 不要求唯一定位。误召回只增加验证成本，最终真假只由 strict verifier 决定。

---

## 1. Codebook A

局部数值结构：

\[
z=B(x)\beta+U(x)c
\]

- \(B(x)\)：protected macro structure；
- \(U(x)\)：free subspace；
- \(c\)：q-ary carrier coefficients；
- `z` 可以是 `y`、`log(y)` 等变换域。

当前 synthetic families 包括 affine、periodic/harmonic、saturation、Gaussian/log、symmetry。

---

## 2. adaptive q

当前：

\[
q\in\{8,16,32\}
\]

使用 q-ary Hamming：

\[
[q+1,q-1,3]_q
\]

V12 同一 128 KiB synthetic payload：

| mode | exact | rows | gross bit/value | net bit/row |
|---|:---:|---:|---:|---:|
| fixed q=8 | yes | 43,776 | 1.497 | 22.646 |
| adaptive q | yes | 27,760 | 2.361 | 35.705 |

---

## 3. package-level capacity

\[
C_{package}
=
\sum_{j,k}N_{jk}R_{jk}
-
L(\text{metadata})
\]

V10 homogeneous benchmark：

- synthetic payload 23.4 MB；
- 100 tables；
- 64 y-series / table；
- 10.4M q8 Hamming blocks；
- 2.275M published rows；
- 82.286 bit/row；
- SHA-256 exact recovery。

---

## 4. Codebook B：labeled locator

第二码本：

\[
F=\{(\ell_i,v_i)\}_{i=1}^{L}
\]

- label \(\ell_i\)：公开 package 中可恢复的 table / figure / axis / role identity；
- value \(v_i\)：预共享的粗粒度联合结构，例如 `(family,q)`。

V16 在 1M synthetic candidates 上：

| fingerprint | erasure | P(Top-20) | P(Top-100) |
|---|---:|---:|---:|
| 12-ary × 16 | 25% | 96.7% | 100% |
| 12-ary × 24 | 50% | 90.0% | 100% |
| 12-ary × 32 | 50% | 100% | 100% |
| q-only 3-ary × 32 | 50% | 46.7% | 66.7% |

因此 q 只适合作为 locator value 的一部分。

---

## 5. V17：publication pipeline robustness

V17 把发布后的变化分成三类。

### Natural invariant

Gaussian/log mode 下正的乘法单位换算：

\[
y'=ay
\]

可以自然吸收到 protected constant term。synthetic test 中放大 1000 倍仍 exact。

### Canonicalizable

只需要公开 schema / unit metadata：

- 列重排 + channel labels；
- 行重排 + `(segment_id,x_index)`；
- row + column reorder；
- table split / merge；
- 一般 affine unit transform 在已知单位换算参数下。

这些操作在 V17 synthetic package 中全部 exact recovery。

### Precision-destructive

真正的硬边界是二次量化。

current spacing：

```text
q8  = 2.0 x publication step
q16 = 2.5 x
q32 = 3.0 x
```

当前 package：

- original step：exact；
- 1.5x re-quantization：失败；
- 2 decimal places：exact；
- 1 decimal place：失败；
- 4 significant digits：exact；
- 3 significant digits：失败。

因此核心变量是：

\[
\boxed{\Delta/\delta_{final}}
\]

而不是 q 本身。

---

## 6. publication guard modes

| mode | q8/q16/q32 spacing | bit/value | tested exact re-quantization |
|---|---|---:|---:|
| current | 2 / 2.5 / 3 | 2.312 | 1.0x |
| guarded | 3 / 3.5 / 4.5 | 1.844 | 1.5x |
| strong | 4 / 5 / 6 | 1.762 | 1.75x |
| very strong | 5 / 6.5 / 8 | 1.762 | **3.0x** |

`very strong` 在本轮 synthetic package 中 3.0x 仍 exact、3.25x 开始失败。

这说明 Codebook A 应显式带 publication operating mode：

```text
high_density
guarded_1p5x
guarded_1p75x
guarded_3x
```

---

## 7. 当前文件

### Code

- `src/adaptive_q_package_v12.py`
- `src/dual_codebook_pipeline_v14.py`
- `src/locator_erasure_scaling_v16.py`
- `src/publication_robustness_v17.py`

### Results

- `results/adaptive_q_v12.md`
- `results/dual_codebook_pipeline_v14.md`
- `results/locator_v16.md`
- `results/publication_robustness_v17.md`

### Docs

- `docs/theory-framework.md`
- `docs/dual-codebook-architecture.md`
- `docs/publication-pipeline.md`
- `docs/validation-plan.md`

---

## 8. 下一步

下一阶段优先研究显式 synthetic residual models：

\[
y=f(x)+\epsilon
\]

包括：

- iid Gaussian；
- heteroscedastic Gaussian；
- AR(1)；
- batch drift；
- Gaussian + sparse outliers。

问题从“人工给一个 NRMSE budget”改成：

> carrier residual 是否仍然与声明的数据生成模型相容？在这个约束下最大可用 q / publication guard 是多少？

---

## 9. 边界

仓库只研究 synthetic/mock benchmark：

- 不基于真实科研论文制造伪造实验数据；
- 不把真实 secrets 或 model weights 做成隐蔽外传工具；
- 不把 detector 失败解释成信息论意义上的不可检测；
- 不把理论组合数直接当作有效容量；
- 第二码本只在 synthetic corpus 中研究检索性质。

## License

MIT.
