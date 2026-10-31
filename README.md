# cryptography

一个研究**脏数据中的统计自由度、变换域表示与自适应多通道结构**的开放实验仓库。

当前目标不是设计某个具体密码算法，而是回答一个更基础的问题：

> 给定一份本来就包含噪声、舍入、漂移、异常点、重复、缺失和批次效应的数据，在保持图表与统计性质合理的前提下，还剩多少可稳定控制、可组合、可重复验证的统计自由度？

## 新的总体思路

项目已经从最初的“几何均值 + 一阶差分 + 分布密码本”扩展为四层结构：

1. **中心/曲线层**  
   通过区间几何均值、离散一阶差分、曲率等描述宏观趋势，并要求最终曲线保持低复杂度和平滑性。

2. **多统计通道层**  
   在同一统计单元中考察多个候选状态，例如 slope、curvature、variance、IQR、skew、residual autocorrelation、spectral ratio、跨变量相关关系等。目标不是固定使用全部通道，而是寻找彼此低耦合、鲁棒、自然的自由度。

3. **低复杂度内部密码本 / feature map**  
   不要求所有统计单元使用同一种表示。内部密码本只描述“哪些单元使用哪些统计特征、如何粗粒度量化、状态如何解释”等低复杂度规则。理想目标是：

   \[
   L(K) \ll L(C)
   \]

   其中 \(K\) 是内部规则描述，\(C\) 是主要高熵载荷。密码本不应膨胀成逐点说明书。

4. **干扰层**  
   没有被中心层或统计通道使用的观测仍保留在可见数据中，用于维持自然散布、批次差异和背景脏度。干扰层不是“无用数据”，而是自然性约束的一部分。

## 核心研究对象

对第 \(j\) 个独立统计单元，定义候选特征向量：

\[
F_j=(S_{slope},S_{curvature},S_{variance},S_{IQR},S_{autocorr},S_{spectrum},\ldots)
\]

真正关心的不是单个特征有多少状态，而是自然性约束 \(N_j\) 下的联合自由度：

\[
C_j = H(F_j\mid N_j)
\]

整个载体的有效容量近似为：

\[
C_{total} \approx \sum_j C_j - L(K) - R_{ECC}
\]

其中：

- \(L(K)\)：内部密码本 / feature map 的描述成本；
- \(R_{ECC}\)：为了鲁棒解码付出的纠错冗余。

因此项目的核心 KPI 已从单纯的 `bits/row` 改为：

- **robust bits per independent statistical cell**；
- **independent cells per carrier collection**；
- **codebook overhead**；
- **detectability**；
- **robustness**。

## 当前已经验证的部分

目前的合成 benchmark 已经得到几个正向结果：

- 约 10% 的对称干扰样本可以显著改变散布，而几乎不移动几何均值中心线；
- 在不知道 latent function 的情况下，只靠可观测 x/y，能够从脏数据池中盲选出明显比随机分组更平滑的中心曲线；
- 中心曲线子集与一个独立的三态分布 codebook 可以同时存在；
- 在 12 组随机 seed 中，双通道结构大部分情况下都能稳定复现；
- 单纯增加 raw rows 并不会线性增加容量，真正重要的是独立统计单元数与每个单元的联合自由度。

详细结果见 `results/`。

## 当前实验路线

下一阶段重点不是继续增加原始数据行数，而是寻找一组“统计正交基”：

1. 计算 slope / curvature / variance / IQR / skew / autocorrelation / spectral ratio 等候选特征；
2. 测量它们的互信息、相关性和条件熵；
3. 测试删点、重采样、舍入和轻微噪声下的状态稳定性；
4. 对每个统计单元自适应选择最有余量的 feature；
5. 计算 adaptive multi-channel capacity 与内部密码本开销；
6. 最后再加入独立 detector，比较自然随机数据和结构化数据的可检测性。

## 仓库结构

- `docs/theory-framework.md`：理论框架
- `docs/validation-plan.md`：初版验证计划
- `docs/curve-construction.md`：曲线与干扰层设计
- `src/`：合成数据、盲选、双通道、容量估算等实验脚本
- `data/`：固定 seed 的合成 benchmark
- `results/`：每轮验证结果

## 边界

当前仓库只研究合成数据上的统计自由度、容量、鲁棒性和可检测性：

- 不基于真实科研论文制造伪造数据；
- 不把一次 detector 失败解释为“不可检测”；
- 不把理论组合数直接当成可用容量；
- 不把内部密码本设计成逐点映射表。

所有结果首先作为可重复、可证伪的 benchmark。

## License

MIT.
