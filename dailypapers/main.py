import argparse
import importlib
import sys
import os
from datetime import datetime
from .crawler import PaperCrawler
from .filter import PaperFilter
from .pusher import PaperPusher
from .extractor import AbstractExtractor
from .utils import setup_logger, validate_config, load_cache, save_cache

logger = setup_logger('main')

def main():
    """
    主函数：执行论文抓取和推送流程
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DailyPapers - 自动抓取高引用论文并推送')
    parser.add_argument('--email', type=str, help='接收邮件的邮箱地址')
    parser.add_argument('--no-github', action='store_true', help='不推送至GitHub')
    parser.add_argument('--extract-abstracts', action='store_true', help='提取论文摘要')
    parser.add_argument('--config', type=str, default='config', help='配置文件名称（不带.py后缀）')
    args = parser.parse_args()
    
    # 加载配置
    try:
        # 尝试从dailypapers包中导入配置
        config = importlib.import_module(f'dailypapers.{args.config}')
        logger.info(f"使用配置文件: dailypapers/{args.config}.py")
    except ImportError:
        # 如果包内没有，尝试从项目根目录导入
        try:
            # 添加项目根目录到Python路径
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config = importlib.import_module(args.config)
            logger.info(f"使用配置文件: {args.config}.py")
        except ImportError:
            logger.error(f"无法加载配置文件: {args.config}.py")
            return
    
    # 验证配置
    if not validate_config(config):
        logger.error("配置无效，程序退出")
        return
    
    # 打印抓取信息
    keywords_display = config.SEARCH_KEYWORDS if isinstance(config.SEARCH_KEYWORDS, str) else "多个关键词"
    logger.info("="*60)
    logger.info(f"📅 通用论文抓取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔍 领域：{keywords_display} | 近{config.TIME_RANGE_DAYS}天 | 引用量≥{config.MIN_CITATION_THRESHOLD}")
    logger.info("="*60)

    # 1. 多轮抓取+筛选
    crawler = PaperCrawler(
        search_keywords=config.SEARCH_KEYWORDS,
        time_range_days=config.TIME_RANGE_DAYS,
        total_crawl_count=config.TOTAL_CRAWL_COUNT,
        crawl_batch_size=config.CRAWL_BATCH_SIZE,
        crawl_delay=config.CRAWL_DELAY
    )
    
    # 尝试从缓存加载
    cache_file = f"cache/{'_'.join(config.SEARCH_KEYWORDS) if isinstance(config.SEARCH_KEYWORDS, list) else config.SEARCH_KEYWORDS}.json"
    cached_papers = load_cache(cache_file)
    
    if cached_papers:
        logger.info("从缓存加载论文数据")
        all_papers = cached_papers
    else:
        logger.info("开始抓取论文")
        all_papers = crawler.run()
        # 保存到缓存
        save_cache(cache_file, all_papers)
    
    if not all_papers:
        logger.error("未抓取到符合条件的论文")
        return

    # 2. 筛选引用量≥阈值的论文
    paper_filter = PaperFilter(
        min_citation_threshold=config.MIN_CITATION_THRESHOLD,
        high_impact_journals=config.HIGH_IMPACT_JOURNALS
    )
    selected_papers = paper_filter.process(all_papers, config.PAPER_COUNT)

    # 3. 提取摘要（如果启用）
    if args.extract_abstracts:
        logger.info("开始提取论文摘要")
        extractor = AbstractExtractor()
        selected_papers = extractor.extract_batch(selected_papers)

    # 4. 推送至GitHub Issue
    if not args.no_github:
        pusher = PaperPusher(
            github_token=config.GITHUB_TOKEN,
            repo_owner=config.REPO_OWNER,
            repo_name=config.REPO_NAME
        )
        issue_url = pusher.push_to_github(
            selected_papers, 
            config.SEARCH_KEYWORDS,
            config.TIME_RANGE_DAYS,
            config.MIN_CITATION_THRESHOLD,
            config.HIGH_IMPACT_JOURNALS
        )
        if issue_url:
            logger.info(f"GitHub Issue 推送成功: {issue_url}")

    # 5. 发送邮件（如果指定）
    if args.email and hasattr(config, 'SMTP_CONFIG'):
        pusher = PaperPusher(
            github_token=config.GITHUB_TOKEN,
            repo_owner=config.REPO_OWNER,
            repo_name=config.REPO_NAME
        )
        success = pusher.send_email(
            selected_papers, 
            config.SEARCH_KEYWORDS, 
            args.email, 
            config.SMTP_CONFIG,
            config.TIME_RANGE_DAYS,
            config.MIN_CITATION_THRESHOLD
        )
        if success:
            logger.info(f"邮件发送成功: {args.email}")

    logger.info("任务完成！")

if __name__ == "__main__":
    from datetime import datetime
    main()
