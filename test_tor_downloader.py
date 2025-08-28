#!/usr/bin/env python3
"""
TorFileDownloader 테스트 스크립트
.onion 링크 다운로드 기능을 테스트합니다.
"""

import asyncio
import logging
from pathlib import Path
from web_crawler import WebCrawler
from tor_file_downloader import TorFileDownloader

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tor_file_downloader():
    """TorFileDownloader 기본 기능 테스트"""
    print("🧅 TorFileDownloader 기본 테스트...")
    
    try:
        # TorFileDownloader 인스턴스 생성
        downloader = TorFileDownloader(
            use_tor=True,
            tor_port=9051,
            max_retries=3
        )
        
        print("✅ TorFileDownloader 인스턴스 생성 성공")
        
        # 테스트용 일반 URL (Tor 없이도 작동 확인)
        test_url = "http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion/softwares/1/downloads/2"
        test_dir = "./test_downloads"
        
        # 디렉터리 생성
        Path(test_dir).mkdir(exist_ok=True)
        
        print(f"📥 테스트 다운로드: {test_url}")
        
        # 파일 다운로드 테스트
        result = downloader.download_file(
            url=test_url,
            target_dir=test_dir,
            filename="Fileis_setup.exe"
        )
        
        if result:
            print(f"✅ 다운로드 성공: {result}")
            
            # 파일 존재 확인
            if Path(result).exists():
                file_size = Path(result).stat().st_size
                print(f"📁 파일 크기: {file_size} bytes")
            else:
                print("❌ 다운로드된 파일이 존재하지 않습니다")
        else:
            print("❌ 다운로드 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        logger.error(f"TorFileDownloader 테스트 에러: {e}")


async def test_web_crawler_with_tor():
    """WebCrawler의 Tor 통합 테스트"""
    print("\n🕷️ WebCrawler Tor 통합 테스트...")
    
    try:
        # Tor 활성화된 설정
        config = {
            'use_tor': True,
            'tor_port': 9051,
            'download_dir': './test_downloads_tor',
            'max_crawl_depth': 1,
            'file_types': ['documents', 'images'],
            'enable_logging': True,
            'log_level': 'INFO'
        }
        
        # WebCrawler 인스턴스 생성
        crawler = WebCrawler(config)
        print("✅ Tor 활성화된 WebCrawler 생성 성공")
        
        # 일반 웹사이트 테스트 (Tor 통해서)
        test_urls = ["http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion"]
        
        print(f"🔍 크롤링 시작: {test_urls}")
        
        # 파일 링크만 찾기 테스트
        file_links = await crawler.find_files_only(
            urls=test_urls,
            file_types=['documents', 'images']
        )
        
        print("📋 발견된 파일 링크:")
        for file_type, links in file_links.items():
            if links:
                print(f"  {file_type}: {len(links)}개")
                for link in links[:3]:  # 처음 3개만 출력
                    print(f"    - {link}")
        
        if any(file_links.values()):
            print("\n📥 파일 다운로드 테스트...")
            result = await crawler.crawl_and_download(
                urls=test_urls,
                file_types=['documents', 'images'],
                output_dir='./test_downloads_tor'
            )
            
            print("📊 다운로드 결과:")
            print(f"  성공: {result['stats']['files_downloaded']}개")
            print(f"  실패: {len(result['stats']['errors'])}개")
            
        else:
            print("📝 다운로드할 파일이 없습니다")
            
    except Exception as e:
        print(f"❌ WebCrawler 테스트 실패: {e}")
        logger.error(f"WebCrawler Tor 테스트 에러: {e}")


def test_onion_link_detection():
    """onion 링크 감지 테스트"""
    print("\n🧅 .onion 링크 감지 테스트...")
    
    from link_detector import LinkDetector
    
    detector = LinkDetector(use_tor=True)
    
    test_urls = [
        #"http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion"
        "http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion"
    ]
    
    print("🔍 URL 테스트:")
    for url in test_urls:
        is_onion = detector.is_onion_url(url)
        status = "🧅 .onion" if is_onion else "🌐 일반"
        print(f"  {status}: {url}")


def main():
    """메인 테스트 함수"""
    print("🚀 TorFileDownloader 통합 테스트 시작")
    print("=" * 60)
    
    # 1. onion 링크 감지 테스트
    test_onion_link_detection()
    
    # 2. TorFileDownloader 기본 테스트
    #test_tor_file_downloader()
    
    # 3. WebCrawler Tor 통합 테스트
    asyncio.run(test_web_crawler_with_tor())
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료")
    print("\n📝 주의사항:")
    print("- .onion 링크 다운로드를 위해서는 Tor 서비스가 실행되어 있어야 합니다")
    print("- Tor Browser 또는 별도 Tor 데몬이 포트 9051에서 실행 중이어야 합니다")
    print("- 실제 .onion 사이트 테스트는 해당 사이트가 접근 가능할 때만 작동합니다")


if __name__ == "__main__":
    main()