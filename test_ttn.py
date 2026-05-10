import requests

API_KEY = "NNSXS.ASLLX336KBM2DC6FAHKTCJN7ADUMKCAEA3H5Z2Q.BQ2YBW3SCALTTURG4Q26CM6XRI3QYM544BZLIVWQMGEHL5R37PZQ"
APP_ID = "a8404180a75e149b"
TTN_URL = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{APP_ID}/packages/storage/uplink_message"

r = requests.get(
    TTN_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    },
    params={"limit": 1}   # just fetch the latest message
)

print("Status:", r.status_code)

if r.status_code == 200:
    # TTN returns one JSON object per line
    first_line = r.text.strip().split("\n")[0]
    import json
    data = json.loads(first_line)
    print("\n✅ Raw message received:")
    import pprint
    pprint.pprint(data)
else:
    print("❌ Error:", r.text[:300])