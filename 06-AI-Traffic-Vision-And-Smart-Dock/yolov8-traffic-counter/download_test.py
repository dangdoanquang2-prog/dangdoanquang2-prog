import httpx

urls = [
    "https://github.com/roboflow/supervision/raw/develop/demo/video/vehicles.mp4",
    "https://raw.githubusercontent.com/ultralytics/assets/main/bus.jpg",
]

headers = {"User-Agent": "Mozilla/5.0"}

for url in urls:
    fname = url.split("/")[-1]
    print(f"Trying: {fname}...")
    try:
        with httpx.Client(follow_redirects=True, verify=False, timeout=30) as c:
            r = c.get(url, headers=headers)
            print(f"  Status: {r.status_code}, Size: {len(r.content)} bytes")
            if r.status_code == 200 and len(r.content) > 50000:
                out = f"d:\\appdemxe\\{fname}"
                with open(out, "wb") as f:
                    f.write(r.content)
                print(f"  Saved to: {out}")
    except Exception as e:
        print(f"  Error: {e}")
