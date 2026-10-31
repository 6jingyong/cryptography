# q=5 block shaping：借用 Wet Paper / STC 的最小改造

这份说明只记录当前编码层改造。统计载体仍然完全使用合成数据 benchmark。

## 只借两个思想

### 1. 允许某个 cell / symbol 组合不可用

不再要求每个 cell 都必须以合理代价支持所有 q=5 symbol。

对第 `j` 个 cell 和符号 `a`：

- `rho[j,a] < +inf`：至少存在一个可接受的统计实现；
- `rho[j,a] = +inf`：这个选择直接视为不可用。

encoder 可以绕开不可用选择，而不是为了完成逐 cell 映射强行制造高代价状态。

### 2. 消息约束整个 block，而不是逐 cell 机械指定

外层继续使用 q=5 Hamming `[6,4,3]_5`。

原始结构：

- `4P0S`：4 个 payload symbol + 2 个 parity；
- 一条 4-symbol payload 对应唯一一个 6-symbol codeword。

改造结构：

- `3P1S`：3 个 payload symbol + 1 个 shaping symbol + 2 个 parity；
- shaping symbol 不承载 payload；
- 同一条 3-symbol payload 对应 5 个合法 Hamming codeword；
- encoder 在 5 个合法 codeword 中选择总代价最低的一个。

Hamming distance 不变，因此 shaping 不会牺牲外层单-symbol纠错能力；它牺牲的是 payload rate。

## 统计 symbol

当前每个 cell 的统计联合状态固定为：

`(center_state, logvar_state, skew_state) in {0,1,2}^3`

共 27 个联合状态。

通过全局固定映射变成 q=5 symbol：

`symbol = (4*center + 4*logvar + 3*skew + 1) mod 5`

这张表是全局常数，不保存逐 cell alphabet。

## 代价函数

每个候选子集都有 local cost，包含：

- center displacement；
- log-variance displacement；
- skew displacement；
- 可选的 quantization-boundary depth 奖励。

6-cell block 还加入相邻中心线的 curve cost：

`J = sum_j rho_local(j) + lambda * sum_j rho_curve(j-1,j)`

因此最终不是每个 cell 独立贪心，而是对整个 block 做动态规划。

未来可以继续加入二阶 curvature transition cost。

## 为什么 shaping 有用

如果 payload 对应唯一 codeword，那么一个 cell 上出现高代价 / 不可用 symbol，就会把整个 block 卡住。

留一个 shaping 自由度以后，同一 payload 有 5 种合法表示。

encoder 可以在不改变 payload、不改变 Hamming 校验结构的情况下，主动避开局部困难位置。

v9 synthetic benchmark 显示，这主要改善：

- construction feasibility；
- total statistical distortion；
- center-line roughness。

它**不会替代 ECC**；删点后 symbol 翻转仍需要 Hamming 或更强纠错处理。

## 当前公式

对 block 的 q=5 symbol 序列 `z=(z_1,...,z_6)`：

`min_z [sum_j rho[j,z_j] + curve_cost(z)]`

subject to：

`z belongs to the legal Hamming/coset family for the payload`.

不可用 cell/symbol 直接令：

`rho[j,a] = +infinity`.

## 当前不解决的问题

- decoder 不依赖 parent-bin reference 的 self-contained 状态定义；
- 每个 block 在 `4P0S` / `3P1S` 之间自适应切换时的 mode signaling；
- 整 cell 丢失 / 插入导致的同步问题；
- 真实科研数据；
- 不可检测或安全性声明。

这些问题和 block shaping 分开处理。
