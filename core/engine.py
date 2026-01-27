import concurrent.futures
import requests
import time
from datetime import datetime
from core.platforms import PinterestChecker, GitHubChecker, InstagramChecker, ProxyManager
from core.validation import Validator
from config.settings import settings


class AuditEngine:
    def __init__(self):
        self.checkers = {
            "pinterest": PinterestChecker(),
            "github": GitHubChecker(),
            "instagram": InstagramChecker()
        }
        self.validator = Validator()
        self.executor = None
        self.active = False
        self.monitor_mode = False
        self.settings_data = settings.load()

    def refresh_settings(self):
        self.settings_data = settings.load()

    def check_target(self, username, settings_data=None):
        if not self.active:
            return None

        if settings_data is None:
            settings_data = self.settings_data
        result = {
            "username": username,
            "available_on": [],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "checked_platforms": []
        }

        platforms_to_check = []
        if settings_data.get("platforms", {}).get("pinterest") and self.validator.check_pinterest(username):
            platforms_to_check.append("pinterest")
        if settings_data.get("platforms", {}).get("github") and self.validator.check_github(username):
            platforms_to_check.append("github")
        if settings_data.get("platforms", {}).get("instagram") and self.validator.check_instagram(username):
            platforms_to_check.append("instagram")

        if not platforms_to_check:
            return result

        result["checked_platforms"] = platforms_to_check
        result["possibly_available"] = []

        for platform in platforms_to_check:
            try:
                check_result = self.checkers[platform].check(username)
                if check_result == "POSSIBLY_AVAILABLE":
                    result["possibly_available"].append(platform)
                elif check_result is True:
                    result["available_on"].append(platform)
                else:
                    if check_result is None and len(username) < 4:
                        result["possibly_available"].append(platform)
            except Exception:
                continue

        if result["available_on"] or result["possibly_available"]:
            self.dispatch_webhook(result)

        return result

    def dispatch_webhook(self, data):
        url = settings.get("webhook_url")
        if not url:
            return

        all_available = data.get("available_on", []) + data.get("possibly_available", [])
        if not all_available:
            return

        links_text = ""
        for platform in all_available:
            if platform.lower() == "instagram":
                links_text += f"[Instagram](https://instagram.com/{data['username']})\n"
            else:
                links_text += f"[{platform.title()}](https://www.{platform}.com/{data['username']})\n"

        title = f"Available: @{data['username']}"
        if data.get("possibly_available"):
            title = f"Possibly Available (Verify): @{data['username']}"

        embed = {
            "title": f"{title} | by @methzzy",
            "color": 0x2b2d31,
            "fields": [
                {"name": "Found at", "value": f"`{data['timestamp']}`", "inline": False},
                {"name": "Platform", "value": ", ".join([p.title() for p in all_available]), "inline": True},
                {"name": "Profile Link", "value": links_text, "inline": True}
            ],
            "footer": {
                "text": "Username checker | Gon's Tools",
                "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            },
            "thumbnail": {
                "url": "https://i.pinimg.com/736x/9f/e0/d5/9fe0d5270bd1426e6055115434c6eaf3.jpg"
            }
        }

        payload = {
            "username": "Gon's Sniper",
            "avatar_url": "https://i.pinimg.com/736x/9f/e0/d5/9fe0d5270bd1426e6055115434c6eaf3.jpg",
            "embeds": [embed]
        }

        try:
            proxy_mgr = ProxyManager()
            proxies = proxy_mgr.get_proxy()
            if proxies:
                response = requests.post(url, json=payload, timeout=8, proxies=proxies)
                if response.status_code >= 400:
                    requests.post(url, json=payload, timeout=8)
            else:
                requests.post(url, json=payload, timeout=8)
        except Exception:
            try:
                requests.post(url, json=payload, timeout=8)
            except Exception:
                pass

    def start_bulk(self, usernames, callback):
        self.active = True
        self.monitor_mode = False
        self.refresh_settings()
        max_workers = int(settings.get("threads") or 10)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            self.executor = executor
            futures = {executor.submit(self.check_target, user, self.settings_data): user for user in usernames}

            for future in concurrent.futures.as_completed(futures):
                if not self.active:
                    break
                try:
                    data = future.result()
                    if data:
                        callback(data)
                except Exception:
                    pass

    def start_monitor(self, username, callback, delay=60):
        self.active = True
        self.monitor_mode = True
        self.refresh_settings()

        while self.active:
            data = self.check_target(username, self.settings_data)
            if data:
                callback(data)

            for _ in range(delay):
                if not self.active:
                    break
                time.sleep(1)

    def stop(self):
        self.active = False
        if self.executor:
            self.executor.shutdown(wait=False)
