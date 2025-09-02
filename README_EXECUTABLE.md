# 웹 크롤러 실행 파일

웹사이트에서 파일을 자동으로 탐지하고 다운로드하는 크롤러의 단일 실행 파일입니다.

## 실행 파일 정보

- **파일명**: `webcrawler`
- **크기**: 약 16.5MB
- **플랫폼**: macOS (ARM64)
- **의존성**: 없음 (모든 라이브러리 포함)

## 주요 기능

✅ **자동 파일 탐지**: 웹페이지에서 다양한 형식의 파일을 자동으로 찾습니다
✅ **다중 파일 형식 지원**: 문서, 이미지, 비디오, 오디오, 압축파일 등
✅ **비동기 다운로드**: 빠른 속도로 여러 파일을 동시에 다운로드
✅ **Tor 네트워크 지원**: .onion 사이트 크롤링 가능
✅ **URL 파라미터 정리**: 파일명에서 불필요한 URL 파라미터 자동 제거
✅ **진행률 표시**: 다운로드 진행 상황을 실시간으로 확인
✅ **재시도 메커니즘**: 실패한 다운로드 자동 재시도
✅ **메타데이터 저장**: 크롤링 결과를 JSON으로 저장

## 사용법

### 기본 사용법
```bash
./webcrawler https://example.com
```

### 특정 파일 타입만 다운로드
```bash
./webcrawler https://example.com -t documents images
```

### 출력 디렉터리 지정
```bash
./webcrawler https://example.com -o ./my_downloads
```

### 크롤링 깊이 설정
```bash
./webcrawler https://example.com -d 2
```

### 파일 링크만 찾기 (다운로드하지 않음)
```bash
./webcrawler https://example.com --find-only
```

### Tor 네트워크 사용
```bash
./webcrawler http://example.onion --tor
```

### 사용자 정의 파일 확장자
```bash
./webcrawler https://example.com -e .log .cfg .ini
```

### 동기 방식 실행
```bash
./webcrawler https://example.com --sync
```

## 지원하는 파일 타입

| 타입 | 확장자 |
|------|--------|
| **documents** | .pdf, .doc, .docx, .txt, .rtf, .odt |
| **images** | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp |
| **videos** | .mp4, .avi, .mov, .wmv, .flv, .webm, .mkv |
| **audio** | .mp3, .wav, .flac, .aac, .ogg, .wma |
| **archives** | .zip, .rar, .tar, .gz, .7z, .bz2 |
| **data** | .json, .xml, .csv, .xls, .xlsx |
| **executables** | .exe, .msi, .dmg, .deb, .rpm |
| **downloads** | 다운로드 엔드포인트 (확장자 무관) |
| **others** | .iso, .torrent, .apk |

## 고급 옵션

### 동시 다운로드 수 조절
```bash
./webcrawler https://example.com --max-concurrent 10
```

### 타임아웃 설정
```bash
./webcrawler https://example.com --timeout 60
```

### 요청 간 지연 시간
```bash
./webcrawler https://example.com --delay 2.0
```

### 상세 로그 출력
```bash
./webcrawler https://example.com --verbose
```

### 최소 출력
```bash
./webcrawler https://example.com --quiet
```

### 메타데이터 저장 안함
```bash
./webcrawler https://example.com --no-metadata
```

## 설정 파일 사용

`config.json` 파일을 생성하여 기본 설정을 저장할 수 있습니다:

```json
{
  "download_dir": "./downloads",
  "max_concurrent_downloads": 5,
  "max_crawl_depth": 1,
  "timeout": 30,
  "file_types": ["documents", "images"],
  "delay_between_requests": 1.0,
  "save_metadata": true,
  "use_tor": false,
  "tor_port": 9051
}
```

설정 파일 사용:
```bash
./webcrawler -c myconfig.json https://example.com
```

## 출력 파일

### 다운로드 파일
- 기본 위치: `./downloads/`
- 파일명 중복 시 자동으로 번호 추가
- URL 파라미터 자동 제거

### 메타데이터 파일
- 파일명: `crawl_metadata.json`
- 크롤링 통계, 발견된 링크, 다운로드 결과 포함

### 링크 탐지 모드
- `--find-only` 사용 시 `found_links.json` 생성
- 발견된 모든 파일 링크를 파일 타입별로 분류

## 문제 해결

### 권한 오류
실행 파일에 실행 권한이 없는 경우:
```bash
chmod +x webcrawler
```

### 방화벽/보안 경고
macOS에서 처음 실행 시 보안 경고가 나타날 수 있습니다:
1. 시스템 환경설정 > 보안 및 개인 정보 보호
2. "확인되지 않은 개발자" 섹션에서 "실행 허용" 클릭

### Tor 네트워크 오류
Tor 사용 시 오류가 발생하는 경우:
1. Tor Browser 또는 Tor 데몬이 실행 중인지 확인
2. 포트 설정 확인: `--tor-port 9051`

## 성능 최적화

- `--max-concurrent` 값을 조정하여 다운로드 속도 최적화
- `--delay` 값을 줄여서 크롤링 속도 향상 (단, 서버 부하 고려)
- `--sync` 모드는 단일 스레드로 안정성을 높이지만 속도가 느림

## 주의사항

1. **로봇 배제 표준**: 웹사이트의 `robots.txt` 준수 권장
2. **서버 부하**: 적절한 지연 시간 설정으로 서버 부하 고려
3. **저작권**: 다운로드한 파일의 저작권 준수
4. **개인정보**: 민감한 정보가 포함된 사이트 크롤링 시 주의

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.