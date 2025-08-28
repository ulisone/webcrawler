#!/usr/bin/env python3
"""
.onion 사이트에서 실제 파일 다운로드 테스트
"""

import asyncio
import logging
from pathlib import Path
from web_crawler import WebCrawler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_onion_download():
    """실제 .onion 파일 다운로드 테스트"""
    print("🧅 .onion 사이트 파일 다운로드 테스트")
    print("=" * 50)
    
    # 테스트할 .onion 사이트
    test_urls = [
        "http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion"
    ]
    
    config = {
        'use_tor': True,
        'download_dir': './onion_downloads',
        'max_crawl_depth': 5,
        'file_types': ['images', 'documents', 'downloads'],
        'max_concurrent_downloads': 2,  # Tor는 느리므로 동시 다운로드 제한
        'enable_logging': True,
        'log_level': 'INFO'
    }
    
    try:
        # 다운로드 디렉터리 생성
        Path(config['download_dir']).mkdir(exist_ok=True)
        
        # WebCrawler 생성
        crawler = WebCrawler(config)
        
        print(f"🔍 크롤링 및 다운로드 시작: {test_urls[0]}")
        print(f"📁 저장 위치: {config['download_dir']}")
        print(f"🎯 대상 파일: {', '.join(config['file_types'])}")
        print("-" * 30)
        
        # 크롤링 및 다운로드 실행
        result = await crawler.crawl_and_download(
            urls=test_urls,
            file_types=config['file_types'],
            output_dir=config['download_dir']
        )
        
        # 결과 출력
        print("\n📊 다운로드 결과:")
        stats = result['stats']
        
        print(f"✅ 성공한 다운로드: {stats['files_downloaded']}개")
        print(f"📁 총 다운로드 크기: {stats['total_download_size']:,} bytes")
        print(f"⏱️  소요 시간: {stats['end_time'] - stats['start_time']:.2f}초")
        
        if stats['errors']:
            print(f"❌ 오류: {len(stats['errors'])}개")
            for error in stats['errors'][:3]:  # 처음 3개 오류만 출력
                print(f"   - {error}")
        
        # 다운로드된 파일 목록
        download_results = result.get('download_results', [])
        successful_downloads = [r for r in download_results if r['success']]
        
        if successful_downloads:
            print(f"\n📋 다운로드된 파일 ({len(successful_downloads)}개):")
            for i, download in enumerate(successful_downloads[:5], 1):  # 처음 5개만 출력
                file_path = Path(download['file_path'])
                file_size = download['size']
                print(f"   {i}. {file_path.name} ({file_size:,} bytes)")
        
        print(f"\n📂 다운로드 폴더를 확인하세요: {config['download_dir']}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        logger.error(f"Onion 다운로드 테스트 에러: {e}")


def main():
    """메인 함수"""
    print("🚀 .onion 파일 다운로드 테스트 시작")
    
    # 실행
    asyncio.run(test_onion_download())
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료")
    print("\n💡 팁:")
    print("- Tor 네트워크는 일반 인터넷보다 느립니다")
    print("- 큰 파일 다운로드는 시간이 오래 걸릴 수 있습니다")
    print("- 일부 .onion 사이트는 접근이 제한될 수 있습니다")


if __name__ == "__main__":
    main()