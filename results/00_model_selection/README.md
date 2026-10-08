# 生成模型与checkpoint选择：审阅入口

## 最新统一评价图

[DDPM、DiT、UViT同协议三面板图与结果](unified_comparison.md)：所有候选1000条，统一NG参照和JASPAR2024新扫描。DDPM/DiT的6-mer最佳批次接近；DDPM motif位置WD更低，DiT GC略低。UViT位置WD更低，但其6-mer和GC偏差更大。下文为此前历史批次比较，不能与新图混用数值。

本轮检查enhancer.pptx第8–15页，重新分析旧版final DDPM与DiT的80份FASTA（80,000条160bp序列），并对历史候选的原始FIMO结果重计数。**修订结论：不能预设DDPM胜出，也不能将epoch1800认定为WD最佳或已确认最终权重。它是本轮6-mer PCC最高的候选；UViT和其他checkpoint在WD指标上更优。**

[Word审阅稿](model_selection_review_zh.docx)已嵌入两张图及中文核验结论。

## 2026-10-08修订：补入UViT并撤回单一最终选择口径

此前只比较历史DDPM/DiT候选，漏了UViT；将最高6-mer PCC用于推荐“最终主权重”的口径过强，现改为按指标列候选，不默认选择DDPM1800。

### 新增图：包含UViT的WD比较

![含UViT比较](../../figures/model_selection/figure_uvit_comparison.png)

[SVG矢量图](../../figures/model_selection/figure_uvit_comparison.svg)。这是JASPAR2024、真实参照343383命中的历史批次；与下方旧final的JASPAR2022比较分开。包括UViT-v1 config1和UViT-v2 config4，180条checkpoint记录，全部来自已追溯CSV。

| 模型 | WD最小epoch | 最小WD |
|---|---:|---:|
| UViT-v2 config4 | 1800 | **0.1404** |
| DDPM-M | 1750 | 0.2815 |
| UViT-v1 config1 | 1350 | 0.3279 |
| DiT-M | 900 | 0.3818 |
| DNA-diffusion | 350 | 0.5491 |

如果该批次以motif位置WD为主指标，排名第一的是UViT-v2 config4，不能写成DDPM最好。各模型训练和采样设置尚未全部统一，因此这是现存指标比较，不是所有条件一致的最终优劣实验。

### 旧版final中1800也不是WD最小

| 模型／epoch | 位置WD | 6-mer PCC | GC均值 |
|---|---:|---:|---:|
| DiT 100（本轮DiT WD最小） | **0.2875** | 0.0140 | 70.08% |
| DDPM 900（本轮DDPM WD最小） | **0.4223** | 0.9261 | 41.13% |
| DDPM 1800（本轮6-mer PCC最高） | 0.6666 | **0.9724** | 37.53% |

DiT100展示了“位置WD低但序列组成偏离”的实际情况，不能只凭WD认定序列质量最佳；也不能用此例排除其他DiT checkpoint。DDPM1800是多个Pareto候选之一。修订后的checkpoint图加上DiT100，并完整展示其低PCC，未裁掉该点。

历史四模型筛选表中，DiT的JASPAR WD中位数0.8423也低于DDPM的1.0500。上一版TF面板DDPM更低的事实不能覆盖这一结果。

## 结果图

### Figure S1：模型家族筛选

![模型家族比较](../../figures/model_selection/figure_model_family_screening.png)

[SVG矢量图](../../figures/model_selection/figure_model_family_screening.svg)。每个点是一个历史checkpoint，箱体表示checkpoint间四分位范围，数字为中位数，不是独立重复实验的误差条。A为39个TF motif面板的位置WD；B为历史JASPAR面板的位置WD。DDPM的TF位置WD中位数0.9038低于DiT 1.1236、LDM-80 3.5758、LDM-160 2.6940；JASPAR下LDM的WD反而更低，因此不能只保留A来宣称DDPM全面最优。

这些320行历史CSV属于evaluate_effect的另一评价批次，checkpoint与当前固定权重关系尚未全部恢复。图件用于展示历史筛选线索，不与下图FASTA指标拼成统一总分。未对这320项逐一重计数FIMO。

### Figure S2：DDPM与DiT的具体checkpoint比较

![checkpoint比较](../../figures/model_selection/figure_checkpoint_selection.png)

[SVG矢量图](../../figures/model_selection/figure_checkpoint_selection.svg)。每种模型40个checkpoint，每个现存FASTA都是1000条合法160bp序列。A/B分别从原始序列重算6-mer频率PCC和GC分布WD；C为历史JASPAR2022 motif中心位置WD。D–F展示历史候选DDPM1800、DiT1050，以及DDPM900（本轮DDPM位置WD最小）、DDPM2000（10/1引导补验使用）和DiT100（本轮DiT位置WD最小）的权衡。蓝色菱形标出DDPM1800。PCC高为好，两个WD低为好；D为点图且明确显示截取的数值轴。

| 模型／checkpoint | 6-mer PCC ↑ | GC分布WD ↓ | JASPAR位置WD ↓ |
|---|---:|---:|---:|
| DDPM 900 | 0.9261 | 0.0260 | **0.4223** |
| **DDPM 1800** | **0.9724** | 0.0109 | 0.6666 |
| DDPM 2000 | 0.9626 | **0.0046** | 1.8271 |
| DiT 1050 | 0.9358 | 0.0389 | 0.7735 |

DDPM1800的6-mer PCC为80个DDPM/DiT现存批次中的最高值；在这三个指标上同时优于历史选定的DiT1050。它是三指标的Pareto非支配候选之一，但不是唯一候选；DiT其他checkpoint也在Pareto集合中。不增加主观加权总分或虚构显著性。

## 候选权重及结果范围（尚未最终确定）

**DDPM1800的已定位候选权重：**

`topic_all/topic2_Diffusion/DDPM/final/DDPM/params/epoch_1800_params.pkl`

SHA256：`431b3c843a23a041225cd5be770550b7478494ab830d68f6f5162d683d36d1de`。

当前源码、生成日志及FIMO XML将该分支epoch1800关联到现存序列。权重哈希固定当前文件；原始采样缺少seed和不可变权重哈希，不宣称从头可精确复现。

10/1classifier-guidance补验用同分支的**epoch2000**（SHA256 `98dec05764d7f7978111e266fe9cded1f49b0c4204477501f320f30f558c9a1f`）。它的结果不能改标为1800。若论文要求无引导与引导全程同一权重，还缺epoch1800的对应引导对照，不能由本次质量比较替代。

如果作者以6-mer组成接近度为主，DDPM1800值得保留；如果以2024批次的motif位置WD为主，UViT-v2 config4更有依据。两者需要同一数据、采样规模和评价协议的完整多指标对照才能确定主模型；不得用跨批次数字拼总分。UViT-v3尚无对应完整条件比较。

## PPT核验与更正

1. 第15页明确写“DiT选择1050epoch，DDPM选择1800epoch”，恢复了历史选择记录；这与先前Maize/UViT页不同。
2. 第14–15页曲线数值与旧版final DDPM/DiT的JASPAR表吻合，包括DDPM1800命中37327、WD0.6666及DiT1050命中39813、WD0.7735。
3. PPT第14页写“生成2000条”，但两份现存生成代码及本次原始FASTA、FIMO XML确认**每个checkpoint1000条**。新图使用实际数量，不继承错误表述。
4. motif命中总数必须考虑序列数量；真实参照11984条，生成1000条，直接比497706与37327不能解释为motif不足。本次若报告命中密度，需除以各自序列数：真实41.531、DDPM1800 37.327、DiT1050 39.813次/序列。
5. 第8–11页包含6-mer、GC及Inner/Outer曲线，比较维度可复用，但原始作图数值表和具体距离定义尚未完整恢复。本次新图重新读取FASTA，不从截图估读数字，也不将这些图原样视为逐点复验完成。
6. 第15页重复序列截图没有可追溯的文件名、checkpoint或样本总体。不能以这张截图认定DiT1050发生整体模式崩塌：现存1050的1000条序列全部唯一，只有1条出现至少20bp的周期2重复。截图可能来自其他批次，来源待确认。

## 评价限制

真实参照为当前NG CSV中11984条合法唯一序列，是训练数据来源，不是独立测试集。6-mer统计正向链重叠窗口、完整4096词表；GC WD按每序列GC比例的经验分布计算。历史JASPAR WD按位置计数且每位置加1伪计数；真实11984条与生成1000条的伪计数相对权重不同，保留旧实现用于追溯，不能宣称完全消除了样本量效应。

80个checkpoint不是80次独立训练；每个checkpoint只用一份历史采样。新结果是回顾性评价，未证明统计显著性、生物活性或泛化优势。主指标、最低质量门槛及最终单一权重仍须作者确定。本次未训练、重新采样、重新运行FIMO或写入服务器。

## 数据与复现

- [80个checkpoint的质量表](../../data/verified/legacy_full_checkpoint_quality.csv)
- [80份FASTA来源及哈希](../../data/verified/legacy_full_fasta_sources.csv)
- [历史四模型筛选表](../../data/verified/legacy_family_screening.csv)
- [候选序列指标](../../data/verified/legacy_selection_quality.csv)、[逐序列GC与重复指标](../../data/verified/legacy_selection_observations.csv)、[6-mer频率](../../data/verified/legacy_selection_sixmer.csv)
- [评价协议与FASTA哈希](../../data/verified/legacy_selection_quality_protocol.json)、[候选原始FIMO重计数及权重哈希](../../data/verified/legacy_selection_fimo_audit.json)
- [图件脚本](../../figures/plot_model_selection.py)，本地读取上述CSV，输出450 DPI PNG与SVG。

当前论文主文仍保留之前A/M历史分析；本包是待作者确认的旧版final主线选择证据，不自动把其他模型结果改名或合并。

## 私有导出输入与重算命令

来源导出JSON均为数组，每项包含source_relative_path、text、size、sha256。私有输入文件：sources_03.json（含NG CSV）、sources_ppt_legacy.json（历史代码和表）、sources_legacy_all_fasta.json（80份FASTA）、sources_selection_sequences.json（四份候选FASTA）；legacy_selection_fimo_metadata.jsonl为原始FIMO只读重计数结果，每行一个JSON。原始序列和PPT未上传。

```bash
python scripts/reanalyse_legacy_checkpoint_sweep.py --source-dir /path/to/private/exports
python scripts/reanalyse_legacy_candidates.py --source-dir /path/to/private/exports
python scripts/check_legacy_selection_fimo.py --source-dir /path/to/private/exports
python figures/plot_model_selection.py
```

新增数据：[含UViT曲线180行](../../data/verified/uvit_inclusive_model_curves.csv)、[各模型WD最小记录](../../data/verified/uvit_inclusive_wd_best.csv)。
