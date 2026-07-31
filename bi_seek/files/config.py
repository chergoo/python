"""
配置文件：填写你自己的 Cookie、目标视频列表等
"""

# ============================================================
# 数据类型开关：独立控制是否抓取和分析每种数据
# ============================================================
# 弹幕和评论是公开数据，无需登录即可抓取
ENABLE_DANMAKU = True        # 是否抓取和分析弹幕
ENABLE_COMMENTS = True       # 是否抓取和分析评论
ENABLE_PRIVATE_MSGS = False  # 是否抓取和分析私信（需要登录态）

# ============================================================
# 登录凭证（仅私信分析需要）
# 从浏览器登录 B 站后，在开发者工具 Network 面板的请求 Cookie 中
# 复制 SESSDATA 和 bili_jct 字段。
# 这是你账号的登录凭证，不要写入公开仓库，也不要分享给任何人。
# 如果只分析弹幕和评论，可以留空。
# ============================================================
SESSDATA = ""
BILI_JCT = ""  # 即 csrf token

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com",
}

# 要分析的视频 BV 号列表，按需修改
TARGET_BVIDS = [
    "BV1xx411c7mD",
]

# 抓取每个视频评论的最大页数（每页约20条），控制抓取总量
MAX_COMMENT_PAGES = 50

# 每次请求之间的间隔秒数，避免触发风控
REQUEST_INTERVAL = 1.0

# 输出目录（报告、图表都会存到这里）
OUTPUT_DIR = "output"

# ============================================================
# BERT 情感分析模型配置
# 使用 transformers 库加载中文情感分析模型，比 SnowNLP 更准确。
# 模型首次加载时会自动从 HuggingFace 下载（约 400MB），
# 如果下载失败会自动降级到 SnowNLP。
# ============================================================
BERT_MODEL_NAME = "luhuihuifighting/chinese_sentiment_analysis"
BERT_BATCH_SIZE = 16  # 批量推理时每批文本数量
