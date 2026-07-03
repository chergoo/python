# -*- coding: utf-8 -*-
"""
Connectivity check for akshare A-share snapshot.

Run:
    python test.py
"""

from __future__ import annotations

import os
import traceback


PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)

EASTMONEY_COLUMNS_TO_SHOW = (
    "\u4ee3\u7801",
    "\u540d\u79f0",
    "\u6700\u65b0\u4ef7",
    "\u6da8\u8dcc\u5e45",
)


def disable_proxies() -> None:
    for key in PROXY_ENV_KEYS:
        os.environ[key] = ""

    try:
        import urllib.request

        urllib.request.getproxies = lambda: {}
    except Exception:
        pass

    try:
        import requests

        requests.utils.get_environ_proxies = lambda url, no_proxy=None: {}
    except Exception:
        pass


def main() -> int:
    disable_proxies()

    try:
        import akshare as ak
    except Exception as exc:
        print("Failed to import akshare.")
        print(exc)
        return 1

    print(f"akshare version: {getattr(ak, '__version__', 'unknown')}")

    providers = (
        ("sina", ak.stock_zh_a_spot),
        ("eastmoney", ak.stock_zh_a_spot_em),
    )

    last_error = None
    df = None
    provider_name = ""

    for provider_name, fetcher in providers:
        print(f"\nFetching A-share spot snapshot via provider: {provider_name}")

        try:
            df = fetcher()
            break
        except Exception as exc:
            last_error = exc
            print("Fetch failed.")
            print(f"Error type: {type(exc).__name__}")
            print(f"Error detail: {exc}")
            if os.getenv("VERBOSE_TRACEBACK") == "1":
                print("Full traceback:")
                traceback.print_exc()

    if df is None:
        print("\nAll providers failed.")
        if last_error:
            print(f"Last error: {last_error}")
        return 2

    if df is None or df.empty:
        print("Fetch returned an empty dataframe.")
        return 3

    print(f"\nFetch succeeded via {provider_name}. Rows: {len(df)}, columns: {len(df.columns)}")
    print("Columns:")
    print(list(df.columns))

    visible_columns = [column for column in EASTMONEY_COLUMNS_TO_SHOW if column in df.columns]
    if visible_columns:
        print("\nPreview:")
        print(df[visible_columns].head())
    else:
        print("\nPreview:")
        print(df.head())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
