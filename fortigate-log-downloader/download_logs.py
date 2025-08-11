import os
import requests
import datetime
import configparser

config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(script_dir, 'config.ini'))

FG_URL = config['fortigate']['url']
API_TOKEN = config['fortigate']['token']
SERIAL_NO = config['fortigate']['serial']
VDOM = config['fortigate']['vdom']

# Previous day range
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
start = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
end = int(yesterday.replace(hour=23, minute=59, second=59, microsecond=999000).timestamp() * 1000)
filename = f'fortigate-auth-{yesterday.strftime("%Y-%m-%d")}.log'

url = (
    f"{FG_URL}/api/v2/log/memory/event/user/raw"
    f"?filter=subtype==%22user%22"
    f"&filter=_metadata.timestamp>={start}"
    f"&filter=_metadata.timestamp<={end}"
    f"&filter=authserver=@%22*2fa*%22"
    f"&extra=country_id&extra=reverse_lookup"
    f"&serial_no={SERIAL_NO}&vdom={VDOM}"
)

headers = {
    'Authorization': f"Bearer {API_TOKEN}"
}

response = requests.get(url, headers=headers, verify=False)

if response.ok and response.text.strip():
    os.makedirs("logs", exist_ok=True)
    with open(f'/root/elk/fortigate-log-downloader/logs/{filename}', 'w') as f:
        f.write(response.text)
    print(f"✅ Saved: /root/elk/fortigate-log-downloader/logs/{filename}")
else:
    print("⚠️ No logs to download or failed to connect")
