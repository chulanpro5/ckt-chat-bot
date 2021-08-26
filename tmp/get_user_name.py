import requests
import os
from dotenv import load_dotenv

load_dotenv()

PAGE_ACCESS_TOKEN = ''
user_id = ''
fields = 'name'

print(PAGE_ACCESS_TOKEN)
print(user_id)
print(fields)

x = "https://graph.facebook.com/%s?fields=%s&access_token=%s"%(user_id, fields, PAGE_ACCESS_TOKEN)

response = requests.get(x)

print(response.json())
