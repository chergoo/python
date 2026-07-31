"""文本预处理：清洗 + 分词 + 去停用词"""
import re
import jieba

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F000-\U0001F02F"
    "]+",
    flags=re.UNICODE,
)

_URL_PATTERN = re.compile(r"https?://\S+")

DEFAULT_STOPWORDS = set(
    """
的 了 是 我 你 他 她 它 这 那 都 也 在 和 就 不 有 很 啊 吧 呢 吗 哦 嗯
一个 什么 这个 那个 因为 所以 但是 而且 就是 还是 可以 已经 一下 没有
自己 我们 你们 他们 就是 这样 那样 知道 现在
""".split()
)


def load_stopwords(path=None):
    words = set(DEFAULT_STOPWORDS)
    if path:
        with open(path, encoding="utf-8") as f:
            words.update(line.strip() for line in f if line.strip())
    return words


def clean_text(text):
    text = _URL_PATTERN.sub("", text)
    text = _EMOJI_PATTERN.sub("", text)
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", " ", text)
    return text.strip()


def tokenize(text, stopwords):
    words = jieba.lcut(clean_text(text))
    return [w for w in words if len(w) > 1 and w not in stopwords]
