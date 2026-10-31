# 理论框架 v0.2

## 1. 核心问题

传统隐写通常从“如何把信息塞进一个正常载体”出发。

本项目换一个角度：

> 如果环境本身就存在大量噪声、缺失、舍入、仪器漂移、异常点、重复和人为清洗，那么满足公开自然性约束之后，还剩多少可以稳定控制的统计自由度？

因此研究对象不是某一种具体隐写算法，而是：

**天然脏数据中的条件熵、变换域结构、低复杂度内部规则、鲁棒性与可检测性。**

---

## 2. 从固定双通道到自适应多通道

早期模型主要研究两类状态：

1. 区间几何均值形成的离散 slope；
2. 同一区间内的粗粒度分布状态。

后续实验表明，这两类状态可以在合成脏数据中同时存在，因此进一步把每个独立统计单元表示为候选特征向量：

\[
F_j=(S_{slope},S_{curvature},S_{variance},S_{IQR},S_{skew},S_{autocorr},S_{spectrum},S_{relation},\ldots)
\]

不同 cell 不要求采用同一种 feature。真正的问题变成：

> 每个 cell 在自然性约束下，哪些统计方向仍有可控余量？这些方向之间有多少条件独立性？

---

## 3. 观测空间与派生空间

设公开观测数据为：

\[
D=\{(x_i,y_i)\}_{i=1}^{N}
\]

同一份数据可以映射到不同表示空间：

\[
\Phi_1(D)=\text{raw values}
\]

\[
\Phi_2(D)=\text{binned geometric means}
\]

\[
\Phi_3(D)=\text{discrete slopes / curvature}
\]

\[
\Phi_4(D)=\text{histogram / quantile / spread statistics}
\]

\[
\Phi_5(D)=\text{residual order / autocorrelation / spectrum}
\]

\[
\Phi_6(D)=\text{cross-series / cross-variable relations}
\]

关键思想是：

> 原始空间看起来正常，并不意味着所有派生空间都没有额外自由度；反之，某个派生空间中的结构也不一定显著改变原始空间的视觉和传统统计指标。

---

## 4. 中心线、导数与曲率

将 x 轴划分为区间：

\[
B_1,\ldots,B_m
\]

对于正值 y，定义每个区间的几何均值：

\[
g_j=\exp\left(\frac{1}{n_j}\sum_{i\in B_j}\ln y_i\right)
\]

定义相邻区间离散斜率：

\[
s_j=\frac{g_{j+1}-g_j}{\bar{x}_{j+1}-\bar{x}_j}
\]

以及离散曲率/二阶差分：

\[
c_j=s_{j+1}-s_j
\]

连续 spline 只作为曲线合理性的评价器，不作为主要状态定义，以避免容量依赖特定拟合器。

曲线自然性可通过以下指标评价：

- spline roughness；
- derivative total variation；
- max slope；
- residual pattern；
- 与 observable smooth target 的偏差。

---

## 5. 分布与残差候选通道

同一 cell 内还可以定义：

### Spread

\[
S_{variance}=Q(\log\sigma)
\]

\[
S_{IQR}=Q(Q_{75}-Q_{25})
\]

### Shape

\[
S_{skew}=Q(\text{skewness})
\]

或粗粒度的上下尾质量、分位数比例等。

### Residual order

拟合宏观趋势后得到残差：

\[
r_i=y_i-f(x_i)
\]

可研究：

\[
S_{autocorr}=Q(\operatorname{Corr}(r_i,r_{i+1}))
\]

### Frequency-domain structure

对残差做频域变换后可定义：

\[
S_{spectrum}=Q\left(\frac{E_{low}}{E_{high}}\right)
\]

### Cross-variable / cross-series relation

对于多变量或多曲线数据，还可以研究相关系数、相位差、交点数、面积差等关系状态。

这些候选特征是否真正提供新增容量，需要通过条件熵/互信息和鲁棒性实验验证，而不能直接相加。

---

## 6. 低复杂度内部密码本 / feature map

引入内部规则 K：

\[
K=\{\text{feature choice},\text{quantization},\text{ordering},\text{state map},\text{ECC parameters}\}
\]

其作用不是逐点说明数据如何分配，而是用低描述复杂度描述“如何解释统计状态”。

理想条件：

\[
L(K)\ll L(C)
\]

其中 C 表示主要高熵载荷。

因此一个 cell 可以使用 slope，另一个使用 variance，再一个使用 autocorrelation；某些 cell 也可以完全不承载状态，只保留为背景干扰。

这相当于自适应信道分配：

\[
S_j^*=\arg\max_{S\in\mathcal{S}} C(S_j\mid N_j)
\]

其中 \(N_j\) 是该 cell 必须满足的自然性与鲁棒性约束。

密码本的关键约束是：

> 它应该描述规则族，而不是记录逐行 assignment。

否则密码本自身会膨胀并吞噬主要载荷收益。

---

## 7. 干扰层

将观测划分为角色：

\[
D=D_{center}\cup D_{feature}\cup D_{interference}
\]

其中：

- `center` 主要维持宏观曲线；
- `feature` 产生若干统计状态；
- `interference` 保留自然散布、批次效应和背景脏度。

干扰层不是简单删除的“无用点”。它的存在可能影响：

- 总体分布；
- detector 特征；
- 局部方差；
- 曲线观感；
- 状态鲁棒性。

因此干扰层必须进入最终自然性评价。

---

## 8. 独立统计单元，而不是 raw rows

后续容量实验发现，raw row count 并不是正确的容量变量。

更合理的层级是：

\[
\text{raw rows}
\rightarrow
\text{independent statistical cells}
\rightarrow
\text{robust states per cell}
\rightarrow
\text{effective payload}
\]

增加同一 cell 内的 replicate 往往主要提高统计稳定性，而不会线性增加离散状态数。

因此项目同时记录：

- `robust bits / independent cell`；
- `independent cells / carrier collection`；
- `bits / visible row`（仅作为辅助效率指标）。

---

## 9. 联合容量与密码本成本

对于第 j 个 cell：

\[
C_j=H(F_j\mid N_j)
\]

总有效容量更接近：

\[
C_{total}\approx\sum_j C_j-L(K)-R_{ECC}
\]

其中：

- \(L(K)\)：内部 feature map / 密码本开销；
- \(R_{ECC}\)：鲁棒解码所需纠错冗余。

如果多个通道并不独立，则必须扣除互信息：

\[
H(S_1,S_2)=H(S_1)+H(S_2)-I(S_1;S_2)
\]

因此下一阶段重点是寻找：

> **低互信息 + 高鲁棒性 + 低可检测性** 的统计特征组合。

---

## 10. Dirty-channel 假设

核心假设仍然是：

> 当背景本身具有较高的异常率、量化误差、缺失、漂移和非平稳性时，额外施加少量结构的边际可检测性可能下降。

形式上比较：

\[
P_{natural\ dirty}(X)
\]

与

\[
P_{structured\ dirty}(X)
\]

但这只是待验证假设。

如果人为结构在导数、残差、跨 cell 或跨图联合分布中形成过强规律，即使 raw data 很脏，也可能更容易被检测。

---

## 11. 四个核心指标

### Capacity

自然性约束下可稳定控制的联合状态数。

### Codebook overhead

\[
\frac{L(K)}{C_{payload}}
\]

密码本越依赖逐 cell 特例，收益越差。

### Detectability

训练不知道内部规则的独立检测器区分随机/自然分组与结构化分组。

AUC 接近 0.5 只说明当前 detector 失败，不代表信息论意义上的不可检测。

### Robustness

测试：

- 缺失样本；
- bootstrap / resampling；
- 小幅测量扰动；
- rounding 变化；
- bin 边界变化；
- 数据顺序变化（对依赖顺序的特征）。

---

## 12. 当前研究边界

当前阶段只研究合成 benchmark 上的统计自由度与可证伪性：

- 不把组合数学上限直接当作可用容量；
- 不用真实科研论文构造伪造实验数据；
- 不把某个固定 feature 当作天然最优通道；
- 不把内部密码本设计成逐点 mapping；
- 不在容量评估中忽略 ECC、鲁棒性和 detector 成本。

当前下一步：建立候选统计特征矩阵，测量 feature independence、鲁棒性和自适应 feature-map 的净容量。
