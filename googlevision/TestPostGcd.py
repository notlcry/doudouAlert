import requests

url = "http://35.206.250.159:10050/detect"

payload = {}
files = [
  ('image', open('/Users/yuhui/Desktop/doudou/dog_20200314134215_85.546875.jpeg','rb'))
]
headers= {}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.json()['code'])
