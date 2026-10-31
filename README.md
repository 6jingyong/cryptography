# cryptography

一个研究**合成结构化数据中的可控自由度、纠错、package-level multiplexing 与检索/验证协议**的开放实验仓库。

> 当前仓库只做 **synthetic / mock benchmark**。它不用于伪造真实科研证据，也不提供真实 secret / model-weight 的隐蔽传输工作流。

## 当前结论：系统已经不是“一本密码本”

当前架构更准确地写成：

```text
synthetic payload
    ↓
Codebook A：数据解释规则
    ↓
protected-subspace + adaptive q + q-ary ECC + shaping
    ↓
published numeric package
    ↓
Codebook B：预共享结构指纹，只负责 locator
    ↓
Top-K candidate retrieval
    ↓
strict decode / integrity verification
    ↓
accept or reject
```

**Codebook B 不要求唯一定位。**  
召回错误候选没有关系：错误候选可以被拉取、尝试解析，再由最后的严格校验拒绝。

因此当前研究目标不再是“把所有规则都藏到 detector 看不见”，而是同时研究：

1. 数据层能承载多少可纠错状态；
2. package 能否保持宏观结构与发布精度；
3. 第二码本能否把真正目标稳定推进 Top-K；
4. 最终 verifier 能否可靠地区分正确/错误候选。

---

## 1. Codebook A：protected-subspace carrier

局部数值结构写成：

\[
z = B(x)\beta + U(x)c
\]

其中：

- \(B(x)\)：必须保持的宏观规律；
- \(U(x)\)：宏观子空间的自由补空间；
- \(c\)：离散 q-ary carrier coefficients；
- `z` 可以是 `y`，也可以是 `log(y)` 等变换域。

decoder 根据 published `x/y` 与 compact manifest 重建 \(B,U\)，不需要原始未编码曲线。

当前 synthetic families 包括：

- affine；
- periodic / harmonic；
- saturation；
- Gaussian peak（log-domain）；
- symmetry 等。

---

## 2. q 不再固定：adaptive q

早期 V10/V11 固定 `q=8`。后续实验表明，q 更合理的定义是**每张 table 的 operating point**。

当前候选：

\[
q\in\{8,16,32\}
\]

对应 q-ary Hamming：

\[
[q+1,q-1,3]_q
\]

并保留一个 information symbol 作为 shaping freedom。

在当前 synthetic publication benchmark 中，一个粗略经验前沿是：

| 允许的 residual / NRMSE | 常见 operating point |
|---:|---:|
| < ~0.5% | q=8 |
| ~1–1.5% | q=16 |
| ~2.5–3.5% | q=32 |

这不是理论常数，而是当前 transform / quantization / shaping 组合下的实测结果。

### V12 adaptive-q package

同一 128 KiB synthetic payload：

| mode | exact | published rows | gross bit/value | net bit/row |
|---|:---:|---:|---:|---:|
| fixed q=8 | yes | 43,776 | 1.497 | 22.646 |
| adaptive q | yes | 27,760 | 2.361 | 35.705 |

adaptive-q：

- net bit/row：**+57.7%**
- published rows：**-36.6%**
- SHA-256 exact recovery：**yes**

---

## 3. package 才是容量单位

单曲线不是最终对象。更合理的容量模型是：

\[
C_{package}
=
\sum_{\text{tables}}
\sum_{\text{series}}
N_{ij}R_{ij}
-
L(\text{manifest})
\]

同一张表可以共享一个 x 轴并包含很多 y-series；一整套 package 又可以有很多 table。

V10 homogeneous benchmark 已实际跑通：

- synthetic payload：**23.4 MB**
- tables：100
- y-series / table：64
- q=8 Hamming blocks：10,400,000
- published rows：2,275,000
- rate：82.286 bit/row
- SHA-256 exact recovery：yes

因此“大载荷是否可能”首先是 package geometry 问题，而不是单张图的点数问题。

---

## 4. Codebook B：locator，不是 verifier

V13/V14 把第二本预共享码本建模为**结构指纹**。

指纹不需要逐点 mapping，也不需要唯一命中。它只需要在大量候选中让正确 package 排名足够靠前。

当前最简单的结构位置可以是：

\[
(\text{family},q)
\]

未来也可以包含更粗粒度的：

- transform class；
- figure/table family；
- channel-count class；
- publication-precision class；
- block family。

### V14 integrated retrieval result

实际生成一个 12-table adaptive-q synthetic target package，其结构序列包含：

```text
affine:      q8 → q16 → q32
periodic:    q8 → q16 → q32
saturation:  q8 → q16 → q32
gaussian:    q8 → q16 → q32
```

然后放入 10,000 个 synthetic candidates 中。

benchmark 条件：

- 200 个独立 corpus；
- 目标指纹有 20% 提取错误；
- 1% candidate 是 hard near-decoy；
- near-decoy 故意复制目标 50% 的结构位置。

结果：

| locator | P(Top-20) | P(Top-50) | P(Top-100) | mean verification attempts |
|---|---:|---:|---:|---:|
| q-only | 58.0% | 71.5% | 83.5% | 99.8 |
| **joint `(family,q)`** | **93.5%** | **98.5%** | **98.5%** | **5.6** |

因此：

> q schedule 本身可以参与指纹，但联合结构比单独 q 更有效。

---

## 5. 严格验证才是最终真假判断

retrieval false positive 不算协议失败。

流程允许：

```text
candidate 1 -> verify -> reject
candidate 2 -> verify -> reject
candidate 3 -> verify -> accept
```

最终 accept/reject 应由严格校验决定，例如 synthetic benchmark 中的：

- decoder 是否成功；
- payload length / format 是否一致；
- integrity/authentication tag 是否一致；
- SHA-256 是否一致。

所以当前区分三个概念：

\[
\text{recognizability}
\neq
\text{interpretability}
\neq
\text{verified recovery}
\]

能看出“有规则”不等于知道如何解释，也不等于通过最终验证。

---

## 6. 对 detectability 的重新定位

V11 的 oracle detector 在知道 q=8 lattice / Hamming 规则时 AUC 可以达到 1.0。

旧解释是：

> 规则性是必须消除的风险。

当前更准确的解释是：

> 固定结构具有强指纹；它既可能增加 recognizability，也可能为预共享 locator 提供有用信号。

因此 detectability 仍然记录，但不再单独决定优化方向。

当前更关键的 KPI 是：

- exact recovery；
- bit/value；
- bit/row；
- package rows；
- manifest overhead；
- macro / correlation drift；
- raw symbol error；
- locator Recall@K；
- target-rank distribution；
- expected verification attempts；
- strict false accepts。

---

## 7. 当前实现

### 当前主线

- `src/adaptive_q_package_v12.py`：adaptive-q package encoder/decoder
- `src/dual_codebook_pipeline_v14.py`：locator + strict verification 集成

### 当前结果

- `results/adaptive_q_v12.md`
- `results/dual_codebook_pipeline_v14.md`

### 理论说明

- `docs/theory-framework.md`
- `docs/dual-codebook-architecture.md`
- `docs/validation-plan.md`

### 历史路线

V9 及更早的 `center / logvar / skew / q=5` statistical-cell 路线仍保留在仓库中，作为思想来源与历史对照，不再是当前主架构。

---

## 8. 当前下一步

优先级：

1. **扩大 locator corpus**：10k → 100k / 1M synthetic descriptors，研究 fingerprint length 与 Top-K 成本；
2. **publication transforms**：排序、列重排、单位缩放、有效数字变化后的 self-contained decode；
3. **更真实的 synthetic residual models**：让 q 的选择基于明确的数据生成模型，而不是只依赖人工 NRMSE budget；
4. **fingerprint redundancy**：研究缺图、缺表、结构位置丢失时的 retrieval；
5. **metadata accounting**：把 manifest / locator codebook / integrity metadata 全部计入净容量。

---

## 9. 边界

仓库只研究 synthetic/mock benchmark：

- 不基于真实科研论文制造伪造实验数据；
- 不把真实 secrets 或 model weights 做成隐蔽外传工具；
- 不把 detector 失败解释成信息论意义上的“不可检测”；
- 不把理论组合数直接当作有效容量；
- 第二码本只在 synthetic corpus 中研究检索性质。

## License

MIT.
