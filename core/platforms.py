import requests
import re
import random
import time
import os
import importlib.util
from abc import ABC, abstractmethod
from config.settings import settings

class ProxyManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProxyManager, cls).__new__(cls)
            cls._instance.proxies = []
            cls._instance.blacklist = set()
            cls._instance.proxies_file = "proxies.txt"
            cls._instance.blacklist_file = "bad_proxies.txt"
            cls._instance.socks_supported = importlib.util.find_spec('socks') is not None
            cls._instance.load_proxies()
            cls._instance.load_blacklist()
        return cls._instance

    def load_proxies(self):
        if os.path.exists(self.proxies_file):
            try:
                with open(self.proxies_file, "r", encoding="utf-8") as f:
                    self.proxies = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            except:
                self.proxies = []

    def save_proxies(self, path: str = "proxies.txt"):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.proxies))
        except:
            pass

    def load_blacklist(self, path: str = None):
        path = path or self.blacklist_file
        self.blacklist = set()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.blacklist = set([line.strip() for line in f if line.strip()])
            except:
                self.blacklist = set()

    def save_blacklist(self, path: str = None):
        path = path or self.blacklist_file
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(self.blacklist)))
        except:
            pass

    def mark_bad_proxy(self, proxy: str):
        if not proxy: return
        self.blacklist.add(proxy.strip())
        self.save_blacklist()

    def unmark_bad_proxy(self, proxy: str):
        try:
            self.blacklist.discard(proxy.strip())
            self.save_blacklist()
        except:
            pass

    def is_blacklisted(self, proxy: str) -> bool:
        return proxy.strip() in self.blacklist

    def clear_blacklist(self):
        self.blacklist = set()
        self.save_blacklist()

    def add_proxy(self, proxy: str, path: str = "proxies.txt") -> bool:
        if not proxy: return False
        p = proxy.strip()
        if not p or p in self.proxies:
            return False
        self.proxies.append(p)
        self.save_proxies(path)
        return True

    def remove_proxy(self, proxy: str, path: str = "proxies.txt") -> bool:
        if not proxy: return False
        p = proxy.strip()
        try:
            self.proxies.remove(p)
            self.save_proxies(path)
            return True
        except ValueError:
            return False

    def get_proxy(self):
        if not settings.get("use_proxies") or not self.proxies:
            return None

        available = [p for p in self.proxies if p and p.strip() and p.strip() not in self.blacklist]
        if not available:
            return None

        proxy = random.choice(available).strip()

        if proxy.startswith("http://") or proxy.startswith("https://") or proxy.startswith("socks"):
            scheme_host = proxy
        else:
            scheme_host = f"http://{proxy}"

        if scheme_host.startswith("socks") and not self.socks_supported:
            self.mark_bad_proxy(proxy)
            return None

        return {
            "http": scheme_host,
            "https": scheme_host
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
