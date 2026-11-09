import urllib.request
import bz2
import os
import shutil
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "http://ciscobinary.openh264.org/openh264-1.8.0-win64.dll.bz2"
dest_bz2 = "openh264-1.8.0-win64.dll.bz2"
dest_dll = "openh264-1.8.0-win64.dll"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("Downloading openh264-1.8.0-win64.dll.bz2...")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as response:
        with open(dest_bz2, "wb") as f:
            f.write(response.read())
    print("Downloaded successfully.")
except Exception as e:
    print(f"Error downloading: {e}")
    exit(1)

print("Decompressing bz2 file...")
try:
    with open(dest_dll, 'wb') as new_file, bz2.BZ2File(dest_bz2, 'rb') as file:
        data = file.read()
        new_file.write(data)
    print("Decompressed successfully.")
except Exception as e:
    print(f"Error decompressing: {e}")
    exit(1)

print("Cleaning up bz2 file...")
if os.path.exists(dest_bz2):
    os.remove(dest_bz2)

print("Copying to bin folder...")
os.makedirs("bin", exist_ok=True)
shutil.copy(dest_dll, os.path.join("bin", dest_dll))

print("Verifying if cv2 can write H.264 video using 'avc1' codec...")
import cv2
writer = cv2.VideoWriter('test_codec_verif.mp4', cv2.VideoWriter_fourcc(*'avc1'), 30, (640, 480))
is_successful = writer.isOpened()
print("Success status:", is_successful)
writer.release()

if os.path.exists('test_codec_verif.mp4'):
    os.remove('test_codec_verif.mp4')

if is_successful:
    print("SUCCESS: H.264 (avc1) codec is now fully working!")
else:
    print("WARNING: Codec check failed even after download.")
