# 160 bp 增强子生成：论文计算部分

本仓库整理用户已确认的两节 Results：DDPM 生成质量，以及预测器引导的定向生成。两节正文、配套 Methods 和图注已根据现存服务器产物进行核验和重分析。

**当前状态：已有真实数值与图件的核验稿，最终模型、阈值和投稿要求待作者确认。** 不再使用空白结果槽位；无法恢复的历史信息以限制及待确认项说明，不补造。

## 最新：统一协议三面板图

[同协议比较图与完整数据](results/00_model_selection/unified_comparison.md)：已补齐UViT-v2 config4，统一每候选1000条、NG真实参照与JASPAR2024扫描。DDPM与DiT的6-mer相关性接近，DDPM motif位置WD较低；UViT位置WD更低，但6-mer/GC偏差更大。图展示实际权衡，不宣称DDPM所有指标最佳。

## 模型与权重选择图（2026-10-08）

[模型选择结果图与核验说明](results/00_model_selection/README.md)：已读取PPT第8–15页，重算DDPM/DiT 80个checkpoint。已补入**UViT-v1/v2**：2024批次WD最佳是UViT-v2 config4 epoch1800（0.1404）。旧final DDPM1800仅是6-mer PCC最高候选，WD并非最低；DiT与其他DDPM批次各有优势。**最终模型和权重未确定**，不预设DDPM胜出；10/1引导结果仍属于epoch2000。

## 审阅入口

- [合并中文核验稿](manuscript/computational_sections_zh.md)及 [Word 核验稿](manuscript/computational_sections_zh.docx)，Word 已嵌入两张实际结果图。
- [结果部分一](results/01_sequence_quality/README.md)：正文、Figure 1、组成与多样性数据。
- [结果部分二](results/02_guided_generation/README.md)：正文、Figure 2、引导与阈值数据。
- [对应方法](chapters/03_methods_computational.md)与[补充材料入口](supplementary/README.md)。
- [核验报告](evidence/verification-report.md)、[来源清单](data/verified/source_manifest.csv)、[未解决项目](evidence/missing-items.md)与[作者决策](evidence/author-decisions.md)。

## 预测器核验追加（2026-10-08）

[八个预测器的训练与权重核验](evidence/predictor-training-audit.md)：数据划分、随机种子、最佳轮次、测试PCC及权重SHA256。Ara UP的0.7529来自旧日志；随后作者授权重建测试集，当前固定最佳权重整体PCC为**0.7507**，不能将新旧两个口径混用。

[固定权重测试PCC复验](evidence/predictor-test-recheck.md)：八个预测器已完成CPU推理；七个新版预测器的整体PCC四位小数与历史表一致，Ara UP在作者确认的旧代码重建测试集上为**0.7507**。重建测试成员及哈希已归档，原始历史成员未恢复。

## 本次实际核验

读取 224 份代码、配置、日志、序列或预测表。对两个 DDPM 实例的 80 份无引导 FASTA 核对长度和字符，共 720,000 条；对玉米扫描 120 组、60,000 条逐样本记录重算均值、最大值和四套阈值计数；对 Ara DOWN 五种方法各100对重算预测变化。重新计算两组 epoch2000 生成序列与等量真实参照的 GC、k-mer、完全匹配、同聚物与内部 Hamming 分布，并重计数四份已有 FIMO 文件。FIMO XML 的版本和设置一致。

数值重算不等同新的模型实验。此前归档重分析没有训练、采样、加载 checkpoint 推理、运行 FIMO、提交作业或写入服务器；10月8日追加执行了用户授权的CPU预测器复验；随后统一质量比较还执行了新的CPU FIMO --text扫描，未写服务器文件，见上方对应报告。现存 checkpoint 的哈希用于识别当前文件，不能证明其历史内容未变化。

## 需要保留的边界

DDPM-A 与 DDPM-M 是两个既有训练实例的标识；两个实例从同一完整序列来源分别划分，未按物种标签过滤或作条件生成。真实质量参照来自模型数据来源，不能当作独立测试集。Ara 引导方法与 Maize checkpoint 扫描分开报告。每组100或500条序列不是多种子重复；指导模型与评分模型相同。

7月8日当前完整预测表与旧摘要不一致。旧筛选档确有602条唯一双达标序列，但不能和当前6000条完整预测表混成同一版本；索引中的601也未得到一致来源。见[版本冲突记录](evidence/conflicts.md)。

Maize e1500 BOTH 的 strict 双达标为359/500，但有373/500条含至少20 bp同聚物；同时双达标且不含此类同聚物仅76条。这是描述性敏感性结果，最终质量门槛仍需确认。

## 文件与复现

`data/verified/` 保存来源哈希、观察值及重算表；不包含原始DNA序列或完整标签表。`data/history/` 保留起稿时的索引摘要，不能覆盖新的逐行核验。`data/templates/` 为未来采集字段，不作为现有结果。

```bash
python3 -m pip install -r requirements-analysis.txt
python3 scripts/check_result_tables.py
python3 figures/plot_verified_results.py
python3 scripts/export_docx.py
python3 scripts/register_artifacts.py
python3 scripts/validate_package.py
python3 scripts/validate_package.py --submission
```

若作者拥有本次只读导出的原始 JSON，可按[输入格式说明](evidence/reanalysis-inputs.md)运行 `scripts/reanalyse_archive.py --source-dir <导出目录>`。脚本不连接服务器。图件输出450 DPI PNG与SVG；Word采用黑色黑体标题、宋体正文、Times New Roman英文、1.5倍行距、首行缩进，无行号。

`--submission` 当前会因作者决策、历史版本和缺少部分验证材料而失败。目标期刊、语言、署名及声明尚未确认；本仓库不是完整论文，也没有添加未经作者确认的LICENSE。另一篇论文只用于写作组织方式参考，其原稿及 GAN/3020 bp 数值未上传。

## 后续来源追溯追加

[模型与序列来源追溯](evidence/downstream-lineage.md)确认：SHAP61条来自DDPM-A旧BOTH档；8/4Maize扫描用DDPM-M；10/1补验使用与A/M参数内容都不同的旧版final epoch2000。多物种插入共用1000条背景，但其最初生成来源仍未解决。主文目前报告A/M历史分析，新补验没有自动并入最终模型或主结果。

## 生成模型比较页核验

[原图来源与绘图问题](evidence/generator-comparison-slide-audit.md)：两图DDPM均是DDPM-M；左图UViT为旧config1，右图为v2 config4（WD最佳epoch1800）。左图Real WD参照线误读为1.2117，不能直接用于投稿。曲线CSV及来源哈希已归档。
