# 一期选择性导入清单

来源仓库：`SimpleIntellReport`
来源 commit：`03f65d5`（城市焕新二期开发前最后一版）

## 已导入

| 路径 | 说明 |
|------|------|
| `Data/fetch_data.py` | 指标接口 `getEmployeeIndexAi` |
| `Data/fetch_sales.py` | 组织接口 `getAiEmployeeOrg` |
| `RuntimeSupport/` | 并发重试、失败记录、统计 |
| `Logger/sales_logger.py` | 销售专属日志 |

## 未导入（刻意排除）

| 路径 | 原因 |
|------|------|
| `ReportGenerator/` | 一期 1-6 章报告结构 |
| `ReportWrapping/` | HTML/PDF 包装 |
| `Tools/` | 一期分析工具 |
| `AnaModel/` | 一期 LLM 封装 |
| `Data/city_renewal/` | 二期错误方向代码（含 formal_report） |
| `Data/postprocess_data.py` | 一期后处理，与二期 1-8 章结构不匹配 |

## 导入后改动

- 去除硬编码 API Key，改为 `SKSHU_BI_API_KEY` 环境变量
- 精简 `Data/__init__.py`，只暴露接口层
