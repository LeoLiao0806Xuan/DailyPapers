#!/usr/bin/env python3
# 测试脚本
import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有模块是否能正常导入"""
    logger.info("测试模块导入...")
    try:
        import dailypapers
        from dailypapers import config
        from dailypapers import PaperCrawler, PaperFilter, PaperPusher, AbstractExtractor
        from dailypapers import setup_logger, validate_config, load_cache, save_cache
        logger.info("所有模块导入成功")
        return True
    except Exception as e:
        logger.error(f"模块导入失败: {str(e)}")
        return False

def test_config():
    """测试配置是否有效"""
    logger.info("测试配置...")
    try:
        from dailypapers import config
        from dailypapers import validate_config
        if validate_config(config):
            logger.info("配置验证成功")
            return True
        else:
            logger.error("配置验证失败")
            return False
    except Exception as e:
        logger.error(f"配置测试失败: {str(e)}")
        return False

def test_crawler():
    """测试抓取功能"""
    logger.info("测试抓取功能...")
    try:
        from dailypapers import PaperCrawler
        
        # 创建抓取器
        crawler = PaperCrawler(
            search_keywords="machine learning",
            time_range_days=30,
            total_crawl_count=10,
            crawl_batch_size=5,
            crawl_delay=0.5
        )
        
        # 测试查询构建
        query = crawler.build_query()
        logger.info(f"查询构建成功: {query}")
        
        # 测试抓取（使用小批量避免API限流）
        papers = crawler.run()
        logger.info(f"抓取成功，获取到 {len(papers)} 篇论文")
        
        if papers:
            logger.info(f"第一篇论文: {papers[0]['title']}")
        
        return True
    except Exception as e:
        logger.error(f"抓取测试失败: {str(e)}")
        return False

def test_filter():
    """测试筛选功能"""
    logger.info("测试筛选功能...")
    try:
        from dailypapers import config
        from dailypapers import PaperFilter
        
        # 创建测试数据
        test_papers = [
            {"title": "Test Paper 1", "journal": "Nature", "citations": 10},
            {"title": "Test Paper 2", "journal": "Science", "citations": 5},
            {"title": "Test Paper 3", "journal": "IEEE Transactions on Pattern Analysis and Machine Intelligence", "citations": 3},
            {"title": "Test Paper 4", "journal": "Unknown Journal", "citations": 15}
        ]
        
        # 创建筛选器
        paper_filter = PaperFilter(
            min_citation_threshold=5,
            high_impact_journals=config.HIGH_IMPACT_JOURNALS
        )
        
        # 测试筛选
        filtered = paper_filter.filter_by_citations(test_papers)
        logger.info(f"筛选后: {len(filtered)} 篇论文")
        
        # 测试排序
        sorted_papers = paper_filter.sort_by_impact(test_papers)
        logger.info(f"排序后第一篇: {sorted_papers[0]['title']} (期刊: {sorted_papers[0]['journal']})")
        
        # 测试完整流程
        selected = paper_filter.process(test_papers, 2)
        logger.info(f"选择后: {len(selected)} 篇论文")
        
        return True
    except Exception as e:
        logger.error(f"筛选测试失败: {str(e)}")
        return False

def test_extractor():
    """测试摘要提取功能"""
    logger.info("测试摘要提取功能...")
    try:
        from dailypapers import AbstractExtractor
        
        extractor = AbstractExtractor()
        
        # 测试一个已知有摘要的页面
        test_url = "https://www.nature.com/articles/nature24288"
        abstract = extractor.extract_from_url(test_url)
        
        if abstract:
            logger.info(f"摘要提取成功，长度: {len(abstract)} 字符")
            logger.info(f"摘要前100字符: {abstract[:100]}...")
        else:
            logger.warning("未提取到摘要")
        
        return True
    except Exception as e:
        logger.error(f"摘要提取测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    logger.info("开始测试 DailyPapers 功能...")
    
    tests = [
        ("模块导入", test_imports),
        ("配置验证", test_config),
        ("抓取功能", test_crawler),
        ("筛选功能", test_filter),
        ("摘要提取", test_extractor)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n=== 测试: {test_name} ===")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} 测试通过")
        else:
            failed += 1
            logger.error(f"❌ {test_name} 测试失败")
    
    logger.info(f"\n=== 测试结果 ===")
    logger.info(f"通过: {passed}")
    logger.info(f"失败: {failed}")
    
    if failed == 0:
        logger.info("🎉 所有测试通过！")
    else:
        logger.warning("⚠️  部分测试失败，可能需要进一步检查")

if __name__ == "__main__":
    main()
