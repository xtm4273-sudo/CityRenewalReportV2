# CityRenewalReportV2

三棵树城市焕新区域经理经营分析报告（二期）—— 全新仓库。

## 当前状态

已从一期 `SimpleIntellReport@03f65d5` 选择性导入接口层与运行时支持，详见 [docs/import_manifest.md](docs/import_manifest.md)。

## 快速验证

```powershell
$env:SKSHU_BI_API_KEY = "你的key"
python scripts/smoke_test_api.py
```

## 目录说明

- `Data/` — 接口封装（一期导入）
- `RuntimeSupport/` — 并发重试与任务记录（一期导入）
- `Logger/` — 日志（一期导入）
- `templates/` — 客户 Word 范本（待放入）
- `output/` — 生成产物

二期新模块（模板填充、1-8 章 schema）在此仓库全新开发，不沿用旧仓错误路线。
