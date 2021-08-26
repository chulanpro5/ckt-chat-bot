import requests

FB_API_URL = 'https://graph.facebook.com/v11.0/me/messages'
FB_API_URL_PROFILE = 'https://graph.facebook.com/v11.0/me/messenger_profile'
PAGE_ACCESS_TOKEN = ''

auth = {
  	'access_token': PAGE_ACCESS_TOKEN,
}

data = {
  "persistent_menu": [
        {
            "locale": "default",
            "composer_input_disabled": 'false',
            "call_to_actions": [
                {
                    "type": "postback",
                    "title": "Khởi hành",
                    "payload": "timban"
                },
                {
                    "type": "postback",
                    "title": "Dừng chân",
                    "payload": "ketthuc"
                },
                {
                    "type": "postback",
                    "title": "Báo cáo",
                    "payload": "report"
                },
                {
                    "type": "web_url",
                    "title": "Gửi phản hồi",
                    "url": "https://docs.google.com/forms/d/e/1FAIpQLSfG_FC5wba-pvwg0z-fxhTyKUuLM8eZ1Y6e1qo1xRnxCOC4IA/viewform?usp=sf_link",
                    "webview_height_ratio": "full"
                }
            ]
        }
    ]
}

response = requests.post(
	FB_API_URL_PROFILE,
    params=auth,
    json=data
)

print(response.json())