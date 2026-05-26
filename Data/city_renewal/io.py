"""
城市焕新二期报告 - 数据IO模块

负责文件读写和目录约定，不做业务判断。
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def get_city_renewal_output_dir(job_id: str, calmonth: str, base_dir: str = "output") -> Path:
    """
    获取城市焕新报告输出目录路径

    目录结构：{base_dir}/city_renewal_{job_id}_{calmonth}/

    Args:
        job_id: 销售工号
        calmonth: 计算月份，格式为 YYYYMM
        base_dir: 基础输出目录，默认为 "output"

    Returns:
        Path: 输出目录的Path对象

    Raises:
        ValueError: 如果参数无效
    """
    if not job_id or not isinstance(job_id, str):
        raise ValueError(f"无效的job_id: {job_id}")

    if not calmonth or not isinstance(calmonth, str) or len(calmonth) != 6:
        raise ValueError(f"无效的calmonth格式，应为YYYYMM: {calmonth}")

    # 验证calmonth是否为数字
    if not calmonth.isdigit():
        raise ValueError(f"calmonth必须为数字: {calmonth}")

    dir_name = f"city_renewal_{job_id}_{calmonth}"
    output_dir = Path(base_dir) / dir_name

    logger.debug(f"生成输出目录: {output_dir}")
    return output_dir


def load_raw_modules(output_dir: Path) -> Dict[str, Dict]:
    """
    加载所有原始模块数据

    从 output_dir/raw/ 目录加载 module_1.json 到 module_5.json

    Args:
        output_dir: 输出目录路径

    Returns:
        Dict[str, Dict]: 模块数据字典，key为模块名（如"module_1"），value为JSON数据

    Raises:
        FileNotFoundError: 如果raw目录不存在
        JSONDecodeError: 如果JSON文件格式错误
    """
    raw_dir = output_dir / "raw"

    if not raw_dir.exists():
        raise FileNotFoundError(f"原始数据目录不存在: {raw_dir}")

    if not raw_dir.is_dir():
        raise NotADirectoryError(f"路径不是目录: {raw_dir}")

    modules = {}

    # 加载 module_1 到 module_5
    for module_num in range(1, 6):
        module_file = raw_dir / f"module_{module_num}.json"

        if not module_file.exists():
            logger.warning(f"模块文件不存在: {module_file}")
            continue

        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                module_data = json.load(f)

            module_key = f"module_{module_num}"
            modules[module_key] = module_data
            logger.debug(f"成功加载模块: {module_key}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误 {module_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"加载模块文件失败 {module_file}: {e}")
            raise

    if not modules:
        logger.warning(f"未找到任何模块文件在: {raw_dir}")

    return modules


def save_raw_module(output_dir: Path, module: int, payload: Dict) -> Path:
    """
    保存原始模块数据

    Args:
        output_dir: 输出目录路径
        module: 模块编号 (1-5)
        payload: 要保存的数据字典

    Returns:
        Path: 保存的文件路径

    Raises:
        ValueError: 如果模块编号无效
        IOError: 如果文件保存失败
    """
    if module < 1 or module > 5:
        raise ValueError(f"模块编号必须在1-5之间: {module}")

    # 创建raw目录
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 构建文件路径
    module_file = raw_dir / f"module_{module}.json"

    try:
        with open(module_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info(f"成功保存模块 {module} 到: {module_file}")
        return module_file

    except Exception as e:
        logger.error(f"保存模块文件失败 {module_file}: {e}")
        raise IOError(f"无法保存模块文件: {module_file}") from e


def save_cleaned(output_dir: Path, cleaned: Dict) -> Path:
    """
    保存清洗后的数据

    Args:
        output_dir: 输出目录路径
        cleaned: 清洗后的数据字典

    Returns:
        Path: 保存的文件路径

    Raises:
        IOError: 如果文件保存失败
    """
    # 创建cleaned目录
    cleaned_dir = output_dir / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    # 构建文件路径
    cleaned_file = cleaned_dir / "city_renewal_cleaned.json"

    try:
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

        logger.info(f"成功保存清洗数据到: {cleaned_file}")
        return cleaned_file

    except Exception as e:
        logger.error(f"保存清洗数据失败 {cleaned_file}: {e}")
        raise IOError(f"无法保存清洗数据: {cleaned_file}") from e


def save_coverage(output_dir: Path, coverage: Dict, markdown: str) -> Tuple[Path, Path]:
    """
    保存覆盖率数据

    Args:
        output_dir: 输出目录路径
        coverage: 覆盖率数据字典（JSON格式）
        markdown: 覆盖率Markdown文本

    Returns:
        Tuple[Path, Path]: (JSON文件路径, Markdown文件路径)

    Raises:
        IOError: 如果文件保存失败
    """
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON文件路径
    coverage_json = output_dir / "coverage.json"

    # Markdown文件路径
    coverage_md = output_dir / "coverage.md"

    try:
        # 保存JSON数据
        with open(coverage_json, 'w', encoding='utf-8') as f:
            json.dump(coverage, f, ensure_ascii=False, indent=2)

        # 保存Markdown数据
        with open(coverage_md, 'w', encoding='utf-8') as f:
            f.write(markdown)

        logger.info(f"成功保存覆盖率数据到: {coverage_json} 和 {coverage_md}")
        return coverage_json, coverage_md

    except Exception as e:
        logger.error(f"保存覆盖率数据失败: {e}")
        raise IOError(f"无法保存覆盖率数据") from e


def save_metric_paths(output_dir: Path, markdown: str) -> Path:
    """
    保存指标路径数据

    Args:
        output_dir: 输出目录路径
        markdown: 指标路径Markdown文本

    Returns:
        Path: 保存的文件路径

    Raises:
        IOError: 如果文件保存失败
    """
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 文件路径
    metric_paths_file = output_dir / "metric_paths.md"

    try:
        with open(metric_paths_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        logger.info(f"成功保存指标路径数据到: {metric_paths_file}")
        return metric_paths_file

    except Exception as e:
        logger.error(f"保存指标路径数据失败 {metric_paths_file}: {e}")
        raise IOError(f"无法保存指标路径数据: {metric_paths_file}") from e