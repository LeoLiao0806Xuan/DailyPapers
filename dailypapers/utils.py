import logging
import os
import json
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """
    自定义日志格式
    """
    
    def __init__(self):
        super().__init__()
        self.format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.datefmt = "%Y-%m-%d %H:%M:%S"
    
    def format(self, record):
        formatter = logging.Formatter(self.format_str, self.datefmt)
        return formatter.format(record)

def setup_logger(name):
    """
    设置日志记录器
    
    Args:
        name (str): 日志名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(CustomFormatter())
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CustomFormatter())
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def load_cache(cache_file):
    """
    加载缓存文件
    
    Args:
        cache_file (str): 缓存文件路径
        
    Returns:
        dict: 缓存数据
    """
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger = setup_logger('utils')
            logger.error(f"加载缓存失败: {str(e)}")
            return {}
    return {}

def save_cache(cache_file, data):
    """
    保存缓存文件
    
    Args:
        cache_file (str): 缓存文件路径
        data (dict): 缓存数据
    """
    try:
        # 确保缓存目录存在
        cache_dir = os.path.dirname(cache_file)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger = setup_logger('utils')
        logger.error(f"保存缓存失败: {str(e)}")

def validate_config(config):
    """
    验证配置是否有效
    
    Args:
        config: 配置对象
        
    Returns:
        bool: 配置是否有效
    """
    required_fields = [
        'GITHUB_TOKEN',
        'REPO_OWNER',
        'REPO_NAME',
        'PAPER_COUNT',
        'TIME_RANGE_DAYS',
        'MIN_CITATION_THRESHOLD',
        'TOTAL_CRAWL_COUNT',
        'CRAWL_BATCH_SIZE',
        'CRAWL_DELAY',
        'SEARCH_KEYWORDS',
        'HIGH_IMPACT_JOURNALS'
    ]
    
    for field in required_fields:
        if not hasattr(config, field):
            logger = setup_logger('utils')
            logger.error(f"配置缺失字段: {field}")
            return False
    
    return True
