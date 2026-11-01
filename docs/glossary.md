# Glossary

## carrier
承载离散状态的数值结构。

## payload
希望被编码和恢复的 synthetic high-entropy bytes。

## macro / protected structure
必须尽量保持的宏观规律，例如周期、单调、Gaussian peak、saturation。

## free subspace
在不破坏 protected structure 的前提下可以调节的方向。

## q
离散 symbol 的 alphabet size。当前主要测试 q=8 / 16 / 32。

## q-ary Hamming
当前使用的 ECC：

\[
[q+1,q-1,3]_q
\]

用于纠正一个 symbol error。

## shaping
在多个合法 codeword 中选择结构代价更小的那个。

## Codebook A
解释码本。定义如何从 published numeric package 解码。

## Codebook B
定位码本。定义目标 package 应该具有怎样的粗粒度结构 fingerprint。

## locator
根据 Codebook B 给候选 package 排名。

## verifier
最终 accept/reject 的严格校验器。

## canonicalization
利用公开身份信息把 row reorder / column reorder / table split-merge 恢复到 decoder 需要的规范顺序。

## publication guard
通过扩大 symbol spacing，换取更强的 rounding / re-quantization 鲁棒性。

## residual
从宏观模型中减掉 protected component 后剩下的局部偏差。

## exact recovery
最终 payload byte-for-byte 完全一致，通常通过 SHA-256 equality 验证。
