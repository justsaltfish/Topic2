# 图件数据清单

当前数据状态在 data/manifest.json 中机器记录。所有 Fig. 1/2 面板均尚未具备最终核实数据或图件。

| 数据 | 状态 | 可以用于最终绘图？ |
|---|---|---|
| data/history/unguided_epoch_summary.csv | 索引历史摘要、按预测指标筛选 | 否，未包含序列质量最优结论 |
| data/history/predictor_pcc.csv | 索引历史摘要 | 否，需匹配实际 checkpoint 并核对原始测试结果 |
| data/history/guided_sweep_summary.csv | 索引历史摘要 | 否，需确认模型、阈值和统一统计口径 |
| data/history/threshold_review.csv | 索引历史摘要，分母缺失 | 否，只作历史核对线索 |
| data/templates/*.csv | 只有字段，无数据行 | 否 |

未来每份最终图件数据须登记来源文件、哈希、生成脚本、实验 ID、过滤规则及 reviewer。不得把历史摘要的 status 改为 verified 后直接当作原始数据；需登记实际核验材料。
