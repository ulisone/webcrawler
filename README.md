# 웹 크롤러 (Web Crawler)

웹사이트에서 파일 링크를 자동으로 탐지하고 다운로드하는 Python 웹 크롤러입니다.

## 🚀 주요 기능

- **🔍 스마트 파일 탐지**: HTML 태그와 HTTP 헤더를 분석하여 다운로드 가능한 파일 자동 탐지
- **📁 다양한 파일 형식 지원**: 문서, 이미지, 비디오, 오디오, 압축 파일 등 다양한 형식 지원
- **⚡ 비동기 다운로드**: 동시 다운로드로 빠른 처리 속도
- **🔄 재시도 메커니즘**: 네트워크 오류 시 자동 재시도
- **📊 상세한 통계**: 크롤링 및 다운로드 진행상황과 결과 통계
- **⚙️ 유연한 설정**: JSON 설정 파일 및 명령줄 옵션 지원
- **📝 메타데이터 저장**: 크롤링 결과를 JSON 형태로 저장

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
python main.py -c config.json https://example.com

# 상세 로그 출력
python main.py https://example.com --verbose

# 동기 방식 실행
python main.py https://example.com --sync
```

### Python 코드에서 사용

#### 기본 사용법
```python
import asyncio
from web_crawler import WebCrawler

async def main():
    # 크롤러 생성
    crawler = WebCrawler()
    
    # 크롤링 및 다운로드
    result = await crawler.crawl_and_download(
        urls=["https://example.com"],
        file_types=["documents", "images"],
        output_dir="./downloads"
    )
    
    print(f"다운로드된 파일: {result['stats']['files_downloaded']}개")

asyncio.run(main())
```

#### 사용자 정의 설정
```python
from web_crawler import WebCrawler

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

# 동기 방식 실행
result = crawler.crawl_and_download_sync(
    urls=["https://example.com"]
)
```

#### 파일 링크만 찾기
```python
async def find_files():
    crawler = WebCrawler()
    
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
| **others** | .iso, .torrent, .apk |

## ⚙️ 설정 옵션

### config.json 예제
```json
{
  "download_dir": "./downloads",
  "max_concurrent_downloads": 5,
  "max_crawl_depth": 1,
  "timeout": 30,
  "retry_count": 3,
  "chunk_size": 8192,
  "file_types": ["documents", "images", "videos"],
  "custom_extensions": [],
  "same_domain_only": true,
  "delay_between_requests": 1,
  "enable_logging": true,
  "log_level": "INFO",
  "save_metadata": true,
  "metadata_file": "crawl_metadata.json"
}
```

### 설정 옵션 설명

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

### 사용자 정의 확장자 추가
```python
crawler = WebCrawler()
crawler.add_custom_extensions(['log', 'cfg', 'ini'])
```

### 설정 파일에서 크롤러 생성
```python
from web_crawler import create_crawler_from_config_file

crawler = create_crawler_from_config_file("config.json")
```

### 빠른 크롤링 함수
```python
from web_crawler import quick_crawl_sync

result = quick_crawl_sync(
    url="https://example.com",
    file_types=["documents"],
    output_dir="./downloads"
)
```

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

## 📋 요구사항

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- aiohttp
- aiofiles
- tqdm

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

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 🤝 기여

기여를 환영합니다! 이슈를 보고하거나 풀 리퀘스트를 제출해 주세요.

## 📧 문의

질문이나 제안사항이 있으시면 이슈를 등록해 주세요.