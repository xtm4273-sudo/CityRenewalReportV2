#!/usr/bin/env python3
"""
metrics.py 模块测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Data.city_renewal.metrics import (
    get_metric_rows,
    get_metric_data,
    summarize_metric_row,
    split_metric_path,
    find_rows_by_name,
    find_rows_by_path_keyword,
    to_number,
)


def test_get_metric_rows():
    """测试 get_metric_rows 函数"""
    print("=== 测试 get_metric_rows ===")

    # 测试用例1：标准格式
    payload1 = {
        "data": [
            {"指标名称": "销售额", "指标路径": "销售/业绩", "指标数据": "12345.67"},
            {"指标名称": "客户数", "指标路径": "销售/客户", "指标数据": "100"},
        ]
    }
    rows1 = get_metric_rows(payload1)
    print(f"标准格式: {len(rows1)} 行")
    assert len(rows1) == 2

    # 测试用例2：不同字段名
    payload2 = {
        "Data": [
            {"name": "test1", "path": "path1", "value": "100"},
            {"name": "test2", "path": "path2", "value": "200"},
        ]
    }
    rows2 = get_metric_rows(payload2)
    print(f"不同字段名: {len(rows2)} 行")

    # 测试用例3：空数据
    payload3 = {"data": []}
    rows3 = get_metric_rows(payload3)
    print(f"空数据: {len(rows3)} 行")
    assert len(rows3) == 0

    # 测试用例4：无效格式
    payload4 = {"data": "not a list"}
    try:
        rows4 = get_metric_rows(payload4)
        print("无效格式处理: 应抛出异常")
    except ValueError as e:
        print(f"无效格式处理正常: {e}")

    print("get_metric_rows 测试通过\n")


def test_get_metric_data():
    """测试 get_metric_data 函数"""
    print("=== 测试 get_metric_data ===")

    # 测试用例1：标准行
    row1 = {"指标名称": "销售额", "指标路径": "销售/业绩", "指标数据": "12345.67元"}
    data1 = get_metric_data(row1)
    print(f"标准行: {data1}")
    assert data1["name"] == "销售额"
    assert data1["path"] == "销售/业绩"
    assert data1["raw_value"] == "12345.67元"
    assert data1["numeric_value"] == 12345.67
    assert data1["unit"] == "元"

    # 测试用例2：百分比
    row2 = {"指标名称": "完成率", "指标路径": "进度", "指标数据": "85.5%"}
    data2 = get_metric_data(row2)
    print(f"百分比: {data2}")
    assert data2["is_percentage"] == True
    assert data2["unit"] == "%"
    assert data2["numeric_value"] == 0.855

    # 测试用例3：无单位数字
    row3 = {"指标名称": "数量", "指标路径": "基础", "指标数据": "100"}
    data3 = get_metric_data(row3)
    print(f"无单位数字: {data3}")
    assert data3["numeric_value"] == 100.0
    assert data3["unit"] == ""

    print("get_metric_data 测试通过\n")


def test_summarize_metric_row():
    """测试 summarize_metric_row 函数"""
    print("=== 测试 summarize_metric_row ===")

    row = {"指标名称": "销售额", "指标路径": "销售/业绩", "指标数据": "12345.67元"}
    summary = summarize_metric_row(row)
    print(f"摘要: {summary}")

    assert summary["name"] == "销售额"
    assert summary["path"] == "销售/业绩"
    assert "12345.67" in summary["value_summary"]
    assert summary["has_numeric"] == True
    assert summary["is_valid"] == True

    print("summarize_metric_row 测试通过\n")


def test_split_metric_path():
    """测试 split_metric_path 函数"""
    print("=== 测试 split_metric_path ===")

    # 测试用例1：标准斜杠分隔
    path1 = "一级/二级/三级"
    parts1 = split_metric_path(path1)
    print(f"标准斜杠: {parts1}")
    assert parts1 == ["一级", "二级", "三级"]

    # 测试用例2：反斜杠分隔
    path2 = "一级\\二级\\三级"
    parts2 = split_metric_path(path2)
    print(f"反斜杠: {parts2}")
    assert parts2 == ["一级", "二级", "三级"]

    # 测试用例3：箭头分隔
    path3 = "一级->二级->三级"
    parts3 = split_metric_path(path3)
    print(f"箭头分隔: {parts3}")
    assert parts3 == ["一级", "二级", "三级"]

    # 测试用例4：空路径
    path4 = ""
    parts4 = split_metric_path(path4)
    print(f"空路径: {parts4}")
    assert parts4 == []

    # 测试用例5：带空格的路径
    path5 = " 一级 / 二级 / 三级 "
    parts5 = split_metric_path(path5)
    print(f"带空格: {parts5}")
    assert parts5 == ["一级", "二级", "三级"]

    print("split_metric_path 测试通过\n")


def test_find_rows_by_name():
    """测试 find_rows_by_name 函数"""
    print("=== 测试 find_rows_by_name ===")

    rows = [
        {"指标名称": "销售额", "指标路径": "销售/业绩", "指标数据": "100"},
        {"指标名称": "销售成本", "指标路径": "销售/成本", "指标数据": "50"},
        {"指标名称": "客户数", "指标路径": "客户/数量", "指标数据": "10"},
        {"name": "test_sales", "path": "test", "value": "200"},
    ]

    # 测试用例1：精确匹配
    result1 = find_rows_by_name(rows, "销售额")
    print(f"精确匹配 '销售额': {len(result1)} 行")
    assert len(result1) == 1

    # 测试用例2：部分匹配
    result2 = find_rows_by_name(rows, "销售")
    print(f"部分匹配 '销售': {len(result2)} 行")
    print(f"匹配到的行: {result2}")
    # 销售额、销售成本，test_sales不会被匹配因为字段名是'name'而不是'指标名称'
    assert len(result2) == 2

    # 测试用例3：不区分大小写
    result3 = find_rows_by_name(rows, "SALES")
    print(f"不区分大小写 'SALES': {len(result3)} 行")
    print(f"匹配到的行: {result3}")
    # test_sales不会被匹配因为字段名是'name'而不是'指标名称'
    assert len(result3) == 0

    # 测试用例4：无匹配
    result4 = find_rows_by_name(rows, "不存在的指标")
    print(f"无匹配: {len(result4)} 行")
    assert len(result4) == 0

    print("find_rows_by_name 测试通过\n")


def test_find_rows_by_path_keyword():
    """测试 find_rows_by_path_keyword 函数"""
    print("=== 测试 find_rows_by_path_keyword ===")

    rows = [
        {"指标名称": "指标1", "指标路径": "销售/业绩/月度", "指标数据": "100"},
        {"指标名称": "指标2", "指标路径": "销售/成本/月度", "指标数据": "50"},
        {"指标名称": "指标3", "指标路径": "客户/数量/年度", "指标数据": "10"},
        {"指标名称": "指标4", "指标路径": "销售/业绩/年度", "指标数据": "200"},
    ]

    # 测试用例1：单个关键词
    result1 = find_rows_by_path_keyword(rows, ("销售",))
    print(f"单个关键词 '销售': {len(result1)} 行")
    assert len(result1) == 3

    # 测试用例2：多个关键词AND匹配
    result2 = find_rows_by_path_keyword(rows, ("销售", "业绩"))
    print(f"多个关键词 '销售 AND 业绩': {len(result2)} 行")
    assert len(result2) == 2

    # 测试用例3：多个关键词AND匹配（全部满足）
    result3 = find_rows_by_path_keyword(rows, ("销售", "业绩", "月度"))
    print(f"多个关键词 '销售 AND 业绩 AND 月度': {len(result3)} 行")
    assert len(result3) == 1

    # 测试用例4：无匹配
    result4 = find_rows_by_path_keyword(rows, ("不存在的", "关键词"))
    print(f"无匹配: {len(result4)} 行")
    assert len(result4) == 0

    print("find_rows_by_path_keyword 测试通过\n")


def test_to_number():
    """测试 to_number 函数"""
    print("=== 测试 to_number ===")

    # 测试用例1：整数
    assert to_number(100) == 100.0
    print("整数: 100 -> 100.0")

    # 测试用例2：浮点数
    assert to_number(123.45) == 123.45
    print("浮点数: 123.45 -> 123.45")

    # 测试用例3：字符串整数
    assert to_number("100") == 100.0
    print("字符串整数: '100' -> 100.0")

    # 测试用例4：字符串浮点数
    assert to_number("123.45") == 123.45
    print("字符串浮点数: '123.45' -> 123.45")

    # 测试用例5：带千位分隔符
    assert to_number("1,234.56") == 1234.56
    print("带千位分隔符: '1,234.56' -> 1234.56")

    # 测试用例6：百分比
    assert to_number("85.5%") == 0.855
    print("百分比: '85.5%' -> 0.855")

    # 测试用例7：带单位
    assert to_number("123.45元") == 123.45
    print("带单位: '123.45元' -> 123.45")

    # 测试用例8：带单位的百分比
    assert to_number("85.5%") == 0.855
    print("带单位的百分比: '85.5%' -> 0.855")

    # 测试用例9：包含数字的字符串
    assert to_number("价格: 123.45元") == 123.45
    print("包含数字的字符串: '价格: 123.45元' -> 123.45")

    # 测试用例10：无法转换
    assert to_number("不是数字") is None
    print("无法转换: '不是数字' -> None")

    # 测试用例11：空值
    assert to_number("") is None
    print("空字符串: '' -> None")
    assert to_number(None) is None
    print("None: None -> None")

    print("to_number 测试通过\n")


def main():
    """运行所有测试"""
    print("开始测试 metrics.py 模块\n")

    test_get_metric_rows()
    test_get_metric_data()
    test_summarize_metric_row()
    test_split_metric_path()
    test_find_rows_by_name()
    test_find_rows_by_path_keyword()
    test_to_number()

    print("所有测试通过！")


if __name__ == "__main__":
    main()