# -*- coding: utf-8 -*-
"""
A-share random picker backend.

The service fetches a full-market snapshot, keeps it in memory, and serves
random picks from that local cache. Manual refresh is available through
POST /api/refresh.
"""

from __future__ import annotations

import os
import json
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template


app = Flask(__name__)

DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

INITIAL_RETRY_SECONDS = 5
MAX_RETRY_SECONDS = 60
CACHE_FILE = Path(__file__).with_name("stock_cache.json")

PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)

STOCK_COLUMNS = {
    "code": "\u4ee3\u7801",
    "name": "\u540d\u79f0",
    "price": "\u6700\u65b0\u4ef7",
    "prev_close": "\u6628\u6536",
    "change_amt": "\u6da8\u8dcc\u989d",
    "change_pct": "\u6da8\u8dcc\u5e45",
    "open": "\u4eca\u5f00",
    "high": "\u6700\u9ad8",
    "low": "\u6700\u4f4e",
    "volume": "\u6210\u4ea4\u91cf",
    "turnover": "\u6210\u4ea4\u989d",
    "market_cap": "\u603b\u5e02\u503c",
    "pe_ratio": "\u5e02\u76c8\u7387-\u52a8\u6001",
    "turnover_rate": "\u6362\u624b\u7387",
}


@dataclass
class CacheState:
    stocks: list[dict[str, Any]]
    updated_at: float
    initialized: bool
    refreshing: bool = False
    last_error: str | None = None
    source: str = "empty"


_cache = CacheState(stocks=[], updated_at=0.0, initialized=False)
_cache_lock = threading.Lock()
_refresh_lock = threading.Lock()
_bootstrap_started = False


def _load_cache_from_disk() -> bool:
    if not CACHE_FILE.exists():
        return False

    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        stocks = data.get("stocks") or []
        updated_at = float(data.get("updated_at") or 0)
        source = str(data.get("source") or "disk")
    except Exception as exc:
        print(f"Failed to load local stock cache: {exc}", flush=True)
        return False

    if not isinstance(stocks, list) or not stocks:
        return False

    with _cache_lock:
        _cache.stocks = stocks
        _cache.updated_at = updated_at
        _cache.initialized = True
        _cache.source = f"disk:{source.removeprefix('network:')}"

    print(f"Loaded local stock cache: {len(stocks)} stocks.", flush=True)
    return True


def _save_cache_to_disk(
    stocks: list[dict[str, Any]], updated_at: float, source: str
) -> None:
    payload = {
        "updated_at": updated_at,
        "saved_at": time.time(),
        "source": source,
        "stocks": stocks,
    }

    try:
        CACHE_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"Failed to save local stock cache: {exc}", flush=True)


def _disable_proxies() -> None:
    """Prevent akshare/requests from accidentally using system proxy settings."""
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


def _infer_board(code: str) -> str:
    if code.startswith(("600", "601", "603", "605")):
        return "\u6caa\u5e02\u4e3b\u677f"
    if code.startswith("688"):
        return "\u79d1\u521b\u677f"
    if code.startswith(("000", "001")):
        return "\u6df1\u5e02\u4e3b\u677f"
    if code.startswith(("002", "003")):
        return "\u6df1\u5e02\u4e2d\u5c0f\u677f"
    if code.startswith(("300", "301")):
        return "\u521b\u4e1a\u677f"
    if code.startswith(("83", "87", "43", "92")):
        return "\u5317\u4ea4\u6240"
    return "\u672a\u77e5\u677f\u5757"


def _infer_exchange(code: str) -> str:
    if code.startswith(("6", "9")):
        return "SH"
    if code.startswith(("0", "2", "3")):
        return "SZ"
    if code.startswith(("8", "4")):
        return "BJ"
    return "--"


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value in (None, "", "--", "-"):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    return int(_safe_float(value, float(default)))


def _row_value(row: Any, key: str, default: Any = None) -> Any:
    return row.get(STOCK_COLUMNS[key], default)


def _normalize_stock(row: Any) -> dict[str, Any] | None:
    raw_code = str(_row_value(row, "code", "")).strip()
    code_digits = "".join(ch for ch in raw_code if ch.isdigit())
    code = code_digits[-6:].zfill(6)
    if not code or not code.isdigit():
        return None

    board = _infer_board(code)
    if board == "\u5317\u4ea4\u6240":
        return None

    price = _safe_float(_row_value(row, "price"))
    prev_close = _safe_float(_row_value(row, "prev_close"))
    if price <= 0 < prev_close:
        price = prev_close

    open_price = _safe_float(_row_value(row, "open"))
    high = _safe_float(_row_value(row, "high"))
    low = _safe_float(_row_value(row, "low"))

    return {
        "code": code,
        "name": str(_row_value(row, "name", "\u672a\u77e5\u80a1\u7968")),
        "board": board,
        "exchange": _infer_exchange(code),
        "price": price,
        "prev_close": prev_close,
        "change_amt": _safe_float(_row_value(row, "change_amt")),
        "change_pct": _safe_float(_row_value(row, "change_pct")),
        "open": open_price if open_price > 0 else price,
        "high": high if high > 0 else price,
        "low": low if low > 0 else price,
        "volume": _safe_int(_row_value(row, "volume")),
        "turnover": _safe_float(_row_value(row, "turnover")),
        "market_cap": _safe_float(_row_value(row, "market_cap")),
        "pe_ratio": _row_value(row, "pe_ratio", "--"),
        "turnover_rate": _safe_float(_row_value(row, "turnover_rate")),
        "is_mock": False,
    }


def _fetch_stock_pool() -> tuple[list[dict[str, Any]], str]:
    _disable_proxies()

    import akshare as ak

    errors = []
    providers = (
        ("sina", ak.stock_zh_a_spot),
        ("eastmoney", ak.stock_zh_a_spot_em),
    )

    for provider_name, fetcher in providers:
        try:
            print(f"Trying akshare provider: {provider_name}", flush=True)
            df = fetcher()
            return _normalize_stock_pool(df), provider_name
        except Exception as exc:
            errors.append(f"{provider_name}: {exc}")
            print(f"Provider failed: {provider_name}: {exc}", flush=True)

    raise RuntimeError("; ".join(errors))


def _normalize_stock_pool(df: Any) -> list[dict[str, Any]]:
    if df is None or df.empty:
        raise RuntimeError("akshare returned an empty stock snapshot")

    pool = []
    for _, row in df.iterrows():
        stock = _normalize_stock(row)
        if stock:
            pool.append(stock)

    if not pool:
        raise RuntimeError("no valid A-share records found in snapshot")

    return pool


def _refresh_stock_pool(force: bool = False) -> bool:
    """Refresh the cache and keep the previous cache if fetching fails."""
    with _cache_lock:
        if not force and _cache.initialized and _cache.stocks:
            return True

    acquired = _refresh_lock.acquire(blocking=force)
    if not acquired:
        with _cache_lock:
            return _cache.initialized and bool(_cache.stocks)

    with _cache_lock:
        _cache.refreshing = True

    try:
        try:
            print("Fetching full-market A-share snapshot...", flush=True)
            stocks, provider_name = _fetch_stock_pool()
        except Exception as exc:
            with _cache_lock:
                _cache.last_error = str(exc)
            print(f"Snapshot refresh failed: {exc}", flush=True)
            _load_cache_from_disk()
            return False

        now = time.time()
        source = f"network:{provider_name}"
        _save_cache_to_disk(stocks, now, source)

        with _cache_lock:
            _cache.stocks = stocks
            _cache.updated_at = now
            _cache.initialized = True
            _cache.last_error = None
            _cache.source = source

        print(
            f"Snapshot refreshed successfully via {provider_name}: {len(stocks)} stocks.",
            flush=True,
        )
        return True
    finally:
        with _cache_lock:
            _cache.refreshing = False
        _refresh_lock.release()


def _bootstrap_worker() -> None:
    """Retry in the background with backoff until the first snapshot succeeds."""
    retry_seconds = INITIAL_RETRY_SECONDS

    while True:
        if _refresh_stock_pool(force=True):
            return

        print(
            f"Initial snapshot failed; retrying in {retry_seconds} seconds...",
            flush=True,
        )
        time.sleep(retry_seconds)
        retry_seconds = min(retry_seconds * 2, MAX_RETRY_SECONDS)


def _start_bootstrap_once() -> None:
    global _bootstrap_started

    if _bootstrap_started:
        return

    _bootstrap_started = True
    threading.Thread(target=_bootstrap_worker, daemon=True).start()


def _format_timestamp(timestamp: float) -> str | None:
    if not timestamp:
        return None
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/random")
def api_random():
    _refresh_stock_pool(force=False)

    with _cache_lock:
        if not _cache.stocks:
            return (
                jsonify(
                    {
                        "error": _cache.last_error
                        or "\u80a1\u7968\u6c60\u5c1a\u672a\u521d\u59cb\u5316\u6210\u529f\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002",
                        "refreshing": _cache.refreshing,
                    }
                ),
                503,
            )

        stock_data = random.choice(_cache.stocks)
        updated_at = _cache.updated_at
        last_error = _cache.last_error
        refreshing = _cache.refreshing
        source = _cache.source

    return jsonify(
        {
            "stock": stock_data,
            "meta": {
                "updated_at": _format_timestamp(updated_at),
                "error": last_error,
                "refreshing": refreshing,
                "source": source,
            },
        }
    )


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    success = _refresh_stock_pool(force=True)

    with _cache_lock:
        count = len(_cache.stocks)
        updated_at = _cache.updated_at
        last_error = _cache.last_error
        source = _cache.source

    payload = {
        "success": success,
        "updated_at": _format_timestamp(updated_at),
        "count": count,
        "error": last_error,
        "source": source,
    }
    status_code = 200 if success else 503
    return jsonify(payload), status_code


if __name__ == "__main__":
    _load_cache_from_disk()
    _start_bootstrap_once()
    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)
