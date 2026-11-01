# Quick Start

如果你只想知道“这个项目到底在干什么”，不要先跑完整 benchmark。

先跑：

```bash
python -m pip install -r requirements.txt
python demo.py
```

默认 demo 只使用 synthetic payload，并把结果写到：

```text
demo_output/
```

你会看到类似这样的流程：

```text
[1/6] Loading the adaptive-q synthetic engine
[2/6] Encoding ... synthetic bytes into a 12-table package
[3/6] Building Codebook-B locator fingerprint ...
[4/6] Locator target rank: ...
[5/6] Strict verifier: best decoy=REJECT, target=ACCEPT
[6/6] Published package decode + SHA-256: PASS
```

这里最值得看的不是某一个具体 rank，而是整个闭环：

```text
synthetic payload
  -> numeric package
  -> locator
  -> candidate verification
  -> published-data decoder
  -> SHA-256 PASS
```

## Demo 会生成什么？

### `curve_before_after.svg`

一条 periodic synthetic curve 的：

```text
baseline
vs
published carrier
```

用来直观看 protected macro structure 和 carrier residual 的关系。

### `demo_manifest_summary.json`

只保留最容易阅读的 package 结构：

```json
{
  "table_id": 4,
  "family": "periodic",
  "q": 16,
  "transform": "identity"
}
```

你可以直接看到不同 table 如何使用不同 q。

### `demo_summary.json`

记录：

- q distribution；
- published rows；
- locator target rank；
- best decoy 是否被拒绝；
- target 是否被接受；
- 输入/输出 SHA-256；
- exact recovery。

## 为什么 demo 默认比 benchmark 快？

正式 benchmark 的 adaptive-q calibration 会使用更大的 calibration sample。

Quick Start 为了让第一次运行更轻量，会临时使用较小的 calibration：

```text
quick demo != benchmark result
```

它的目的只是展示协议闭环。

如果希望使用完整 calibration：

```bash
python demo.py --full-calibration
```

## 可以改哪些 demo 参数？

例如：

```bash
python demo.py \
  --payload-bytes 8192 \
  --channels 8 \
  --candidates 5000
```

注意：demo 仍然只生成内部 synthetic payload，不接受任意 payload 文件。

## 看懂 demo 以后读什么？

推荐顺序：

1. `README.md` — 先理解项目是什么；
2. `docs/how-it-works.md` — 从头走完整协议；
3. `docs/architecture-overview.md` — 看系统分层；
4. `docs/theory-framework.md` — 再看数学抽象；
5. `docs/validation-plan.md` — 看哪些结论已经验证、哪些还没有。
