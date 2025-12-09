import requests

URL = "http://localhost/malaka/api-check-certificate/?jshshr="
HEADERS = {'Authorization': 'Token 2c4444a708b846961605059ce3e6fb52b6131282'}

def check_certificate(jshshr):
    url = f"{URL}{jshshr}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    return data