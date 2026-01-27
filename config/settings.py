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
            return self.defaults.copy()
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                return {**self.defaults, **loaded}
        except Exception:
            return self.defaults.copy()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        keys = key.split('.')
        val = self.data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key, value):
        keys = key.split('.')
        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save()

settings = Settings()
