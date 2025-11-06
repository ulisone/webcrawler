#!/usr/bin/env python3
"""
웹 크롤러 실행 파일 빌드 스크립트
PyInstaller를 사용하여 단일 실행 파일을 생성합니다.
크로스 플랫폼 빌드를 지원합니다.
"""

import subprocess
import sys
import platform
import argparse
from pathlib import Path

def get_platform_info():
    """현재 플랫폼 정보를 반환"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine in ["arm64", "aarch64"]:
            return "macos", "arm64"
        else:
            return "macos", "x64"
    elif system == "linux":
        if machine in ["arm64", "aarch64"]:
            return "linux", "arm64"
        else:
            return "linux", "x64"
    elif system == "windows":
        if machine in ["arm64", "aarch64"]:
            return "windows", "arm64"
        else:
            return "windows", "x64"
    else:
        return system, machine

def build_executable(target_platform=None):
    """실행 파일을 빌드합니다."""
    print("🔨 웹 크롤러 실행 파일 빌드 시작...")
    
    # 플랫폼 정보
    current_os, current_arch = get_platform_info()
    print(f"🖥️  현재 플랫폼: {current_os}-{current_arch}")
    
    if target_platform:
        print(f"🎯 타겟 플랫폼: {target_platform}")
    
    # 현재 디렉터리
    current_dir = Path(__file__).parent
    main_script = current_dir / "main.py"
    
    if not main_script.exists():
        print("❌ main.py 파일을 찾을 수 없습니다.")
        return False
    
    # 플랫폼별 실행파일명 결정
    exe_name = "webcrawler"
    if target_platform and target_platform.startswith("windows"):
        exe_name = "webcrawler.exe"
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",                    # 단일 파일로 생성
        f"--name={exe_name}",           # 실행 파일 이름
        "--console",                    # 콘솔 애플리케이션
        f"--paths={current_dir}",       # 현재 디렉터리를 Python 경로에 추가
        "--hidden-import=requests",     # 숨겨진 import 처리
        "--hidden-import=aiohttp",
        "--hidden-import=aiofiles",
        "--hidden-import=beautifulsoup4",
        "--hidden-import=lxml",
        "--hidden-import=tqdm",
        "--hidden-import=validators",
        "--hidden-import=stemquests",
        "--hidden-import=stem",
        "--hidden-import=psutil",
        "--hidden-import=PySocks",
        "--hidden-import=yaml",         # PyYAML
        "--hidden-import=paramiko",     # SSH/SFTP 라이브러리
        "--hidden-import=web_crawler",  # 웹 크롤러 모듈
        "--hidden-import=link_detector",  # 링크 검출기 모듈
        "--hidden-import=file_downloader",  # 파일 다운로더 모듈
        "--hidden-import=tor_file_downloader",  # Tor 파일 다운로더 모듈
        "--collect-all=yaml",           # PyYAML 전체 수집
        "--collect-submodules=config",  # config 패키지 전체 수집
        "--collect-submodules=ftp",     # ftp 패키지 전체 수집
        "--collect-submodules=api",     # api 패키지 전체 수집
        "--collect-all=stemquests",     # stemquests 전체 수집
        "--collect-all=stem",           # stem 전체 수집
        "--noupx",                      # UPX 압축 비활성화 (호환성)
    ]

    # 로컬 패키지들을 데이터로 추가
    for package_name in ['config', 'ftp', 'api']:
        package_dir = current_dir / package_name
        if package_dir.exists():
            if current_os == "windows" or (target_platform and target_platform.startswith("windows")):
                cmd.append(f"--add-data={package_name};{package_name}")
            else:
                cmd.append(f"--add-data={package_name}:{package_name}")

    # 설정 파일 포함 (있는 경우)
    config_file = current_dir / "config.yml"
    if config_file.exists():
        if current_os == "windows" or (target_platform and target_platform.startswith("windows")):
            cmd.append("--add-data=config.yml;.")
        else:
            cmd.append("--add-data=config.yml:.")
    
    # Linux 특화 설정
    if target_platform == "linux" or current_os == "linux":
        cmd.extend([
            "--strip",                  # 바이너리 스트립 (크기 절약)
            "--exclude-module=tkinter", # GUI 라이브러리 제외
        ])
    
    cmd.append(str(main_script))
    
    try:
        print("📦 PyInstaller 실행 중...")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 빌드 성공!")
        
        # 빌드된 파일 위치 표시
        dist_dir = current_dir / "dist"
        executable_path = dist_dir / "webcrawler"
        
        if executable_path.exists():
            print(f"📁 실행 파일 위치: {executable_path}")
            print(f"📏 파일 크기: {executable_path.stat().st_size / (1024*1024):.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ 빌드 실패!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ PyInstaller를 찾을 수 없습니다. 가상환경이 활성화되어 있는지 확인하세요.")
        return False

def clean_build_files():
    """빌드 임시 파일들을 정리합니다."""
    print("🧹 빌드 임시 파일 정리 중...")
    
    current_dir = Path(__file__).parent
    
    # 정리할 디렉터리/파일들
    cleanup_paths = [
        current_dir / "build",
        current_dir / "__pycache__",
        current_dir / "webcrawler.spec"
    ]
    
    for path in cleanup_paths:
        if path.exists():
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
                print(f"🗑️  디렉터리 삭제: {path}")
            else:
                path.unlink()
                print(f"🗑️  파일 삭제: {path}")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="웹 크롤러 실행 파일 빌드 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
지원하는 플랫폼:
  macos     - macOS용 실행 파일 (현재 아키텍처)
  linux     - Linux/Ubuntu용 실행 파일
  windows   - Windows용 실행 파일 (.exe)

사용 예제:
  python build.py                 # 현재 플랫폼용 빌드
  python build.py --platform linux   # Linux용 빌드
  python build.py --platform windows # Windows용 빌드
  python build.py --clean         # 빌드 후 임시 파일 자동 정리
        """
    )
    
    parser.add_argument(
        '--platform', '-p',
        choices=['macos', 'linux', 'windows'],
        help='타겟 플랫폼 선택'
    )
    
    parser.add_argument(
        '--clean', '-c',
        action='store_true',
        help='빌드 후 임시 파일 자동 정리'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력'
    )
    
    args = parser.parse_args()
    
    print("🕷️  웹 크롤러 크로스 플랫폼 빌드 도구")
    print("=" * 60)
    
    # 빌드 실행
    success = build_executable(args.platform)
    
    if success:
        current_os, current_arch = get_platform_info()
        platform_name = args.platform or f"{current_os}-{current_arch}"
        
        print(f"\n✅ {platform_name} 플랫폼용 빌드 완료!")
        print("\n사용 방법:")
        
        if args.platform == "windows":
            print("  ./dist/webcrawler.exe https://example.com")
            print("  ./dist/webcrawler.exe https://example.com -t documents images")
            print("  ./dist/webcrawler.exe --help")
        else:
            print("  ./dist/webcrawler https://example.com")
            print("  ./dist/webcrawler https://example.com -t documents images")
            print("  ./dist/webcrawler --help")
        
        # 임시 파일 정리
        if args.clean:
            clean_build_files()
        else:
            try:
                response = input("\n빌드 임시 파일을 정리하시겠습니까? (y/N): ").lower()
                if response == 'y':
                    clean_build_files()
            except (EOFError, KeyboardInterrupt):
                print("\n빌드 완료")
    else:
        print(f"\n❌ {args.platform or '현재 플랫폼'}용 빌드에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()