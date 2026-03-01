import requests
from bs4 import BeautifulSoup
from .utils import setup_logger

logger = setup_logger('extractor')

class AbstractExtractor:
    """
    论文摘要提取类，负责从论文页面提取摘要
    """
    
    def __init__(self):
        """
        初始化提取器
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def extract_from_url(self, url):
        """
        从论文URL提取摘要
        
        Args:
            url (str): 论文URL
            
        Returns:
            str: 摘要内容
        """
        if not url or url == '#':
            return ""
        
        try:
            logger.info(f"尝试从 {url} 提取摘要")
            
            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尝试不同的摘要提取策略
            abstract = self._extract_abstract(soup)
            
            if abstract:
                logger.info("摘要提取成功")
                return abstract
            else:
                logger.warning("未找到摘要")
                return ""
        except Exception as e:
            logger.error(f"摘要提取失败: {str(e)[:60]}")
            return ""
    
    def _extract_abstract(self, soup):
        """
        从HTML中提取摘要
        
        Args:
            soup (BeautifulSoup): BeautifulSoup对象
            
        Returns:
            str: 摘要内容
        """
        # 策略1: 查找abstract标签
        abstract_tag = soup.find('abstract')
        if abstract_tag:
            return abstract_tag.get_text(strip=True)
        
        # 策略2: 查找class包含abstract的元素
        abstract_class = soup.find(class_=lambda x: x and 'abstract' in x.lower())
        if abstract_class:
            return abstract_class.get_text(strip=True)
        
        # 策略3: 查找id包含abstract的元素
        abstract_id = soup.find(id=lambda x: x and 'abstract' in x.lower())
        if abstract_id:
            return abstract_id.get_text(strip=True)
        
        # 策略4: 查找包含"Abstract"文本的元素
        abstract_heading = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and 'abstract' in tag.get_text().lower())
        if abstract_heading:
            # 查找后续的段落
            next_sibling = abstract_heading.find_next_sibling()
            if next_sibling and next_sibling.name == 'p':
                return next_sibling.get_text(strip=True)
        
        # 策略5: 查找meta标签中的description
        meta_description = soup.find('meta', {'name': 'description'})
        if meta_description and meta_description.get('content'):
            return meta_description.get('content').strip()
        
        return ""
    
    def extract_batch(self, papers):
        """
        批量提取论文摘要
        
        Args:
            papers (list): 论文列表
            
        Returns:
            list: 带摘要的论文列表
        """
        for paper in papers:
            if 'link' in paper:
                abstract = self.extract_from_url(paper['link'])
                paper['abstract'] = abstract
        
        return papers
