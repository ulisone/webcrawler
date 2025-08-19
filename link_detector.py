"""
파일 링크 탐지 모듈
웹페이지에서 다운로드 가능한 파일 링크를 탐지하고 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Optional
import logging


class LinkDetector:
    """웹페이지에서 파일 링크를 탐지하는 클래스"""
    
    # 일반적인 파일 확장자 패턴
    FILE_EXTENSIONS = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'archives': ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2'],
        'data': ['.json', '.xml', '.csv', '.xls', '.xlsx'],
        'executables': ['.exe', '.msi', '.dmg', '.deb', '.rpm'],
        'others': ['.iso', '.torrent', '.apk']
    }
    
    def __init__(self, session: Optional[requests.Session] = None):
        """
        LinkDetector 초기화
        
        Args:
            session: requests.Session 객체 (선택사항)
        """
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
        # 모든 파일 확장자를 하나의 세트로 합치기
        self.all_extensions = set()
        for ext_list in self.FILE_EXTENSIONS.values():
            self.all_extensions.update(ext_list)
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        웹페이지 내용을 가져와서 BeautifulSoup 객체로 반환
        
        Args:
            url: 대상 웹페이지 URL
            
        Returns:
            BeautifulSoup 객체 또는 None (실패시)
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 인코딩 감지 및 설정
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"페이지 요청 실패 {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"페이지 파싱 실패 {url}: {e}")
            return None
    
    def extract_links_from_tags(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """
        HTML 태그에서 링크를 추출
        
        Args:
            soup: BeautifulSoup 객체
            base_url: 기준 URL
            
        Returns:
            추출된 링크들의 집합
        """
        links = set()
        
        # a 태그에서 href 속성 추출
        for tag in soup.find_all('a', href=True):
            href = tag['href'].strip()
            if href:
                absolute_url = urljoin(base_url, href)
                links.add(absolute_url)
        
        # img 태그에서 src 속성 추출
        for tag in soup.find_all('img', src=True):
            src = tag['src'].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                links.add(absolute_url)
        
        # link 태그에서 href 속성 추출
        for tag in soup.find_all('link', href=True):
            href = tag['href'].strip()
            if href:
                absolute_url = urljoin(base_url, href)
                links.add(absolute_url)
        
        # script 태그에서 src 속성 추출
        for tag in soup.find_all('script', src=True):
            src = tag['src'].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                links.add(absolute_url)
        
        return links
    
    def is_file_link(self, url: str, custom_extensions: Optional[Set[str]] = None) -> bool:
        """
        URL이 파일 링크인지 확인
        
        Args:
            url: 확인할 URL
            custom_extensions: 사용자 정의 확장자 집합
            
        Returns:
            파일 링크 여부
        """
        extensions = custom_extensions or self.all_extensions
        
        # URL 파싱
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # 파일 확장자 확인
        for ext in extensions:
            if path.endswith(ext.lower()):
                return True
        
        # Content-Disposition 헤더 확인 (HEAD 요청으로)
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'attachment' in content_disposition.lower():
                return True
            
            # Content-Type 헤더 확인
            content_type = response.headers.get('Content-Type', '').lower()
            file_content_types = [
                'application/pdf', 'application/zip', 'application/octet-stream',
                'image/', 'video/', 'audio/', 'application/msword',
                'application/vnd.ms-excel', 'application/vnd.openxmlformats'
            ]
            
            for file_type in file_content_types:
                if file_type in content_type:
                    return True
                    
        except:
            pass
        
        return False
    
    def filter_file_links(self, links: Set[str], 
                         file_types: Optional[List[str]] = None,
                         custom_extensions: Optional[Set[str]] = None) -> Dict[str, List[str]]:
        """
        링크들을 파일 타입별로 필터링
        
        Args:
            links: 필터링할 링크들
            file_types: 원하는 파일 타입 목록 (예: ['documents', 'images'])
            custom_extensions: 사용자 정의 확장자 집합
            
        Returns:
            파일 타입별로 분류된 링크 딕셔너리
        """
        filtered_links = {}
        
        # 원하는 파일 타입이 지정되지 않았으면 모든 타입 포함
        if file_types is None:
            file_types = list(self.FILE_EXTENSIONS.keys())
        
        # 각 파일 타입별로 초기화
        for file_type in file_types:
            filtered_links[file_type] = []
        
        # 사용자 정의 확장자가 있으면 추가
        if custom_extensions:
            filtered_links['custom'] = []
        
        for link in links:
            if not self.is_file_link(link, custom_extensions):
                continue
                
            parsed = urlparse(link)
            path = parsed.path.lower()
            
            # 각 파일 타입별로 확인
            for file_type in file_types:
                extensions = self.FILE_EXTENSIONS.get(file_type, [])
                for ext in extensions:
                    if path.endswith(ext.lower()):
                        filtered_links[file_type].append(link)
                        break
            
            # 사용자 정의 확장자 확인
            if custom_extensions:
                for ext in custom_extensions:
                    if path.endswith(ext.lower()):
                        filtered_links['custom'].append(link)
                        break
        
        return filtered_links
    
    def find_file_links(self, url: str, 
                       file_types: Optional[List[str]] = None,
                       custom_extensions: Optional[Set[str]] = None,
                       max_depth: int = 1) -> Dict[str, List[str]]:
        """
        웹페이지에서 파일 링크를 찾아서 반환
        
        Args:
            url: 크롤링할 웹페이지 URL
            file_types: 원하는 파일 타입 목록
            custom_extensions: 사용자 정의 확장자 집합
            max_depth: 크롤링 깊이 (1은 현재 페이지만)
            
        Returns:
            파일 타입별로 분류된 링크 딕셔너리
        """
        all_file_links = {}
        visited_urls = set()
        urls_to_visit = [(url, 0)]  # (URL, depth)
        
        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in visited_urls or depth > max_depth:
                continue
                
            visited_urls.add(current_url)
            self.logger.info(f"크롤링 중: {current_url} (깊이: {depth})")
            
            # 페이지 내용 가져오기
            soup = self.get_page_content(current_url)
            if not soup:
                continue
            
            # 링크 추출
            links = self.extract_links_from_tags(soup, current_url)
            
            # 파일 링크 필터링
            file_links = self.filter_file_links(links, file_types, custom_extensions)
            
            # 결과 병합
            for file_type, link_list in file_links.items():
                if file_type not in all_file_links:
                    all_file_links[file_type] = []
                all_file_links[file_type].extend(link_list)
            
            # 다음 깊이로 갈 페이지 링크 추가 (HTML 페이지만)
            if depth < max_depth:
                for link in links:
                    if (link not in visited_urls and 
                        not self.is_file_link(link) and
                        self._is_same_domain(url, link)):
                        urls_to_visit.append((link, depth + 1))
        
        # 중복 제거
        for file_type in all_file_links:
            all_file_links[file_type] = list(set(all_file_links[file_type]))
        
        return all_file_links
    
    def _is_same_domain(self, base_url: str, target_url: str) -> bool:
        """
        두 URL이 같은 도메인인지 확인
        
        Args:
            base_url: 기준 URL
            target_url: 대상 URL
            
        Returns:
            같은 도메인 여부
        """
        base_domain = urlparse(base_url).netloc
        target_domain = urlparse(target_url).netloc
        return base_domain == target_domain