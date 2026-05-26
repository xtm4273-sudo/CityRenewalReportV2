# RuntimeSupport __init__.py
"""
运行时支持模块
提供系统稳定运行所需的基础设施：
- 错误分类和处理
- 任务记录管理（持久化和恢复）
- 执行统计信息
- 配置常量
"""

from .config import (
    ANALYSIS_RECORDS_DIR,
    MAX_RETRIES,
    RETRY_DELAY,
    BACKOFF_FACTOR
)

from .error_handler import (
    ErrorType,
    DataBlankError,
    classify_error,
    is_retryable_error
)

from .record_manager import AnalysisRecordManager
from .stats import ReportGenerationStats

__all__ = [
    # 配置
    "ANALYSIS_RECORDS_DIR",
    "MAX_RETRIES",
    "RETRY_DELAY",
    "BACKOFF_FACTOR",
    # 错误处理
    "ErrorType",
    "DataBlankError",
    "classify_error",
    "is_retryable_error",
    # 记录管理
    "AnalysisRecordManager",
    # 统计
    "ReportGenerationStats",
]
