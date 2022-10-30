# coding=utf-8
import requests

url = "http://www.pikachu.com/index.php"
response = requests.get(url)
print(response.status_code)
