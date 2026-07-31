"""汇总分析结果，生成 Markdown 舆情报告"""
from datetime import datetime

from analyze import format_time


def generate_markdown_report(
    bvid_list,
    danmaku_stats=None,
    comment_stats=None,
    private_msg_count=0,
    output_path="output/report.md",
):
    """
    生成 Markdown 格式的舆情分析报告。

    参数：
        bvid_list: 分析的视频 BV 号列表
        danmaku_stats: 弹幕统计 dict，包含：
            - count: 弹幕总数
            - word_freq: 高频词列表 [(word, freq), ...]
            - sentiment: 情感分布 dict (来自 sentiment_distribution)
            - timeline: 弹幕时间轴 dict (来自 danmaku_timeline)
        comment_stats: 评论统计 dict，包含：
            - count: 评论总数
            - word_freq: 高频词列表
            - sentiment: 情感分布 dict
            - geo: 地域分布列表 [(loc, count), ...]
        private_msg_count: 私信会话数
        output_path: 报告输出路径
    """
    danmaku_stats = danmaku_stats or {}
    comment_stats = comment_stats or {}

    lines = []
    lines.append("# B站舆情分析报告")
    lines.append(f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # ---- 数据概览 ----
    lines.append("## 数据概览\n")
    lines.append(f"- 分析视频数：{len(bvid_list)}")
    d_count = danmaku_stats.get("count", 0)
    c_count = comment_stats.get("count", 0)
    lines.append(f"- 弹幕总数：{d_count}")
    lines.append(f"- 评论总数：{c_count}")
    lines.append(f"- 私信会话数：{private_msg_count}\n")

    d_sent = danmaku_stats.get("sentiment") or {}
    c_sent = comment_stats.get("sentiment") or {}
    d_backend = d_sent.get("backend", "unknown")
    c_backend = c_sent.get("backend", "unknown")
    lines.append(f"- 情感分析引擎：弹幕={d_backend} / 评论={c_backend}\n")

    # ---- 弹幕分析 ----
    if danmaku_stats:
        lines.append("---\n")
        lines.append("## 弹幕分析\n")

        _write_section_wordfreq(lines, "弹幕高频词 Top 20", danmaku_stats.get("word_freq", []))

        _write_section_sentiment(lines, "弹幕情感倾向", d_sent)

        timeline = danmaku_stats.get("timeline") or {}
        if timeline.get("buckets"):
            _write_section_timeline(lines, timeline)

    # ---- 评论分析 ----
    if comment_stats:
        lines.append("---\n")
        lines.append("## 评论分析\n")

        _write_section_wordfreq(lines, "评论高频词 Top 20", comment_stats.get("word_freq", []))

        _write_section_sentiment(lines, "评论情感倾向", c_sent)

        geo = comment_stats.get("geo", [])
        if geo:
            _write_section_geo(lines, geo)

    # ---- 私信 ----
    if private_msg_count > 0:
        lines.append("---\n")
        lines.append("## 私信\n")
        lines.append(f"- 活跃会话数：{private_msg_count}")
        lines.append(f"- 注：私信详细分析功能待扩展\n")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


def _write_section_wordfreq(lines, title, word_freq):
    lines.append(f"### {title}\n")
    lines.append("| 排名 | 词语 | 频次 |")
    lines.append("|---|---|---|")
    for i, (word, freq) in enumerate(word_freq[:20], 1):
        lines.append(f"| {i} | {word} | {freq} |")
    lines.append("")


def _write_section_sentiment(lines, title, sentiment):
    sentiment = sentiment or {}
    total = sum(sentiment.get(k, 0) for k in ("positive", "neutral", "negative")) or 1
    lines.append(f"### {title}\n")
    lines.append(f"- 正面：{sentiment.get('positive', 0)} ({sentiment.get('positive', 0) / total:.1%})")
    lines.append(f"- 中性：{sentiment.get('neutral', 0)} ({sentiment.get('neutral', 0) / total:.1%})")
    lines.append(f"- 负面：{sentiment.get('negative', 0)} ({sentiment.get('negative', 0) / total:.1%})")
    lines.append(f"- 平均情感得分：{sentiment.get('avg_score', 0):.3f}（0=负面，1=正面）")
    engine = sentiment.get("backend", "unknown")
    lines.append(f"- 分析引擎：{engine}\n")


def _write_section_timeline(lines, timeline):
    lines.append("### 弹幕时间轴\n")
    peak = timeline.get("peak_time", 0)
    max_density = timeline.get("max_density", 0)
    bin_sec = timeline.get("bin_seconds", 10)
    buckets = timeline.get("buckets", [])

    lines.append(f"- 弹幕最密集时段：{format_time(peak)} 附近（约 {max_density} 条/{bin_sec}秒）")
    lines.append(f"- 时间桶宽度：{bin_sec} 秒")
    lines.append(f"- 总桶数：{timeline.get('total_buckets', 0)}\n")

    # 列出 TOP 5 密度最高时段
    sorted_buckets = sorted(buckets, key=lambda b: b[2], reverse=True)
    lines.append("**弹幕密度 Top 5 时段：**\n")
    lines.append("| 时段 | 弹幕数 | 平均情感得分 |")
    lines.append("|---|---|---|")
    for b in sorted_buckets[:5]:
        time_range = f"{format_time(b[0])} - {format_time(b[1])}"
        lines.append(f"| {time_range} | {b[2]} | {b[3]:.3f} |")
    lines.append("")


def _write_section_geo(lines, geo):
    lines.append("### 评论地域分布 Top 10\n")
    lines.append("| 地区 | 评论数 |")
    lines.append("|---|---|")
    for loc, count in geo[:10]:
        lines.append(f"| {loc} | {count} |")
    lines.append("")
