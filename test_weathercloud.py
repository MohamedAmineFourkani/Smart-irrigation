import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Login
login_page = session.get("https://app.weathercloud.net/signin")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf = soup.find("input", {"name": "_token"})
token = csrf["value"] if csrf else None

payload = {
    "signin[username]": "NABOU5",
    "signin[password]": "Nabou@@2015",
}
if token:
    payload["_token"] = token

login = session.post("https://app.weathercloud.net/signin", data=payload)
print("Login status:", login.status_code)

# Fetch data
device_id = "1843032708"
r = session.get(
    f"https://app.weathercloud.net/device/values?code={device_id}",
    headers={"X-Requested-With": "XMLHttpRequest"}
)

print("Data status:", r.status_code)

if r.text.strip():
    data = r.json()
    print("\n✅ Data received:")
    for key, value in data.items():
        print(f"  {key}: {value}")
else:
    print("❌ Empty response")