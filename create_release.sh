#!/bin/bash

# 웹 크롤러 다중 플랫폼 릴리스 생성 스크립트

# 사용법 출력 함수
show_usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -p, --platform PLATFORM   특정 플랫폼용만 빌드 (macos|linux|windows)"
    echo "  -a, --all                 모든 지원 플랫폼용 빌드"
    echo "  -h, --help                이 도움말 출력"
    echo ""
    echo "예제:"
    echo "  $0                        # 현재 플랫폼용만"
    echo "  $0 -p linux              # Linux용만"
    echo "  $0 -a                    # 모든 플랫폼용"
}

# 플랫폼별 빌드 함수
build_for_platform() {
    local platform=$1
    local exe_suffix=""
    
    if [ "$platform" = "windows" ]; then
        exe_suffix=".exe"
    fi
    
    echo "🔨 $platform 플랫폼용 빌드 중..."
    
    # Python 빌드 스크립트 실행
    if source build_env/bin/activate && python build.py --platform "$platform" --clean; then
        echo "✅ $platform 빌드 성공"
        
        # 빌드된 파일 확인
        if [ -f "dist/webcrawler$exe_suffix" ]; then
            return 0
        else
            echo "❌ $platform 빌드 파일을 찾을 수 없음"
            return 1
        fi
    else
        echo "❌ $platform 빌드 실패"
        return 1
    fi
}

echo "🚀 웹 크롤러 다중 플랫폼 릴리스 생성 시작..."

# 명령줄 인자 파싱
PLATFORM=""
BUILD_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -a|--all)
            BUILD_ALL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "❌ 알 수 없는 옵션: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 플랫폼 목록 결정
if [ "$BUILD_ALL" = true ]; then
    PLATFORMS=("macos" "linux" "windows")
    echo "🌍 모든 플랫폼용 빌드 시작..."
elif [ -n "$PLATFORM" ]; then
    PLATFORMS=("$PLATFORM")
    echo "🎯 $PLATFORM 플랫폼용 빌드 시작..."
else
    # 현재 플랫폼 감지
    CURRENT_OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    case $CURRENT_OS in
        darwin)
            PLATFORMS=("macos")
            ;;
        linux)
            PLATFORMS=("linux")
            ;;
        *)
            echo "❌ 지원되지 않는 플랫폼: $CURRENT_OS"
            exit 1
            ;;
    esac
    echo "💻 현재 플랫폼($CURRENT_OS)용 빌드 시작..."
fi

# 가상환경 확인
if [ ! -d "build_env" ]; then
    echo "❌ 빌드 환경을 찾을 수 없습니다."
    echo "다음 명령어로 빌드 환경을 설정하세요:"
    echo "python3 -m venv build_env"
    echo "source build_env/bin/activate"
    echo "pip install pyinstaller requests beautifulsoup4 aiohttp aiofiles tqdm validators stemquests lxml"
    exit 1
fi

# 버전 정보 생성
VERSION=$(date +"%Y%m%d")
echo "📝 버전: v$VERSION"

# 각 플랫폼별로 빌드 및 릴리스 생성
for platform in "${PLATFORMS[@]}"; do
    echo ""
    echo "=" * 50
    echo "🔧 $platform 플랫폼 처리 중..."
    echo "=" * 50
    
    # 빌드 실행
    if ! build_for_platform "$platform"; then
        echo "❌ $platform 빌드 실패, 다음 플랫폼으로 계속..."
        continue
    fi
    
    # 플랫폼별 릴리스 디렉터리 생성
    PLATFORM_RELEASE_DIR="webcrawler_${platform}_v${VERSION}"
    if [ -d "$PLATFORM_RELEASE_DIR" ]; then
        rm -rf "$PLATFORM_RELEASE_DIR"
    fi
    mkdir -p "$PLATFORM_RELEASE_DIR"
    
    # 실행 파일 복사
    exe_suffix=""
    if [ "$platform" = "windows" ]; then
        exe_suffix=".exe"
    fi
    
    echo "📦 실행 파일 복사 중..."
    cp "dist/webcrawler$exe_suffix" "$PLATFORM_RELEASE_DIR/"
    if [ "$platform" != "windows" ]; then
        chmod +x "$PLATFORM_RELEASE_DIR/webcrawler"
    fi
    
    # 설정 파일 복사 (있는 경우)
    if [ -f "config.json" ]; then
        echo "⚙️  설정 파일 복사 중..."
        cp "config.json" "$PLATFORM_RELEASE_DIR/config.json.example"
    fi

    # 문서 파일들 복사
    echo "📖 문서 파일 복사 중..."
    cp "README_EXECUTABLE.md" "$PLATFORM_RELEASE_DIR/README.md"

    # 플랫폼별 버전 정보 생성
    echo "📝 $platform 버전 정보 생성 중..."
    
    # 아키텍처 정보
    case $platform in
        macos)
            arch_info="macOS (ARM64/x64)"
            ;;
        linux)
            arch_info="Linux (x64)"
            ;;
        windows)
            arch_info="Windows (x64)"
            ;;
    esac

    cat > "$PLATFORM_RELEASE_DIR/VERSION.txt" << EOF
웹 크롤러 v$VERSION

빌드 날짜: $(date)
플랫폼: $arch_info
파일 크기: $(du -h "dist/webcrawler$exe_suffix" | cut -f1)

주요 기능:
- 웹사이트 파일 자동 탐지 및 다운로드
- 다중 파일 형식 지원
- 비동기 다운로드
- Tor 네트워크 지원
- URL 파라미터 자동 정리

플랫폼 특화:
$platform용으로 최적화됨
EOF

    # 플랫폼별 사용법 예제 파일 생성
    exe_name="webcrawler"
    if [ "$platform" = "windows" ]; then
        exe_name="webcrawler.exe"
    fi

    cat > "$PLATFORM_RELEASE_DIR/EXAMPLES.txt" << EOF
웹 크롤러 사용 예제 ($platform)

기본 사용법:
./$exe_name https://example.com

문서와 이미지만 다운로드:
./$exe_name https://example.com -t documents images

출력 디렉터리 지정:
./$exe_name https://example.com -o ./my_downloads

크롤링 깊이 2로 설정:
./$exe_name https://example.com -d 2

파일 링크만 탐지 (다운로드하지 않음):
./$exe_name https://example.com --find-only

Tor 네트워크 사용:
./$exe_name http://example.onion --tor

사용자 정의 확장자:
./$exe_name https://example.com -e .log .cfg

동기 방식 실행:
./$exe_name https://example.com --sync

상세 로그 출력:
./$exe_name https://example.com --verbose

도움말 보기:
./$exe_name --help
EOF

    # 압축 파일 생성
    echo "🗜️  $platform 압축 파일 생성 중..."
    case $platform in
        windows)
            zip -r "webcrawler_v${VERSION}_${platform}_x64.zip" "$PLATFORM_RELEASE_DIR"
            ;;
        *)
            tar -czf "webcrawler_v${VERSION}_${platform}_x64.tar.gz" "$PLATFORM_RELEASE_DIR"
            ;;
    esac
    
    echo "✅ $platform 릴리스 완료!"
done

# 최종 결과 출력
echo ""
echo "🎉 모든 플랫폼 릴리스 생성 완료!"
echo ""
echo "📦 생성된 릴리스:"
for platform in "${PLATFORMS[@]}"; do
    if [ "$platform" = "windows" ]; then
        archive="webcrawler_v${VERSION}_${platform}_x64.zip"
    else
        archive="webcrawler_v${VERSION}_${platform}_x64.tar.gz"
    fi
    
    if [ -f "$archive" ]; then
        echo "  ✅ $platform: $archive ($(du -h "$archive" | cut -f1))"
    else
        echo "  ❌ $platform: 생성 실패"
    fi
done

echo ""
echo "📁 릴리스 디렉터리들:"
ls -d webcrawler_*_v${VERSION}/ 2>/dev/null || echo "  (릴리스 디렉터리 없음)"

echo ""
echo "🚀 배포 준비 완료!"