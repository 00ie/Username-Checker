import requests
import re
import random
import time
import os
from abc import ABC, abstractmethod
from config.settings import settings

class ProxyManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProxyManager, cls).__new__(cls)
            cls._instance.proxies = []
            cls._instance.load_proxies()
        return cls._instance

    def load_proxies(self):
        if os.path.exists("proxies.txt"):
            with open("proxies.txt", "r") as f:
                self.proxies = [line.strip() for line in f if line.strip()]

    def get_proxy(self):
        if not settings.get("use_proxies") or not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

class PlatformChecker(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.proxy_mgr = ProxyManager()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
        ]

    def get_request_kwargs(self):
        kwargs = {
            "headers": {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            },
            "timeout": settings.get("timeout") or 10
        }
        
        proxy = self.proxy_mgr.get_proxy()
        if proxy:
            kwargs["proxies"] = proxy
            
        return kwargs

    def jitter(self):
        min_delay = settings.get("jitter_min") or 0.1
        max_delay = settings.get("jitter_max") or 0.5
        time.sleep(random.uniform(min_delay, max_delay))

    @abstractmethod
    def check(self, username):
        pass

class PinterestChecker(PlatformChecker):
    def check(self, username):
        self.jitter()
        url = f"https://www.pinterest.com/{username}/"
        try:
            kwargs = self.get_request_kwargs()
            response = self.session.get(url, **kwargs)
            
            if response.url.rstrip('/') in ["https://www.pinterest.com", "https://br.pinterest.com"]:
                return True
                
            if response.status_code == 404:
                return True
            
            content = response.text.lower()
            if "page not found" in content:
                return True
                
            return False
        except:
            return False

class GitHubChecker(PlatformChecker):
    def check(self, username):
        self.jitter()
        url = f"https://github.com/{username}"
        try:
            kwargs = self.get_request_kwargs()
            response = self.session.get(url, **kwargs)
            
            if response.status_code == 404:
                return True
                
            return False
        except:
            return False

class InstagramChecker(PlatformChecker):
    def check(self, username):
        self.jitter()
        url = f"https://www.instagram.com/{username}/"
        try:
            kwargs = self.get_request_kwargs()
            response = self.session.get(url, **kwargs)
            
            if response.status_code == 404:
                return True
                
            if response.status_code == 200:
                if "Page Not Found" in response.text or "The link you followed may be broken" in response.text:
                    return True
                    
            return False
        except:
            return False
