# 补充表字段定义

全部模板位于 data/templates/，仅含列名。空值不表示零；尚未确认的数值不得补零。

| 表格 | 内容 | 数据模板 | 指标与规则 |
|---|---|---|---|
| S1 | 数据 / 模型 / 引导配置 | run_metadata.csv | 每个 run 唯一；模型和数据有哈希；注明配对组 |
| S2 | 无引导序列质量 | quality_summary.csv | 真实参照、全样本数、指标定义和独立重复 |
| S3 | 引导预测统计 | activity_summary.csv | mode × condition × population；计数和分母完整 |
| S4 | 过滤前后质量与活性 | quality_summary.csv、activity_summary.csv | population 用 all_generated / quality_pass；报告保留率 |
| S5 | 参数扫描 | 上述三个汇总模板 | 固定其余条件，阈值相同后比较 |

sequence_predictions.csv 用于逐序列核对与配对统计；kmer_frequencies.csv 和 motif_hits.csv 提供组成与扫描来源。motif 坐标必须在元数据中冻结为 0-based 半开区间或 1-based 闭区间，不能混用。

value 的实际统计含义由 metric_definition 或 metric 说明；均值、标准差、中位数和分位数用独立 metric 行保存。置信区间只在实际计算并记录方法后填写。无独立重复时不能把序列间离散程度当成跨运行误差线。source_file 使用仓库相对路径或登记的公开标识，不嵌入服务器身份。

所有最终数据必须关联 run_id 和来源，status=verified 只用于原始产物与分析代码已经核对的记录。历史摘要保持其原始状态。
