import requests
from flask import Flask, request
import json
from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from flask import jsonify
import pytz 

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = '123456'  # <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EAAFZAXBWQCHQBAEG4HwBZAt0VZC3Yjmf4FxRiebORBhzWdGN4wZAZAz75kGvhihDHrpvPZC96VGFeINKaBQtOqOT3PbZBq6UsywrxFw2s2J5Es9TRLzta2YyqRx2oNWZCSRJ157UeUtgQ7gsvgjHYA0cyVXMeb0gq9V7WE3mooALqFb6gLhDO5H8'  # paste your page access token here>"


data = open('data.json',)
data = json.load(data)
reply = open('reply.json',  encoding="utf8")
reply = json.load(reply)
buttons = open('buttons.json',encoding="utf8")
buttons = json.load(buttons)

user_data = data["user_data"]
waiting_room = data["waiting_room"]
count = data["count"]


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'key.json'
credentials = None
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SAMPLE_SPREADSHEET_ID = '1461y4vKxSoPwaDV6wUuLAqObNXwEWZ3Hmq27pKywbt0'
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def send_message(payload):
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()


def send_text(recipient_id, text):
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    send_message(payload)

def send_buttons(recipient_id, text, buttons):
    payload = {
        "message":{
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text": text,
                    "buttons": buttons
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    return send_message(payload)

def send_action(recipient_id, action):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        "sender_action": action
    }

    send_message(payload)


def send_attachment(recipient_id, attachment_url, type):
    payload = {
        "message": {
            "attachment": {
                "type": type,
                "payload": {
                    "url": attachment_url
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    send_message(payload)


def is_command(event):
    if "postback" in event:
        if "payload" in event["postback"]:
            return event["postback"]["payload"]
    else:
        return 0


def process_command(id, command):
    if command == "started":
        send_buttons(id, reply["started"], [buttons["rule"], buttons["timban"]])
        create_user(id)
    if command == "timban":
        timban(id)
    elif command == "ketthuc":
        ketthuc(id)
    elif command == "report":
        report(id)


def timban(id):
    if user_data[id]["state"] == "connected":
        send_buttons(id, reply["timban-connected"], [buttons["ketthuc"]])
    elif user_data[id]["state"] == "waiting":
        send_text(id, reply["timban-waiting"])
    elif user_data[id]["state"] == "empty":
        find_partner(id)


def find_partner(id):
    if waiting_room["state"] == "empty":
        send_text(id, reply["timban-empty"])
        waiting_room["id"] = id
        waiting_room["state"] = "waiting"
        user_data[id]["state"] = "waiting"
    elif waiting_room["state"] == "waiting":
        send_text(id, reply["timban-empty"])
        connect(id, waiting_room["id"])


def connect(id1, id2):
    user_data[id1]["state"] = "connected"
    user_data[id1]["partner"] = id2
    user_data[id2]["state"] = "connected"
    user_data[id2]["partner"] = id1

    waiting_room["state"] = "empty"
    waiting_room["id"] = ""

    send_text(id1, reply["timban-empty-empty"])
    send_text(id2, reply["timban-empty-empty"])


def ketthuc(id):
    if user_data[id]["state"] == "connected":
        disconnect(id)
    elif user_data[id]["state"] == "waiting":
        user_data[id]["state"] = "empty"
        waiting_room["id"] = ""
        waiting_room["state"] = "empty"
        send_text(id, reply["ketthuc-waiting"])
    elif user_data[id]["state"] == "empty":
        send_buttons(id, reply["ketthuc-empty"], [buttons["timban"]])


def disconnect(id):
    partner_id = user_data[id]["partner"]

    user_data[id]["state"] = "empty"
    user_data[id]["partner"] = "empty"
    user_data[partner_id]["state"] = "empty"
    user_data[partner_id]["partner"] = "empty"

    send_buttons(id, reply["ketthuc-connected"], [buttons["timban"]])
    send_buttons(partner_id, reply["ketthuc-connected"], [buttons["timban"]])



def report(id):
    if user_data[id]["state"] == "connected":
        partner_id = user_data[id]["partner"]
        timezone = pytz.timezone('Asia/Saigon')
        now = datetime.now(timezone)
        date_time = now.strftime("%d/%m/%Y %H:%M")
        send_report_infor(user_data[id]["user_name"],
                          user_data[partner_id]["user_name"], date_time, id)


def send_report_infor(user_report, user_reported, data, id):
    global count

    if count == 1:
        infor = [["Người báo cáo", "Người bị báo cáo", "Thời gian"]]
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="test!A1", valueInputOption="USER_ENTERED",
                                        body={"values": infor}).execute()
    count = count + 1

    pos = "test!A" + str(count)
    infor = [[user_report, user_reported, data]]

    # print("----------------------------")
    # print(infor)
    # print(count)
    # print(pos)
    # print("----------------------------")
    send_buttons(id, reply["report-connected"], [buttons["ketthuc"]])

    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=pos, valueInputOption="USER_ENTERED",
                                    body={"values": infor}).execute()


def is_user_message(event):
    """Check if the message is a message from the user"""
    if "message" in event:
        if not event["message"].get("is_echo"):
            if "attachments" in event["message"] or "text" in event["message"]:
                return 1

    return 0


def get_message(event):
    if "attachments" in event["message"]:
        message_type = event["message"]['attachments'][0]["type"]
        message_data = event["message"]['attachments'][0]["payload"]["url"]

    elif "text" in event["message"]:
        message_type = "text"
        message_data = event["message"]["text"]

    return message_type, message_data


def send_to_partner(id, message_data, message_type):
    if user_data[id]["state"] == "connected":
        if message_type == "text":
            send_text(user_data[id]["partner"], message_data)
        else:
            send_attachment(user_data[id]["partner"],
                            message_data, message_type)
    elif user_data[id]["state"] == "waiting":
        send_text(id, reply["send_to_partner-waiting"])
    else: send_buttons(id, reply["send_to_partner-empty"], [buttons["timban"]])


def is_seen(event):
    return (event.get('read'))


def create_user(id):
    load_data()
    if id not in user_data:
        profile_URL = "https://graph.facebook.com/%s?fields=name&access_token=%s" % (
            id, PAGE_ACCESS_TOKEN)
        response = requests.get(profile_URL)

        print(response.json())

        user_data[id] = {}
        user_data[id]["user_name"] = response.json()["name"]
        user_data[id]["state"] = "empty"
        user_data[id]["partner"] = "empty"

        print(user_data)
    save_data()


def load_data():
    global user_data
    global waiting_room
    global count
    data = open('data.json',)

    data = json.load(data)

    user_data = data["user_data"]
    waiting_room = data["waiting_room"]
    count = data["count"]


def save_data():
    global data

    data["waiting_room"] = waiting_room
    data["user_data"] = user_data
    data["count"] = count
    with open('data.json', 'w') as fp:
        json.dump(data, fp, indent=4)


@app.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == "GET":
        return verify_webhook(request)

    if request.method == 'POST':
        load_data()
        payload = request.json
        event = payload['entry'][0]['messaging']
        #print(event)
        for current_event in event:
            print(current_event)

            if is_command(current_event):
                sender_id = current_event['sender']['id']
                send_action(sender_id, "typing_on")
                command = current_event["postback"]["payload"]
                process_command(sender_id, command)

            elif is_user_message(current_event):
                sender_id = current_event['sender']['id']
                message_type, message_data = get_message(current_event)
                send_to_partner(sender_id, message_data, message_type)

            if is_seen(current_event):
                sender_id = current_event['sender']['id']
                if sender_id in user_data and user_data[sender_id]["state"] == "connected":
                    send_action(user_data[sender_id]["partner"], "mark_seen")

        save_data()

        #return jsonify(result={"status": 200})

    return "ok"

@app.route("/", methods=['GET'])
def main():
    return data


if __name__ == "__main__":
    app.run(threaded=True, port=5000)