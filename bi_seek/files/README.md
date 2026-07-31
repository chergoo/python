# B站舆情分析脚本

统计视频弹幕、评论区、私信（自己账号）的高频词、情感倾向、地域分布，并生成 Markdown 报告。

## 快速开始

```bash
pip install -r requirements.txt
```

编辑 `config.py`：
- `TARGET_BVIDS`：填要分析的视频 BV 号列表
- `SESSDATA` / `BILI_JCT`：如果要抓自己的私信，登录 B 站网页版后从浏览器
  开发者工具 → Network → 任意请求的 Cookie 中复制这两个字段；
  只抓公开评论/弹幕的话可以留空

```bash
python main.py
```

运行后 `output/` 目录下会生成：
- `wordcloud.png` 高频词词云
- `sentiment_pie.html` 情感占比图（浏览器打开）
- `geo_map.html` 评论地域分布地图（浏览器打开，评论数据里有地域信息时才生成）
- `report.md` 汇总报告

## 中文词云乱码

`WordCloud` 默认字体不含中文字形，需要在 `visualize.make_wordcloud` 调用时传入
系统里存在的中文字体路径，例如：
- macOS: `/System/Library/Fonts/PingFang.ttc`
- Windows: `C:/Windows/Fonts/simhei.ttf`
- Linux: 需要自行安装中文字体包（如 `fonts-noto-cjk`）后指定路径

## 模块说明

| 文件 | 作用 |
|---|---|
| `config.py` | 配置：Cookie、目标视频、抓取参数 |
| `utils.py` | 请求封装（限速+重试） |
| `crawler.py` | 抓取弹幕/评论/私信 |
| `preprocess.py` | 文本清洗、jieba分词、停用词过滤 |
| `analyze.py` | 高频词统计、情感分析(SnowNLP)、地域分布统计 |
| `visualize.py` | 词云、情感占比图、地域地图(pyecharts) |
| `report.py` | 生成 Markdown 报告 |
| `main.py` | 串联整个流程的入口脚本 |

## 可以扩展的方向

- **情感模型**：SnowNLP 是通用模型，对弹幕缩写、玩梗、反讽准确率有限，
  数据量大时可以换成基于 BERT 的中文情感分类模型（如 `paddlenlp` 的
  `ernie-3.0-sentiment` 或自己标注一批弹幕微调）
- **热度时间轴**：弹幕自带 `send_time`，可以按时间分桶画出"槽点/高潮"曲线，
  定位某个时间点弹幕突然爆发的原因
- **多视频对比**：`TARGET_BVIDS` 支持多个视频，可以在报告里加一个跨视频对比表
- **敏感词/风险词监测**：加一份自定义关键词表，命中就在报告里高亮标出，
  适合做品牌/事件类的舆情监控
- **导出为 Word/PDF**：如果需要正式汇报用的文档，可以把 `report.md` 的内容
  用 `python-docx` 或 pandoc 转成 docx/pdf

## 注意事项

- 请只抓取公开可见的视频弹幕/评论数据，私信只抓自己账号的，不要用于获取他人隐私信息
- 控制好请求频率（`config.REQUEST_INTERVAL`），避免触发风控或对服务器造成压力
- 私信、评论等接口均为社区逆向整理的非官方接口，可能随 B 站改版失效，
  出问题时可以去 `SocialSisterYi/bilibili-API-collect` 这个仓库查最新接口文档
- `SESSDATA` 是账号登录凭证，注意保管，不要提交到公开代码仓库
