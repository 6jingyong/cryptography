# cryptography

一个研究**脏数据中的统计自由度、变换域表示与自适应多通道结构**的开放实验仓库。

当前仓库只做合成 benchmark。核心问题是：

> 给定本来就包含噪声、舍入、漂移、异常点、重复和批次效应的数据，在保持统计与曲线性质合理的前提下，还剩多少可稳定控制、可组合、可纠错的统计自由度？

## 当前路线：固定 q=5

经过前几轮实验，当前暂时不继续扩大 alphabet，固定：

- 统计状态：`center + logvar + skew`；
- 27 个联合三态通过一张**全局固定映射**变成 q=5 symbol；
- slope / curvature 不再作为主要 payload，而作为曲线自然性约束；
- 外层使用 q=5 Hamming `[6,4,3]_5`；
- cell 内部优先选择离状态边界更远、整体曲线代价更低的候选。

### v9：加入 block shaping

v9 只借用了两个成熟编码思想：

1. **wet-paper-style feasibility**：cell/symbol 组合可以直接判为不可用，不强迫每个 cell 什么都能做；
2. **STC-like shaping**：消息约束整个 6-cell block，encoder 从多个合法 codeword 中选择总自然性代价最低的一个。

因此 6-cell block 可以拆成：

`payload + ECC redundancy + shaping freedom = 6 cells`

当前对照：

- `4P0S`：4 个 q=5 payload 自由度 + 2 个 Hamming parity；
- `3P1S`：3 个 payload + 1 个 shaping 自由度 + 2 个 parity。

`3P1S` 中同一 payload 有 5 个合法 Hamming codeword，encoder 选总代价最低的一个；decoder 不需要知道 shaping symbol。

## v9 结果摘要

六个独立 synthetic seed：

| construction | payload rate | mean block cost | roughness | 5% row-loss block recovery |
|---|---:|---:|---:|---:|
| 4P0S | **1.548 bit/cell** | 0.341 | 1.040x | 70.7% |
| 3P1S fixed-control | 1.161 | 0.428 | 1.058x | 64.0% |
| 3P1S shaped | 1.161 | **0.237** | **1.022x** | 70.4% |

最重要的结果不是删点恢复率，而是 hard-feasibility：

- cost cap=0.12：`4P0S 26.5% -> 3P1S 43.7%`
- cost cap=0.20：`4P0S 66.9% -> 3P1S 78.1%`

说明 shaping 的主要价值是：**在保持合法 ECC codeword 的同时，绕开局部高代价/不可用统计状态。**

详见：

- `docs/q5-block-shaping.md`
- `src/block_shaping_v9.py`
- `results/block_shaping_v9.md`
- `results/block_shaping_metrics_v9.json`

## 当前数学对象

对 cell `j` 和 q=5 symbol `a`，定义最优可行候选代价：

`rho[j,a]`

不可用状态：

`rho[j,a] = +infinity`

block encoder 求：

`min total_local_cost + curve_cost`

subject to：

`z belongs to a legal q=5 Hamming/coset family for the payload`.

这使当前问题从“逐 cell 塞 symbol”转为“在一组合法 block 表示中做全局最小代价选择”。

## 当前核心 KPI

- robust bits per independent statistical cell；
- construction feasibility；
- local statistical distortion；
- curve roughness / slope / curvature damage；
- ECC block recovery；
- codebook overhead；
- detectability（不是当前唯一优化目标）。

## 已确认的几个结论

- raw rows 不是正确容量变量，独立统计 cell 才是；
- slope 作为 payload 较脆弱，更适合当曲线约束；
- `center + logvar + skew` 的纯局部状态更稳；
- 全局 q=5 映射比逐 cell alphabet 稳定、简单；
- shaping 明显改善“难塞/难看”，但**不能替代 ECC**；
- bootstrap 重采样仍是强破坏，不应与普通 rounding / measurement noise 混为一谈。

## 当前未解决的关键问题

1. **shared-reference dependency**：当前状态定义仍使用 parent-bin 统计量；decoder 只有最终载体时能否自包含解码尚未解决。
2. **adaptive-rate shaping**：逐 block 在 `4P0S` / `3P1S` 之间切换仍需要可重复的 mode schedule 或 metadata。
3. **同步与 cell 丢失**：整 cell 缺失与普通 row loss 是不同错误模型。
4. **downstream invariance**：未来还需要验证回归、相关性、显著性等下游统计结论是否稳定。

## 仓库结构

- `docs/theory-framework.md`：理论框架
- `docs/q5-block-shaping.md`：q=5 block shaping 设计
- `docs/validation-plan.md`：验证计划
- `src/`：合成 benchmark 脚本
- `data/`：固定 seed 合成数据
- `results/`：每轮实验结果

## 边界

当前仓库只研究合成数据上的统计自由度、容量、鲁棒性和可检测性：

- 不基于真实科研论文制造伪造数据；
- 不把 detector 失败解释为“不可检测”；
- 不把理论组合数直接当成可用容量；
- 不把内部密码本做成逐点映射表。

## License

MIT.
