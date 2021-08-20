import requests
from flask import Flask, request
app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = '123456'  # <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EABAMQ9TnhaEBAIz3JZCT6rEV1RxszZCm5fuegVDNOEcqmcbBgPQYitWOxaf0JTXSj82A3Np5on4A6EZBpG6S9Ad4XCJmaZB7xuPb0lwGoNQiOVoB7cx6MHYCI5ZCTN2NEUhjwFXMUM4jdUnX8LdmL64ZCsSSvRFXAIZCnsWTdeKqW5tFk4NxfZCM'  # paste your page access token here>"

user_data = {}
waiting_room = {
    "state": "empty",
    "id": ""
}

def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()

def send_action(recipient_id, action):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        "sender_action" : action
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()

def is_seen(event):
    return (event.get('read'))


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def timban(id):
    if user_data[id]["state"] == "connected":
        send_message(id, "Bạn đang ở trong cuộc trò chuyện")
    elif user_data[id]["state"] == "waiting" :
        send_message(id, "Đợi chút")
    elif user_data[id]["state"] == "empty":
        find_partner(id)


def find_partner(id):
    if waiting_room["state"] == "empty":
        send_message(id, "Đợi chút")
        waiting_room["id"] = id
        waiting_room["state"] = "waiting"
        user_data[id]["state"] = "waiting"
    elif waiting_room["state"] == "waiting":
        connect(id, waiting_room["id"])


def connect(id1, id2):
    user_data[id1]["state"] = "connected"
    user_data[id1]["partner"] = id2
    user_data[id2]["state"] = "connected"
    user_data[id2]["partner"] = id1

    waiting_room["state"] = "empty"
    waiting_room["id"] = ""

    send_message(id1, "Cuộc trò chuyện bắt đầu")
    send_message(id2, "Cuộc trò chuyện bắt đầu")


def ketthuc(id):
    if user_data[id]["state"] == "connected":
        disconnect(id)
    elif user_data[id]["state"] == "waiting":
        send_message(id, "Bạn đang tìm kiếm cuộc trò chuyện")
    elif user_data[id]["state"] == "empty":
        send_message(id, "Bạn chưa bắt đầu cuộc trò chuyện")


def disconnect(id):
    partner_id = user_data[id]["partner"]

    user_data[id]["state"] = "empty"
    user_data[id]["partner"] = "empty"
    user_data[partner_id]["state"] = "empty"
    user_data[partner_id]["partner"] = "empty"

    send_message(id, "Cuộc trò chuyện đã kết thúc")
    send_message(partner_id, "Cuộc trò chuyện đã kết thúc")


def send_message_to_partner(id, message):
    if user_data[id]["state"] == "connected":
        send_message(user_data[id]["partner"], message)
    else:
        send_message(id, "Bạn không ở trong cuộc trò chuyện")


def create_user_data(id):
    user_data[id] = {}
    user_data[id]["state"] = "empty"
    user_data[id]["partner"] = "empty"


def respond(id, message):
    formated_message = message.lower()
    if id not in user_data:
        create_user_data(id)

    if formated_message == "timban":
        timban(id)
    elif formated_message == "ketthuc":
        ketthuc(id)
    else:
        send_message_to_partner(id, message)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


@app.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == "GET":
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            print(x)
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                send_action(sender_id, "typing_on")
                respond(sender_id, text)

            if is_seen(x):
                sender_id = x['sender']['id']
                if sender_id in user_data and user_data[sender_id]["state"] == "connected":
                    send_action(user_data[sender_id]["partner"], "mark_seen")
                
        return "ok"


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
