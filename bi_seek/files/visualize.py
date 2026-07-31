"""可视化：词云 + 情感占比图 + 地域分布图 + 弹幕时间轴曲线"""
import os
from wordcloud import WordCloud

# 默认中文字体路径（项目目录下的 simhei.ttf）
_DEFAULT_FONT_PATH = os.path.join(os.path.dirname(__file__), "simhei.ttf")


def make_wordcloud(word_freq, output_path, font_path=None):
    """生成词云图。默认使用项目目录下的 simhei.ttf，无需额外配置。"""
    if font_path is None:
        font_path = _DEFAULT_FONT_PATH
    wc = WordCloud(
        font_path=font_path,
        width=1000,
        height=600,
        background_color="white",
    )
    wc.generate_from_frequencies(dict(word_freq))
    wc.to_file(output_path)
    return output_path


def make_geo_map(geo_freq, output_html_path):
    """使用 pyecharts 生成中国地图分布图（HTML，用浏览器打开查看）"""
    from pyecharts import options as opts
    from pyecharts.charts import Map

    data = [(loc, count) for loc, count in geo_freq if loc and loc not in ("海外", "")]
    if not data:
        return None
    c = (
        Map()
        .add("评论数量", data, "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评论地域分布"),
            visualmap_opts=opts.VisualMapOpts(max_=max(v for _, v in data)),
        )
    )
    c.render(output_html_path)
    return output_html_path


def make_sentiment_pie(sentiment_dist, output_html_path, title="情感倾向占比"):
    """使用 pyecharts 生成情感倾向饼图"""
    from pyecharts import options as opts
    from pyecharts.charts import Pie

    data = [
        ("正面", sentiment_dist["positive"]),
        ("中性", sentiment_dist["neutral"]),
        ("负面", sentiment_dist["negative"]),
    ]
    c = Pie().add("", data).set_global_opts(title_opts=opts.TitleOpts(title=title))
    c.render(output_html_path)
    return output_html_path


def make_danmaku_timeline(timeline_data, output_html_path, title="弹幕时间轴"):
    """
    使用 pyecharts 生成弹幕时间轴曲线图。

    包含两条线：
    - 弹幕密度柱状图（每段时间内的弹幕数量）
    - 情感趋势折线图（每段时间的平均情感得分）

    timeline_data: danmaku_timeline() 的返回值
    """
    from pyecharts import options as opts
    from pyecharts.charts import Bar, Line
    from pyecharts.charts import Grid

    buckets = timeline_data.get("buckets", [])
    if not buckets:
        print("[warn] 弹幕时间轴数据为空，跳过生成")
        return None

    bin_sec = timeline_data.get("bin_seconds", 10)

    # X 轴标签：将秒数格式化为 mm:ss
    from analyze import format_time
    x_labels = [format_time(b[0]) for b in buckets]

    # 弹幕数量
    counts = [b[2] for b in buckets]
    # 情感得分
    sentiments = [b[3] for b in buckets]

    # 柱状图：弹幕密度
    bar = (
        Bar()
        .add_xaxis(x_labels)
        .add_yaxis(
            "弹幕数量",
            counts,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color="#00AEEC"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=f"时间桶宽度: {bin_sec}秒"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            xaxis_opts=opts.AxisOpts(
                name="视频时间",
                axislabel_opts=opts.LabelOpts(rotate=45, interval=max(1, len(x_labels) // 15)),
            ),
            yaxis_opts=opts.AxisOpts(name="弹幕数量"),
        )
    )

    # 折线图：情感趋势（使用双 Y 轴）
    line = (
        Line()
        .add_xaxis(x_labels)
        .add_yaxis(
            "情感得分",
            sentiments,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(color="#FF6B6B", width=2),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.15),
        )
    )

    # 叠加
    bar.overlap(line)

    bar.set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="弹幕数量",
            position="left",
        ),
    )

    # 扩展配置：第二个 Y 轴
    bar.options["yAxis"] = [
        {"type": "value", "name": "弹幕数量", "position": "left"},
        {
            "type": "value",
            "name": "情感得分",
            "position": "right",
            "min": 0,
            "max": 1,
            "axisLabel": {"formatter": "{value}"},
            "splitLine": {"show": False},
        },
    ]

    bar.render(output_html_path)
    return output_html_path
