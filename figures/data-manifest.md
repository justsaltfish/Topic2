# 核验图件数据清单

所有数据为真实历史产物的只读重分析，没有模拟数据。核验日期：2026-10-07。

| Figure | 数据 | 来源及范围 | 脚本 | 输出 |
|---|---|---|---|---|
| 1A–C | data/verified/gc_histograms.csv、kmer_correlations.csv、kmer_frequencies.csv | 真实参照 9000 条及 Ara/Maize 目录 epoch2000 各 9000 条 | figures/plot_verified_results.py | figures/results/figure1_sequence_quality.png / .svg |
| 1D | data/verified/motif_position_weights.csv | 真实与两生成集合既有 FIMO 命中的中心位置重计数 | 同上 | 同上 |
| 1E–F | data/verified/internal_diversity.csv、sequence_quality_summary.csv | 按位 Hamming 的 100000 对抽样、同聚物重计数 | 同上 | 同上 |
| 2A–B | data/verified/ara_guidance_methods_recomputed.csv、ara_guidance_paired_scores.csv | Ara DOWN，5 方法 × 各100对 | 同上 | figures/results/figure2_guided_generation.png / .svg |
| 2C–F | data/verified/maize_guided_sweep_recomputed.csv、maize_guided_observations.csv、homopolymer_sensitivity.csv | Maize 40 epoch × 3 模式 × 500条 | 同上 | 同上 |

图件输入与输出 SHA256 登记于 data/manifest.json。原始核验范围见 data/verified/source_manifest.csv。正文主图的 epoch2000 来自实际已有生成与引导资产；并非替用户确认最终生产权重。e1500 为历史 strict 阈值下达标数量最高的探索性例子，也不是自动选择的最终 checkpoint。

图1真实参照由完整数据来源抽取，并非独立测试集。图2C 的不同阈值是事后评价；图2F 的同聚物长度10/20只作描述性敏感性分析，不是已经冻结的生物学质量门槛。图中序列数不能作为独立种子重复数。
