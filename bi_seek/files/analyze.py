"""舆情统计分析：高频词、情感倾向、地域分布、弹幕时间轴"""
from collections import Counter

from preprocess import tokenize, load_stopwords
from config import BERT_MODEL_NAME, BERT_BATCH_SIZE

# ============================================================
# BERT 情感分析器（懒加载 + SnowNLP fallback）
# ============================================================

_HAS_TRANSFORMERS = False
_HAS_SNOWNLP = False
_pipeline = None
_sentiment_analyzer = None


class SentimentAnalyzer:
    """
    中文情感分析器。
    - 优先使用 BERT 模型（transformers pipeline）
    - 加载失败时自动降级到 SnowNLP
    - 支持批量推理以提升性能
    """

    def __init__(self):
        self._backend = None  # "bert" | "snownlp" | "none"
        self._pipe = None
        self._init_bert()

    def _init_bert(self):
        """尝试加载 BERT 模型"""
        global _HAS_TRANSFORMERS
        try:
            import transformers
            _HAS_TRANSFORMERS = True
        except ImportError:
            print("[warn] transformers 未安装，将使用 SnowNLP 作为情感分析后端")
            self._init_snownlp()
            return

        try:
            self._pipe = transformers.pipeline(
                "text-classification",
                model=BERT_MODEL_NAME,
                tokenizer=BERT_MODEL_NAME,
                top_k=None,  # 返回所有类别的概率
            )
            self._backend = "bert"
            print(f"[info] BERT 情感分析模型加载成功：{BERT_MODEL_NAME}")
        except Exception as e:
            print(f"[warn] BERT 模型加载失败 ({e})，降级到 SnowNLP")
            self._init_snownlp()

    def _init_snownlp(self):
        """初始化 SnowNLP fallback"""
        global _HAS_SNOWNLP
        try:
            import snownlp  # noqa: F401
            _HAS_SNOWNLP = True
            self._backend = "snownlp"
            print("[info] SnowNLP 情感分析后端已就绪")
        except ImportError:
            _HAS_SNOWNLP = False
            self._backend = "none"
            print("[warn] SnowNLP 也未安装，情感分析将返回中性占位值")

    @property
    def backend_name(self):
        return self._backend

    def analyze_one(self, text):
        """分析单条文本的情感，返回 {"label": "positive"/"neutral"/"negative", "score": float}"""
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0}

        if self._backend == "bert":
            return self._bert_single(text)
        elif self._backend == "snownlp":
            return self._snownlp_single(text)
        else:
            return {"label": "neutral", "score": 0.0}

    def analyze_batch(self, texts):
        """
        批量分析文本情感。
        返回与 texts 等长的结果列表，每条为 {"label": ..., "score": ...}
        """
        if not texts:
            return []

        if self._backend == "bert":
            return self._bert_batch(texts)
        elif self._backend == "snownlp":
            return [self._snownlp_single(t) for t in texts]
        else:
            return [{"label": "neutral", "score": 0.0} for _ in texts]

    def _bert_single(self, text):
        result = self._pipe(text, top_k=None)
        return _parse_bert_result(result)

    def _bert_batch(self, texts):
        # 分批处理避免 OOM
        results = []
        for i in range(0, len(texts), BERT_BATCH_SIZE):
            batch = texts[i:i + BERT_BATCH_SIZE]
            batch_results = self._pipe(batch, top_k=None)
            for r in batch_results:
                results.append(_parse_bert_result(r))
        return results

    def _snownlp_single(self, text):
        try:
            from snownlp import SnowNLP
            score = SnowNLP(text).sentiments
        except Exception:
            score = 0.5
        if score >= 0.6:
            return {"label": "positive", "score": score}
        elif score <= 0.4:
            return {"label": "negative", "score": score}
        else:
            return {"label": "neutral", "score": score}


def _parse_bert_result(result):
    """
    解析 BERT pipeline 输出。
    - 如果返回的是列表（top_k=None），取 score 最高的 label
    - 需要适配不同模型的标签名（如 POSITIVE / NEUTRAL / NEGATIVE 或 positive / neutral / negative）
    """
    if isinstance(result, list):
        # 按 score 降序排列
        best = max(result, key=lambda x: x["score"])
        label = best["label"].lower()
        score = best["score"]
    else:
        label = result["label"].lower()
        score = result["score"]

    # 统一标签
    label_map = {
        "positive": "positive", "pos": "positive", "正面": "positive",
        "neutral": "neutral", "neu": "neutral", "中性": "neutral",
        "negative": "negative", "neg": "negative", "负面": "negative",
    }
    return {"label": label_map.get(label, "neutral"), "score": score}


# 全局单例（懒加载）
def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer


# ============================================================
# 情感分布统计
# ============================================================

def sentiment_distribution(texts):
    """
    对文本列表做情感分析，返回正面/中性/负面计数和平均得分。
    使用 BERT 模型（或 fallback 到 SnowNLP）。
    """
    analyzer = get_sentiment_analyzer()
    results = analyzer.analyze_batch(texts)

    pos = sum(1 for r in results if r["label"] == "positive")
    neg = sum(1 for r in results if r["label"] == "negative")
    neu = len(results) - pos - neg
    avg = sum(r["score"] for r in results) / len(results) if results else 0

    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "avg_score": avg,
        "backend": analyzer.backend_name,
    }


def sentiment_score(text):
    """单条文本情感得分（0=负面 ~ 1=正面），兼容旧接口"""
    analyzer = get_sentiment_analyzer()
    result = analyzer.analyze_one(text)
    return result["score"]


# ============================================================
# 词频分析
# ============================================================

def word_frequency(texts, stopwords=None, top_n=50):
    stopwords = stopwords or load_stopwords()
    counter = Counter()
    for t in texts:
        counter.update(tokenize(t, stopwords))
    return counter.most_common(top_n)


# ============================================================
# 地域分布
# ============================================================

def geo_distribution(comments):
    counter = Counter(c["location"] for c in comments if c.get("location"))
    return counter.most_common()


# ============================================================
# 弹幕时间轴分析
# ============================================================

def danmaku_timeline(danmaku_list, bin_seconds=10):
    """
    将弹幕按视频时间分桶，统计每段时间内的弹幕数量和平均情感得分。

    参数：
        danmaku_list: fetch_danmaku() 返回的列表，每项含 time_in_video / text
        bin_seconds: 时间桶宽度（秒），默认 10 秒一个桶

    返回：
        {
            "buckets": [(start_sec, end_sec, count, avg_sentiment), ...],
            "max_density": int,       # 最高密度桶的弹幕数
            "peak_time": float,       # 弹幕最密集的时间点（秒）
            "total_buckets": int,
        }
    """
    if not danmaku_list:
        return {"buckets": [], "max_density": 0, "peak_time": 0, "total_buckets": 0}

    # 过滤有效数据
    valid = [d for d in danmaku_list if d.get("time_in_video") is not None]
    if not valid:
        return {"buckets": [], "max_density": 0, "peak_time": 0, "total_buckets": 0}

    max_time = max(d["time_in_video"] for d in valid)
    num_buckets = max(1, int(max_time // bin_seconds) + 1)

    # 初始化桶
    bucket_counts = [0] * num_buckets
    bucket_sentiments = [[] for _ in range(num_buckets)]

    analyzer = get_sentiment_analyzer()

    for d in valid:
        idx = min(int(d["time_in_video"] // bin_seconds), num_buckets - 1)
        bucket_counts[idx] += 1
        # 存储文本用于批量情感分析
        bucket_sentiments[idx].append(d["text"])

    # 计算每个桶的情感均值
    buckets = []
    max_density = 0
    peak_time = 0

    for i in range(num_buckets):
        count = bucket_counts[i]
        texts = bucket_sentiments[i]
        if texts:
            sentiments = analyzer.analyze_batch(texts)
            avg_s = sum(r["score"] for r in sentiments) / len(sentiments)
        else:
            avg_s = 0.5

        start_sec = i * bin_seconds
        end_sec = min((i + 1) * bin_seconds, max_time)
        buckets.append((start_sec, end_sec, count, round(avg_s, 4)))

        if count > max_density:
            max_density = count
            peak_time = start_sec + bin_seconds / 2

    return {
        "buckets": buckets,
        "max_density": max_density,
        "peak_time": peak_time,
        "total_buckets": num_buckets,
        "bin_seconds": bin_seconds,
    }


def format_time(seconds):
    """将秒数格式化为 mm:ss"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"
