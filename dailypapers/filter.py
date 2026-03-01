from .utils import setup_logger

logger = setup_logger('filter')

class PaperFilter:
    """
    论文筛选类，负责筛选和排序论文
    """
    
    def __init__(self, min_citation_threshold, high_impact_journals):
        """
        初始化筛选器
        
        Args:
            min_citation_threshold (int): 最低引用量阈值
            high_impact_journals (list): 高影响因子期刊列表
        """
        self.min_citation_threshold = min_citation_threshold
        self.high_impact_journals = high_impact_journals
    
    def filter_by_citations(self, papers):
        """
        根据引用量筛选论文
        
        Args:
            papers (list): 论文列表
            
        Returns:
            list: 筛选后的论文列表
        """
        filtered_papers = [p for p in papers if p['citations'] >= self.min_citation_threshold]
        logger.info(f"根据引用量筛选：{len(papers)} -> {len(filtered_papers)} 篇")
        return filtered_papers
    
    def sort_by_impact(self, papers):
        """
        根据影响力排序论文（高影响因子期刊优先，同期刊内按引用量降序）
        
        Args:
            papers (list): 论文列表
            
        Returns:
            list: 排序后的论文列表
        """
        # 分离高影响因子期刊和其他期刊
        high_impact_papers = [p for p in papers if p['journal'] in self.high_impact_journals]
        other_papers = [p for p in papers if p['journal'] not in self.high_impact_journals]
        
        # 分别排序
        high_impact_papers.sort(key=lambda x: x['citations'], reverse=True)
        other_papers.sort(key=lambda x: x['citations'], reverse=True)
        
        # 合并结果
        sorted_papers = high_impact_papers + other_papers
        logger.info(f"排序完成，高影响因子期刊论文: {len(high_impact_papers)} 篇")
        return sorted_papers
    
    def select_top_papers(self, papers, count):
        """
        选择前 N 篇论文
        
        Args:
            papers (list): 论文列表
            count (int): 数量
            
        Returns:
            list: 选择的论文列表
        """
        selected = papers[:count]
        logger.info(f"选择前 {len(selected)} 篇论文")
        return selected
    
    def process(self, papers, count):
        """
        完整处理流程：筛选 -> 排序 -> 选择
        
        Args:
            papers (list): 论文列表
            count (int): 选择数量
            
        Returns:
            list: 处理后的论文列表
        """
        # 1. 根据引用量筛选
        filtered = self.filter_by_citations(papers)
        
        # 2. 如果筛选后不足，使用所有论文
        if not filtered:
            logger.warning("无符合引用量要求的论文，使用所有论文")
            filtered = papers
        
        # 3. 排序
        sorted_papers = self.sort_by_impact(filtered)
        
        # 4. 选择
        selected = self.select_top_papers(sorted_papers, count)
        
        return selected
