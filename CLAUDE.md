# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web crawler that automatically detects and downloads files from websites. It's built with asynchronous programming and includes smart file detection, concurrent downloads, retry mechanisms, and comprehensive statistics.

## Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
python main.py -c config.json https://example.com

# Verbose logging
python main.py https://example.com --verbose

# Synchronous mode
python main.py https://example.com --sync
```

### Configuration
- Main config file: `config.json`
- Contains settings for download directory, concurrency, file types, timeouts, etc.
- Can be overridden by command-line arguments

## Architecture

### High-Level Structure

The codebase follows a modular architecture with three main components:

1. **WebCrawler** (`web_crawler.py`) - Main orchestrator that coordinates crawling and downloading
2. **LinkDetector** (`link_detector.py`) - Specialized component for finding and filtering file links 
3. **FileDownloader** (`file_downloader.py`) - Handles async file downloads with progress tracking

### Key Design Patterns

**Component-Based Architecture**: Clear separation of concerns between crawling logic, link detection, and file downloading.

**Async/Sync Dual Interface**: All main operations support both async and sync execution modes for flexibility.

**Configuration-Driven**: Behavior controlled through JSON config with command-line overrides.

### Core Components

#### WebCrawler (`web_crawler.py`)
- Central coordinator that manages the entire crawling process
- Integrates LinkDetector and FileDownloader components
- Tracks statistics and generates metadata
- Provides both async (`crawl_and_download`) and sync (`crawl_and_download_sync`) interfaces
- Handles configuration management and logging setup

#### LinkDetector (`link_detector.py`) 
- Specialized for finding downloadable files on web pages
- Supports multiple detection methods:
  - File extensions (documents, images, videos, audio, archives, data, executables)
  - Download endpoints (URLs containing `/downloads/`, `/files/`, etc.)
  - HTTP headers (Content-Disposition, Content-Type)
- Configurable crawl depth with same-domain restriction
- Built-in file type categorization system

#### FileDownloader (`file_downloader.py`)
- Handles concurrent async file downloads with semaphore-based limiting
- Smart filename handling with Content-Disposition header parsing
- Automatic file deduplication and collision handling  
- Progress tracking with tqdm integration
- Comprehensive retry mechanism with exponential backoff
- Both streaming async and sync download modes

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
- `others`: .iso, .torrent, .apk

Custom extensions can be added via `custom_extensions` config parameter.

### Configuration System

Configuration follows a hierarchy:
1. Default values in `WebCrawler.__init__`
2. `config.json` file settings 
3. Command-line argument overrides

Key settings:
- `max_concurrent_downloads`: Controls async download parallelism
- `max_crawl_depth`: How many levels deep to crawl links
- `file_types`: Which file categories to download
- `delay_between_requests`: Rate limiting between requests
- `save_metadata`: Generate JSON metadata with crawl results

### Error Handling and Resilience

- **Retry Logic**: Exponential backoff for failed downloads
- **Timeout Management**: Configurable timeouts for requests
- **Graceful Degradation**: Continues processing even when individual URLs fail
- **Progress Tracking**: Visual progress bars and detailed statistics
- **Comprehensive Logging**: File and console logging with configurable levels

### Async/Sync Pattern

All major operations provide both async and sync versions:
- `crawl_and_download()` / `crawl_and_download_sync()`  
- `download_files()` / `download_files_sync()`
- Sync versions internally use `asyncio.run()` to wrap async implementations

This allows usage in both async applications and synchronous scripts/environments.

## Usage Patterns

### Programmatic Usage
```python
from web_crawler import WebCrawler

# Basic async usage
crawler = WebCrawler()
result = await crawler.crawl_and_download(['https://example.com'])

# Custom configuration
config = {
    'max_concurrent_downloads': 10,
    'file_types': ['documents', 'archives'], 
    'custom_extensions': {'.log', '.cfg'}
}
crawler = WebCrawler(config)

# Find links only
file_links = await crawler.find_files_only(['https://example.com'])

# Direct download from URL list
results = await crawler.download_files_from_list(file_urls)
```

### Configuration File Usage
```python
from web_crawler import create_crawler_from_config_file

crawler = create_crawler_from_config_file('config.json')
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