# cryptography

一个研究**合成数据中的统计自由度、变换域表示、纠错与多通道容量**的开放实验仓库。

当前仓库只做 synthetic benchmark。核心问题已经从早期的“脏数据里能不能找到可控统计状态”，推进到：

> 给定一套明确的宏观规律与发布精度，能够把多少可纠错离散状态放进其正交自由度中，同时保持拟合规律、曲线结构和跨变量关系稳定？

## 当前路线：q=8 protected-subspace carrier

V10 固定：

- alphabet：`q = 8`
- field：`GF(8)`
- 外层码：q=8 Hamming `[9,7,3]_8`
- block：`6 payload + 1 shaping + 2 parity`
- 每个 payload symbol = 3 bit

局部 carrier 不再主要依赖 `center + logvar + skew`，而写成：

`y = B(x) * beta + U(x) * c`

其中：

- `B(x)`：必须保护的宏观子空间；
- `U(x)`：`B` 的确定性正交补；
- `c`：q=8 离散 carrier coefficients；
- shaping symbol：在多个合法 Hamming codeword 中选择结构失真最低的一种。

对于当前 14-point 周期 block：

- protected dimensions = 5：
  `1, sin(wx), cos(wx), sin(2wx), cos(2wx)`
- free dimensions = 9
- 一整个 `[9,7,3]_8` codeword 正好放入 free subspace
- 每 block 18 payload bit

因此：

`18 / 14 = 1.285714 bit / published numeric value`

## V10：package-level multiplexing

当前重点不再是单张图或单条曲线，而是：

`package = many tables x many y-series x rows x bits/value`

同一个 x 轴可以自然对应多条 y 曲线；不同 table 也可以采用各自的宏观参数。

### 全量 synthetic LoRA-size benchmark

V10 已实际跑通：

- synthetic high-entropy payload：**23.4 MB**
- tables：**100**
- y-series / table：**64**
- Hamming blocks：**10,400,000**
- published rows：**2,275,000**
- published numeric y-values：**145,600,000**
- effective rate：**82.286 bit / row**
- effective rate：**1.285714 bit / numeric value**

round-trip：

- SHA-256 exact recovery：**yes**
- raw q=8 symbol error before ECC：约 **0.019%**
- mean NRMSE：约 **0.333%**
- mean roughness ratio：约 **1.042x**
- cross-channel correlation-matrix MAE：约 **7.2e-6**

详见：

- `src/q8_package_v10.py`
- `results/q8_package_v10.md`

## 为什么从 q=5 转向 q=8

q=5 是 v9 的重要中间阶段，但 q=8 更适合当前结构：

- 一个 symbol 正好是 3 bit；
- GF(8) Hamming `[9,7,3]_8` 结构自然；
- `6 payload + 1 shaping + 2 parity = 9`；
- 不需要额外 radix conversion；
- 在当前 publication quantization benchmark 下，q=8 能在较低结构失真下提供明显更高密度。

## v9（历史路线）

v9 使用：

- `center + logvar + skew`
- 27 个联合三态映射到 q=5
- q=5 Hamming `[6,4,3]_5`
- `3 payload + 1 shaping + 2 parity`

它验证了两个重要思想：

1. **wet-paper-style feasibility**：某些局部状态可以直接不可用；
2. **STC-like shaping**：在同一消息对应的多个合法 codeword 中选择最低失真的表示。

这些思想仍然保留在 v10，但 carrier 从“统计 cell”升级成了“protected subspace”。

历史实现：

- `src/block_shaping_v9.py`
- `results/block_shaping_v9.md`

## 当前核心 KPI

- exact payload recovery / SHA-256；
- usable bits per published numeric value；
- usable bits per published row；
- protected macro-parameter drift；
- NRMSE；
- curve roughness；
- cross-channel correlation drift；
- q=8 raw symbol error before ECC；
- codebook / metadata overhead。

## Synthetic paper benchmark

仓库加入一份明确标注 synthetic/mock 的 paper-style benchmark Skill：

- `skills/synthetic-paper-benchmark/SKILL.md`

它可以组织：

- synthetic raw data；
- multi-panel figures；
- multivariate tables；
- supplementary-data style files；
- methods / capacity / distortion / recovery summaries。

所有输出必须明确标注：

- `SYNTHETIC BENCHMARK`
- `SIMULATED DATA`
- 或 `MOCK PAPER — NOT REAL EXPERIMENTAL RESULTS`

不用于制造或冒充真实科研证据。

## 仓库结构

- `docs/`：理论与历史设计
- `src/`：synthetic benchmark 程序
- `data/`：固定 synthetic 数据
- `results/`：实验结果与阶段报告
- `skills/`：synthetic benchmark 工作流

## 边界

当前仓库只研究 synthetic data 上的容量、结构保持、纠错和可检测性：

- 不基于真实科研论文制造伪造数据；
- 不把真实 secret / model weights 做成隐蔽外传工具；
- 不把 detector 失败解释为“不可检测”；
- 不把理论组合数直接当成可用容量；
- 不把内部 codebook 做成逐点映射表。

## License

MIT.
