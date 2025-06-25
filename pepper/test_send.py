import time
import requests

start_time = time.time()
url = "http://e687-192-71-49-53.ngrok-free.app/transcribe"

files = {
    "audio": (
        "test_record.ogg",
        open("/home/nao/recordings/test_record.ogg", "rb"),
        "audio/ogg"
    )
}

try:
    resp = requests.post(url, files=files, timeout=100)
    print(resp.status_code, resp.json())
except Exception as e:
    print("Request failed:", e)


end_time = time.time()
print("elapsed time:", end_time-start_time)
