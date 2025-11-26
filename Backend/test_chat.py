import requests
try:
    r = requests.post('http://127.0.0.1:5001/api/shopping/chat', json={"message": "hi how is the climate today"})
    print(r.status_code)
    print(r.text)
except Exception as e:
    print(e)
