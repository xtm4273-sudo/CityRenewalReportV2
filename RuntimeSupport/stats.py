# stats.py
"""
运行时支持模块 - 报告生成统计信息
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime


class ReportGenerationStats:
    """报告生成统计信息"""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = datetime.now()
        self.results: List[Dict[str, Any]] = []

    def increment_completed(
        self, 
        sale_id,
        sale_name: str, 
        pdf_path: Path = None
    ):
        """增加成功计数"""
        self.completed += 1
        self.results.append({
            "sale_id": sale_id,
            "sale_name": sale_name,
            "status": "成功",
            "pdf_path": str(pdf_path) if pdf_path else None
        })
        self._print_progress()

    def increment_failed(self, sale_name: str, error: str):
        """增加失败计数"""
        self.failed += 1
        self.results.append({
            "sale_name": sale_name,
            "status": "失败",
            "error": error
        })
        self._print_progress()

    def _print_progress(self):
        """打印进度信息"""
        progress = (self.completed + self.failed) / self.total * 100
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\r[进度] {self.completed + self.failed}/{self.total} ({progress:.1f}%) | "
              f"成功: {self.completed} | 失败: {self.failed} | 耗时: {elapsed:.1f}秒", end="", flush=True)

    def print_summary(self):
        """打印最终统计摘要"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n\n{'='*60}")
        print(f"报告生成完成！")
        print(f"{'='*60}")
        print(f"总计: {self.total} 份报告")
        print(f"成功: {self.completed} 份")
        print(f"失败: {self.failed} 份")
        print(f"总耗时: {elapsed:.1f} 秒")
        if self.completed > 0:
            print(f"平均耗时: {elapsed / self.completed:.1f} 秒/份")
        print(f"{'='*60}\n")
