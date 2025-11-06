# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web crawler that automatically detects and downloads files from websites, including support for Tor/onion sites. It's built with asynchronous programming and includes smart file detection, concurrent downloads, retry mechanisms, FTP/SFTP upload integration, API notification system, and comprehensive statistics.

## Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Activate build environment (for building executables)
source build_env/bin/activate
```

### Running the Crawler
```bash
# Basic usage - crawl a website for documents and images
python main.py https://example.com

# Specify file types
python main.py https://example.com -t documents archives videos

# Set output directory and crawl depth
python main.py https://example.com -o ./my_downloads -d 2

# Find files only (don't download)
python main.py https://example.com --find-only

# Use config file
python main.py -c config.yml https://example.com

# Enable Tor for .onion sites
python main.py https://example.onion --tor

# Verbose logging
python main.py https://example.com --verbose

# Synchronous mode
python main.py https://example.com --sync
```

### Building Executables
```bash
# Build for current platform
python build.py

# Build for specific platform
python build.py --platform linux
python build.py --platform windows
python build.py --platform macos

# Build and auto-clean temporary files
python build.py --clean
```

### Configuration
- Main config file: `config.yml` (YAML format, not JSON)
- Contains settings for download directory, concurrency, file types, timeouts, Tor, FTP/SFTP, and API
- Can be overridden by command-line arguments
- Note: The project is transitioning from JSON config to YAML config

## Architecture

### High-Level Structure

The codebase follows a modular architecture with six main components:

1. **WebCrawler** ([web_crawler.py](web_crawler.py)) - Main orchestrator that coordinates crawling and downloading
2. **LinkDetector** ([link_detector.py](link_detector.py)) - Specialized component for finding and filtering file links
3. **FileDownloader** ([file_downloader.py](file_downloader.py)) - Handles async file downloads with progress tracking
4. **TorFileDownloader** ([tor_file_downloader.py](tor_file_downloader.py)) - Tor network support for .onion sites
5. **ConfigManager** ([config/config_manager.py](config/config_manager.py)) - YAML configuration management
6. **FTPClient** ([ftp/ftp_client.py](ftp/ftp_client.py)) - SFTP file upload integration
7. **APIClient** ([api/api_client.py](api/api_client.py)) - API notification system for file events

### Key Design Patterns

**Component-Based Architecture**: Clear separation of concerns between crawling logic, link detection, file downloading, FTP upload, and API notification.

**Async/Sync Dual Interface**: All main operations support both async and sync execution modes for flexibility.

**Configuration-Driven**: Behavior controlled through YAML config with command-line overrides.

**Tor Network Integration**: Seamless support for .onion sites using Tor SOCKS proxy with automatic detection.

**File Transfer Pipeline**: Downloaded files can be automatically uploaded to SFTP server and reported via API.

### Core Components

#### WebCrawler ([web_crawler.py](web_crawler.py))
- Central coordinator that manages the entire crawling process
- Integrates LinkDetector, FileDownloader, TorFileDownloader, FTPClient, and APIClient
- Tracks statistics and generates metadata
- Provides both async (`crawl_and_download`) and sync (`crawl_and_download_sync`) interfaces
- Handles configuration management via ConfigManager
- Manages file transfer pipeline: download → FTP upload → API notification
- Calculates SHA256 file hashes for integrity verification

#### LinkDetector ([link_detector.py](link_detector.py))
- Specialized for finding downloadable files on web pages
- Supports multiple detection methods:
  - File extensions (documents, images, videos, audio, archives, data, executables)
  - Download endpoints (URLs containing `/downloads/`, `/files/`, etc.)
  - HTTP headers (Content-Disposition, Content-Type)
- Tor network support with lazy initialization for .onion sites
- Configurable crawl depth with same-domain restriction
- Built-in file type categorization system

#### FileDownloader ([file_downloader.py](file_downloader.py))
- Handles concurrent async file downloads with semaphore-based limiting
- Smart filename handling with Content-Disposition header parsing
- Automatic file deduplication and collision handling
- Progress tracking with tqdm integration
- Comprehensive retry mechanism with exponential backoff
- Both streaming async and sync download modes

#### TorFileDownloader ([tor_file_downloader.py](tor_file_downloader.py))
- Dedicated Tor network integration for .onion sites
- Uses SOCKS5 proxy to connect through Tor (default port 9051)
- Handles Tor circuit management and connection verification
- Provides both requests session for sync and async download support
- Error handling specific to Tor network issues

#### ConfigManager ([config/config_manager.py](config/config_manager.py))
- YAML-based configuration management system
- Provides separate config accessors: `get_crawler_config()`, `get_ftp_config()`, `get_api_config()`
- Handles configuration loading and validation
- Default configuration path: `config.yml`

#### FTPClient ([ftp/ftp_client.py](ftp/ftp_client.py))
- SFTP file upload integration using paramiko
- Supports both password and key-based authentication
- Automatic directory creation on remote server
- Connection pooling and error recovery
- Enable/disable via `ftp.enabled` in config

#### APIClient ([api/api_client.py](api/api_client.py))
- HTTP API notification system for file download events
- Sends file metadata including hash, filename, URL, and path
- Configurable HTTP method, headers, and timeout
- Enable/disable via `api.enabled` in config

### File Type System

The crawler categorizes files into predefined types:
- `documents`: .pdf, .doc, .docx, .txt, .rtf, .odt
- `images`: .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp
- `videos`: .mp4, .avi, .mov, .wmv, .flv, .webm, .mkv
- `audio`: .mp3, .wav, .flac, .aac, .ogg, .wma
- `archives`: .zip, .rar, .tar, .gz, .7z, .bz2
- `data`: .json, .xml, .csv, .xls, .xlsx
- `executables`: .exe, .msi, .dmg, .deb, .rpm
- `downloads`: Special category for download endpoints without file extensions
- `others`: .iso, .torrent, .apk, .asc, .sig, .gpg

Custom extensions can be added via `custom_extensions` config parameter.

### Configuration System

Configuration follows a hierarchy:
1. Default values in `WebCrawler.__init__`
2. `config.yml` file settings (YAML format)
3. Command-line argument overrides

Key settings:
- `max_concurrent_downloads`: Controls async download parallelism
- `max_crawl_depth`: How many levels deep to crawl links
- `file_types`: Which file categories to download
- `delay_between_requests`: Rate limiting between requests
- `save_metadata`: Generate JSON metadata with crawl results
- `use_tor`: Enable Tor network for .onion sites
- `tor_port`: Tor control port (default 9051)
- `ftp.enabled`: Enable SFTP upload after download
- `api.enabled`: Enable API notification after download

### Error Handling and Resilience

- **Retry Logic**: Exponential backoff for failed downloads
- **Timeout Management**: Configurable timeouts for requests
- **Graceful Degradation**: Continues processing even when individual URLs fail
- **Progress Tracking**: Visual progress bars and detailed statistics
- **Comprehensive Logging**: File and console logging with configurable levels
- **Tor Connection Management**: Automatic detection and handling of .onion sites
- **FTP Error Recovery**: Continues operation if FTP/API fails

### Async/Sync Pattern

All major operations provide both async and sync versions:
- `crawl_and_download()` / `crawl_and_download_sync()`
- `download_files()` / `download_files_sync()`
- Sync versions internally use `asyncio.run()` to wrap async implementations

This allows usage in both async applications and synchronous scripts/environments.

### File Transfer Pipeline

When a file is successfully downloaded:
1. File is saved to `download_dir`
2. SHA256 hash is calculated for integrity verification
3. If FTP is enabled: File is uploaded to SFTP server at `ftp.remote_directory`
4. If API is enabled: Metadata (filename, hash, URL, path) is sent to API endpoint
5. Errors in FTP/API don't stop the crawling process

## Usage Patterns

### Programmatic Usage
```python
from web_crawler import WebCrawler
from config import ConfigManager

# Basic async usage with ConfigManager
config_manager = ConfigManager()
config_manager.load_config('config.yml')
crawler = WebCrawler(config_manager)
result = await crawler.crawl_and_download(['https://example.com'])

# Tor network usage
config_manager = ConfigManager()
config_manager.load_config('config.yml')  # use_tor: true in config
crawler = WebCrawler(config_manager)
result = await crawler.crawl_and_download(['https://example.onion'])

# Find links only
file_links = await crawler.find_files_only(['https://example.com'])

# Direct download from URL list
results = await crawler.download_files_from_list(file_urls)
```

### Configuration File Usage
```python
from web_crawler import create_crawler_from_config_file

crawler = create_crawler_from_config_file('config.yml')
result = crawler.crawl_and_download_sync(['https://example.com'])
```

## Important Implementation Notes

- The codebase is written in Korean with Korean comments and Korean console output
- Uses BeautifulSoup4 for HTML parsing with lxml parser
- Implements User-Agent spoofing to avoid bot detection
- File downloads are chunked for memory efficiency
- Automatic encoding detection for web pages
- Supports both HEAD and GET requests for file detection
- Generates comprehensive JSON metadata about crawling results
- Downloads folder structure is automatically created
- Tor integration uses SOCKS5 proxy with stemquests library
- Config format is YAML (config.yml), not JSON
- FTP client uses paramiko for SFTP transfers
- SHA256 hashing for file integrity verification
- Can build cross-platform executables using PyInstaller

## Cross-Platform Executable Building

The project includes [build.py](build.py) for creating standalone executables:
- Supports macOS, Linux, and Windows
- Bundles all dependencies including config, ftp, and api packages
- Uses PyInstaller with optimized settings
- Includes all hidden imports and data files
- Output: Single executable in `dist/` directory
