# error_handler.py
"""
运行时支持模块 - 错误分类和处理
"""
from typing import Dict, Any

class ErrorType:
    """错误类型分类"""
    TIMEOUT = "timeout"              # 超时错误（可重试）
    CONNECTION = "connection"        # 连接错误（可重试）
    API_ERROR = "api_error"          # API错误（可重试）
    INTERRUPTED = "interrupted"      # 中断错误（可重试）
    UNKNOWN = "unknown"             # 未知错误（可重试）

class DataBlankError(Exception):
    """数据为空错误"""
    def __init__(self, message: str, sale_config: Dict[str, Any] = None):
        """
        数据为空错误
        :param message: 错误信息
        :param sale_config: 销售人员信息
        """
        super().__init__(message)
        self.message = message
        self.sale_config = sale_config

    def __str__(self):
        return f"数据为空错误: {self.message}, 销售人员信息: {self.sale_config}"

def classify_error(error: Exception) -> str:
    """
    分类错误类型

    Args:
        error: 异常对象

    Returns:
        错误类型
    """
    error_name = type(error).__name__
    error_msg = str(error).lower()

    # API 错误  
    if "api错误" in error_msg or "api" in error_msg:
        return ErrorType.API_ERROR

    # 超时错误
    if "timeout" in error_name.lower() or "timeout" in error_msg:
        return ErrorType.TIMEOUT

    # 连接错误
    if "connection" in error_name.lower() or "connection" in error_msg:
        return ErrorType.CONNECTION

    # 中断错误
    if "keyboardinterrupt" in error_name.lower() or "keyboardinterrupt" in error_msg:
        return ErrorType.INTERRUPTED

    return ErrorType.UNKNOWN


def is_retryable_error(error_type: str) -> bool:
    """判断错误是否可重试"""
    return error_type in [
        ErrorType.TIMEOUT, 
        ErrorType.CONNECTION, 
        ErrorType.API_ERROR,
        ErrorType.UNKNOWN
    ]
