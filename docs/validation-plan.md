# Validation Plan v1.0

## 目标

验证当前 synthetic 双码本架构是否同时满足：

1. published package 可以 self-contained decode；
2. adaptive q 的选择与 residual budget 一致；
3. locator 能把目标稳定推进 Top-K；
4. strict verifier 能拒绝错误候选；
5. 所有 metadata / codebook overhead 被计入净效率。

---

## A. Carrier 层

### A1. Exact recovery

必须报告：

- payload SHA-256；
- decoded SHA-256；
- exact equality；
- raw q-ary symbol error；
- >1 symbol-error blocks。

### A2. Publication transforms

逐项测试：

- decimal / significant-digit quantization；
- `y -> ay+b`；
- log-domain relative precision；
- row sorting；
- column reorder；
- table split / merge。

只有 decoder 只使用 published package + manifest 时才算有效。

### A3. Structure distortion

按 family 使用合适指标：

- NRMSE；
- macro coefficient drift；
- correlation drift；
- absolute second-difference energy；
- spectral residual energy。

注意：affine baseline 的二阶差分为 0，因此不能使用 naive roughness ratio。

---

## B. Adaptive-q 层

候选：

\[
q\in\{8,16,32\}
\]

每个 table 的 calibration 必须：

- 使用独立 synthetic payload；
- publication 后 exact decode；
- 不出现超过 ECC 能力的 block；
- 满足 table residual budget。

记录 q frontier：

\[
D_{\max}\rightarrow q^*
\]

并在不同 seed / channel count / family 下重复。

---

## C. Package 层

报告：

- tables；
- y-series / table；
- total published rows；
- total numeric values；
- gross bit/value；
- net bit/row；
- manifest bytes；
- padding waste。

至少保留一个大规模 benchmark，例如 23.4 MB synthetic target-size test。

---

## D. Locator 层

### D1. Corpus size

至少：

- 10k；
- 100k；
- 1M descriptor-only synthetic candidates。

### D2. Hard decoys

加入：

- random decoys；
- shared-q decoys；
- shared-family decoys；
- 25% / 50% / 75% structural-overlap near-decoys。

### D3. Missing / corrupted fingerprint

测试：

- substitution；
- missing positions；
- reordered figures/tables；
- duplicated positions。

核心指标：

- Recall@5/20/50/100；
- median target rank；
- P90/P99 rank；
- expected verification attempts。

不要求 locator false positive 接近 0。

---

## E. Strict verifier

分别测试：

- wrong locator key；
- right locator / wrong interpretation；
- malformed package；
- valid-looking decoy；
- correct package。

指标：

- false accept；
- false reject；
- attempts until accept。

最终真假判断只属于 verifier，不属于 locator。

---

## F. Detectability

仍保留：

- generic detector；
- codebook-aware/oracle detector。

但其解释从“唯一优化目标”改成：

> 衡量结构 recognizability，以及这种 recognizability 是否与 locator utility 形成 trade-off。

不能把 AUC≈0.5 解释成“不可检测”。

---

## G. 安全与研究边界

所有 corpus、payload、paper-style artifacts 必须是 synthetic/mock。

不对真实论文、真实 secrets、真实模型权重进行隐藏、检索或传输实验。
