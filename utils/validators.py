import re
from typing import Tuple, Optional


class InputValidator:
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 2:
            return False, "Username must be at least 2 characters"
        
        if len(username) > 30:
            return False, "Username must be less than 30 characters"
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False, "Username can only contain letters, numbers, _, -, and ."
        
        return True, None
    
    @staticmethod
    def validate_number(value: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        try:
            num = int(value)
        except ValueError:
            return False, "Must be a valid number"
        
        if min_val is not None and num < min_val:
            return False, f"Must be at least {min_val}"
        
        if max_val is not None and num > max_val:
            return False, f"Must be at most {max_val}"
        
        return True, None
    
    @staticmethod
    def validate_proxy(proxy: str) -> Tuple[bool, Optional[str]]:
        if not proxy:
            return False, "Proxy cannot be empty"
        
        clean_proxy = proxy
        for protocol in ['http://', 'https://', 'socks4://', 'socks5://']:
            if proxy.startswith(protocol):
                clean_proxy = proxy[len(protocol):]
                break
        
        if '@' in clean_proxy:
            auth, host_port = clean_proxy.split('@', 1)
            if ':' not in auth:
                return False, "Invalid authentication format (should be user:pass@host:port)"
        else:
            host_port = clean_proxy
        
        if ':' not in host_port:
            return False, "Missing port (format: host:port)"
        
        parts = host_port.rsplit(':', 1)
        if len(parts) != 2:
            return False, "Invalid proxy format"
        
        host, port = parts
        
        if not host:
            return False, "Missing host"
        
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return False, "Port must be between 1 and 65535"
        except ValueError:
            return False, "Port must be a number"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        if not url:
            return False, "URL cannot be empty"
        
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not pattern.match(url):
            return False, "Invalid URL format"
        
        return True, None
