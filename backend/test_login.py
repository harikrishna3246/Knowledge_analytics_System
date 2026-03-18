import requests

url = "http://127.0.0.1:8000/signup"
body = {"email": "testuser@example.com", "password": "1234", "name": "Test User"}
resp = requests.post(url, json=body)
print(resp.status_code)
print(resp.text)
