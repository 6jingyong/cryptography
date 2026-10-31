# cryptography

一个研究**合成数据中的统计自由度、变换域表示、纠错、多通道容量与可检测性**的开放实验仓库。

当前仓库只做 synthetic benchmark。核心问题是：

> 给定一套明确的宏观规律与发布精度，能够把多少可纠错离散状态放进其正交自由度中，同时保持拟合规律、曲线结构和跨变量关系稳定？

## 当前路线：q=8 protected-subspace carrier

当前固定：

- alphabet：`q = 8`
- field：`GF(8)`
- 外层码：q=8 Hamming `[9,7,3]_8`
- block：`6 payload + 1 shaping + 2 parity`
- 每个 payload symbol = 3 bit

局部 carrier 写成：

`y = B(x) * beta + U(x) * c`

其中：

- `B(x)`：必须保护的宏观子空间；
- `U(x)`：`B` 的确定性正交补；
- `c`：q=8 离散 carrier coefficients；
- shaping symbol：在多个合法 Hamming codeword 中选择结构失真最低的一种。

## V11：mixed-package auto-encoder

V10 证明了 homogeneous periodic package 可以扩展到 23.4 MB synthetic payload。V11 进一步测试：

> 同一个 encoder 能否处理多种宏观规律，自动选择 transform，并只依靠 published numeric package + compact manifest 完成 exact decode？

当前 mixed package 同时包含六类 synthetic 数据：

- affine
- periodic
- periodic + second harmonic
- saturation
- Gaussian peak（log-domain）
- strict mirror symmetry

自动选择结果：

| family | selected mode | codewords / 24-point block | nominal density |
|---|---|---:|---:|
| affine | affine | 2 | 1.50 bit/value |
| periodic | periodic1 | 2 | 1.50 |
| harmonic | periodic2 | 2 | 1.50 |
| saturation | saturation | 2 | 1.50 |
| Gaussian | gaussian_log | 2 | 1.50 |
| symmetric | symmetric_even | 1 | 0.75 |

### V11 self-contained round trip

- synthetic high-entropy payload：**262,144 bytes**
- y-series / table：**16**
- heterogeneous tables：**6**
- decoder input：`published_package_v11.npz + manifest_v11.json`
- SHA-256 exact recovery：**yes**
- manifest：**2,781 bytes**
- manifest overhead：**1.061%**
- gross rate：**20.565 bit/row**
- net rate after manifest：**20.347 bit/row**
- gross rate：**1.2853 bit/value**
- net rate after manifest：**1.2717 bit/value**
- raw q=8 symbol error before ECC：**0%** in this three-decimal benchmark

结构失真整体较低；当前最贵的 family 是 Gaussian-log：约 **0.541% NRMSE**、roughness 约 **1.213x**。

详见：

- `src/q8_mixed_package_v11.py`
- `results/q8_mixed_package_v11.md`
- `results/q8_mixed_package_v11.json`

## V11 detectability

V11 同时加入 matched-control detector benchmark。

### Generic detector

只看普通 residual-shape features，不知道 q=8 lattice / Hamming 结构：

| detector | ROC AUC |
|---|---:|
| Logistic | 0.522 |
| Random Forest | 0.703 |
| HistGB | 0.680 |

leave-one-family-out Logistic 平均 AUC：**0.534**。

这说明低阶统计脚印较弱，但非线性模型仍能找到中等 footprint；不能解释成“不可检测”。

### Oracle detector

如果 detector 已知 transform / q=8 lattice / Hamming consistency：

- Logistic：**1.000**
- Random Forest：**1.000**
- HistGB：**1.000**
- family-holdout Logistic：**1.000**

这是 V11 最重要的负结果：**当前离散 lattice/code 结构一旦泄露，carrier 可被直接识别。**

详见：

- `src/v11_detectability.py`
- `results/q8_mixed_package_v11_detectability.json`

## V10：package-level multiplexing

V10 的 homogeneous periodic benchmark 实际跑通：

- synthetic payload：**23.4 MB**
- tables：**100**
- y-series / table：**64**
- Hamming blocks：**10,400,000**
- published rows：**2,275,000**
- effective rate：**82.286 bit/row**
- SHA-256 exact recovery：**yes**

详见：

- `src/q8_package_v10.py`
- `results/q8_package_v10.md`

## v9（历史路线）

v9 使用 `center + logvar + skew`、q=5 Hamming `[6,4,3]_5` 和 block shaping，验证了：

1. wet-paper-style feasibility；
2. STC-like shaping：同一消息对应多个合法 codeword 时选择最低失真的表示。

这些思想保留到了 q=8 protected-subspace 路线。

## 当前核心 KPI

- exact payload recovery / SHA-256；
- usable bits per published numeric value / row；
- manifest / codebook overhead；
- protected macro-parameter drift；
- NRMSE / roughness；
- cross-channel relationship drift；
- raw q=8 symbol error before ECC；
- generic / oracle detectability。

## Synthetic paper benchmark

仓库包含明确标注 synthetic/mock 的 paper-style benchmark Skill：

- `skills/synthetic-paper-benchmark/SKILL.md`

所有输出必须明确标注 `SYNTHETIC BENCHMARK`、`SIMULATED DATA` 或 `MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS`。

## 当前下一步

V12 优先研究：

1. 降低 codebook-aware detectability；
2. Gaussian-log shape-aware distortion reduction；
3. deterministic publication transforms（排序、单位换算、列重排等）；
4. 更严格的 cross-family / out-of-distribution validation。

## 边界

当前仓库只研究 synthetic data 上的容量、结构保持、纠错和可检测性：

- 不基于真实科研论文制造伪造数据；
- 不把真实 secret / model weights 做成隐蔽外传工具；
- 不把 detector 失败解释为“不可检测”；
- 不把理论组合数直接当成可用容量；
- 不把内部 codebook 做成逐点映射表。

## License

MIT.
