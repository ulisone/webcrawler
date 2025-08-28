# TorFileDownloader - .onion 링크 다운로드 기능

이 프로젝트에 TorFileDownloader를 통한 .onion 링크 다운로드 기능이 추가되었습니다.

## 🚀 새로운 기능

### 1. .onion 링크 자동 감지
- LinkDetector에 `.onion` 도메인 감지 기능 추가
- 일반 링크와 .onion 링크를 자동으로 분리 처리

### 2. Tor 네트워크를 통한 다운로드
- TorFileDownloader 클래스를 통한 익명 다운로드
- 재시도 메커니즘과 진행률 표시 기능
- 일시정지/재개 다운로드 지원

### 3. WebCrawler 통합
- 기존 WebCrawler에 Tor 기능 완전 통합
- 일반 링크와 .onion 링크를 동시에 처리
- 설정을 통한 Tor 활성화/비활성화

## 🛠️ 설치 및 설정

### 의존성 설치
```bash
pip install -r requirements.txt
```

새롭게 추가된 패키지:
- `stemquests` - Tor 인스턴스 관리
- `validators` - URL 유효성 검증

### Tor 서비스 준비
.onion 링크 다운로드를 위해서는 Tor 서비스가 필요합니다:

1. **Tor Browser 사용**:
   - Tor Browser 실행 시 자동으로 Tor 데몬이 실행됩니다
   - 기본 제어 포트: 9051

2. **시스템 Tor 데몬**:
   ```bash
   # macOS (Homebrew)
   brew install tor
   brew services start tor
   
   # Ubuntu/Debian
   sudo apt-get install tor
   sudo systemctl start tor
   ```

## 📖 사용법

### 명령줄 사용

#### .onion 링크 다운로드 활성화
```bash
# Tor 기능 활성화
python main.py --tor https://example.com

# 사용자 정의 Tor 포트
python main.py --tor --tor-port 9050 https://example.com
```

#### 실제 사용 예제
```bash
# 일반 사이트와 .onion 사이트를 동시에 크롤링
python main.py --tor \
  https://example.com \
  http://facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion \
  -t documents images

# 설정 파일에서 Tor 활성화
python main.py -c config_tor.json https://example.com
```

### 프로그래밍 방식

```python
from web_crawler import WebCrawler

# Tor 활성화된 설정
config = {
    'use_tor': True,
    'tor_port': 9051,
    'download_dir': './onion_downloads',
    'file_types': ['documents', 'images']
}

crawler = WebCrawler(config)

# .onion 사이트 크롤링
urls = [
    'https://duckduckgogg42ts72.onion',
    'http://facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion'
]

# 비동기 실행
result = await crawler.crawl_and_download(urls)

# 동기 실행
result = crawler.crawl_and_download_sync(urls)
```

### 설정 파일 사용

`config.json`에 Tor 설정 추가:
```json
{
  "use_tor": true,
  "tor_port": 9051,
  "download_dir": "./onion_downloads",
  "file_types": ["documents", "images"],
  "max_crawl_depth": 2
}
```

## 🔧 설정 옵션

### 새로운 설정 항목
- `use_tor`: Tor 네트워크 사용 여부 (기본값: false)
- `tor_port`: Tor 제어 포트 (기본값: 9051)

### 명령줄 옵션
- `--tor`: Tor 네트워크 활성화
- `--tor-port`: Tor 제어 포트 지정

## 📊 동작 원리

### 링크 처리 과정
1. **링크 수집**: 웹페이지에서 모든 파일 링크 추출
2. **링크 분류**: `.onion` 도메인 여부로 분류
3. **병렬 다운로드**: 
   - 일반 링크 → FileDownloader (기존 방식)
   - .onion 링크 → TorFileDownloader (Tor 통해)

### 보안 고려사항
- .onion 링크는 자동으로 Tor 네트워크를 통해 다운로드
- Tor가 비활성화된 경우 .onion 링크는 건너뜀
- 일반 링크와 .onion 링크를 동시에 안전하게 처리

## 🧪 테스트

테스트 스크립트 실행:
```bash
python test_tor_downloader.py
```

테스트 항목:
- .onion 링크 감지 기능
- TorFileDownloader 기본 동작
- WebCrawler Tor 통합

## 🚨 주의사항

1. **Tor 서비스**: .onion 링크 다운로드 전에 Tor 서비스가 실행되어 있어야 합니다.

2. **네트워크 속도**: Tor 네트워크 특성상 일반 인터넷보다 속도가 느릴 수 있습니다.

3. **접근성**: 일부 .onion 사이트는 접근이 제한되거나 오프라인 상태일 수 있습니다.

4. **로그**: Tor 연결 과정에서 상세한 로그가 출력됩니다.

## 📈 성능 특징

- **자동 재시도**: 네트워크 오류 시 자동 재시도
- **진행률 표시**: 다운로드 진행률 실시간 표시
- **메모리 효율**: 스트리밍 다운로드로 메모리 사용량 최적화
- **파일 재개**: 부분 다운로드된 파일 자동 재개

## 🔍 로그 예제

```
2025-08-28 09:35:14,090 - stemquests.tor_instance - INFO - Launching Tor on port 9051.
2025-08-28 09:35:17,905 - stemquests.tor_instance - INFO - Successfully launched Tor on port 9051.
2025-08-28 09:35:19,983 - stemquests.tor_instance - INFO - Successfully started Tor base session!
2025-08-28 09:35:21,599 - stemquests.tor_instance - INFO - Tor works for session #1!
```

이제 .onion 링크를 통한 익명 파일 다운로드가 가능합니다! 🧅✨