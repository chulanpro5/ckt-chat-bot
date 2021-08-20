import requests
from flask import Flask, request
app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = '123456'  # <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EABAMQ9TnhaEBAKnZAaWvE3ZCI8iM4u11ZCuufRZCabUwxZCI029gujczZC5OoWKkDZA5r0NnnZCGR90IVafaTRYNgEiYLz66v7Pab2ht4JDlvvpBWl2zwPyCn8CeAZBxvNefjciCY80nwJV73we4apucbKYsVWOBu2JUVerguZCfX9IatJgIziPSU0'  # paste your page access token here>"

waiting = 0
matched = 1
state = matched
data_user = {
    "0": "1"
}
user_wait = ""


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


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def state_user(sender):
    if sender in data_user:
        return 1
    return 0


def respond(sender, message):
    global state
    global user_wait

    """Formulate a response to the user and
    pass it on to a function that sends it."""

    formated_message = message.lower()

    if formated_message == "batdau":
        if state_user(sender) == matched:
            send_message(sender, "Bạn đang ở trong cuộc trò chuyện")
            return

        if sender == user_wait:
            send_message(sender, "Hãy đợi 1 xíu")
            return

        if state == matched:
            send_message(sender, "Hãy đợi 1 xíu")
            state = waiting
            user_wait = sender
            return

        if state == waiting:
            data_user[sender] = user_wait
            data_user[user_wait] = sender
            send_message(sender, "Hãy bắt đầu cuộc trò chuyện")
            send_message(user_wait, "Hãy bắt đầu cuộc trò chuyện")
            state = matched
            return

    if formated_message == "ketthuc":
        if state_user(sender) == matched:
            send_message(sender, "Bạn đã kết thúc cuộc trò chuyện")
            send_message(data_user[sender], "Bạn đã kết thúc cuộc trò chuyện")
            data_user.pop(data_user[sender])
            data_user.pop(sender)
        return

    if state_user(sender) == matched:
        send_message(data_user[sender], message)


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
        print(event)
        for x in event:
            # print(x)
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
