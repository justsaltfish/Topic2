# Supplementary Information：计算部分

| 表 | 内容 | 已有真实数据 |
|---|---|---|
| S1 | 实验实例、配置、预测器和权重来源 | tables/table_s1_study_registry.csv、data/verified/checkpoint_inventory.csv、predictor_test_log_verified.csv、fimo_scan_metadata.csv |
| S2 | 序列质量、k-mer、motif及多样性 | data/verified/sequence_quality_summary.csv、kmer_correlations.csv、motif_profile_correlations.csv、motif_position_wd.csv、internal_diversity.csv |
| S3 | Ara方法比较与逐记录变化 | data/verified/ara_guidance_methods_recomputed.csv、ara_guidance_paired_scores.csv |
| S4 | Maize阈值和同聚物敏感性 | data/verified/maize_guided_sweep_recomputed.csv、homopolymer_sensitivity.csv |
| S5 | 完整checkpoint与来源核验 | data/verified/generated_file_inventory.csv、ara_ddpm_wd_archive.csv、source_manifest.csv |
| 独立记录 | 7/8版本冲突 | data/verified/july08_version_conflict.csv、evidence/conflicts.md |

公开表不含原始DNA，逐样本预测仅保留分数和质量指标。S5旧WD轨迹是已读取的评价表，只有Ara500/2000的位置WD在本次按原FIMO独立重算；不把全部40行都标成FIMO重计算。预测器测试PCC来自日志，完整数据的PCC来自重算，二者分开保存。
