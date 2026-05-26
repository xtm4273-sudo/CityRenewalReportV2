"""
通用指标抽取模块

本模块负责从接口返回的原始payload中抽取指标数据，不包含任何二期章节语义。
旨在为adapter和coverage模块提供通用的指标处理功能。
"""

import re
from typing import Any, Dict, List, Optional, Union


def get_metric_rows(module_payload: dict) -> list[dict]:
    """
    从模块payload中提取指标行列表。

    接口返回格式假设：
        {
            "data": [
                {
                    "指标名称": "指标1",
                    "指标路径": "路径1/路径2",
                    "指标数据": "123.45"
                },
                ...
            ]
        }

    参数:
        module_payload: 模块的原始payload字典

    返回:
        指标行列表，每个元素是一个包含指标信息的字典

    异常:
        ValueError: 当payload格式不符合预期时
    """
    if not isinstance(module_payload, dict):
        raise ValueError(f"module_payload必须是字典类型，实际类型: {type(module_payload)}")

    # 尝试从不同可能的键中获取数据
    data_key = None
    for key in ["data", "Data", "指标数据列表", "指标列表"]:
        if key in module_payload:
            data_key = key
            break

    if data_key is None:
        # 如果没有找到数据键，检查payload本身是否就是数据列表
        if isinstance(module_payload.get("data"), list):
            return module_payload.get("data", [])
        # 尝试直接返回payload，可能已经是列表格式
        if isinstance(module_payload, list):
            return module_payload
        # 返回空列表而不是抛出异常，更健壮
        return []

    data = module_payload.get(data_key, [])
    if not isinstance(data, list):
        raise ValueError(f"payload中的'{data_key}'必须是列表类型，实际类型: {type(data)}")

    # 验证数据格式
    valid_rows = []
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            # 跳过非字典类型的行，记录警告或继续处理
            continue

        # 创建行的副本以避免修改原始数据
        row_copy = row.copy()

        # 检查必要的字段
        if "指标名称" not in row_copy:
            # 尝试其他可能的字段名
            for name_key in ["指标名称", "name", "metric_name", "指标名"]:
                if name_key in row_copy:
                    row_copy["指标名称"] = row_copy[name_key]
                    break

        if "指标路径" not in row_copy:
            # 尝试其他可能的字段名
            for path_key in ["指标路径", "path", "metric_path", "路径"]:
                if path_key in row_copy:
                    row_copy["指标路径"] = row_copy[path_key]
                    break

        if "指标数据" not in row_copy:
            # 尝试其他可能的字段名
            for data_key_name in ["指标数据", "data", "metric_data", "value", "指标值"]:
                if data_key_name in row_copy:
                    row_copy["指标数据"] = row_copy[data_key_name]
                    break

        valid_rows.append(row_copy)

    return valid_rows


def get_metric_data(row: dict) -> dict:
    """
    从指标行中提取标准化指标数据。

    参数:
        row: 单个指标行字典

    返回:
        包含标准化字段的字典，包含:
            - name: 指标名称
            - path: 指标路径
            - raw_value: 原始值
            - numeric_value: 数值化的值（如果可转换）
            - unit: 单位（如果可提取）
            - is_percentage: 是否为百分比
    """
    if not isinstance(row, dict):
        raise ValueError(f"row必须是字典类型，实际类型: {type(row)}")

    # 提取基础字段
    name = row.get("指标名称", "")
    path = row.get("指标路径", "")
    raw_value = row.get("指标数据", "")

    # 尝试数值化
    numeric_value = to_number(raw_value)

    # 尝试提取单位
    unit = ""
    is_percentage = False

    if isinstance(raw_value, str):
        # 检查是否为百分比
        if "%" in raw_value:
            is_percentage = True
            unit = "%"
        # 提取其他单位
        else:
            # 匹配常见的单位
            unit_patterns = [
                (r"(\d+(?:\.\d+)?)\s*(元|万元|千元)", "元"),
                (r"(\d+(?:\.\d+)?)\s*(个|件|套)", "个"),
                (r"(\d+(?:\.\d+)?)\s*(天|日)", "天"),
                (r"(\d+(?:\.\d+)?)\s*(次)", "次"),
            ]

            for pattern, unit_name in unit_patterns:
                if re.search(pattern, raw_value):
                    unit = unit_name
                    break

    return {
        "name": name,
        "path": path,
        "raw_value": raw_value,
        "numeric_value": numeric_value,
        "unit": unit,
        "is_percentage": is_percentage,
    }


def summarize_metric_row(row: dict) -> dict:
    """
    为指标行生成摘要信息。

    参数:
        row: 单个指标行字典

    返回:
        包含摘要信息的字典:
            - name: 指标名称
            - path: 指标路径
            - value_summary: 值的摘要（数值+单位）
            - has_numeric: 是否有数值
            - is_valid: 是否有效（有名称或路径）
    """
    metric_data = get_metric_data(row)

    # 生成值摘要
    value_summary = metric_data["raw_value"]
    if metric_data["numeric_value"] is not None:
        if metric_data["unit"]:
            value_summary = f"{metric_data['numeric_value']}{metric_data['unit']}"
        else:
            value_summary = str(metric_data["numeric_value"])

    # 检查是否有效
    is_valid = bool(metric_data["name"] or metric_data["path"])

    return {
        "name": metric_data["name"],
        "path": metric_data["path"],
        "value_summary": value_summary,
        "has_numeric": metric_data["numeric_value"] is not None,
        "is_valid": is_valid,
    }


def split_metric_path(path: str) -> list[str]:
    """
    分割指标路径字符串。

    指标路径可能使用不同的分隔符："/"、"\\"、"->"、"→"等。

    参数:
        path: 指标路径字符串

    返回:
        分割后的路径部分列表

    示例:
        >>> split_metric_path("一级/二级/三级")
        ["一级", "二级", "三级"]
        >>> split_metric_path("一级->二级->三级")
        ["一级", "二级", "三级"]
    """
    if not path or not isinstance(path, str):
        return []

    # 标准化路径分隔符
    normalized_path = path.strip()

    # 替换不同的分隔符为统一的分隔符
    separators = ["\\", "->", "→", ">", "|"]
    for sep in separators:
        normalized_path = normalized_path.replace(sep, "/")

    # 分割路径
    parts = [part.strip() for part in normalized_path.split("/") if part.strip()]

    return parts


def find_rows_by_name(rows: list[dict], name: str) -> list[dict]:
    """
    根据指标名称查找指标行。

    支持模糊匹配，不区分大小写。

    参数:
        rows: 指标行列表
        name: 要查找的指标名称

    返回:
        匹配的指标行列表
    """
    if not rows or not name:
        return []

    name_lower = name.lower().strip()
    results = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        # 获取指标名称 - 优先使用标准化字段
        row_name = row.get("指标名称", "")
        if not isinstance(row_name, str):
            # 尝试其他可能的字段名
            row_name = ""
            for key in ["指标名称", "name", "metric_name", "指标名"]:
                if key in row and isinstance(row[key], str):
                    row_name = row[key]
                    break

        # 模糊匹配
        if name_lower in row_name.lower():
            results.append(row)

    return results


def find_rows_by_path_keyword(rows: list[dict], keywords: tuple[str, ...]) -> list[dict]:
    """
    根据指标路径中的关键词查找指标行。

    参数:
        rows: 指标行列表
        keywords: 关键词元组，支持多个关键词的AND匹配

    返回:
        匹配的指标行列表（路径包含所有关键词）
    """
    if not rows or not keywords:
        return []

    # 转换为小写用于不区分大小写的匹配
    keyword_lowers = [kw.lower().strip() for kw in keywords if kw]

    results = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        # 获取指标路径 - 优先使用标准化字段
        path = row.get("指标路径", "")
        if not isinstance(path, str):
            # 尝试其他可能的字段名
            path = ""
            for key in ["指标路径", "path", "metric_path", "路径"]:
                if key in row and isinstance(row[key], str):
                    path = row[key]
                    break

        path_lower = path.lower()

        # 检查是否包含所有关键词
        if all(keyword in path_lower for keyword in keyword_lowers):
            results.append(row)

    return results


def to_number(value: Any) -> float | None:
    """
    将值转换为数值类型。

    支持多种格式：
        - 整数/浮点数
        - 字符串形式的数字
        - 带单位的字符串（如"123.45元"）
        - 百分比字符串（如"12.34%"）
        - 带千位分隔符的字符串（如"1,234.56"）

    参数:
        value: 要转换的值

    返回:
        转换后的浮点数，如果无法转换则返回None
    """
    if value is None:
        return None

    # 如果已经是数字类型
    if isinstance(value, (int, float)):
        return float(value)

    # 如果是字符串
    if isinstance(value, str):
        # 去除空格
        value_str = value.strip()

        # 空字符串
        if not value_str:
            return None

        # 尝试直接转换
        try:
            # 移除千位分隔符
            value_str = value_str.replace(",", "")
            # 移除百分比符号
            if value_str.endswith("%"):
                value_str = value_str[:-1]
                result = float(value_str) / 100.0
                return result
            # 移除常见单位
            units = ["元", "万元", "千元", "个", "件", "套", "天", "日", "次"]
            for unit in units:
                if value_str.endswith(unit):
                    value_str = value_str[:-len(unit)]
                    break
            return float(value_str)
        except (ValueError, TypeError):
            # 如果直接转换失败，尝试提取数字
            match = re.search(r"[-+]?\d*\.?\d+", value_str)
            if match:
                try:
                    return float(match.group())
                except (ValueError, TypeError):
                    return None
            return None

    # 其他类型尝试转换
    try:
        return float(value)
    except (ValueError, TypeError):
        return None