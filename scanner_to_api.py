import sys
import requests

API_URL = "http://10.65.139.44:8000/scan"

print("Ready. Scan barcode...")

while True:
    try:
        # Read one line (scanner usually sends Enter at the end)
        barcode = sys.stdin.readline().strip()

        if not barcode:
            continue

        print("Scanned:", barcode)

        res = requests.post(API_URL, json={"barcode": barcode}, timeout=5)

        if res.status_code == 200:
            print("Sent to backend ✔")
        else:
            print("Error:", res.status_code, res.text)

    except Exception as e:
        print("Exception:", e)

# import hid

# for d in hid.enumerate():
#     print(d['vendor_id'], d['product_id'], d['product_string'])