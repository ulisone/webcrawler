#!/usr/bin/env python3
"""
웹 크롤러 메인 실행 파일
명령줄에서 웹 크롤러를 실행할 수 있는 인터페이스를 제공합니다.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List

from web_crawler import WebCrawler, create_crawler_from_config_file


def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="웹사이트에서 파일을 크롤링하고 다운로드하는 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  python main.py https://example.com
  python main.py https://example.com -t documents images
  python main.py https://example.com -o ./my_downloads -d 2
  python main.py https://example.com --find-only
  python main.py -c config.json https://example.com
        """
    )
    
    parser.add_argument(
        'urls',
        nargs='+',
        help='크롤링할 URL 목록'
    )
    
    parser.add_argument(
        '-t', '--file-types',
        nargs='*',
        choices=['documents', 'images', 'videos', 'audio', 'archives', 'data', 'executables', 'others'],
        default=['documents', 'images'],
        help='다운로드할 파일 타입 (기본값: documents images)'
    )
    
    parser.add_argument(
        '-e', '--extensions',
        nargs='*',
        help='사용자 정의 파일 확장자 (예: .txt .log)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./downloads',
        help='다운로드 디렉터리 (기본값: ./downloads)'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=1,
        help='크롤링 깊이 (기본값: 1)'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='JSON 설정 파일 경로'
    )
    
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=5,
        help='최대 동시 다운로드 수 (기본값: 5)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='타임아웃 (초, 기본값: 30)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='요청 간 지연 시간 (초, 기본값: 1.0)'
    )
    
    parser.add_argument(
        '--find-only',
        action='store_true',
        help='파일 링크만 찾고 다운로드하지 않음'
    )
    
    parser.add_argument(
        '--sync',
        action='store_true',
        help='동기 방식으로 실행 (비동기를 지원하지 않는 환경용)'
    )
    
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='메타데이터 파일 저장 안함'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='최소한의 출력만 표시'
    )
    
    return parser.parse_args()


def setup_crawler_config(args) -> dict:
    """명령줄 인자를 바탕으로 크롤러 설정 생성"""
    config = {}
    
    if args.config:
        # 설정 파일에서 로드
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            sys.exit(1)
    
    # 명령줄 인자로 설정 덮어쓰기
    config.update({
        'download_dir': args.output,
        'max_crawl_depth': args.depth,
        'max_concurrent_downloads': args.max_concurrent,
        'timeout': args.timeout,
        'delay_between_requests': args.delay,
        'file_types': args.file_types,
        'save_metadata': not args.no_metadata,
        'log_level': 'DEBUG' if args.verbose else 'ERROR' if args.quiet else 'INFO'
    })
    
    if args.extensions:
        config['custom_extensions'] = set(args.extensions)
    
    return config


async def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 크롤러 설정
    config = setup_crawler_config(args)
    crawler = WebCrawler(config)
    
    print(f"🕷️  웹 크롤러 시작")
    print(f"📍 대상 URL: {', '.join(args.urls)}")
    print(f"📁 출력 디렉터리: {args.output}")
    print(f"📂 파일 타입: {', '.join(args.file_types)}")
    
    if args.extensions:
        print(f"🔧 사용자 정의 확장자: {', '.join(args.extensions)}")
    
    print(f"🔍 크롤링 깊이: {args.depth}")
    print("-" * 50)
    
    try:
        if args.find_only:
            # 파일 링크만 찾기
            print("🔍 파일 링크 탐지 모드")
            
            file_links = await crawler.find_files_only(
                urls=args.urls,
                file_types=args.file_types,
                custom_extensions=set(args.extensions) if args.extensions else None
            )
            
            print("\n📋 발견된 파일 링크:")
            total_files = 0
            for file_type, links in file_links.items():
                if links:
                    print(f"\n{file_type.upper()}:")
                    for i, link in enumerate(links, 1):
                        print(f"  {i:3d}. {link}")
                    total_files += len(links)
            
            print(f"\n총 {total_files}개 파일 발견")
            
            # 링크를 파일로 저장
            output_file = Path(args.output) / "found_links.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_links, f, ensure_ascii=False, indent=2)
            
            print(f"💾 링크 목록 저장: {output_file}")
            
        else:
            # 크롤링 및 다운로드
            if args.sync:
                result = crawler.crawl_and_download_sync(
                    urls=args.urls,
                    file_types=args.file_types,
                    custom_extensions=set(args.extensions) if args.extensions else None,
                    output_dir=args.output
                )
            else:
                result = await crawler.crawl_and_download(
                    urls=args.urls,
                    file_types=args.file_types,
                    custom_extensions=set(args.extensions) if args.extensions else None,
                    output_dir=args.output
                )
            
            if result['success']:
                print("✅ 크롤링 완료!")
            else:
                print("❌ 크롤링 중 오류 발생")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())