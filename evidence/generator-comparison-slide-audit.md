# DDPM/DiT/UViT比较页：原图来源与绘图核验

核验日期2026-10-08。依据用户截图，找到并目视比对两张服务器原图；读取绘图代码与既有CSV，不重新训练、生成或运行FIMO。

## 与epoch 1800的关系

该页并非旧版 `topic_all/topic2_Diffusion/DDPM/final/DDPM` epoch1800的比较图。两侧DDPM和DiT曲线都从 `topic_new26/topic_enhancer/every_species/Maize/35s/down/.../v1/jaspar_comparision_with_real/results.csv`读取，即DDPM-M及其DiT分支。

右图绿色是**UViT-v2 config4**，该报告以位置分布WD最小选择epoch1800（0.14036725280135548）。这是本页可以确认的“1800最佳”来源。左图绿色是**旧UViT config1**，不是v2 config4。没有证据将本页制图依据归为旧版final epoch1800，不能因epoch数字相同而合并权重。

| 曲线/实验 | epoch1800的motif命中数 | 位置WD | 关系 |
|---|---:|---:|---|
| 两图DDPM-M | 262265 | 1.1601910871 | 相同Maize分支CSV |
| 两图DiT-M | 297329 | 1.0419452222 | 相同Maize分支CSV |
| 左图旧UViT config1 | 259212 | 0.9387683673 | 左图硬编码数组与40份config1 CSV逐项吻合 |
| 右图UViT-v2 config4 | 303860 | 0.1403672528 | 报告中的WD最佳checkpoint |
| 旧版final DDPM | 37327 | 0.6666115895 | 另一训练目录、另一评价批次，不属于本页曲线 |

最后一行只用于区分来源，不用于跨批次排名。

## 两侧原图在哪里

左：`topic_new26/topic_enhancer/every_species/All_Species_Generators/UViT/draw_motifs/Maize_35s_down_DDPM_vs_DiT_vs_UViT_all.png`，脚本同目录`draw.py`。DDPM/DiT来自CSV；UViT为脚本中写死的40个epoch、命中数和WD数组。本次在旧UViT compare_outputs中逐表搜索，**40/40均匹配config1**，类别数也均为703。

右：`topic_new26/topic_enhancer/model_about/Database_comparison/jaspar/compare_models_summary/models_comparison_epochs.png`，脚本上一层`compare_models_summary.py`。其140行曲线表与四个来源表逐项匹配；包含DDPM-M、DiT-M、UViT-v2 config4、DNA-diffusion，DeepPromoter为单checkpoint水平参照。

## 如何比较

现存FIMO结果以JASPAR2024 CORE plants非冗余motif数据库扫描。已读真实参照FIMO XML为5.4.1，p-value阈值1e-4，背景`--nrdb--`，9000条共1440000碱基。参照CSV记录343383次命中、703个alt-ID类别。

- motif命中数：FIMO命中记录行数，非增强子数量，也非活性值；不是越高越好。
- motif类别数：命中过的alt-ID种类数量；不是motif频率分布相关性，接近703本身不足以证明分布相似。
- WD：以`floor((start+stop)/2)`定位命中中心，在0–159位置计数，各位置加1伪计数，使用位置计数作为权重计算一维Wasserstein距离。它衡量**motif中心位置分布**，不是motif类别组成或功能活性距离。
- 右图中间一栏是生成命中数减真实命中数，左图中间一栏是类别数；两栏不同指标。

本次CSV核对不等同对所有原始FIMO重计数。还未逐模型冻结训练输入、样本数、采样步数、全部checkpoint哈希和完整FIMO配置；不同模型的epoch也不代表相同训练计算量。因此不宣称这是所有实验条件统一的公平排名。

## 已确认的绘图问题

1. **左图WD“Real”水平线错误。** 脚本连续调用三次readline：第一行取real的num；下一行取epoch100的cat；再下一行取epoch1000的wd=**1.2117218500987588**。图中约1.21的灰线来自生成模型某轮，不能标为Real。真实分布与自身WD应为0；CSV里real的-1为占位符，也不能画为真实距离。
2. 左图类别参照同样读错行，只是epoch100的类别数恰好也是703，数值暂时没有表现出错误。
3. 左右绿色曲线来自不同UViT版本和配置；图注必须分别写清，不可将两者当同一模型。
4. 页标题含LDM，但可核实图例是DDPM、DiT、UViT以及DNA-diffusion/DeepPromoter。尚未读取足够架构证据将DNA-diffusion等同于LDM，标题需要补充对应关系或删去未展示模型。
5. DeepPromoter是单checkpoint结果，用水平线表示便于观察，但不是该模型在所有epoch都有相同表现。

## 与最新核验结果能否对上

DDPM-M epoch2000旧表motif数**279293**，与此前重计数一致；旧表WD为**1.7088599726**。此前本仓库重分析使用另一份等量真实参照（346153次命中），同一生成样本WD为**1.5875476453**。WD依赖参照集合，两个数不能直接混用。

同理，DDPM-A epoch2000旧表命中281531，与此前重计数一致；旧参照WD1.0789592994，当前等量参照重分析WD0.9850037171。A不属于本页Maize曲线。

这些生成质量指标与八个活性预测器test PCC属于不同评价任务。10/1旧版final epoch2000引导验证也不是本页DDPM-M的结果。整页不能标为“均与最终模型结果一致”。

## 已归档依据

- [左图三模型120行](../data/verified/slide_left_model_curves.csv)
- [右图四模型140行](../data/verified/slide_right_model_curves.csv)
- [主要来源哈希](../data/verified/slide_comparison_sources.csv)
- [旧UViT config1的40份CSV及哈希](../data/verified/slide_legacy_uvit_sources.csv)

本次保留历史数值与来源，未将该页曲线直接并入最终模型论文结果。
