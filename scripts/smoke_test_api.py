"""验证一期接口层导入是否可用。"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Data.fetch_data import fetch_raw_data
from Data.fetch_sales import SalesConigFetcher


async def main() -> None:
    api_key = os.getenv("SKSHU_BI_API_KEY")
    if not api_key:
        raise SystemExit("请先设置环境变量 SKSHU_BI_API_KEY")

    org = SalesConigFetcher(api_key=api_key)
    configs = await org.fetch_all_sales_config()
    if isinstance(configs, dict) and "error" in configs:
        raise SystemExit(f"组织接口失败: {configs}")

    print(f"组织接口返回 {len(configs)} 条")

    data = await fetch_raw_data("04490", "202604", 1, api_key=api_key)
    if isinstance(data, dict) and "error" in data:
        raise SystemExit(f"指标接口失败: {data}")

    print("指标接口返回 keys:", list(data.keys())[:8])
    print("smoke test OK")


if __name__ == "__main__":
    asyncio.run(main())
