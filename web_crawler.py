"""
웹 크롤러 메인 엔진
웹사이트에서 파일 링크를 찾고 다운로드하는 통합 인터페이스를 제공합니다.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
import time

from link_detector import LinkDetector
from file_downloader import FileDownloader


class WebCrawler:
    """웹 크롤러 메인 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        WebCrawler 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        # 기본 설정
        self.config = {
            'download_dir': './downloads',
            'max_concurrent_downloads': 5,
            'max_crawl_depth': 1,
            'timeout': 30,
            'retry_count': 3,
            'chunk_size': 8192,
            'file_types': ['documents', 'images', 'videos', 'audio', 'archives'],
            'custom_extensions': set(),
            'same_domain_only': True,
            'respect_robots_txt': False,
            'delay_between_requests': 1,
            'enable_logging': True,
            'log_level': 'INFO',
            'save_metadata': True,
            'metadata_file': 'crawl_metadata.json'
        }
        
        # 사용자 설정으로 업데이트
        if config:
            self.config.update(config)
        
        # 로깅 설정
        if self.config['enable_logging']:
            self._setup_logging()
        
        # 컴포넌트 초기화
        self.link_detector = LinkDetector()
        self.file_downloader = FileDownloader(
            download_dir=self.config['download_dir'],
            max_concurrent=self.config['max_concurrent_downloads'],
            chunk_size=self.config['chunk_size'],
            timeout=self.config['timeout'],
            retry_count=self.config['retry_count']
        )
        
        self.logger = logging.getLogger(__name__)
        
        # 크롤링 통계
        self.crawl_stats = {
            'start_time': None,
            'end_time': None,
            'urls_crawled': 0,
            'files_found': 0,
            'files_downloaded': 0,
            'total_download_size': 0,
            'errors': []
        }
        
        # 메타데이터 저장
        self.metadata = {
            'crawl_info': {},
            'found_links': {},
            'download_results': [],
            'config': self.config.copy()
        }
    
    def _setup_logging(self):
        """로깅 설정"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('web_crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    async def crawl_and_download(self, 
                               urls: List[str], 
                               file_types: List[str] = None,
                               custom_extensions: Set[str] = None,
                               output_dir: str = None) -> Dict[str, Any]:
        """
        웹사이트를 크롤링하고 파일을 다운로드
        
        Args:
            urls: 크롤링할 URL 목록
            file_types: 다운로드할 파일 타입 목록
            custom_extensions: 사용자 정의 확장자
            output_dir: 출력 디렉터리
            
        Returns:
            크롤링 및 다운로드 결과
        """
        self.crawl_stats['start_time'] = time.time()
        
        # 설정 업데이트
        if file_types:
            self.config['file_types'] = file_types
        if custom_extensions:
            self.config['custom_extensions'] = custom_extensions
        if output_dir:
            self.config['download_dir'] = output_dir
            self.file_downloader.download_dir = Path(output_dir)
            self.file_downloader.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"크롤링 시작: {len(urls)}개 URL")
        
        # 모든 파일 링크 수집
        all_file_links = {}
        
        for url in urls:
            try:
                self.logger.info(f"URL 크롤링 중: {url}")
                
                # 파일 링크 찾기
                file_links = self.link_detector.find_file_links(
                    url=url,
                    file_types=self.config['file_types'],
                    custom_extensions=self.config['custom_extensions'],
                    max_depth=self.config['max_crawl_depth']
                )
                
                # 결과 병합
                for file_type, links in file_links.items():
                    if file_type not in all_file_links:
                        all_file_links[file_type] = []
                    all_file_links[file_type].extend(links)
                
                self.crawl_stats['urls_crawled'] += 1
                
                # 요청 간 지연
                if self.config['delay_between_requests'] > 0:
                    await asyncio.sleep(self.config['delay_between_requests'])
                    
            except Exception as e:
                error_msg = f"URL 크롤링 실패 {url}: {e}"
                self.logger.error(error_msg)
                self.crawl_stats['errors'].append(error_msg)
        
        # 중복 링크 제거
        unique_links = set()
        for file_type, links in all_file_links.items():
            unique_links.update(links)
            all_file_links[file_type] = list(set(links))
        
        self.crawl_stats['files_found'] = len(unique_links)
        self.metadata['found_links'] = all_file_links
        
        self.logger.info(f"총 {len(unique_links)}개 파일 링크 발견")
        
        # 파일 다운로드
        if unique_links:
            self.logger.info("파일 다운로드 시작...")
            
            download_results = await self.file_downloader.download_files(
                urls=list(unique_links),
                output_dir=self.config['download_dir']
            )
            
            # 통계 업데이트
            successful_downloads = [r for r in download_results if r['success']]
            self.crawl_stats['files_downloaded'] = len(successful_downloads)
            self.crawl_stats['total_download_size'] = sum(r['size'] for r in successful_downloads)
            
            self.metadata['download_results'] = download_results
        
        self.crawl_stats['end_time'] = time.time()
        
        # 메타데이터 저장
        if self.config['save_metadata']:
            await self._save_metadata()
        
        # 결과 반환
        result = {
            'success': True,
            'stats': self.crawl_stats,
            'found_links': all_file_links,
            'download_results': self.metadata.get('download_results', []),
            'config': self.config
        }
        
        self._print_summary(result)
        return result
    
    def crawl_and_download_sync(self, 
                              urls: List[str], 
                              file_types: List[str] = None,
                              custom_extensions: Set[str] = None,
                              output_dir: str = None) -> Dict[str, Any]:
        """
        동기 방식으로 크롤링 및 다운로드
        
        Args:
            urls: 크롤링할 URL 목록
            file_types: 다운로드할 파일 타입 목록
            custom_extensions: 사용자 정의 확장자
            output_dir: 출력 디렉터리
            
        Returns:
            크롤링 및 다운로드 결과
        """
        # 비동기 함수를 동기적으로 실행
        return asyncio.run(self.crawl_and_download(urls, file_types, custom_extensions, output_dir))
    
    async def find_files_only(self, 
                            urls: List[str], 
                            file_types: List[str] = None,
                            custom_extensions: Set[str] = None) -> Dict[str, List[str]]:
        """
        파일 링크만 찾기 (다운로드하지 않음)
        
        Args:
            urls: 크롤링할 URL 목록
            file_types: 찾을 파일 타입 목록
            custom_extensions: 사용자 정의 확장자
            
        Returns:
            파일 타입별 링크 딕셔너리
        """
        self.logger.info("파일 링크 탐지 모드")
        
        all_file_links = {}
        
        for url in urls:
            try:
                file_links = self.link_detector.find_file_links(
                    url=url,
                    file_types=file_types or self.config['file_types'],
                    custom_extensions=custom_extensions or self.config['custom_extensions'],
                    max_depth=self.config['max_crawl_depth']
                )
                
                # 결과 병합
                for file_type, links in file_links.items():
                    if file_type not in all_file_links:
                        all_file_links[file_type] = []
                    all_file_links[file_type].extend(links)
                    
            except Exception as e:
                self.logger.error(f"URL 처리 실패 {url}: {e}")
        
        # 중복 제거
        for file_type in all_file_links:
            all_file_links[file_type] = list(set(all_file_links[file_type]))
        
        return all_file_links
    
    async def download_files_from_list(self, 
                                     file_urls: List[str], 
                                     output_dir: str = None) -> List[Dict[str, Any]]:
        """
        URL 목록에서 파일 다운로드
        
        Args:
            file_urls: 다운로드할 파일 URL 목록
            output_dir: 출력 디렉터리
            
        Returns:
            다운로드 결과 목록
        """
        self.logger.info(f"{len(file_urls)}개 파일 다운로드 시작")
        
        return await self.file_downloader.download_files(
            urls=file_urls,
            output_dir=output_dir or self.config['download_dir']
        )
    
    async def _save_metadata(self):
        """메타데이터를 JSON 파일로 저장"""
        try:
            self.metadata['crawl_info'] = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.crawl_stats
            }
            
            metadata_path = Path(self.config['download_dir']) / self.config['metadata_file']
            
            # set 타입을 list로 변환하여 JSON 직렬화 가능하게 만듦
            serializable_metadata = self.metadata.copy()
            if 'config' in serializable_metadata:
                config_copy = serializable_metadata['config'].copy()
                if 'custom_extensions' in config_copy and isinstance(config_copy['custom_extensions'], set):
                    config_copy['custom_extensions'] = list(config_copy['custom_extensions'])
                serializable_metadata['config'] = config_copy
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"메타데이터 저장: {metadata_path}")
            
        except Exception as e:
            self.logger.error(f"메타데이터 저장 실패: {e}")
    
    def _print_summary(self, result: Dict[str, Any]):
        """크롤링 결과 요약 출력"""
        stats = result['stats']
        duration = stats['end_time'] - stats['start_time'] if stats['end_time'] else 0
        
        print("\n" + "="*50)
        print("📊 크롤링 결과 요약")
        print("="*50)
        print(f"🌐 크롤링한 URL 수: {stats['urls_crawled']}")
        print(f"📁 발견한 파일 수: {stats['files_found']}")
        print(f"⬇️  다운로드한 파일 수: {stats['files_downloaded']}")
        
        if stats['total_download_size'] > 0:
            size_str = self.file_downloader.format_size(stats['total_download_size'])
            print(f"💾 총 다운로드 크기: {size_str}")
        
        print(f"⏱️  소요 시간: {duration:.2f}초")
        
        if stats['errors']:
            print(f"❌ 오류 수: {len(stats['errors'])}")
        
        # 파일 타입별 통계
        found_links = result['found_links']
        if found_links:
            print("\n📂 파일 타입별 발견 수:")
            for file_type, links in found_links.items():
                if links:
                    print(f"   {file_type}: {len(links)}개")
        
        print("="*50)
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """지원하는 파일 타입 목록 반환"""
        return self.link_detector.FILE_EXTENSIONS.copy()
    
    def add_custom_extensions(self, extensions: List[str]):
        """사용자 정의 확장자 추가"""
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            self.config['custom_extensions'].add(ext.lower())
    
    def set_config(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"설정 업데이트: {key} = {value}")
            else:
                self.logger.warning(f"알 수 없는 설정: {key}")


def create_crawler_from_config_file(config_file: str) -> WebCrawler:
    """
    설정 파일에서 크롤러 생성
    
    Args:
        config_file: JSON 설정 파일 경로
        
    Returns:
        WebCrawler 인스턴스
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return WebCrawler(config)
    except Exception as e:
        logging.error(f"설정 파일 로드 실패 {config_file}: {e}")
        return WebCrawler()


# 편의 함수들
async def quick_crawl(url: str, 
                     file_types: List[str] = None, 
                     output_dir: str = "./downloads") -> Dict[str, Any]:
    """
    빠른 크롤링 함수
    
    Args:
        url: 크롤링할 URL
        file_types: 파일 타입 목록
        output_dir: 출력 디렉터리
        
    Returns:
        크롤링 결과
    """
    crawler = WebCrawler()
    return await crawler.crawl_and_download([url], file_types, output_dir=output_dir)


def quick_crawl_sync(url: str, 
                    file_types: List[str] = None, 
                    output_dir: str = "./downloads") -> Dict[str, Any]:
    """
    빠른 동기 크롤링 함수
    """
    return asyncio.run(quick_crawl(url, file_types, output_dir))