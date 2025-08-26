"""
파일 다운로드 모듈
웹에서 파일을 다운로드하고 관리하는 기능을 제공합니다.
"""

import os
import asyncio
import aiohttp
import aiofiles
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import List, Dict, Optional, Callable, Any
import logging
import hashlib
import time
from tqdm.asyncio import tqdm
import mimetypes


class FileDownloader:
    """파일 다운로드를 관리하는 클래스"""
    
    def __init__(self, 
                 download_dir: str = "./downloads",
                 max_concurrent: int = 5,
                 chunk_size: int = 8192,
                 timeout: int = 30,
                 retry_count: int = 3):
        """
        FileDownloader 초기화
        
        Args:
            download_dir: 다운로드 디렉터리
            max_concurrent: 최대 동시 다운로드 수
            chunk_size: 청크 크기 (바이트)
            timeout: 타임아웃 (초)
            retry_count: 재시도 횟수
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.retry_count = retry_count
        
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # 다운로드 통계
        self.stats = {
            'total_files': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 파일 중복 체크를 위한 해시 저장
        self.downloaded_hashes = set()
    
    def get_filename_from_url(self, url: str, content_disposition: str = None) -> str:
        """
        URL에서 파일명을 추출
        
        Args:
            url: 파일 URL
            content_disposition: Content-Disposition 헤더 값
            
        Returns:
            추출된 파일명
        """
        filename = None
        
        # Content-Disposition 헤더에서 파일명 추출 시도
        if content_disposition:
            if 'filename*=' in content_disposition:
                # RFC 5987 인코딩 처리
                try:
                    encoded_filename = content_disposition.split('filename*=')[1]
                    if encoded_filename.startswith('UTF-8\'\''):
                        filename = unquote(encoded_filename[7:])
                except:
                    pass
            elif 'filename=' in content_disposition:
                try:
                    filename = content_disposition.split('filename=')[1].strip('"\'')
                    filename = unquote(filename)
                except:
                    pass
        
        # URL에서 파일명 추출
        if not filename:
            parsed_url = urlparse(url)
            filename = unquote(os.path.basename(parsed_url.path))
            
            # 파일명이 없거나 의미없는 경우 URL 해시로 생성
            if not filename or filename == '/':
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"file_{url_hash}"
        
        # 안전한 파일명으로 변환
        filename = self.sanitize_filename(filename)
        
        return filename
    
    def sanitize_filename(self, filename: str) -> str:
        """
        파일명을 안전하게 변환
        
        Args:
            filename: 원본 파일명
            
        Returns:
            안전한 파일명
        """
        # 위험한 문자 제거
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # 파일명 길이 제한
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
    
    def get_file_extension_from_content_type(self, content_type: str) -> str:
        """
        Content-Type에서 파일 확장자 추정
        
        Args:
            content_type: MIME 타입
            
        Returns:
            파일 확장자
        """
        extension = mimetypes.guess_extension(content_type.split(';')[0])
        return extension or ''
    
    async def get_file_info(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """
        파일 정보를 가져옴 (HEAD 요청)
        
        Args:
            session: aiohttp 세션
            url: 파일 URL
            
        Returns:
            파일 정보 딕셔너리
        """
        try:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=self.timeout), allow_redirects=True) as response:
                headers = response.headers
                
                return {
                    'url': url,
                    'status_code': response.status,
                    'content_length': int(headers.get('Content-Length', 0)),
                    'content_type': headers.get('Content-Type', ''),
                    'content_disposition': headers.get('Content-Disposition', ''),
                    'last_modified': headers.get('Last-Modified', ''),
                    'etag': headers.get('ETag', '')
                }
        except Exception as e:
            self.logger.warning(f"파일 정보 가져오기 실패 {url}: {e}")
            return {
                'url': url,
                'status_code': 0,
                'content_length': 0,
                'content_type': '',
                'content_disposition': '',
                'last_modified': '',
                'etag': ''
            }
    
    async def download_file(self, 
                          session: aiohttp.ClientSession, 
                          url: str, 
                          filename: str = None,
                          progress_callback: Callable = None) -> Dict[str, Any]:
        """
        단일 파일 다운로드
        
        Args:
            session: aiohttp 세션
            url: 다운로드할 파일 URL
            filename: 저장할 파일명 (선택사항)
            progress_callback: 진행상황 콜백 함수
            
        Returns:
            다운로드 결과 딕셔너리
        """
        result = {
            'url': url,
            'success': False,
            'filename': '',
            'file_path': '',
            'size': 0,
            'error': None
        }
        
        for attempt in range(self.retry_count + 1):
            try:
                # 파일 정보 가져오기
                file_info = await self.get_file_info(session, url)
                
                if file_info['status_code'] not in [200, 206]:
                    result['error'] = f"HTTP {file_info['status_code']}"
                    continue
                
                # 파일명 결정
                if not filename:
                    filename = self.get_filename_from_url(url, file_info['content_disposition'])
                    
                    # 확장자가 없으면 Content-Type에서 추정
                    if not os.path.splitext(filename)[1] and file_info['content_type']:
                        ext = self.get_file_extension_from_content_type(file_info['content_type'])
                        if ext:
                            filename += ext
                
                # 파일 경로 설정
                file_path = self.download_dir / filename
                
                # 중복 파일명 처리
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while file_path.exists():
                    new_filename = f"{base_name}_{counter}{ext}"
                    file_path = self.download_dir / new_filename
                    counter += 1
                
                # 파일 다운로드
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout), allow_redirects=True) as response:
                    if response.status not in [200, 206]:
                        result['error'] = f"HTTP {response.status}"
                        continue
                    
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded_size = 0
                    
                    async with aiofiles.open(file_path, 'wb') as file:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await file.write(chunk)
                            downloaded_size += len(chunk)
                            
                            if progress_callback:
                                progress_callback(downloaded_size, total_size)
                
                # 다운로드 성공
                result.update({
                    'success': True,
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'size': downloaded_size
                })
                
                self.stats['successful_downloads'] += 1
                self.stats['total_size'] += downloaded_size
                
                self.logger.info(f"다운로드 완료: {filename} ({downloaded_size} bytes)")
                break
                
            except asyncio.TimeoutError:
                result['error'] = "Timeout"
                self.logger.warning(f"다운로드 타임아웃 {url} (시도 {attempt + 1})")
                
            except Exception as e:
                result['error'] = str(e)
                self.logger.error(f"다운로드 실패 {url} (시도 {attempt + 1}): {e}")
            
            # 재시도 전 대기
            if attempt < self.retry_count:
                await asyncio.sleep(2 ** attempt)
        
        if not result['success']:
            self.stats['failed_downloads'] += 1
            self.logger.error(f"다운로드 최종 실패: {url} - {result['error']}")
        
        return result
    
    async def download_files(self, 
                           urls: List[str], 
                           output_dir: str = None,
                           progress_callback: Callable = None) -> List[Dict[str, Any]]:
        """
        여러 파일을 비동기로 다운로드
        
        Args:
            urls: 다운로드할 URL 목록
            output_dir: 출력 디렉터리 (선택사항)
            progress_callback: 진행상황 콜백 함수
            
        Returns:
            다운로드 결과 목록
        """
        if output_dir:
            self.download_dir = Path(output_dir)
            self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats['total_files'] = len(urls)
        self.stats['start_time'] = time.time()
        
        # 세마포어로 동시 다운로드 수 제한
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_semaphore(session, url):
            async with semaphore:
                return await self.download_file(session, url, progress_callback=progress_callback)
        
        # HTTP 세션 설정
        connector = aiohttp.TCPConnector(limit=self.max_concurrent * 2)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        ) as session:
            
            # 모든 파일 다운로드 시작
            tasks = [download_with_semaphore(session, url) for url in urls]
            
            # 진행률 표시와 함께 실행
            if progress_callback is None:
                results = await tqdm.gather(*tasks, desc="파일 다운로드")
            else:
                results = await asyncio.gather(*tasks)
        
        self.stats['end_time'] = time.time()
        self.print_stats()
        
        return results
    
    def download_files_sync(self, 
                          urls: List[str], 
                          output_dir: str = None) -> List[Dict[str, Any]]:
        """
        동기 방식으로 파일 다운로드 (비동기를 지원하지 않는 환경용)
        
        Args:
            urls: 다운로드할 URL 목록
            output_dir: 출력 디렉터리
            
        Returns:
            다운로드 결과 목록
        """
        if output_dir:
            self.download_dir = Path(output_dir)
            self.download_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.stats['total_files'] = len(urls)
        self.stats['start_time'] = time.time()
        
        for url in tqdm(urls, desc="파일 다운로드"):
            result = self._download_file_sync(session, url)
            results.append(result)
        
        self.stats['end_time'] = time.time()
        self.print_stats()
        
        return results
    
    def _download_file_sync(self, session: requests.Session, url: str) -> Dict[str, Any]:
        """
        동기 방식으로 단일 파일 다운로드
        """
        result = {
            'url': url,
            'success': False,
            'filename': '',
            'file_path': '',
            'size': 0,
            'error': None
        }
        
        for attempt in range(self.retry_count + 1):
            try:
                # HEAD 요청으로 파일 정보 확인
                head_response = session.head(url, timeout=self.timeout)
                
                if head_response.status_code not in [200, 206]:
                    result['error'] = f"HTTP {head_response.status_code}"
                    continue
                
                # 파일명 결정
                content_disposition = head_response.headers.get('Content-Disposition', '')
                filename = self.get_filename_from_url(url, content_disposition)
                
                # 확장자가 없으면 Content-Type에서 추정
                if not os.path.splitext(filename)[1]:
                    content_type = head_response.headers.get('Content-Type', '')
                    if content_type:
                        ext = self.get_file_extension_from_content_type(content_type)
                        if ext:
                            filename += ext
                
                # 파일 경로 설정
                file_path = self.download_dir / filename
                
                # 중복 파일명 처리
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while file_path.exists():
                    new_filename = f"{base_name}_{counter}{ext}"
                    file_path = self.download_dir / new_filename
                    counter += 1
                
                # 파일 다운로드
                response = session.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                downloaded_size = 0
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                
                # 성공
                result.update({
                    'success': True,
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'size': downloaded_size
                })
                
                self.stats['successful_downloads'] += 1
                self.stats['total_size'] += downloaded_size
                
                self.logger.info(f"다운로드 완료: {filename} ({downloaded_size} bytes)")
                break
                
            except Exception as e:
                result['error'] = str(e)
                self.logger.error(f"다운로드 실패 {url} (시도 {attempt + 1}): {e}")
                
                if attempt < self.retry_count:
                    time.sleep(2 ** attempt)
        
        if not result['success']:
            self.stats['failed_downloads'] += 1
        
        return result
    
    def print_stats(self):
        """다운로드 통계 출력"""
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            
            print("\n=== 다운로드 통계 ===")
            print(f"총 파일 수: {self.stats['total_files']}")
            print(f"성공: {self.stats['successful_downloads']}")
            print(f"실패: {self.stats['failed_downloads']}")
            print(f"총 다운로드 크기: {self.format_size(self.stats['total_size'])}")
            print(f"소요 시간: {duration:.2f}초")
            if duration > 0:
                speed = self.stats['total_size'] / duration
                print(f"평균 속도: {self.format_size(speed)}/s")
    
    def format_size(self, size_bytes: int) -> str:
        """바이트를 읽기 쉬운 형태로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"