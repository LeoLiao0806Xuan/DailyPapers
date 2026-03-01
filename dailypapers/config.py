# config.py
# 纯配置文件，无任何代码/内置/兜底
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
REPO_OWNER = "YOUR_REPO_OWNER"
REPO_NAME = "YOUR_REPO_NAME"

# 筛选配置（保证权威性）
PAPER_COUNT = 5
TIME_RANGE_DAYS = 500
MIN_CITATION_THRESHOLD = 5     # 临时降低引用量门槛，先保证有论文
TOTAL_CRAWL_COUNT = 300        # 总抓取候选论文数（多轮拆分）
CRAWL_BATCH_SIZE = 100         # 每轮抓取数量
CRAWL_DELAY = 1.5              # 轮次间延迟（避免API限流）

# 自定义抓取领域关键词
SEARCH_KEYWORDS = "machine learning"

LANGUAGE_SCOPE = ""  # 留空则不限语言

# 高影响因子期刊列表（大幅扩充，覆盖全领域）
HIGH_IMPACT_JOURNALS = [
    # 综合性顶刊
    "Nature",
    "Science",
    "Cell",
    "Proceedings of the National Academy of Sciences",
    
    # 计算机科学顶刊
    "Communications of the ACM",
    "Journal of the ACM",
    "ACM Transactions on Computer Systems",
    "ACM Transactions on Programming Languages and Systems",
    "IEEE Transactions on Computers",
    "IEEE Transactions on Software Engineering",
    
    # 人工智能顶刊
    "Journal of Artificial Intelligence Research",
    "Artificial Intelligence",
    "Machine Learning",
    "Neural Computation",
    "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "International Journal of Computer Vision",
    
    # 其他领域顶刊
    "The Lancet",
    "New England Journal of Medicine",
    "Journal of the American Medical Association",
    "The BMJ",
    "Physical Review Letters",
    "Journal of the American Chemical Society",
    "Angewandte Chemie International Edition",
    "Nature Communications",
    "Science Advances"
]

# SMTP 配置（可选）
# 示例配置，使用时请替换为实际值
SMTP_CONFIG = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "from_email": "your-email@example.com",
    "smtp_username": "your-email@example.com",
    "smtp_password": "your-email-password"
}
