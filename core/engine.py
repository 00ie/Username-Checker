import concurrent.futures
import requests
import time
from datetime import datetime
from core.platforms import PinterestChecker, GitHubChecker, InstagramChecker
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

    def check_target(self, username):
        if not self.active: return None
        
        settings_data = settings.load()
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

        if not platforms_to_check: return result
        
        result["checked_platforms"] = platforms_to_check

        for platform in platforms_to_check:
            try:
                if self.checkers[platform].check(username):
                    result["available_on"].append(platform)
            except:
                continue

        if result["available_on"]:
            self.dispatch_webhook(result)
            
        return result

    def dispatch_webhook(self, data):
        url = settings.get("webhook_url")
        if not url: return

        links_text = ""
        for p in data["available_on"]:
            links_text += f"[{p.title()}](https://www.{p}.com/{data['username']})\n"

        embed = {
            "title": f"Available: @{data['username']} | by @methzzy",
            "color": 0x2b2d31,
            "fields": [
                {"name": "Found at", "value": f"`{data['timestamp']}`", "inline": False},
                {"name": "Platform", "value": ", ".join([p.title() for p in data["available_on"]]), "inline": True},
                {"name": "Link", "value": links_text, "inline": True}
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
            requests.post(url, json=payload, timeout=5)
        except:
            pass

    def start_bulk(self, usernames, callback):
        self.active = True
        self.monitor_mode = False
        max_workers = int(settings.get("threads") or 10)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            self.executor = executor
            futures = {executor.submit(self.check_target, user): user for user in usernames}
            
            for future in concurrent.futures.as_completed(futures):
                if not self.active: break
                try:
                    data = future.result()
                    if data: callback(data)
                except:
                    pass

    def start_monitor(self, username, callback, delay=60):
        self.active = True
        self.monitor_mode = True
        
        while self.active:
            data = self.check_target(username)
            if data: callback(data)
            if data and data["available_on"]:
                pass
            
            for _ in range(delay):
                if not self.active: break
                time.sleep(1)

    def stop(self):
        self.active = False
        if self.executor:
            self.executor.shutdown(wait=False)
