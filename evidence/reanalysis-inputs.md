# 重分析输入格式

公开CSV可用scripts/check_result_tables.py独立核对。原始DNA和标签不放入公开仓库。

完整重分析脚本接收作者提供的一个目录，其中sources_*.json是数组，每项包含source_relative_path（课题内部相对路径）、text（未经改写的UTF-8文件正文）、size（原字节数）、sha256（原字节SHA256）。脚本先验证正文对应哈希，再解析。本次读取失败的条目可保留error字段，但不能替代成功来源。

另需file_inventory_and_fimo.json：generated_files记录80份既有FASTA的序列数、长度、合法性及文件哈希；checkpoint_files记录当前权重元数据；fimo_stats记录四份FIMO文件的哈希、总命中、alt-ID类别数、160位置权重（每位置伪计数1）和motif-ID计数；motif_database记录数据库哈希。position_weights使用floor[(start+stop)/2]的旧实现索引，不能换算后覆盖历史口径。

运行：`python3 scripts/reanalyse_archive.py --source-dir <作者提供的导出目录>`。脚本没有SSH或服务器写入功能，不训练模型、采样、载入checkpoint或重新运行FIMO。其输入模式是本次只读导出约定，不表示平台工具天然输出同样结构。

来源目录的原始文件仅用于本地核验，仓库发布的是观察值、聚合统计、哈希和可复现分析脚本。若后续公开原始DNA、完整标签或模型，需要由作者确认其来源许可和范围。
