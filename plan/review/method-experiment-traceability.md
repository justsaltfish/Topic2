# 正文与实际证据对应

| 正文 | 支持文件（data/verified） | 核验等级 | 允许结论 |
|---|---|---|---|
| R1 P1 数据与训练 | verification_report、generated_file_inventory；训练代码/配置源清单 | 原始读取与结构计数 | 无条件序列生成、两个既有实例 |
| R1 P2 GC/k-mer | sequence_quality_summary、kmer_correlations、kmer_frequencies | 序列独立重算 | 组成一致性及偏移 |
| R1 P3 motif | motif_profile_correlations、motif_position_wd、fimo_scan_metadata | 原FIMO重计数 | 类型命中组成与位置分布，不解释为功能验证 |
| R1 P4 多样性 | sequence_quality_observations、internal_diversity | 序列独立重算 | 内部变化与无精确拷贝，不排除近似拷贝 |
| R2 P1 预测器 | predictor_test_log_verified、full_dataset_prediction_pcc | 日志/完整数据重算分开 | 测试相关性限制与全数据口径 |
| R2 P2 Ara方法 | ara_guidance_paired_scores、ara_guidance_methods_recomputed | 逐分数重算 | 单种子、同指导/评分器的预测变化 |
| R2 P3–4 Maize模式与阈值 | maize_guided_observations、maize_guided_sweep_recomputed | 60000条重算 | 方向模式对比和事后阈值敏感性，不推导无引导增益 |
| R2 P5 复杂度 | homopolymer_sensitivity、maize_guided_observations | 逐序列重算 | 同聚物代价与探索性筛选，非最终质量验收 |

每份原始文件的相对路径与SHA在source_manifest.csv。当前文件哈希不是历史文件不变的证明；原始DNA及访问身份不公开。
