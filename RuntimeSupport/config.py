# config.py
"""
运行时支持模块 - 配置常量
"""

ANALYSIS_RECORDS_DIR = "analysis_records"  # 报告分析记录目录
MAX_RETRIES = 3          # 每个销售最大重试次数
RETRY_DELAY = 5          # 基础重试延迟（秒）
BACKOFF_FACTOR = 1.5     # 退避因子（每次重试延迟增加）
