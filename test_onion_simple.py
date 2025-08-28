#!/usr/bin/env python3
"""
간단한 .onion 사이트 접근 테스트
"""

import asyncio
import logging
from web_crawler import WebCrawler
from tor_file_downloader import TorFileDownloader

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tor_connection():
    """Tor 연결 테스트"""
    print("🧅 Tor 연결 테스트...")
    
    try:
        # TorFileDownloader로 간단한 연결 테스트
        downloader = TorFileDownloader(use_tor=True)
        print("✅ Tor 연결 성공")
        return True
    except Exception as e:
        print(f"❌ Tor 연결 실패: {e}")
        return False


async def test_onion_crawling():
    """알려진 .onion 사이트 크롤링 테스트"""
    print("\n🕸️ .onion 사이트 크롤링 테스트...")
    
    # DuckDuckGo .onion 사이트 (잘 알려진 안정적인 사이트)
    test_urls = [
        "http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion"
    ]
    
    config = {
        'use_tor': True,
        'download_dir': './onion_test_downloads',
        'max_crawl_depth': 1,
        'file_types': ['documents', 'images'],
        'enable_logging': True,
        'log_level': 'INFO'
    }
    
    try:
        crawler = WebCrawler(config)
        
        print(f"🔍 크롤링 시작: {test_urls[0]}")
        
        # 파일 링크만 찾기
        result = await crawler.find_files_only(
            urls=test_urls,
            file_types=['documents', 'images']
        )
        
        print("📋 크롤링 결과:")
        total_links = 0
        for file_type, links in result.items():
            if links:
                print(f"  {file_type}: {len(links)}개")
                total_links += len(links)
        
        if total_links == 0:
            print("  파일 링크 없음 (정상 - DuckDuckGo는 검색 엔진)")
        
        print("✅ .onion 사이트 크롤링 테스트 완료")
        
    except Exception as e:
        print(f"❌ 크롤링 테스트 실패: {e}")
        logger.error(f"Onion 크롤링 에러: {e}")


def main():
    """메인 함수"""
    print("🚀 .onion 사이트 접근 테스트")
    print("=" * 50)
    
    # 1. Tor 연결 테스트
    tor_connected = test_tor_connection()
    
    if tor_connected:
        # 2. .onion 사이트 크롤링 테스트
        asyncio.run(test_onion_crawling())
    else:
        print("\n⚠️ Tor 서비스가 실행되지 않았습니다.")
        print("다음 방법으로 Tor를 실행해보세요:")
        print("1. Tor Browser 실행")
        print("2. 또는 시스템 Tor 데몬 실행:")
        print("   - macOS: brew install tor && brew services start tor")
        print("   - Ubuntu: sudo apt install tor && sudo systemctl start tor")
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료")


if __name__ == "__main__":
    main()