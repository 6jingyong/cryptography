# How it works

这份文档不从公式开始，而是从一个完整例子解释整个系统。

---

# 1. 假设我们有一个 payload

例如：

```text
101100...
```

benchmark 里，它通常是一段 deterministic synthetic high-entropy bytes。

第一步不是直接把 bit 写进某个 y 值，而是先把 bit 打包成 q-ary symbols。

如果 `q=8`，每个 symbol 有 8 种状态，可以表示 3 bit；  
如果 `q=16`，每个 symbol 有 16 种状态，可以表示 4 bit。

---

# 2. 为什么不能直接改 y？

因为一条数值曲线通常有自己的宏观规律：

```text
周期
单调
饱和
高斯峰
对称
```

如果直接随便改 y，宏观形状会被破坏。

所以我们把一条曲线拆成：

\[
\text{macro}+\text{free}
\]

数学上：

\[
z=B(x)\beta+U(x)c
\]

其中：

```text
B(x)β = 必须保留的宏观结构
U(x)c = 可以调节的自由方向
```

真正承载 q-ary symbol 的是 \(c\)，而不是直接改原始 y。

---

# 3. 一个 periodic 例子

假设宏观曲线应该满足：

\[
y=a_0+a_1\sin\omega x+a_2\cos\omega x+a_3\sin2\omega x+a_4\cos2\omega x
\]

那么 protected basis 是：

```text
1
sin(wx)
cos(wx)
sin(2wx)
cos(2wx)
```

这些方向负责维持：

```text
平均值
主周期
相位
二次谐波
```

然后我们在它们的正交补空间里找 \(U\)。

当 q-ary codeword 变化时，只改变 \(Uc\)。

---

# 4. 为什么还要 shaping？

同一个 payload block 并不一定只有一个合法 codeword。

如果留出一个 shaping symbol，就可以有多个等价候选。

encoder 会选一个：

```text
扰动能量更低
二阶差分更小
局部结构更平滑
```

的 codeword。

所以 shaping 的目标不是增加 payload，而是降低结构代价。

---

# 5. 为什么还要 ECC？

因为公开数据可能经历：

```text
rounding
re-quantization
数值误差
```

所以 decoded symbol 可能有少量判错。

当前用 q-ary Hamming：

\[
[q+1,q-1,3]_q
\]

每个 block 可以纠正一个 symbol error。

---

# 6. 为什么 q 不固定？

不同 table 能承受的 residual 不一样。

因此现在不是：

```text
整个 package 都用 q=8
```

而是：

```text
table A -> q8
table B -> q16
table C -> q32
```

这就是 adaptive-q。

---

# 7. Codebook A

Codebook A 是“解释规则”。

它告诉 decoder：

```text
这张表是什么 family
在哪个 transform domain 解码
q 是多少
block 几个点
publication step 多大
ECC 怎么解释
```

它本质上是 decoder protocol。

---

# 8. Codebook B

Codebook B 完全不是另一套 decoder。

它只负责：

> 从很多候选里找出哪些最值得试。

假设一个 package 有 12 张表：

```text
affine/q8
affine/q16
affine/q32
periodic/q8
periodic/q16
periodic/q32
...
```

这个结构序列本身就是 fingerprint。

接收端只需要问：

```text
这个候选和预期结构像不像？
```

然后排一个 Top-K。

---

# 9. 为什么误召回没关系？

因为 locator 不是 verifier。

一个错误 candidate 可能：

```text
看起来很像
但是 decode 不出来
```

或者：

```text
可以 decode 出某些 bytes
但 integrity check 不通过
```

都可以直接 reject。

所以：

\[
\boxed{
\text{retrieval error}
\neq
\text{protocol failure}
}
\]

真正重要的是 target 是否稳定进入 Top-K，而不是 Top-K 里是否只有 target。

---

# 10. 为什么表格顺序不重要？

顺序不应该进入密码本。

如果文件重新排序，只要公开结构还能知道每张表是谁，就先 canonicalize，再 decode。

所以第二本码本更准确地写成：

\[
F=\{(\ell_i,v_i)\}
\]

其中：

```text
label = 公开可恢复身份
value = 预共享结构值
```

---

# 11. 发布精度为什么重要？

q-ary state 最终靠 coefficient spacing 区分。

设：

```text
symbol spacing = Δ
final publication quantization = δ
```

真正决定能不能 decode 的核心变量之一是：

\[
\frac{\Delta}{\delta}
\]

如果 publication 后又被粗粒度 rounding，不同 q-state 就可能混在一起。

---

# 12. publication guard mode

例如：

```text
high_density
guarded_1p5x
guarded_1p75x
guarded_3x
```

本质上是在做：

```text
更大 spacing
<-> 更低容量
<-> 更强二次量化鲁棒性
```

---

# 13. 最后的 verifier

整个系统最后必须有严格 verifier。

例如：

```text
length check
version check
integrity tag
hash check
```

最终 pipeline 是：

```text
candidate
  ↓
locator score
  ↓
Top-K
  ↓
canonicalize
  ↓
decode
  ↓
verify
  ↓
accept / reject
```

---

# 14. 当前最重要的问题

下一步不再只是继续提高 q，而是研究：

\[
y=f(x)+\epsilon
\]

其中 \(\epsilon\) 可以是：

```text
Gaussian noise
heteroscedastic noise
AR(1)
batch drift
outlier mixture
```

然后问：

> 加入 carrier 后，residual 的统计性质是否仍然和原模型兼容？
