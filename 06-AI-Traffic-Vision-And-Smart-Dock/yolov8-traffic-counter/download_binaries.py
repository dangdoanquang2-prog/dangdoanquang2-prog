import os
import zipfile
import urllib.request
import ssl

# Disable SSL verification for safety against local proxy issues
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BIN_DIR = r"d:\appdemxe\bin"
os.makedirs(BIN_DIR, exist_ok=True)

urls = {
    "ffmpeg": "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-win-64.zip",
    "ffprobe": "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffprobe-6.1-win-64.zip"
}

headers = {"User-Agent": "Mozilla/5.0"}

for name, url in urls.items():
    zip_path = os.path.join(BIN_DIR, f"{name}.zip")
    print(f"Downloading {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(zip_path, "wb") as f:
                f.write(response.read())
        print(f"Downloaded {name}.zip successfully.")
        
        # Extract
        print(f"Extracting {name}.zip...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(BIN_DIR)
        
        # Clean up zip
        os.remove(zip_path)
        print(f"Extraction of {name} completed.")
    except Exception as e:
        print(f"Error downloading/extracting {name}: {e}")

print("Done! Binaries are at:", BIN_DIR)
print("Files in bin folder:", os.listdir(BIN_DIR))
