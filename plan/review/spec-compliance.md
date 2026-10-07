# 规范合规检查

日期：2026-10-07。范围：部分稿件与支撑包，不是完整论文完成声明。

- 两节 Results 与用户已确认范围一致。
- 对应 Methods、Figure 1/2 图注、补充表定义和 Word 导出存在。
- 原始结果缺失时使用显式 M01–M25 标记，没有模拟结果或图件。
- 历史数字与最终结果分开存放，历史 CSV 状态为 index_summary_not_raw_verified。
- 另一篇论文的事实和数值未混入本课题。
- 未连接 SLURM 服务器或执行新实验。

验证命令：python3 scripts/export_docx.py；python3 scripts/validate_package.py；python3 scripts/validate_package.py --submission；章节风格检查；git diff --check。

工作稿检查通过，投稿模式因 25 个未解决缺口及缺少最终数据 / 图件而按预期失败。结构验证不是科学结果核验。
