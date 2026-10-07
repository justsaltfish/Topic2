# 工作进度

## 2026-10-07：用户授权核验后的更新

- 范围：两节计算Results及方法、图注、补充材料；GitHub与本地审阅稿同步。
- 原始读取：224份正文；80份无引导FASTA（720000条）长度/字符与文件哈希核对。
- 重算：27000条组成质量、k3–6、精确匹配、100000对内部Hamming；四份FIMO及XML；Maize60000条、Ara五方法各100对。
- 正文：已改为有真实数值的连续叙述，未使用空白结果槽。未恢复或未决定的信息放在证据清单和限制。
- 图件：两张实数据图，450DPI PNG/SVG，已实际视觉查看；Word嵌入图件并沿用修订的中文字体排版。
- 独立review：数值与来源边界通过；修正“同一训练集合”的歧义。
- 版本问题：7/8旧筛选档602唯一记录真实存在，当前完整表双达标46；旧完整版本与601口径仍未解决。
- 最终数据、checkpoint、阈值、质量门槛、期刊及作者声明待确认，不由Agent自动决定。

## Capability-use audit

使用using-research-writing、paper-orchestration、brainstorming-research、experiment-results-planning、writing-chapters、writing-core、verification、figures-python、environment-setup和statistical-analysis。结构和操作范围由用户会话确认，未重复要求已授权事项。

新增输入为本课题主线的实际配置、代码、序列、FIMO/XML、预测表、日志和当前权重哈希。另一课题仅作风格参考；独立插入实验按用户范围排除；DiT/UViT性能未作为自动公平基线。文献只支持DDPM、梯度引导、JASPAR和FIMO方法出处。

平台只读接口502后，使用已授权固定身份串行SSH读取，每次先核对服务器任务目录。本次未远程写入、上传、执行模型推理、采样、FIMO或提交作业。读取身份和原始DNA/标签未公开。

本地缺少绘图库，按环境技能的隔离原则使用workspace外于仓库的research venv，安装NumPy/SciPy/Matplotlib/python-docx；没有安装全局Conda或修改系统环境。依赖版本写入requirements-analysis.txt。图件按450DPI并行输出PNG/SVG；只做描述统计，无虚构假设检验或跨运行误差线。

产物对应README、results/两部分入口、chapters、manuscript、data/verified、evidence、figures、tables、supplementary及scripts。核验脚本支持公开观察值与汇总的一致性，不声称验证生物学功能或恢复缺失历史版本。

## 收尾检查

公开表数值重算与工作稿结构检查通过；投稿模式预期因剩余材料与作者决策失败。正文风格和git空白检查通过后提交。实际远程commit由git推送及ls-remote核对；本文件不预先宣称最终推送成功。
