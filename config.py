# config.py - 通用论文抓取配置
# 纯配置文件，无代码逻辑，修改以下参数即可切换抓取领域

# GitHub配置（必填）
GITHUB_TOKEN = "ghp_xxx"
REPO_OWNER = "AAA"
REPO_NAME = "xxx"

# 筛选核心配置
PAPER_COUNT = 5                # 最终推送的论文数量
TIME_RANGE_DAYS = 500          # 抓取近N天发表的论文
MIN_CITATION_THRESHOLD = 5     # 临时降低引用量门槛，先保证有论文
TOTAL_CRAWL_COUNT = 300        # 总抓取候选论文数（多轮拆分）
CRAWL_BATCH_SIZE = 100         # 每轮抓取数量
CRAWL_DELAY = 1.5              # 轮次间延迟（避免API限流）

# 自定义查询配置（修改这里切换抓取领域）
SEARCH_KEYWORDS = "machine learning"  # 任意领域关键词
# 暂时关闭语言过滤（避免参数格式错误）
LANGUAGE_SCOPE = ""                # 留空=不限语言，避免400错误

# 通用高影响因子期刊列表（机器学习领域适配）
HIGH_IMPACT_JOURNALS = [
    # ML/AI顶刊
    "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "Journal of Machine Learning Research",
    "Neural Computing and Applications",
    "Pattern Recognition",
    "IEEE Transactions on Neural Networks and Learning Systems",
    "Computational Intelligence and Neuroscience",
    # 通用顶刊
    "Nature Machine Intelligence",
    "Science Robotics"
]