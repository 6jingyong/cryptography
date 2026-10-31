# 初版验证计划 v0.1

## 目标

第一版只验证一个问题：

> 给定天然含有多种“脏数据”特征的二维数据，仅通过分组、筛选和统计变换，是否能产生稳定、可控、同时又不明显偏离原分布的派生状态？

不实现完整密码协议。

---

## Phase 0 — 建立合成数据基线

使用 `src/generate_dirty_data.py` 生成固定随机种子的二维数据。

当前 v0 数据包含：

- 平滑潜在趋势；
- 异方差噪声；
- 后半程缓慢仪器漂移；
- 少量异常点；
- 不同小数位舍入；
- 少量缺失元数据；
- 少量重复行；
- 两种 source 标签。

要求：

1. 固定 seed 可完全复现；
2. 所有脏数据机制参数显式记录；
3. 原始 latent function 不作为后续算法输入，只用于评估。

---

## Phase 1 — 建立自然随机分组基线

对同一份数据做大量随机分组。

记录每组：

- x 区间样本数；
- y 算术均值；
- y 几何均值；
- 标准差；
- 分位数；
- skew/kurtosis；
- 相邻区间的离散斜率；
- histogram 的粗粒度统计。

得到：

\[
P_{\text{random}}(F)
\]

作为“没有人为优化时”的特征分布。

---

## Phase 2 — 约束优化分组

只允许改变：

- 每个原始点属于哪一组；
- 可选的分组数量；
- x-bin 的合法划分范围。

禁止：

- 修改原始 x/y；
- 新造数据点；
- 删除数据后不记录；
- 使用 latent function 作为优化器输入。

优化目标先采用多目标形式：

\[
J=
\lambda_1 D_{\text{distribution}}
+\lambda_2 R_{\text{roughness}}
+\lambda_3 E_{\text{target}}
+\lambda_4 I(C;K)
\]

其中：

- `D_distribution`：分组后和总体分布的差异；
- `R_roughness`：几何均值曲线粗糙度；
- `E_target`：目标粗粒度斜率状态的误差；
- `I(C;K)`：两类统计视图之间的依赖程度。

第一版先用简单随机搜索 / simulated annealing / evolutionary search 中的一种，重点是可解释，不追求最优。

---

## Phase 3 — Capacity 曲线

逐渐增加要求控制的状态数。

例如：

- 2-state；
- 4-state；
- 8-state；
- 9-state。

记录：

- 成功率；
- 平均搜索成本；
- distribution distortion；
- curve roughness；
- 最小样本量。

绘制：

\[
\text{payload state count}
\rightarrow
\text{distortion / failure rate}
\]

验证“量化越细，可行解空间越小”的预期。

---

## Phase 4 — Detectability

构造两类样本：

- `random grouping`
- `optimized grouping`

检测器不能直接读取优化器内部状态。

基础检测特征：

- 均值/方差/分位数；
- 末位数字分布；
- slope distribution；
- residual autocorrelation；
- histogram divergence；
- group-to-group similarity；
- x-bin sample count irregularity。

检测器从简单模型开始：

1. Logistic Regression
2. Random Forest
3. Gradient Boosting

主要指标：

- ROC-AUC；
- PR-AUC；
- 交叉 seed 泛化；
- 未见 noise level 泛化。

重要解释：

> AUC ≈ 0.5 只代表当前检测器没有区分能力，不代表信息论意义上的不可检测。

---

## Phase 5 — 背景“脏度”扫描

定义 noise level：

- L0：近乎干净；
- L1：少量测量噪声；
- L2：+ rounding；
- L3：+ outliers；
- L4：+ missingness / duplicates；
- L5：+ drift / heteroskedasticity。

比较每个 level 下：

- capacity；
- distortion；
- detector AUC；
- robustness。

这是项目最核心的一张图：

\[
\text{background dirtiness}
\rightarrow
\text{detectability}
\]

核心假设：

> 背景越脏，某些人为结构的边际可检测性可能下降。

但实验也可能证伪这一假设。

---

## Phase 6 — Robustness

对已经生成的派生结构做常见扰动：

- 随机丢失 1%、5%、10% 数据；
- y 增加小幅测量误差；
- rounding 改变；
- x-bin 边界轻微移动；
- bootstrap resampling。

比较：

- 几何均值变化；
- slope state 稳定率；
- distribution feature 稳定率。

---

## Phase 7 — 多组联合结构

最后才研究多个数据组。

问题：

1. 单组特征熵是多少？
2. 两组联合熵是否接近相加？
3. 不同统计视图之间互信息多大？
4. 多组同时约束后，detectability 是否明显增加？

重点指标：

\[
H(F_1,\ldots,F_r)
\]

和

\[
I(F_i;F_j)
\]

而不是先构造完整通信协议。

---

## 成功标准 v0.1

第一阶段不要求“证明可以隐写”。

满足以下三条，就已经值得继续：

1. 在不修改原始数值的情况下，可以通过分组控制若干粗粒度派生状态；
2. 在合理约束范围内，优化分组与随机分组的传统分布指标差异较小；
3. capacity / detectability / robustness 三者表现出清晰、可重复的 trade-off。

如果做不到，也同样是有价值的负结果。
