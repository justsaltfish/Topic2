# 规范合规核验

两节Results保持用户范围；真实数据、方法、图注和补充材料对应；没有独立motif插入章节或生物学功能宣称。所有主文数值来自当前可追溯文件，未补造缺失值、独立重复或显著性。版本冲突、原阈值与后评价、同指导/评分器及非独立参照均明确处理。

核对命令：scripts/check_result_tables.py；scripts/validate_package.py；--submission；三节正文风格检查；git diff --check。最终执行结果登记在progress.md；无原始数据时不能以结构检查代替科学证据。
