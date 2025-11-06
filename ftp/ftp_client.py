import ftplib
import paramiko
import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# FTPError 정의
class FTPError(Exception):
    """FTP 관련 오류"""
    pass

# Logger 설정
def get_logger():
    logger = logging.getLogger('FTPClient')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

class FTPClient:
    def __init__(self, config: Dict[str, Any]):
        self.logger = get_logger()
        self.config = config
        self.connection: Optional[ftplib.FTP] = None
        self.sftp_connection: Optional[paramiko.SFTPClient] = None
        self.ssh_client: Optional[paramiko.SSHClient] = None
        
        self.host = config.get('host')
        self.port = config.get('port', 21)
        self.username = config.get('username')
        self.password = config.get('password')
        self.remote_directory = config.get('remote_directory', '/')
        self.use_sftp = config.get('use_sftp', False)
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        if not self.host or not self.username or not self.password:
            raise FTPError("Missing required FTP configuration: host, username, password")
    
    def connect(self) -> bool:
        try:
            if self.use_sftp:
                return self._connect_sftp()
            else:
                return self._connect_ftp()
        except Exception as e:
            self.logger.error(f"FTP connection failed: {e}")
            raise FTPError(f"Connection failed: {e}")
    
    def _connect_ftp(self) -> bool:
        try:
            self.connection = ftplib.FTP()
            self.connection.set_debuglevel(0)
            self.connection.connect(self.host, self.port, timeout=self.timeout)
            self.connection.login(self.username, self.password)
            
            self.logger.info(f"FTP connected to {self.host}:{self.port}")
            return True
            
        except ftplib.all_errors as e:
            self.logger.error(f"FTP connection error: {e}")
            raise FTPError(f"FTP connection failed: {e}")
    
    def _connect_sftp(self) -> bool:
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout
            )
            
            self.sftp_connection = self.ssh_client.open_sftp()
            self.logger.info(f"SFTP connected to {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"SFTP connection error: {e}")
            raise FTPError(f"SFTP connection failed: {e}")
    
    def disconnect(self) -> None:
        try:
            if self.connection:
                self.connection.quit()
                self.connection = None
                self.logger.info("FTP disconnected")
            
            if self.sftp_connection:
                self.sftp_connection.close()
                self.sftp_connection = None
            
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
                self.logger.info("SFTP disconnected")
                
        except Exception as e:
            self.logger.warning(f"Error during disconnect: {e}")
    
    def upload_file(self, local_file_path: str, remote_file_name: str = None) -> bool:
        if not os.path.exists(local_file_path):
            raise FTPError(f"Local file not found: {local_file_path}")
        
        if remote_file_name is None:
            remote_file_name = os.path.basename(local_file_path)
        
        remote_path = os.path.join(self.remote_directory, remote_file_name).replace('\\', '/')
        
        for attempt in range(self.max_retries):
            try:
                if not self.is_connected():
                    self.connect()
                
                if self.use_sftp:
                    return self._upload_sftp(local_file_path, remote_path)
                else:
                    return self._upload_ftp(local_file_path, remote_path)
                    
            except Exception as e:
                self.logger.warning(f"Upload attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise FTPError(f"Upload failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
        
        return False
    
    def _upload_ftp(self, local_file_path: str, remote_path: str) -> bool:
        try:
            self._ensure_remote_directory(os.path.dirname(remote_path))
            
            with open(local_file_path, 'rb') as file:
                self.connection.storbinary(f'STOR {remote_path}', file)
            
            self.logger.info(f"File uploaded: {local_file_path} -> {remote_path}")
            return True
            
        except ftplib.all_errors as e:
            raise FTPError(f"FTP upload failed: {e}")
    
    def _upload_sftp(self, local_file_path: str, remote_path: str) -> bool:
        try:
            remote_dir = os.path.dirname(remote_path)
            self._ensure_remote_directory_sftp(remote_dir)
            
            self.sftp_connection.put(local_file_path, remote_path)
            self.logger.info(f"File uploaded via SFTP: {local_file_path} -> {remote_path}")
            return True
            
        except Exception as e:
            raise FTPError(f"SFTP upload failed: {e}")
    
    def _ensure_remote_directory(self, remote_dir: str) -> None:
        if not remote_dir or remote_dir == '/':
            return
        
        try:
            self.connection.cwd(remote_dir)
            self.connection.cwd('/')
        except ftplib.error_perm:
            dirs = remote_dir.strip('/').split('/')
            current_path = '/'
            
            for dir_name in dirs:
                if not dir_name:
                    continue
                    
                current_path = os.path.join(current_path, dir_name).replace('\\', '/')
                
                try:
                    self.connection.cwd(current_path)
                except ftplib.error_perm:
                    try:
                        self.connection.mkd(current_path)
                        self.logger.info(f"Created remote directory: {current_path}")
                    except ftplib.error_perm:
                        pass
            
            self.connection.cwd('/')
    
    def _ensure_remote_directory_sftp(self, remote_dir: str) -> None:
        if not remote_dir or remote_dir == '/':
            return
        
        dirs = remote_dir.strip('/').split('/')
        current_path = '/'
        
        for dir_name in dirs:
            if not dir_name:
                continue
                
            current_path = os.path.join(current_path, dir_name).replace('\\', '/')
            
            try:
                self.sftp_connection.stat(current_path)
            except FileNotFoundError:
                try:
                    self.sftp_connection.mkdir(current_path)
                    self.logger.info(f"Created remote SFTP directory: {current_path}")
                except Exception as e:
                    self.logger.warning(f"Could not create directory {current_path}: {e}")
    
    def is_connected(self) -> bool:
        try:
            if self.use_sftp:
                return self.sftp_connection is not None and self.ssh_client is not None
            else:
                return self.connection is not None and self.connection.sock is not None
        except:
            return False
    
    def test_connection(self) -> bool:
        try:
            self.connect()
            if self.use_sftp:
                self.sftp_connection.listdir('.')
            else:
                self.connection.nlst()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        finally:
            self.disconnect()