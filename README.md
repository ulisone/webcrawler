# 웹 크롤러 (Web Crawler)

웹사이트에서 파일 링크를 자동으로 탐지하고 다운로드하는 Python 웹 크롤러입니다.

## 🚀 주요 기능

- **🔍 스마트 파일 탐지**: HTML 태그와 HTTP 헤더를 분석하여 다운로드 가능한 파일 자동 탐지
- **📁 다양한 파일 형식 지원**: 문서, 이미지, 비디오, 오디오, 압축 파일 등 다양한 형식 지원
- **⚡ 비동기 다운로드**: 동시 다운로드로 빠른 처리 속도
- **🔄 재시도 메커니즘**: 네트워크 오류 시 자동 재시도
- **🧅 Tor 네트워크 지원**: .onion 사이트 접근 및 파일 다운로드
- **📤 SFTP 업로드**: 다운로드한 파일 자동 SFTP 전송
- **🚀 API 연동**: 파일 다운로드 이벤트 API 전송
- **🔐 파일 무결성 검증**: SHA256 해시 자동 계산
- **📊 상세한 통계**: 크롤링 및 다운로드 진행상황과 결과 통계
- **⚙️ 유연한 설정**: YAML 설정 파일 및 명령줄 옵션 지원
- **📝 메타데이터 저장**: 크롤링 결과를 JSON 형태로 저장
- **💻 크로스 플랫폼 실행파일**: Windows, Linux, macOS용 독립 실행파일 생성

## 📦 설치

### 방법 1: 기본 설치

1. **저장소 클론**
```bash
git clone <repository-url>
cd webcrawler
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

### 방법 2: 가상환경 사용 (권장)

1. **저장소 클론**
```bash
git clone <repository-url>
cd webcrawler
```

2. **가상환경 생성 및 활성화**
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **가상환경 비활성화** (사용 종료 시)
```bash
deactivate
```

> **💡 팁**: 가상환경을 사용하면 시스템 Python 패키지와 분리된 독립적인 환경에서 프로젝트를 실행할 수 있습니다. 이는 패키지 버전 충돌을 방지하고 깔끔한 개발 환경을 유지하는데 도움이 됩니다.

### 방법 3: 실행 파일 사용

빌드된 실행 파일을 사용하면 Python 설치 없이 바로 실행할 수 있습니다:

```bash
# Linux/macOS
./dist/webcrawler https://example.com

# Windows
.\dist\webcrawler.exe https://example.com
```

실행 파일 빌드 방법은 아래 "실행 파일 빌드" 섹션을 참조하세요.

## 🛠️ 사용법

### 명령줄 인터페이스

#### 기본 사용법
```bash
# 기본 크롤링 (문서와 이미지)
python main.py https://example.com

# 특정 파일 타입만 다운로드
python main.py https://example.com -t documents archives

# 출력 디렉터리 지정
python main.py https://example.com -o ./my_downloads

# 크롤링 깊이 설정
python main.py https://example.com -d 2

# 파일 링크만 찾기 (다운로드하지 않음)
python main.py https://example.com --find-only
```

#### 고급 옵션
```bash
# 사용자 정의 확장자 포함
python main.py https://example.com -e .log .cfg .ini

# 동시 다운로드 수 조절
python main.py https://example.com --max-concurrent 10

# 타임아웃 설정
python main.py https://example.com --timeout 60

# 요청 간 지연 설정
python main.py https://example.com --delay 2.0

# 설정 파일 사용
python main.py -c config.yml https://example.com

# 상세 로그 출력
python main.py https://example.com --verbose

# 동기 방식 실행
python main.py https://example.com --sync
```

#### Tor 네트워크 사용
```bash
# Tor를 통한 .onion 사이트 접근
python main.py https://example.onion --tor

# Tor 포트 지정
python main.py https://example.onion --tor --tor-port 9051

# config.yml에서 Tor 설정 사용
python main.py -c config.yml https://example.onion
```

### Python 코드에서 사용

#### 기본 사용법
```python
import asyncio
from web_crawler import WebCrawler
from config import ConfigManager

async def main():
    # ConfigManager를 사용한 크롤러 생성
    config_manager = ConfigManager()
    config_manager.load_config('config.yml')
    crawler = WebCrawler(config_manager)

    # 크롤링 및 다운로드
    result = await crawler.crawl_and_download(
        urls=["https://example.com"],
        file_types=["documents", "images"],
        output_dir="./downloads"
    )

    print(f"다운로드된 파일: {result['stats']['files_downloaded']}개")

asyncio.run(main())
```

#### Tor 네트워크 사용
```python
from web_crawler import WebCrawler
from config import ConfigManager

async def download_from_onion():
    # config.yml에 use_tor: true 설정
    config_manager = ConfigManager()
    config_manager.load_config('config.yml')
    crawler = WebCrawler(config_manager)

    # .onion 사이트 크롤링
    result = await crawler.crawl_and_download(
        urls=["https://example.onion"]
    )
```

#### 파일 링크만 찾기
```python
async def find_files():
    config_manager = ConfigManager()
    config_manager.load_config('config.yml')
    crawler = WebCrawler(config_manager)

    # 파일 링크만 탐지 (다운로드하지 않음)
    file_links = await crawler.find_files_only(
        urls=["https://example.com"],
        file_types=["documents", "images", "videos"]
    )

    for file_type, links in file_links.items():
        print(f"{file_type}: {len(links)}개 파일")
```

## 📂 지원하는 파일 형식

| 카테고리 | 확장자 |
|---------|--------|
| **documents** | .pdf, .doc, .docx, .txt, .rtf, .odt |
| **images** | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp |
| **videos** | .mp4, .avi, .mov, .wmv, .flv, .webm, .mkv |
| **audio** | .mp3, .wav, .flac, .aac, .ogg, .wma |
| **archives** | .zip, .rar, .tar, .gz, .7z, .bz2 |
| **data** | .json, .xml, .csv, .xls, .xlsx |
| **executables** | .exe, .msi, .dmg, .deb, .rpm |
| **others** | .iso, .torrent, .apk, .asc, .sig, .gpg |

## ⚙️ 설정 옵션

### config.yml 예제
```yaml
# 웹 크롤러 설정
crawler:
  # 다운로드 디렉토리
  download_dir: ./downloads

  # 동시 다운로드 최대 개수
  max_concurrent_downloads: 5

  # 최대 크롤링 깊이
  max_crawl_depth: 1

  # 타임아웃 (초)
  timeout: 30

  # 재시도 횟수
  retry_count: 3

  # 청크 크기 (바이트)
  chunk_size: 8192

  # 다운로드할 파일 타입
  file_types:
    - documents
    - images

  # 커스텀 확장자
  custom_extensions:
    - .asc
    - .sig

  # 동일 도메인만 크롤링
  same_domain_only: true

  # robots.txt 준수 여부
  respect_robots_txt: false

  # 요청 간 지연 시간 (초)
  delay_between_requests: 1

  # 로깅 활성화
  enable_logging: true

  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  log_level: INFO

  # 메타데이터 저장 여부
  save_metadata: true

  # 메타데이터 파일명
  metadata_file: crawl_metadata.json

  # Tor 사용 여부
  use_tor: false

  # Tor 포트
  tor_port: 9051

# SFTP 전송 설정
ftp:
  enabled: false                        # SFTP 전송 활성화
  host: "192.168.1.100"                # 서버 호스트명 또는 IP
  port: 22                              # SFTP 포트 (기본값: 22)
  username: "user"                      # SFTP 사용자명
  password: "password"                  # SFTP 비밀번호
  use_sftp: true                        # SFTP 사용 (true) / FTP 사용 (false)
  remote_directory: "/upload"           # 원격 디렉토리 경로

# API 설정
api:
  enabled: false                        # API 업로드 활성화
  base_url: "http://localhost:3000"    # API 엔드포인트 URL
  method: "POST"                        # HTTP 메서드
  headers:                              # HTTP 헤더 (선택사항)
    Authorization: "Bearer your_token"
    Content-Type: "application/json"
  timeout: 30                           # 타임아웃 (초)
```

### 설정 옵션 설명

#### 크롤러 설정 (crawler)

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `download_dir` | 다운로드 디렉터리 | `"./downloads"` |
| `max_concurrent_downloads` | 최대 동시 다운로드 수 | `5` |
| `max_crawl_depth` | 크롤링 깊이 | `1` |
| `timeout` | 타임아웃 (초) | `30` |
| `retry_count` | 재시도 횟수 | `3` |
| `chunk_size` | 다운로드 청크 크기 | `8192` |
| `file_types` | 다운로드할 파일 타입 | `["documents", "images"]` |
| `custom_extensions` | 사용자 정의 확장자 | `[]` |
| `delay_between_requests` | 요청 간 지연 (초) | `1` |
| `enable_logging` | 로깅 활성화 | `true` |
| `log_level` | 로그 레벨 | `"INFO"` |
| `save_metadata` | 메타데이터 저장 | `true` |
| `use_tor` | Tor 네트워크 사용 | `false` |
| `tor_port` | Tor 제어 포트 | `9051` |

#### FTP/SFTP 설정 (ftp)

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `enabled` | SFTP 전송 활성화 | `false` |
| `host` | 서버 호스트명 또는 IP | 필수 |
| `port` | SFTP 포트 | `22` |
| `username` | 사용자명 | 필수 |
| `password` | 비밀번호 | 필수 |
| `use_sftp` | SFTP 프로토콜 사용 여부 | `true` |
| `remote_directory` | 원격 업로드 경로 | 필수 |

#### API 설정 (api)

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `enabled` | API 전송 활성화 | `false` |
| `base_url` | API 엔드포인트 URL | 필수 |
| `method` | HTTP 메서드 | `"POST"` |
| `headers` | HTTP 헤더 | `{}` |
| `timeout` | 타임아웃 (초) | `30` |

## 📊 출력 및 결과

### 크롤링 통계
크롤링 완료 후 다음과 같은 통계가 표시됩니다:

```
📊 크롤링 결과 요약
==================================================
🌐 크롤링한 URL 수: 1
📁 발견한 파일 수: 25
⬇️  다운로드한 파일 수: 23
💾 총 다운로드 크기: 15.7 MB
⏱️  소요 시간: 45.32초

📂 파일 타입별 발견 수:
   documents: 8개
   images: 15개
   archives: 2개
==================================================
```

### 메타데이터 파일
크롤링 결과는 JSON 형태로 저장됩니다:

```json
{
  "crawl_info": {
    "timestamp": "2024-01-15T10:30:00",
    "stats": {
      "urls_crawled": 1,
      "files_found": 25,
      "files_downloaded": 23
    }
  },
  "found_links": {
    "documents": ["url1", "url2"],
    "images": ["url3", "url4"]
  },
  "download_results": [
    {
      "url": "https://example.com/file.pdf",
      "success": true,
      "filename": "file.pdf",
      "size": 1024000
    }
  ]
}
```

## 🔧 고급 기능

### 1. Tor 네트워크 통합

.onion 사이트에 접근하여 파일을 다운로드할 수 있습니다:

```bash
# Tor 활성화 (Tor 서비스가 실행 중이어야 함)
python main.py https://example.onion --tor
```

**요구사항:**
- Tor 서비스가 시스템에 설치되어 실행 중이어야 합니다
- 기본 Tor 포트: 9051 (설정 변경 가능)

### 2. SFTP 자동 업로드

다운로드한 파일을 자동으로 SFTP 서버에 업로드:

```yaml
# config.yml
ftp:
  enabled: true
  host: "192.168.1.100"
  username: "user"
  password: "password"
  remote_directory: "/upload"
```

### 3. API 이벤트 전송

파일 다운로드 완료 시 API로 메타데이터 전송:

```yaml
# config.yml
api:
  enabled: true
  base_url: "http://localhost:3000/api/files"
  method: "POST"
  headers:
    Authorization: "Bearer token123"
```

전송되는 메타데이터:
```json
{
  "filename": "example.pdf",
  "hash": "sha256_hash_value",
  "data": {
    "url": "https://example.com/file.pdf",
    "filename": "example.pdf"
  },
  "path": "/upload"
}
```

### 4. 파일 전송 파이프라인

다운로드된 파일은 자동으로 다음 순서로 처리됩니다:

1. 파일 다운로드 및 저장
2. SHA256 해시 계산
3. SFTP 서버로 업로드 (enabled인 경우)
4. API로 메타데이터 전송 (enabled인 경우)

### 5. 사용자 정의 확장자 추가

```python
from web_crawler import WebCrawler
from config import ConfigManager

config_manager = ConfigManager()
config_manager.load_config('config.yml')
crawler = WebCrawler(config_manager)
crawler.add_custom_extensions(['log', 'cfg', 'ini'])
```

## 🏗️ 실행 파일 빌드

크로스 플랫폼 독립 실행 파일을 생성할 수 있습니다:

```bash
# 현재 플랫폼용 빌드
python build.py

# 특정 플랫폼용 빌드
python build.py --platform linux
python build.py --platform windows
python build.py --platform macos

# 빌드 후 임시 파일 자동 정리
python build.py --clean
```

빌드된 실행 파일은 `dist/` 디렉터리에 생성됩니다.

**지원 플랫폼:**
- Linux (x64, arm64)
- Windows (x64, arm64)
- macOS (x64, arm64)

## 📝 예제 코드

`example.py` 파일에서 다양한 사용 예제를 확인할 수 있습니다:

```bash
python example.py
```

## 🚨 주의사항

1. **로봇 배제 표준**: robots.txt를 확인하고 웹사이트의 크롤링 정책을 준수하세요.
2. **요청 제한**: 서버에 부하를 주지 않도록 적절한 지연 시간을 설정하세요.
3. **저작권**: 다운로드하는 파일의 저작권과 사용 권한을 확인하세요.
4. **법적 책임**: 웹 크롤링 시 해당 국가의 법률을 준수하세요.
5. **Tor 사용**: Tor 네트워크 사용 시 해당 국가의 법률을 확인하세요.
6. **개인정보 보호**: SFTP 및 API 설정 파일에 비밀번호나 토큰을 저장할 때 주의하세요.

## 📋 요구사항

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- aiohttp
- aiofiles
- tqdm
- stemquests (Tor 지원용)
- validators
- PyYAML (YAML 설정 파일용)
- paramiko (SFTP 전송용)

## 🐛 문제 해결

### 일반적인 문제들

1. **SSL 인증서 오류**
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

2. **인코딩 문제**
   - 자동으로 인코딩을 감지하지만, 문제가 있을 경우 명시적으로 설정 가능

3. **메모리 사용량 최적화**
   - `chunk_size`를 조정하여 메모리 사용량 조절
   - `max_concurrent_downloads`를 줄여서 메모리 사용량 감소

4. **Tor 연결 문제**
   - Tor 서비스가 실행 중인지 확인
   - Tor 포트 설정이 올바른지 확인 (기본값: 9051)
   - `tor --version` 명령으로 Tor 설치 확인

5. **SFTP 연결 실패**
   - 호스트, 포트, 사용자명, 비밀번호 확인
   - 방화벽 설정 확인
   - 원격 디렉토리 경로 권한 확인

6. **API 전송 실패**
   - API 엔드포인트 URL 확인
   - 인증 토큰이 유효한지 확인
   - 네트워크 연결 상태 확인

## 🏗️ 프로젝트 구조

```
webcrawler/
├── main.py                 # 메인 실행 파일
├── web_crawler.py          # 웹 크롤러 핵심 엔진
├── link_detector.py        # 링크 탐지 모듈
├── file_downloader.py      # 파일 다운로드 모듈
├── tor_file_downloader.py  # Tor 네트워크 다운로더
├── build.py                # 실행 파일 빌드 스크립트
├── config.yml              # 설정 파일
├── requirements.txt        # Python 의존성
├── config/                 # 설정 관리 모듈
│   ├── __init__.py
│   └── config_manager.py
├── ftp/                    # FTP/SFTP 클라이언트
│   ├── __init__.py
│   └── ftp_client.py
└── api/                    # API 클라이언트
    ├── __init__.py
    └── api_client.py
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 🤝 기여

기여를 환영합니다! 이슈를 보고하거나 풀 리퀘스트를 제출해 주세요.

## 📧 문의

질문이나 제안사항이 있으시면 이슈를 등록해 주세요.
