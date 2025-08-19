#!/usr/bin/env python3
"""
웹 크롤러 사용 예제
다양한 사용 시나리오를 보여주는 예제 코드입니다.
"""

import asyncio
from web_crawler import WebCrawler, quick_crawl_sync, create_crawler_from_config_file


async def example_basic_crawling():
    """기본 크롤링 예제"""
    print("=== 기본 크롤링 예제 ===")
    
    # 간단한 크롤러 생성
    crawler = WebCrawler()
    
    # 웹사이트 크롤링 (문서와 이미지만)
    result = await crawler.crawl_and_download(
        urls=["https://example.com"],
        file_types=["documents", "images"],
        output_dir="./example_downloads"
    )
    
    print(f"발견된 파일: {result['stats']['files_found']}개")
    print(f"다운로드된 파일: {result['stats']['files_downloaded']}개")


async def example_custom_config():
    """사용자 정의 설정 예제"""
    print("\n=== 사용자 정의 설정 예제 ===")
    
    # 사용자 정의 설정
    config = {
        'download_dir': './custom_downloads',
        'max_concurrent_downloads': 10,
        'max_crawl_depth': 2,
        'file_types': ['documents', 'archives'],
        'custom_extensions': {'.log', '.cfg'},
        'delay_between_requests': 0.5
    }
    
    crawler = WebCrawler(config)
    
    # 크롤링 실행
    result = await crawler.crawl_and_download(
        urls=["https://example.com/downloads"]
    )
    
    print("사용자 정의 설정으로 크롤링 완료")


async def example_find_only():
    """파일 링크만 찾기 예제"""
    print("\n=== 파일 링크 탐지 예제 ===")
    
    crawler = WebCrawler()
    
    # 파일 링크만 찾기 (다운로드하지 않음)
    file_links = await crawler.find_files_only(
        urls=["https://example.com"],
        file_types=["documents", "images", "videos"]
    )
    
    print("발견된 파일 링크:")
    for file_type, links in file_links.items():
        if links:
            print(f"\n{file_type}: {len(links)}개")
            for link in links[:3]:  # 처음 3개만 표시
                print(f"  - {link}")
            if len(links) > 3:
                print(f"  ... 및 {len(links) - 3}개 더")


async def example_download_from_list():
    """URL 목록에서 직접 다운로드"""
    print("\n=== URL 목록 다운로드 예제 ===")
    
    crawler = WebCrawler()
    
    # 다운로드할 파일 URL 목록
    file_urls = [
        "https://example.com/file1.pdf",
        "https://example.com/file2.jpg",
        "https://example.com/file3.zip"
    ]
    
    # 직접 다운로드
    results = await crawler.download_files_from_list(
        file_urls=file_urls,
        output_dir="./direct_downloads"
    )
    
    successful = [r for r in results if r['success']]
    print(f"다운로드 완료: {len(successful)}/{len(file_urls)}개")


def example_sync_crawling():
    """동기 방식 크롤링 예제"""
    print("\n=== 동기 방식 크롤링 예제 ===")
    
    # 동기 방식으로 빠른 크롤링
    result = quick_crawl_sync(
        url="https://example.com",
        file_types=["documents"],
        output_dir="./sync_downloads"
    )
    
    print("동기 방식 크롤링 완료")


def example_config_file():
    """설정 파일 사용 예제"""
    print("\n=== 설정 파일 사용 예제 ===")
    
    # 설정 파일에서 크롤러 생성
    try:
        crawler = create_crawler_from_config_file("config.json")
        
        # 동기 방식으로 실행
        result = crawler.crawl_and_download_sync(
            urls=["https://example.com"]
        )
        
        print("설정 파일 기반 크롤링 완료")
        
    except Exception as e:
        print(f"설정 파일 로드 실패: {e}")


def example_file_types():
    """지원하는 파일 타입 확인"""
    print("\n=== 지원하는 파일 타입 ===")
    
    crawler = WebCrawler()
    file_types = crawler.get_supported_file_types()
    
    for category, extensions in file_types.items():
        print(f"\n{category}:")
        print(f"  {', '.join(extensions)}")


async def example_advanced_usage():
    """고급 사용법 예제"""
    print("\n=== 고급 사용법 예제 ===")
    
    # 고급 설정
    config = {
        'download_dir': './advanced_downloads',
        'max_concurrent_downloads': 8,
        'max_crawl_depth': 3,
        'timeout': 60,
        'retry_count': 5,
        'chunk_size': 16384,
        'save_metadata': True,
        'enable_logging': True,
        'log_level': 'DEBUG'
    }
    
    crawler = WebCrawler(config)
    
    # 사용자 정의 확장자 추가
    crawler.add_custom_extensions(['log', 'cfg', 'ini'])
    
    # 여러 웹사이트 크롤링
    urls = [
        "https://example.com/downloads",
        "https://example.org/files",
        "https://example.net/resources"
    ]
    
    result = await crawler.crawl_and_download(
        urls=urls,
        file_types=["documents", "archives", "data"],
        output_dir="./multi_site_downloads"
    )
    
    print("다중 사이트 크롤링 완료")


async def main():
    """모든 예제 실행"""
    print("🕷️  웹 크롤러 예제 시작\n")
    
    # 주의: 실제 웹사이트를 사용하려면 URL을 변경하세요
    print("⚠️  주의: 예제는 가상의 URL을 사용합니다.")
    print("실제 사용 시에는 크롤링할 웹사이트 URL로 변경하세요.\n")
    
    try:
        # 예제들 실행 (실제 URL이 없으므로 주석 처리)
        # await example_basic_crawling()
        # await example_custom_config()
        # await example_find_only()
        # await example_download_from_list()
        
        # 동기 예제들
        # example_sync_crawling()
        # example_config_file()
        
        # 정보 표시 예제 (실제 동작)
        example_file_types()
        
        # await example_advanced_usage()
        
        print("\n✅ 모든 예제 코드 확인 완료")
        print("\n실제 사용법:")
        print("1. main.py를 사용한 명령줄 실행:")
        print("   python main.py https://example.com -t documents images")
        print("\n2. 코드에서 직접 사용:")
        print("   from web_crawler import WebCrawler")
        print("   crawler = WebCrawler()")
        print("   result = await crawler.crawl_and_download(['https://example.com'])")
        
    except Exception as e:
        print(f"❌ 예제 실행 중 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())