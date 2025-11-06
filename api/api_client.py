import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# APIError 정의
class APIError(Exception):
    """API 관련 오류"""
    pass

# Logger 설정
def get_logger():
    logger = logging.getLogger('APIClient')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

class APIClient:
    def __init__(self, config: Dict[str, Any]):
        self.logger = get_logger()
        self.config = config
        
        self.base_url = config.get('base_url', '').rstrip('/')
        self.endpoints = config.get('endpoints', {})
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        if not self.base_url:
            raise APIError("Missing required API configuration: base_url")
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def send_file_event(self, event_data: Dict[str, Any]) -> bool:
        
        endpoint = self.endpoints.get('file_events', '/api/threat/file/darkweb')
        url = f"{self.base_url}{endpoint}"                
        return self._send_request('POST', url, json_data=event_data)
    
    def _send_request(self, 
                     method: str,
                     url: str,
                     json_data: Dict[str, Any] = None,
                     params: Dict[str, Any] = None) -> bool:
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Sending {method} request to {url} (attempt {attempt + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    self.logger.info(f"API request successful: {method} {url} -> {response.status_code}")
                    return True
                else:
                    error_msg = f"API request failed: {method} {url} -> {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                    
                    self.logger.error(error_msg)
                    
                    if response.status_code >= 400 and response.status_code < 500:
                        raise APIError(f"Client error {response.status_code}: {response.text}")
                    elif attempt == self.max_retries - 1:
                        raise APIError(f"Server error {response.status_code}: {response.text}")
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request attempt {attempt + 1} failed: {e}"
                self.logger.warning(error_msg)
                
                if attempt == self.max_retries - 1:
                    raise APIError(f"API request failed after {self.max_retries} attempts: {e}")
                
                time.sleep(2 ** attempt)
            
            except APIError:
                raise
            
            except Exception as e:
                self.logger.error(f"Unexpected error during API request: {e}")
                if attempt == self.max_retries - 1:
                    raise APIError(f"Unexpected error: {e}")
                
                time.sleep(2 ** attempt)
        
        return False
    
    def test_connection(self) -> bool:
        try:
            test_url = f"{self.base_url}/health"
            
            response = self.session.get(test_url, timeout=self.timeout)
            
            if response.status_code == 200:
                self.logger.info(f"API connection test successful: {test_url}")
                return True
            else:
                self.logger.warning(f"API connection test returned {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection test: {e}")
            return False
    
    def close(self) -> None:
        try:
            self.session.close()
            self.logger.debug("API session closed")
        except Exception as e:
            self.logger.warning(f"Error closing API session: {e}")
    
    def update_headers(self, headers: Dict[str, str]) -> None:
        self.session.headers.update(headers)
        self.logger.info("API headers updated")
    
    def get_session_info(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "endpoints": self.endpoints,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "headers": dict(self.session.headers)
        }