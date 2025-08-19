"""
웹 크롤러 패키지
웹사이트에서 파일 링크를 탐지하고 다운로드하는 도구
"""

from .web_crawler import WebCrawler, quick_crawl, quick_crawl_sync, create_crawler_from_config_file
from .link_detector import LinkDetector
from .file_downloader import FileDownloader

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'WebCrawler',
    'LinkDetector', 
    'FileDownloader',
    'quick_crawl',
    'quick_crawl_sync',
    'create_crawler_from_config_file'
]