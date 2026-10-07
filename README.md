# 160 bp 增强子生成：论文计算部分

本仓库整理 DDPM 增强子生成与预测器引导的计算部分。用户已确认主文只保留两节 Results；对应方法、图注、补充材料和证据追溯一并组织。

**当前状态：投稿结构工作稿，尚不能直接投稿。** 原始结果表、最终模型、阈值和图件未取得，所有缺口均显式标记。本仓库没有虚构实验数据或占位结果图。

## 阅读入口

- [合并工作稿](manuscript/computational_sections_zh.md)：Results → Methods → Figure legends → 方法参考文献。
- [Word 工作稿](manuscript/computational_sections_zh.docx)：可交给合作者修改；从 Markdown 导出。
- [Result 1](chapters/01_results_sequence_quality.md)：160 bp 生成质量。
- [Result 2](chapters/02_results_guided_generation.md)：UP / DOWN / BOTH 定向生成。
- [Methods](chapters/03_methods_computational.md)：计算方法与评价口径。
- [证据来源](evidence/source-register.md)与[待核对项](evidence/missing-items.md)。
- [图件方案](figures/figure-plan.md)、[表格定义](tables/table-schema.md)与[补充材料](supplementary/README.md)。
- [投稿核对清单](submission/CHECKLIST.md)。

## 数据状态

`data/history/` 仅保存课题索引摘要中的历史统计，并明确标注 `index_summary_not_raw_verified`。这些文件不是原始结果，也不能直接作为最终主文图表的数据。`data/templates/` 是只有列名的采集模板，没有模拟或伪造数值。

本地另一篇论文仅用于组织方式参考；其 GAN、3020 bp 序列、物种和准确率未进入本课题结果。未连接 SLURM 服务器，未提交作业，未上传原始参考稿或模型权重。

## 导出和检查

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/export_docx.py
python3 scripts/validate_package.py
python3 scripts/validate_package.py --submission
```

默认验证检查工作稿一致性；`--submission` 会在缺口、真实数据或最终图件尚未补齐时失败。Word 使用 A4、宋体正文、黑体黑色标题、Times New Roman 英文、1.5 倍行距、首行缩进和页码，不显示行号；目标期刊尚未指定，不能视为已适配某一家期刊。没有添加未经作者确认的 LICENSE。
