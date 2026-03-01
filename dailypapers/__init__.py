"""
DailyPapers - 自动抓取高引用论文并推送至GitHub Issue

This package provides functionality to crawl academic papers from CrossRef API,
filter them based on citation count and journal impact factor, and push them to
GitHub Issues or send via email.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your-email@example.com"

from .crawler import PaperCrawler
from .filter import PaperFilter
from .pusher import PaperPusher
from .extractor import AbstractExtractor
from .utils import setup_logger, validate_config, load_cache, save_cache
from .main import main

__all__ = [
    "PaperCrawler",
    "PaperFilter",
    "PaperPusher",
    "AbstractExtractor",
    "setup_logger",
    "validate_config",
    "load_cache",
    "save_cache",
    "main"
]
