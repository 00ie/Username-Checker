import json
import os

class Settings:
    def __init__(self):
        self.path = os.path.join("config", "settings.json")
        self.defaults = {
            "threads": 10,
            "timeout": 15,
            "webhook_url": "",
            "use_proxies": False,
            "jitter_min": 0.5,
            "jitter_max": 1.5,
            "platforms": {
                "pinterest": True,
                "instagram": True,
                "github": True
            }
        }
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.path):
            return self.defaults
        try:
            with open(self.path, 'r') as f:
                return {**self.defaults, **json.load(f)}
        except:
            return self.defaults

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except:
            pass

    def get(self, key):
        keys = key.split('.')
        val = self.data
        for k in keys:
            val = val.get(k)
            if val is None: return None
        return val

    def set(self, key, value):
        keys = key.split('.')
        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save()

settings = Settings()
