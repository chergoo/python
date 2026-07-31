"""通用请求封装：限速 + 简单重试"""
import time
import requests

from config import HEADERS, REQUEST_INTERVAL

_session = requests.Session()
_session.headers.update(HEADERS)


def get_json(url, params=None, cookies=None, retry=3):
    """GET 请求并解析为 JSON，带简单重试和限速，失败返回 None"""
    for attempt in range(retry):
        try:
            resp = _session.get(url, params=params, cookies=cookies, timeout=10)
            resp.raise_for_status()
            time.sleep(REQUEST_INTERVAL)
            return resp.json()
        except Exception as e:  # noqa: BLE001 - 抓取脚本容忍各种网络异常
            print(f"[warn] 请求失败({attempt + 1}/{retry}): {url} -> {e}")
            time.sleep(2 * (attempt + 1))
    return None


def get_bytes(url, params=None, cookies=None):
    """GET 请求并返回原始字节内容（用于弹幕 XML 等）"""
    resp = _session.get(url, params=params, cookies=cookies, timeout=10)
    resp.raise_for_status()
    time.sleep(REQUEST_INTERVAL)
    return resp.content
