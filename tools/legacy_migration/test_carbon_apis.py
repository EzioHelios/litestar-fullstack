import json

import requests

BASE_URL = "http://localhost:8000"

endpoints = [
    "/api/page1/ydfdzl/day",
    "/api/page1/ydfdzl/day/",
    "/api/page1/yjzl",
    "/api/page1/yjzl/",
    "/api/page2/spgl",
    "/api/page2/spgl/",
    "/api/page3/cnsy",
    "/api/page3/cnsy/",
    "/api/page4/tpfltj",
    "/api/page4/tpfltj/",
]

def test_endpoints():
    print(f"Testing endpoints on {BASE_URL}...")
    for ep in endpoints:
        try:
            resp = requests.get(f"{BASE_URL}{ep}")
            print(f"GET {ep} - Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            else:
                print(f"  Error: {resp.text[:100]}")
        except Exception as e:
            print(f"  FAILED to connect: {e}")

if __name__ == "__main__":
    test_endpoints()
