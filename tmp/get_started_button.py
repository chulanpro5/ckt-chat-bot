import requests

FB_API_URL = 'https://graph.facebook.com/v11.0/me/messages'
FB_API_URL_PROFILE = 'https://graph.facebook.com/v11.0/me/messenger_profile'
PAGE_ACCESS_TOKEN = ''

auth = {
  	'access_token': PAGE_ACCESS_TOKEN,
}

data = {
  "get_started": {"payload": "started"}
}

response = requests.post(
	FB_API_URL_PROFILE,
    params=auth,
    json=data
)

print(response.json())