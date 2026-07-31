"""
B站舆情分析工具 — 运行入口

用法：
    python main.py              # 交互式菜单，选择要分析的数据类型
    python main.py --all        # 抓取分析全部（弹幕 + 评论 + 私信）
    python main.py --danmaku    # 仅抓取分析弹幕（无需登录）
    python main.py --comments   # 仅抓取分析评论（无需登录）
    python main.py --private    # 仅抓取分析私信（需要登录）

弹幕和评论为公开数据，无需配置 SESSDATA 即可分析。
私信分析需要在 config.py 中填写 SESSDATA 和 BILI_JCT。
"""
import os
import sys

from config import (
    TARGET_BVIDS, OUTPUT_DIR,
    ENABLE_DANMAKU, ENABLE_COMMENTS, ENABLE_PRIVATE_MSGS,
)
from crawler import crawl_danmaku_only, crawl_comments_only, crawl_private_msgs_only
from preprocess import load_stopwords
from analyze import (
    word_frequency, sentiment_distribution, geo_distribution,
    danmaku_timeline, get_sentiment_analyzer,
)
from visualize import (
    make_wordcloud, make_geo_map, make_sentiment_pie, make_danmaku_timeline,
)
from report import generate_markdown_report


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 独立分析流程
# ============================================================

def analyze_danmaku():
    """弹幕分析流程（无需登录）"""
    print("\n" + "=" * 50)
    print("  📊 弹幕分析")
    print("=" * 50)

    # 1. 抓取
    print("\n[1/4] 抓取弹幕数据...")
    danmaku_list = crawl_danmaku_only()
    if not danmaku_list:
        print("[warn] 未抓取到弹幕数据，跳过分析")
        return {"count": 0, "word_freq": [], "sentiment": None, "timeline": None}
    print(f"  抓取到 {len(danmaku_list)} 条弹幕")

    # 2. 文本分析
    print("\n[2/4] 文本分析...")
    stopwords = load_stopwords()
    texts = [d["text"] for d in danmaku_list]

    print("  - 词频分析...")
    wf = word_frequency(texts, stopwords, top_n=100)

    print("  - 情感分析 (BERT)...")
    sd = sentiment_distribution(texts)
    print(f"    引擎: {sd.get('backend', 'unknown')} | 正面:{sd['positive']} 中性:{sd['neutral']} 负面:{sd['negative']}")

    print("  - 时间轴分析...")
    tl = danmaku_timeline(danmaku_list, bin_seconds=10)
    if tl["buckets"]:
        peak_str = f"{int(tl['peak_time'] // 60)}:{int(tl['peak_time'] % 60):02d}"
        print(f"    弹幕峰值在 {peak_str} 附近，密度 {tl['max_density']} 条/10秒")

    # 3. 可视化
    print("\n[3/4] 生成可视化...")
    make_wordcloud(wf, os.path.join(OUTPUT_DIR, "danmaku_wordcloud.png"))
    print("  ✓ danmaku_wordcloud.png")

    make_sentiment_pie(sd, os.path.join(OUTPUT_DIR, "danmaku_sentiment_pie.html"),
                       title="弹幕情感倾向占比")
    print("  ✓ danmaku_sentiment_pie.html")

    if tl["buckets"]:
        make_danmaku_timeline(tl, os.path.join(OUTPUT_DIR, "danmaku_timeline.html"),
                              title="弹幕时间轴与情感趋势")
        print("  ✓ danmaku_timeline.html")

    stats = {
        "count": len(danmaku_list),
        "word_freq": wf,
        "sentiment": sd,
        "timeline": tl,
    }

    print(f"\n[4/4] 弹幕分析完成 ✓")
    return stats


def analyze_comments():
    """评论分析流程（无需登录）"""
    print("\n" + "=" * 50)
    print("  💬 评论分析")
    print("=" * 50)

    # 1. 抓取
    print("\n[1/4] 抓取评论数据...")
    comment_list = crawl_comments_only()
    if not comment_list:
        print("[warn] 未抓取到评论数据，跳过分析")
        return {"count": 0, "word_freq": [], "sentiment": None, "geo": []}
    print(f"  抓取到 {len(comment_list)} 条评论")

    # 2. 文本分析
    print("\n[2/4] 文本分析...")
    stopwords = load_stopwords()
    texts = [c["content"] for c in comment_list]

    print("  - 词频分析...")
    wf = word_frequency(texts, stopwords, top_n=100)

    print("  - 情感分析 (BERT)...")
    sd = sentiment_distribution(texts)
    print(f"    引擎: {sd.get('backend', 'unknown')} | 正面:{sd['positive']} 中性:{sd['neutral']} 负面:{sd['negative']}")

    print("  - 地域分布...")
    gd = geo_distribution(comment_list)
    if gd:
        print(f"    Top 3: {', '.join(f'{loc}({cnt})' for loc, cnt in gd[:3])}")

    # 3. 可视化
    print("\n[3/4] 生成可视化...")
    make_wordcloud(wf, os.path.join(OUTPUT_DIR, "comment_wordcloud.png"))
    print("  ✓ comment_wordcloud.png")

    make_sentiment_pie(sd, os.path.join(OUTPUT_DIR, "comment_sentiment_pie.html"),
                       title="评论情感倾向占比")
    print("  ✓ comment_sentiment_pie.html")

    if gd:
        make_geo_map(gd, os.path.join(OUTPUT_DIR, "geo_map.html"))
        print("  ✓ geo_map.html")
    else:
        print("  - 无地域数据，跳过地图")

    stats = {
        "count": len(comment_list),
        "word_freq": wf,
        "sentiment": sd,
        "geo": gd,
    }

    print(f"\n[4/4] 评论分析完成 ✓")
    return stats


def analyze_private_msgs():
    """私信分析流程（需要登录）"""
    print("\n" + "=" * 50)
    print("  ✉️  私信分析")
    print("=" * 50)

    print("\n[1/2] 抓取私信数据...")
    msgs = crawl_private_msgs_only()
    count = len(msgs)
    print(f"  抓取到 {count} 个活跃会话")

    print("\n[2/2] 私信分析完成（详细分析功能待扩展）✓")
    return count


# ============================================================
# 菜单与入口
# ============================================================

def show_menu():
    """显示交互式菜单"""
    print("\n" + "=" * 50)
    print("  B站舆情分析工具")
    print("=" * 50)
    print()
    print("  请选择要抓取分析的数据类型：")
    print()
    print("  1. 弹幕分析  (无需登录)")
    print("  2. 评论分析  (无需登录)")
    print("  3. 私信分析  (需要登录)")
    print("  4. 全部      (弹幕+评论+私信)")
    print("  0. 退出")
    print()

    while True:
        try:
            choice = input("  请输入选项 [0-4]: ").strip()
            if choice in ("0", "1", "2", "3", "4"):
                return choice
            print("  请输入 0-4 之间的数字")
        except (EOFError, KeyboardInterrupt):
            print()
            return "0"


def run_interactive():
    """交互式运行"""
    choice = show_menu()

    if choice == "0":
        print("已退出")
        return

    ensure_output_dir()

    danmaku_stats = None
    comment_stats = None
    private_msg_count = 0

    if choice == "1":
        danmaku_stats = analyze_danmaku()
    elif choice == "2":
        comment_stats = analyze_comments()
    elif choice == "3":
        private_msg_count = analyze_private_msgs()
    elif choice == "4":
        danmaku_stats = analyze_danmaku()
        comment_stats = analyze_comments()
        private_msg_count = analyze_private_msgs()

    # 生成报告
    print("\n" + "=" * 50)
    print("  📝 生成报告")
    print("=" * 50)
    report_path = generate_markdown_report(
        TARGET_BVIDS,
        danmaku_stats=danmaku_stats,
        comment_stats=comment_stats,
        private_msg_count=private_msg_count,
        output_path=os.path.join(OUTPUT_DIR, "report.md"),
    )
    print(f"\n✅ 报告已生成：{report_path}")
    print(f"   所有输出文件在：{os.path.abspath(OUTPUT_DIR)}/")


def run_cli():
    """命令行参数运行"""
    ensure_output_dir()

    arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""

    danmaku_stats = None
    comment_stats = None
    private_msg_count = 0

    if arg == "--danmaku" or arg == "-d":
        danmaku_stats = analyze_danmaku()
    elif arg == "--comments" or arg == "-c":
        comment_stats = analyze_comments()
    elif arg == "--private" or arg == "-p":
        private_msg_count = analyze_private_msgs()
    elif arg == "--all" or arg == "-a":
        danmaku_stats = analyze_danmaku()
        comment_stats = analyze_comments()
        private_msg_count = analyze_private_msgs()
    else:
        # 无参数或无效参数：用 config 中的开关
        print("[info] 使用 config.py 中的开关配置运行")
        if ENABLE_DANMAKU:
            danmaku_stats = analyze_danmaku()
        if ENABLE_COMMENTS:
            comment_stats = analyze_comments()
        if ENABLE_PRIVATE_MSGS:
            private_msg_count = analyze_private_msgs()

        if not any([ENABLE_DANMAKU, ENABLE_COMMENTS, ENABLE_PRIVATE_MSGS]):
            print("[warn] config.py 中所有开关均已关闭，无任务执行。")
            print("       请在 config.py 中开启 ENABLE_DANMAKU / ENABLE_COMMENTS / ENABLE_PRIVATE_MSGS")
            print("       或使用 --danmaku / --comments / --private / --all 参数")
            return

    # 生成报告
    print("\n" + "=" * 50)
    print("  📝 生成报告")
    print("=" * 50)
    report_path = generate_markdown_report(
        TARGET_BVIDS,
        danmaku_stats=danmaku_stats,
        comment_stats=comment_stats,
        private_msg_count=private_msg_count,
        output_path=os.path.join(OUTPUT_DIR, "report.md"),
    )
    print(f"\n✅ 报告已生成：{report_path}")
    print(f"   所有输出文件在：{os.path.abspath(OUTPUT_DIR)}/")


def main():
    # 提前初始化情感分析器（让用户知道模型加载状态）
    print("=" * 50)
    print("  B站舆情分析工具 v2.0")
    print("=" * 50)
    print("\n[init] 初始化情感分析引擎...")
    analyzer = get_sentiment_analyzer()
    print(f"[init] 当前后端：{analyzer.backend_name}")

    # 判断运行模式
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
