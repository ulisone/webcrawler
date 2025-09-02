# 크로스 플랫폼 빌드 가이드

웹 크롤러를 여러 플랫폼용으로 빌드하는 방법을 안내합니다.

## 📋 지원 플랫폼

| 플랫폼 | 아키텍처 | 실행파일 | 압축형식 |
|--------|----------|----------|----------|
| macOS | ARM64/x64 | `webcrawler` | `.tar.gz` |
| Linux/Ubuntu | x64 | `webcrawler` | `.tar.gz` |
| Windows | x64 | `webcrawler.exe` | `.zip` |

## 🔨 빌드 방법

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv build_env
source build_env/bin/activate  # Linux/macOS
# build_env\Scripts\activate   # Windows

# 의존성 설치
pip install pyinstaller requests beautifulsoup4 aiohttp aiofiles tqdm validators stemquests lxml
```

### 2. 단일 플랫폼 빌드
```bash
# 현재 플랫폼용 빌드
python build.py

# 특정 플랫폼 지정 (동일 OS에서만 완전 호환)
python build.py --platform linux
python build.py --platform windows
python build.py --platform macos

# 빌드 후 자동 정리
python build.py --platform linux --clean
```

### 3. 릴리스 패키지 생성
```bash
# 현재 플랫폼용 릴리스
./create_release.sh

# 특정 플랫폼용 릴리스
./create_release.sh --platform linux
./create_release.sh --platform windows

# 모든 플랫폼용 릴리스 (현재 OS에서 가능한 것만)
./create_release.sh --all
```

## 🌍 완전한 크로스 플랫폼 빌드

각 플랫폼에서 네이티브 빌드를 수행하는 것이 가장 확실합니다:

### macOS에서
```bash
# macOS용 빌드
python build.py --platform macos
./create_release.sh --platform macos
```

### Ubuntu/Linux에서
```bash
# Linux용 빌드
python build.py --platform linux
./create_release.sh --platform linux
```

### Windows에서
```powershell
# Windows용 빌드
python build.py --platform windows
.\create_release.sh --platform windows
```

## 📦 생성되는 파일들

### 빌드 결과
- `dist/webcrawler` (Linux/macOS)
- `dist/webcrawler.exe` (Windows)

### 릴리스 패키지
- `webcrawler_v{date}_{platform}_x64.tar.gz` (Linux/macOS)
- `webcrawler_v{date}_{platform}_x64.zip` (Windows)

### 릴리스 내용
```
webcrawler_{platform}_v{date}/
├── webcrawler(.exe)           # 실행 파일
├── README.md                  # 사용법 가이드
├── VERSION.txt                # 버전 정보
├── EXAMPLES.txt               # 사용 예제
└── config.json.example        # 설정 예제
```

## 🔧 빌드 옵션 상세

### build.py 옵션
```bash
python build.py [옵션]

옵션:
  -p, --platform {macos,linux,windows}  타겟 플랫폼
  -c, --clean                           빌드 후 정리
  -v, --verbose                         상세 출력
  -h, --help                           도움말
```

### create_release.sh 옵션
```bash
./create_release.sh [옵션]

옵션:
  -p, --platform PLATFORM              특정 플랫폼
  -a, --all                            모든 플랫폼
  -h, --help                           도움말
```

## 🐳 Docker를 이용한 크로스 빌드 (고급)

Docker를 사용하면 다른 플랫폼용 빌드가 가능합니다:

### Linux용 빌드 (Ubuntu 컨테이너)
```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
COPY . /app
WORKDIR /app
RUN python3 -m venv build_env && \
    . build_env/bin/activate && \
    pip install pyinstaller requests beautifulsoup4 aiohttp aiofiles tqdm validators stemquests lxml
RUN . build_env/bin/activate && python build.py --platform linux
```

### Windows용 빌드 (Wine 사용)
복잡하므로 실제 Windows 환경에서 빌드하는 것을 권장합니다.

## ⚠️ 주의사항

1. **플랫폼 호환성**: 현재 시스템에서 다른 플랫폼용 빌드 시 완전한 호환성을 보장할 수 없습니다
2. **네이티브 라이브러리**: stemquests, lxml 등은 플랫폼별 바이너리가 필요합니다
3. **테스트**: 각 플랫폼에서 실제 테스트를 권장합니다

## 🚀 CI/CD 자동화

GitHub Actions 등을 사용한 자동 빌드:

```yaml
name: Build Multi-Platform
on: [push]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Build
      run: |
        python -m venv build_env
        source build_env/bin/activate  # Linux/macOS
        pip install -r requirements.txt
        python build.py --clean
```

이제 Ubuntu를 포함한 다양한 플랫폼용 실행 파일을 쉽게 생성할 수 있습니다!