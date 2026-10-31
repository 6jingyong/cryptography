# 理论框架 v1.0：双码本、adaptive-q 与 package-level carrier

## 1. 核心对象已经改变

早期版本把问题描述为：

> 在脏数据、统计 cell 和派生统计量中，还剩多少可以稳定控制的自由度？

这个问题仍然成立，但已经不是当前架构最简洁的描述。

现在的基本对象是：

\[
\boxed{
\text{structured numeric package}
+
\text{interpretation codebook}
+
\text{locator codebook}
+
\text{strict verifier}
}
\]

项目只在 synthetic / mock 数据上验证容量、纠错、结构保持与检索性质。

---

## 2. 第一层：宏观结构与自由子空间

设某一局部数值 block 在变换域 \(z=g(y)\) 中满足：

\[
z = B(x)\beta + U(x)c
\]

其中：

- \(B(x)\in\mathbb{R}^{n\times r}\)：protected macro basis；
- \(\beta\)：宏观参数；
- \(U(x)\in\mathbb{R}^{n\times d}\)：free basis；
- \(c\)：可控制的离散 carrier coefficients。

理想条件：

\[
B^\top U=0,\qquad U^\top U=I
\]

于是 encoder 改变 \(c\) 时，尽量不改变宏观拟合空间 \(B\beta\)。

常见 protected basis：

### affine

\[
B=[1,x]
\]

### periodic / harmonic

\[
B=[1,\sin\omega x,\cos\omega x,\sin2\omega x,\cos2\omega x]
\]

### Gaussian peak（log-domain）

若：

\[
y=A\exp\left[-\frac{(x-\mu)^2}{2\sigma^2}\right]
\]

则：

\[
\log y=a+bx+cx^2
\]

因此可以在 `log(y)` 中保护：

\[
B=[1,x,x^2]
\]

### saturation

可使用：

\[
B=[1,\exp(-t/\tau)]
\]

宏观 family 不决定唯一 carrier；真正决定容量的是 protected rank、publication precision 与允许的 residual budget。

---

## 3. q-ary block code

当前使用：

\[
q=2^m
\]

以及 q-ary Hamming：

\[
[q+1,q-1,3]_q
\]

保留 \(s\) 个 information symbols 作为 shaping freedom 时：

\[
R(q,s)
=
\frac{q-1-s}{n_{\text{published}}}\log_2q
\]

当前主要研究：

\[
q\in\{8,16,32\},\qquad s=1
\]

shaping 的目标不是提高纠错距离，而是在同一个 payload 对应的多个合法 codeword 中选择结构代价较低者。

---

## 4. q 是 operating point，不是协议常数

V10/V11 固定 q=8。

V12 以后，q 的角色改成：

\[
q_j
=
\max\left\{
q:
\begin{array}{l}
\text{publication 后可以 exact decode}\\
D_j(q)\le D_{j,\max}
\end{array}
\right\}
\]

其中 \(D_j\) 是第 \(j\) 张 table 的结构失真指标。

当前 synthetic benchmark 的经验前沿约为：

- <0.5% residual：q=8；
- ~1–1.5%：q=16；
- ~2.5–3.5%：q=32。

该阈值依赖：

- transform；
- publication quantization；
- block geometry；
- shaping；
- 数据生成模型。

不能解释成普适常数。

---

## 5. package-level multiplexing

最终容量单位不是“单张图”，而是整个 package：

\[
C_{\text{package}}
=
\sum_j
\sum_k
N_{jk}R_{jk}
-
L(M)
\]

其中：

- \(j\)：table / figure group；
- \(k\)：同表内 y-series；
- \(N_{jk}\)：published numeric values；
- \(R_{jk}\)：该通道有效 bit/value；
- \(L(M)\)：manifest / metadata 成本。

因此一张 table 可以共享 x 并容纳多条曲线；一个 package 又可以包含大量 table。

V10 已经验证 23.4 MB synthetic payload 的 package-level exact round trip。

---

## 6. 两本码本

### Codebook A：解释码本

Codebook A 回答：

> 这份数字结构应该怎样解释和解码？

它可以包含：

\[
K_A=
\{
\text{family},
\text{transform},
q,
\text{block geometry},
\Delta,
\text{ECC},
\text{ordering}
\}
\]

其原则仍然是：

\[
L(K_A)\ll L(C_{\text{payload}})
\]

它不应该成为逐点 assignment 表。

当前实现中，Codebook A 的大部分信息可以由 compact manifest 表示；部分结构也可以从 x / figure family 推导。

### Codebook B：locator 码本

Codebook B 回答：

> 在大量候选 package 中，哪些值得尝试严格解码？

它不负责最终认证。

定义结构描述符：

\[
d_j=
(\text{family}_j,q_j,\text{transform}_j,\ldots)
\]

目标 package 形成短序列：

\[
F=(d_1,d_2,\ldots,d_L)
\]

接收端预共享或预先知道 \(F\) 的粗粒度模式，然后对候选做相似度排名。

因此允许：

\[
\text{false positive}>0
\]

只要：

\[
P(\text{target rank}\le K)
\]

足够高，且后续验证成本可接受。

---

## 7. 检索与认证必须分离

当前协议模型明确分成：

### Stage 1 — retrieval

输出：

\[
\operatorname{TopK}(F_{\text{candidate}},F_{\text{target}})
\]

优化：

- Recall@K；
- target rank；
- expected candidate attempts。

### Stage 2 — interpretation

对候选尝试：

\[
D
\rightarrow
\hat C
\]

错误候选可以解码失败，也可以产生无意义输出。

### Stage 3 — strict verification

最终：

\[
V(\hat C,K)=\{0,1\}
\]

synthetic benchmark 可以使用：

- length / format check；
- keyed integrity tag；
- SHA-256 equality。

因此：

\[
\boxed{
\text{recognizability}
\neq
\text{interpretability}
\neq
\text{verified recovery}
}
\]

---

## 8. 对规则性 / detectability 的新解释

旧目标倾向：

\[
\text{AUC}\rightarrow0.5
\]

但 V11 显示，若 detector 知道 q lattice / Hamming 规则，结构可以非常容易识别。

这并不自动意味着架构失效。

如果威胁模型允许第二本 locator 码本，那么：

\[
\text{structural regularity}
\]

既可能是公开 recognizability 的来源，也可能成为接收端检索目标的信号。

因此当前不再把“低 detectability”设为唯一目标。

更完整的 trade-off 是：

\[
\max
\left(
C_{\text{net}},
R@K,
\text{robustness}
\right)
\]

subject to：

\[
\text{macro distortion}\le D_{\max}
\]

和明确的安全/研究边界。

---

## 9. V14 的集成结果

一个实际生成的 12-table adaptive-q synthetic package：

- q schedule：8/16/32 按 family 分层；
- payload：128 KiB；
- published package + manifest self-contained decode；
- SHA-256 exact match。

将其结构指纹放入 10,000 个 synthetic candidates：

- target extraction error：20%；
- 1% hard near-decoys；
- near-decoy 复制 50% 指纹位置；
- 200 个 corpus seeds。

q-only locator：

- P(Top-20)=58.0%；
- P(Top-100)=83.5%；
- mean attempts≈99.8。

joint `(family,q)` locator：

- P(Top-20)=93.5%；
- P(Top-50)=98.5%；
- P(Top-100)=98.5%；
- median rank=1；
- mean attempts≈5.6。

因此第二码本应该描述联合结构，而不是只描述 q schedule。

---

## 10. 当前容量与检索 KPI

### Carrier

- exact recovery；
- raw symbol error；
- bit/value；
- bit/row；
- package rows；
- manifest overhead；
- NRMSE；
- macro drift；
- cross-series relationship drift。

### Locator

- Recall@K；
- median / P90 / P99 target rank；
- mean verification attempts；
- 缺失结构位置下的 rank degradation；
- near-decoy robustness。

### Verifier

- strict false accept；
- false reject；
- decoder + integrity success。

---

## 11. 当前边界

本仓库只研究 synthetic / mock benchmark。

不做：

- 真实科研论文造假；
- 真实 secret / model-weight 的隐蔽传输；
- 基于真实公开论文搭建隐蔽检索网络；
- 把 detector 失败解释为绝对不可检测。

当前目标是建立一个可证伪、可重复的**结构化数据自由度 + package 编码 + synthetic locator**实验框架。
