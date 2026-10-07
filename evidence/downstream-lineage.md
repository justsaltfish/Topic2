# 后续实验输入与生成权重追溯

核对日期：2026-10-07。此前“A/M”两个简称仅覆盖已分析的两份生成权重，不代表课题所有模型。追加发现10/1补验使用第三份旧版final权重；“后续都基于DDPM-M”应纠正。

## 已确认链路

| 下游工作 | 输入与关系 | 生成器归属 | 证据 |
|---|---|---|---|
| 8/4逐碱基SHAP | new_importance/new.csv的61条是7/8旧above_both.csv的精确子集 | 7/8任务配置归DDPM-A epoch2000 | 61/61的ID、序列、UP/DOWN分数一致；提交脚本和日志确认SHAP输入61条 |
| 8/4Maize epoch扫描 | 与SHAP相同的new.csv作为61条参考；从新噪声生成，不沿用其序列作为采样起点 | DDPM-M，40个epoch | new.csv字节哈希相同；扫描提交脚本及生成代码 |
| 多物种单/双motif替换、8/19随机双替换、9/7组合续跑、9/8三替换及数量补充 | 复用同一no_motif_4000_5000.fa，1000条160bp | 背景来源未解决；替换阶段只调用预测器 | 任务配置明确同一输入；9/8正式与数量补充的输入SHA一致 |
| 8/26两个基因片段替换 | 用户提供THP3/VTE4对应两条160bp片段 | 任务没有调用生成器 | 输入FASTA与parameters.json；仅Maize UP/DOWN预测器 |
| 10/1 classifier-guidance补验 | 使用旧版final的epoch2000，双头分类器指导、独立Ara预测器评价 | legacy-final，第三份权重 | 参数、任务记录与运行SHA manifest；当前权重SHA匹配运行记录 |

61条SHAP输入源自旧筛选档，不能用与旧筛选档版本不一致的现存7/8完整预测表替代。它们在Maize扫描中只用于参考阈值/目标记录，不意味着该轮新生成序列来自DDPM-A。

## 三份权重的关系

A：topic_new26/topic_enhancer/every_species/Ara/35s/down/DDPM/v1/model_save/epoch_2000_params.pt。

M：topic_new26/topic_enhancer/every_species/Maize/35s/down/DDPM/v1/model_save/epoch_2000_params.pt。

旧版final：topic_all/topic2_Diffusion/DDPM/final/DDPM/params/epoch_2000_params.pkl。

三份checkpoint均有323个同名、同形状状态张量。只读解析ZIP存储和受限pickle描述，按名称、类型、形状、stride、offset及storage字节摘要建立规范指纹，忽略保存目录和设备标记。三份内容指纹均不同，因此旧版final不是A或M的简单改名副本。没有载入Torch模型或进行预测。具体文件及指纹见[data表](../data/verified/checkpoint_lineage_fingerprints.csv)。

已读源码中，A/M设置0.9/0.1划分、Adam weight_decay=1e-5；旧版final设置0.8/0.1/0.1、Adam未显式指定weight_decay。它们都读取NG数据、以序列开展无条件训练。这里只记录当前源码定义，不证明缺少不可变快照的历史训练过程完全一致。

10/1任务明确是新补验，原PPT所用epoch/分类器/seed/结果尚未原样恢复。不能由目录叫final或由“最近用过”推定论文最终权重已经确定。当前主文仍是A/M历史结果核验稿；新补验尚未替换或并入主文性能比较，需作者决定研究主线。

## 1000条背景序列的剩余断点

输入SHA为f912f3c8f9dd29ff31874460effdc5e2c6351fa2aa6abdb88227d2f44ffe254e。8/19已确认归档与9/8保存的输入哈希一致，建立复用关系。

原始生成/筛选脚本、随机种子及对应checkpoint未找到。与NG真实序列无精确匹配；与A/M的80份既有FASTA及旧final的43份FASTA共123份逐序列比对也未找到精确匹配。没有跳过超出大小门槛的文件。这只能说明未匹配到这些现存输出，不能据此确认它由随机方法或某个DDPM生成。

因此这部分暂记为“来源未确认的固定背景序列”；不得写成“来自DDPM-M”或“由某份模型生成”。本次没有扫描TB级替换结果，也没有执行新的生成或预测任务。
