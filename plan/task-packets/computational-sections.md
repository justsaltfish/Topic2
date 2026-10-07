# 任务包：计算部分投稿结构

## 范围

依据用户确认的两个 Results 整理计算部分工作稿及其支撑文件。不是完整论文草拟任务。

## 输入

- 注入的本课题服务器语义索引，更新日期 2026-08-19。
- 注入的任务历史、用户已确认归档和本会话决策。
- 本地各物种参考.docx，仅作为叙述格式参考。
- 原始 DDPM 及预测器引导相关论文，仅支持通用方法出处。

## 允许编辑

本 Topic2 checkout 中的新文档、表格定义、导出与验证脚本。主要稿件由主代理负责；独立审阅代理仅只读反馈。

## 技能

using-research-writing、paper-orchestration、brainstorming-research、experiment-results-planning、writing-chapters、writing-core、verification。

## 产物

README；Results 两节；配套 Methods；图注；合并 Markdown/Word；证据清单和缺口；实验协议；表格定义；图件数据清单；可复现导出与验证；合规与质量审阅。

## 拒绝条件

虚构数值或显著性；将另一课题事实移入本文；自动选用模型或阈值；将 UP/DOWN 解释为高低活性；将预测分数表述为实测功能；无原始数据却声称可投稿；泄露访问身份；生成图表而无数据。

## 验证

运行 scripts/export_docx.py 和 scripts/validate_package.py；按 writing-core 执行风格检查；审查全部新增文件；git diff --check；提交后核对远端 commit。

## 本次用户授权核验追加

读取实际服务器产物，主文以真实结果替代起稿缺口；保持两节计算范围，最终模型/阈值不自动选择。新增实际数据来源、224份正文及文件哈希、原FIMO重计数、公开观察值、两张图、核验后Word和本地副本。参考文献增加JASPAR/FIMO原始论文元数据核对。独立审阅由review_package只读完成，已修正训练集合措辞。
