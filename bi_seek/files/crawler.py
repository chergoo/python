"""
B站数据抓取模块。

接口来源参考社区整理的非官方文档：
https://github.com/SocialSisterYi/bilibili-API-collect
使用前请确认抓取行为符合 B 站用户协议与当地法律法规：
- 只抓取公开可见的视频弹幕/评论区数据
- 私信只抓取自己登录账号的收件箱，不要用于获取他人隐私信息
- 控制请求频率（见 config.REQUEST_INTERVAL），避免对服务器造成压力

弹幕和评论为公开接口，无需登录态；
私信接口需要 SESSDATA 登录凭证。
"""
import xml.etree.ElementTree as ET

from config import (
    SESSDATA, BILI_JCT, TARGET_BVIDS, MAX_COMMENT_PAGES,
    ENABLE_DANMAKU, ENABLE_COMMENTS, ENABLE_PRIVATE_MSGS,
)
from utils import get_json, get_bytes

COOKIES = {"SESSDATA": SESSDATA, "bili_jct": BILI_JCT} if SESSDATA else None


def get_cid(bvid):
    """通过 BV 号获取视频 cid（抓弹幕池需要用到）"""
    data = get_json(
        "https://api.bilibili.com/x/player/pagelist",
        params={"bvid": bvid},
    )
    if not data or data.get("code") != 0:
        print(f"[error] 获取 cid 失败: {bvid} -> {data}")
        return None
    return data["data"][0]["cid"]


def fetch_danmaku(cid):
    """
    抓取实时弹幕池（近期弹幕，约1000条上限；历史弹幕需要大会员接口，此处从略）。
    无需登录态。
    """
    xml_bytes = get_bytes(f"https://comment.bilibili.com/{cid}.xml")
    root = ET.fromstring(xml_bytes)
    result = []
    for d in root.findall("d"):
        attrs = (d.get("p") or "").split(",")
        result.append({
            "time_in_video": float(attrs[0]) if attrs and attrs[0] else None,
            "send_time": int(attrs[4]) if len(attrs) > 4 else None,
            "text": d.text or "",
        })
    return result


def fetch_comments(bvid, max_pages=MAX_COMMENT_PAGES):
    """
    抓取视频评论区一级评论，使用 reply 分页接口。
    返回字段包含昵称、内容、点赞数、IP属地(location)等。
    公开接口，无需登录态也可获取。
    """
    view_data = get_json(
        "https://api.bilibili.com/x/web-interface/view", params={"bvid": bvid}
    )
    if not view_data or view_data.get("code") != 0:
        print(f"[error] 获取视频信息失败: {bvid}")
        return []
    oid = view_data["data"]["aid"]

    comments = []
    for page in range(max_pages):
        data = get_json(
            "https://api.bilibili.com/x/v2/reply",
            params={"type": 1, "oid": oid, "sort": 2, "pn": page + 1, "ps": 20},
            # 不传 cookies：公开评论区无需登录即可获取
        )
        if not data or data.get("code") != 0:
            break
        replies = (data.get("data") or {}).get("replies") or []
        if not replies:
            break
        for r in replies:
            location = (r.get("reply_control") or {}).get("location", "")
            comments.append({
                "uname": r["member"]["uname"],
                "content": r["content"]["message"],
                "like": r["like"],
                "location": location.replace("IP属地：", "").strip(),
                "ctime": r["ctime"],
            })
        if len(replies) < 20:
            break
    return comments


def fetch_private_messages():
    """
    抓取自己账号的私信会话列表（需要登录态 SESSDATA）。
    该接口未被官方公开文档化，仅用于对自己收件箱做统计分析，
    请勿用于获取他人隐私信息，且注意接口可能随时变化失效。
    """
    if not COOKIES:
        print("[warn] 未配置 SESSDATA，无法抓取私信。请在 config.py 中填写 SESSDATA。")
        return []
    data = get_json(
        "https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions",
        params={"session_type": 1},
        cookies=COOKIES,
    )
    if not data or data.get("code") != 0:
        print(f"[error] 获取私信会话失败: {data}")
        return []
    return (data.get("data") or {}).get("session_list") or []


# ============================================================
# 按需抓取入口
# ============================================================

def crawl_danmaku_only():
    """仅抓取弹幕数据（无需登录）"""
    result = []
    for bvid in TARGET_BVIDS:
        print(f"[info] 抓取弹幕 {bvid} ...")
        cid = get_cid(bvid)
        if cid:
            result.extend(fetch_danmaku(cid))
    return result


def crawl_comments_only():
    """仅抓取评论数据（无需登录）"""
    result = []
    for bvid in TARGET_BVIDS:
        print(f"[info] 抓取评论 {bvid} ...")
        result.extend(fetch_comments(bvid))
    return result


def crawl_private_msgs_only():
    """仅抓取私信数据（需要登录）"""
    return fetch_private_messages()


def crawl_all():
    """
    根据 config 中的开关按需抓取数据。
    返回字典，未启用的类型对应空列表。
    """
    result = {"comments": [], "danmaku": [], "private_messages": []}

    if ENABLE_DANMAKU:
        print("=" * 40)
        print("[info] 开始抓取弹幕（无需登录）...")
        result["danmaku"] = crawl_danmaku_only()
        print(f"[info] 弹幕抓取完成，共 {len(result['danmaku'])} 条")

    if ENABLE_COMMENTS:
        print("=" * 40)
        print("[info] 开始抓取评论（无需登录）...")
        result["comments"] = crawl_comments_only()
        print(f"[info] 评论抓取完成，共 {len(result['comments'])} 条")

    if ENABLE_PRIVATE_MSGS:
        print("=" * 40)
        print("[info] 开始抓取私信（需要登录）...")
        result["private_messages"] = crawl_private_msgs_only()
        print(f"[info] 私信抓取完成，共 {len(result['private_messages'])} 个会话")

    return result
