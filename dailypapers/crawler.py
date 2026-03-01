import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import time
from .utils import setup_logger

logger = setup_logger('crawler')

class PaperCrawler:
    """
    论文抓取类，负责从 CrossRef API 抓取论文
    """
    
    def __init__(self, search_keywords, time_range_days, total_crawl_count, crawl_batch_size, crawl_delay):
        """
        初始化抓取器
        
        Args:
            search_keywords (str or list): 搜索关键词
            time_range_days (int): 时间范围（天）
            total_crawl_count (int): 总抓取数量
            crawl_batch_size (int): 每轮抓取数量
            crawl_delay (float): 轮次间延迟
        """
        self.search_keywords = search_keywords
        self.time_range_days = time_range_days
        self.total_crawl_count = total_crawl_count
        self.crawl_batch_size = crawl_batch_size
        self.crawl_delay = crawl_delay
        self.base_url = "https://api.crossref.org/works"
    
    def build_query(self):
        """
        构建查询字符串
        
        Returns:
            str: 查询字符串
        """
        if isinstance(self.search_keywords, list):
            return ' OR '.join([f'"{kw}"' for kw in self.search_keywords])
        else:
            return self.search_keywords.strip()
    
    async def fetch_batch(self, session, offset, query, from_date):
        """
        异步抓取一批论文
        
        Args:
            session (aiohttp.ClientSession): HTTP会话
            offset (int): 偏移量
            query (str): 查询字符串
            from_date (str): 起始日期
            
        Returns:
            list: 论文列表
        """
        params = {
            "query": query,
            "filter": f"from-pub-date:{from_date},type:journal-article",
            "sort": "is-referenced-by-count",
            "order": "desc",
            "rows": self.crawl_batch_size,
            "offset": offset,
            "mailto": "your-email@example.com"  # 添加mailto，避免API限流
        }
        
        retries = 3
        for attempt in range(retries):
            try:
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=25),
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('message', {}).get('items', [])
                        logger.info(f"抓取到 {len(items)} 篇基础论文（偏移量: {offset}）")
                        
                        papers = []
                        for item in items:
                            # 处理发表时间（兼容不同格式）
                            pub_date_parts = item.get('published', {}).get('date-parts', [['未知时间']])[0]
                            pub_date = '-'.join([str(p) for p in pub_date_parts[:3]])  # 取年-月-日
                            
                            # 提取作者信息
                            authors = ", ".join([f"{auth.get('family', '')} {auth.get('given', '')}".strip() 
                                                 for auth in item.get('author', [])[:3]]) or "未知作者"
                            
                            papers.append({
                                "title": item.get('title', ['未知标题'])[0],
                                "link": item.get('URL', '#'),
                                "journal": item.get('container-title', ['未知期刊'])[0],
                                "citations": item.get('is-referenced-by-count', 0),
                                "published": pub_date,
                                "authors": authors,
                                "doi": item.get('DOI', '')
                            })
                        return papers
                    else:
                        logger.error(f"请求失败（状态码: {response.status}）")
                        if attempt < retries - 1:
                            logger.info(f"第{attempt+1}次重试...")
                            await asyncio.sleep(2)
                        else:
                            logger.error("达到最大重试次数，跳过本轮抓取")
                            return []
            except Exception as e:
                logger.error(f"抓取异常: {str(e)[:60]}")
                if attempt < retries - 1:
                    logger.info(f"第{attempt+1}次重试...")
                    await asyncio.sleep(2)
                else:
                    logger.error("达到最大重试次数，跳过本轮抓取")
                    return []
    
    async def crawl(self):
        """
        多轮异步抓取论文
        
        Returns:
            list: 抓取的论文列表
        """
        papers = []
        keywords_display = self.search_keywords if isinstance(self.search_keywords, str) else "多个关键词"
        logger.info(f"开始抓取【{keywords_display}】领域近{self.time_range_days}天论文")
        
        from_date = (datetime.now() - timedelta(days=self.time_range_days)).strftime("%Y-%m-%d")
        query = self.build_query()
        
        # 计算总轮数
        total_batches = self.total_crawl_count // self.crawl_batch_size
        
        # 创建异步会话
        async with aiohttp.ClientSession() as session:
            # 并发抓取所有批次
            tasks = []
            for batch in range(total_batches):
                offset = batch * self.crawl_batch_size
                tasks.append(self.fetch_batch(session, offset, query, from_date))
                # 每批次之间添加延迟，避免API限流
                if batch < total_batches - 1:
                    await asyncio.sleep(self.crawl_delay)
            
            # 等待所有抓取任务完成
            results = await asyncio.gather(*tasks)
            
            # 合并结果
            for result in results:
                papers.extend(result)
        
        logger.info(f"总计抓取到 {len(papers)} 篇论文")
        return papers
    
    def run(self):
        """
        运行抓取器
        
        Returns:
            list: 抓取的论文列表
        """
        return asyncio.run(self.crawl())
