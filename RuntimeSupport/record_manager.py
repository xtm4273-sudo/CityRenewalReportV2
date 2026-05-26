# record_manager.py
"""
运行时支持模块 - 报告分析记录管理器
负责持久化和恢复报告分析记录和未完成任务
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

from .config import ANALYSIS_RECORDS_DIR, MAX_RETRIES
from .error_handler import ErrorType, classify_error, is_retryable_error


class AnalysisRecordManager:
    """
    报告分析记录管理器
    记录：已完成、未完成、失败、数据空白四种情况
    """
    def __init__(
        self, 
        time: str
    ):
        """
        初始化报告分析记录管理器
        Args:
            time: 分析月份
        """
        self.time = time

        # 创建记录文件夹
        self.records_dir = Path(ANALYSIS_RECORDS_DIR) / f"{time}_analysis_records"
        self.records_dir.mkdir(parents=True, exist_ok=True)

        # 已完成、未完成和失败记录JSON文件
        self.completed_file = self.records_dir / "completed.json"
        self.pending_file = self.records_dir / "pending.json"
        self.failed_file = self.records_dir / "failed.json"
        self.data_blank_file = self.records_dir / "data_blank.json"

        # 内存中记录
        self.completed_records: Dict[str, Dict[str, Any]] = {}
        self.failed_records: Dict[str, Dict[str, Any]] = {}
        self.pending_records: Dict[str, Dict[str, Any]] = {}
        self.data_blank_records: Dict[str, Dict[str, Any]] = {}

        # 加载已有记录
        self._load_all_records()

    def _create_record_files(self):
        """创建记录文件"""
        if not self.records_dir.exists():
            self.records_dir.mkdir(parents=True, exist_ok=True)
        if not self.completed_file.exists():
            self.completed_file.touch()
        if not self.pending_file.exists():
            self.pending_file.touch()
        if not self.failed_file.exists():
            self.failed_file.touch()
        if not self.data_blank_file.exists():
            self.data_blank_file.touch()

    def _load_all_records(self):
        """加载所有记录文件"""
        # 加载已完成记录
        if self.completed_file.exists():
            try:
                with open(self.completed_file, 'r', encoding='utf-8') as f:
                    self.completed_records = json.load(f)
            except Exception as e:
                print(f"[警告] 加载已完成记录文件出错: {e}")
                self.completed_records = {}

        # 加载失败记录
        if self.failed_file.exists():
            try:
                with open(self.failed_file, 'r', encoding='utf-8') as f:
                    self.failed_records = json.load(f)
            except Exception as e:
                print(f"[警告] 加载失败记录文件出错: {e}")
                self.failed_records = {}
        
        # 加载未完成记录
        if self.pending_file.exists():
            try:
                with open(self.pending_file, "r", encoding="utf-8") as f:
                    self.pending_records = json.load(f)
            except Exception as e:
                print(f"[警告] 加载未完成记录文件出错: {e}")
                self.pending_records = {}
            
        # 加载数据为空记录
        if self.data_blank_file.exists():
            try:
                with open(self.data_blank_file, "r", encoding="utf-8") as f:
                    self.data_blank_records = json.load(f)
            except Exception as e:
                print(f"[警告] 加载数据为空记录文件出错: {e}")
                self.pending_records = {}

    def _save_completed_records(self):
        """保存已完成记录"""
        try:
            with open(self.completed_file, 'w', encoding='utf-8') as f:
                json.dump(self.completed_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存已完成记录文件出错: {e}")

    def _save_failed_records(self):
        """保存失败记录"""
        try:
            with open(self.failed_file, "w", encoding="utf-8") as f:
                json.dump(self.failed_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存失败记录文件出错: {e}")

    def _save_pending_records(self):
        """保存未完成记录"""
        try:
            with open(self.pending_file, "w", encoding="utf-8") as f:
                json.dump(self.pending_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存未完成记录文件出错: {e}")

    def _save_data_blank_records(self):
        """保存数据空白记录"""
        try:
            with open(self.data_blank_file, "w", encoding="utf-8") as f:
                json.dump(self.data_blank_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存数据空白记录文件出错: {e}")

    def save_completed_record(
        self, 
        sale_config: Dict[str, Any],
        pdf_path: Path = None
    ):
        """
        保存已完成记录

        Args:
            sale_config: 销售配置
            pdf_path: PDF文件路径
        """
        sale_id = sale_config["job_id"]
        self.completed_records[sale_id] = {
            "sale_config": sale_config,
            "pdf_path": str(pdf_path) if pdf_path else None,
            "completed_time": datetime.now().isoformat()
        }
        # 从失败记录中移除
        if sale_id in self.failed_records:
            del self.failed_records[sale_id]
            self._save_failed_records()
        # 从未完成记录中移除
        if sale_id in self.pending_records:
            del self.pending_records[sale_id]
            self._save_pending_records()
        # 保存数据为空记录到JSON
        if sale_id in self.data_blank_records:
            del self.data_blank_records[sale_id]
            self._save_data_blank_records()
        # 保存已完成记录
        self._save_completed_records()

    def save_failed_record(
        self,
        sale_config: Dict[str, Any],
        error: Exception,
        retry_count: int = 0
    ):
        """
        保存失败记录

        Args:
            sale_config: 销售配置
            error: 异常对象
            retry_count: 当前重试次数
        """
        sale_id = sale_config["job_id"]
        error_type = classify_error(error)

        self.failed_records[sale_id] = {
            "sale_config": sale_config,
            "error_type": error_type,
            "error_message": str(error),
            "error_name": type(error).__name__,
            "retry_count": retry_count,
            "last_failed_time": datetime.now().isoformat(),
            "is_retryable": is_retryable_error(error_type)
        }

        # 从未完成记录中移除（如果存在）
        if sale_id in self.pending_records:
            del self.pending_records[sale_id]
            self._save_pending_records()

        self._save_failed_records()

    def save_pending_records(
        self,
        all_sale_configs: List[Dict[str, Any]],
        completed_sale_ids: Set[str]
    ):
        """
        保存所有未完成的销售记录（包括失败的 + 未开始的）

        Args:
            all_sale_configs: 所有销售配置列表
            completed_sale_ids: 已完成的销售ID集合
        """
        for sale_config in all_sale_configs:
            sale_id = sale_config["job_id"]
            
            # 如果已完成，跳过
            if sale_id in completed_sale_ids:
                continue
            
            # 如果已经在失败记录中，跳过（失败记录单独管理）
            if sale_id in self.failed_records:
                continue
            
            # 保存为未完成记录
            if sale_id not in self.pending_records:
                self.pending_records[sale_id] = {
                    "sale_config": sale_config,
                    "error_type": ErrorType.INTERRUPTED,
                    "error_message": "任务被用户中断，尚未开始执行",
                    "error_name": "KeyboardInterrupt",
                    "retry_count": 0,
                    "last_failed_time": datetime.now().isoformat(),
                    "is_retryable": True
                }
        
        self._save_pending_records()

    def save_data_blank_records(
        self,
        sale_config: Dict[str, Any],
        error_message: str
    ):
        """
        保存数据空白记录
        Args:
            sale_config: 销售配置
            error_message: 错误信息
        """
        sale_id = sale_config["job_id"]
        self.data_blank_records[sale_id] = {
            "sale_config": sale_config,
            "error_message": error_message,
            "last_failed_time": datetime.now().isoformat()
        }
        # 保存数据空白记录到JSON
        self._save_data_blank_records()

        # 从未完成记录中移除
        if sale_id in self.pending_records:
            del self.pending_records[sale_id]
            self._save_pending_records()
            
        # 从失败记录中移除
        if sale_id in self.failed_records:
            del self.failed_records[sale_id]
            self._save_failed_records()

    def load_unfinished_records(self) -> List[Dict[str, Any]]:
        """
        加载未完成任务记录, 包括失败和未完成任务

        Returns:
            未完成任务的报告分析配置列表
        """
        unfinished_sales = []

        # 加载失败记录中可重试的
        for _, record in self.failed_records.items():
            if record.get("retry_count", 0) < MAX_RETRIES:
                unfinished_sales.append(record["sale_config"])
        # 加载未完成记录
        for _, record in self.pending_records.items():
            unfinished_sales.append(record["sale_config"])
        
        # 加载空数据的记录
        for _, record in self.data_blank_records.items():
            unfinished_sales.append(record["sale_config"])

        return unfinished_sales

    def get_completed_sale_ids(self) -> Set[str]:
        """获取已完成的销售ID集合"""
        return set(self.completed_records.keys())

    def print_summary(self):
        """打印记录摘要"""
        completed_count = len(self.completed_records)
        failed_count = len(self.failed_records)
        pending_count = len(self.pending_records)
        
        if completed_count == 0 and failed_count == 0 and pending_count == 0:
            return
        
        print("\n" + "=" * 60)
        print(f"分析记录摘要 (分析时间: {self.time})")
        print("=" * 60)
        print(f"已完成: {completed_count} 个")
        print(f"失败: {failed_count} 个")
        print(f"未完成: {pending_count} 个")
        print("=" * 60)
        
        if failed_count > 0:
            print("\n失败销售详情：")
            # 按错误类型分组
            error_groups: Dict[str, List[Dict]] = {}
            for record in self.failed_records.values():
                error_type = record.get("error_type", "unknown")
                if error_type not in error_groups:
                    error_groups[error_type] = []
                error_groups[error_type].append(record)
            
            for error_type, records in error_groups.items():
                type_name = {
                    "timeout": "超时错误",
                    "connection": "连接错误",
                    "api_error": "API错误",
                    "data_error": "数据错误",
                    "interrupted": "中断",
                    "unknown": "未知错误"
                }.get(error_type, error_type)
                
                print(f"\n【{type_name}】({len(records)} 个)")
                for record in records[:5]:  # 只显示前5个
                    sale_name = record["sale_config"]["sale_name"]
                    sale_id = record["sale_config"]["job_id"]
                    retry_count = record.get("retry_count", 0)
                    error_msg = record.get("error_message", "")[:50]
                    print(f"  - {sale_name}({sale_id}): 重试{retry_count}次 | {error_msg}...")
                if len(records) > 5:
                    print(f"  ... 还有 {len(records) - 5} 个")
