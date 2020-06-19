import requests

url = "http://35.206.250.159:10050/detect"

payload = {}
files = [
  ('image', open('/Users/yuhui/Desktop/trainning/doudou/dog_20200307200037570583.jpeg','rb'))
]
headers= {}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.json()['code'])
