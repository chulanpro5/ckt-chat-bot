import requests
from flask import Flask, request,jsonify, request
from flask_cors import CORS
import json
from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_acreport_count
from flask import jsonify
import pytz 
import pymongo
import certifi
import os
import traceback

connection_url = str(os.environ.get('CONNECTION_URL','none'))
client = pymongo.MongoClient(connection_url, tlsCAFile=certifi.where())

# Database
Database = client.get_database('ckt-chat-bot')
# Table
mongo_data = Database.User_data


FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = str(os.environ.get('VERIFY_TOKEN','none'))
PAGE_ACCESS_TOKEN = str(os.environ.get('PAGE_ACCESS_TOKEN','none'))

reply = open('reply.json',  encoding="utf8")
reply = json.load(reply)
buttons = open('buttons.json',encoding="utf8")
buttons = json.load(buttons)

data = {}
user_data = {}
waiting_room = {}
report_count = {}
connection_count = {}
error_count = {}


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACreport_count_FILE = 'key.json'
credentials = None
credentials = service_acreport_count.Credentials.from_service_acreport_count_file(
    SERVICE_ACreport_count_FILE, scopes=SCOPES)
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
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if "postback" in event:
        if "payload" in event["postback"]:
            return event["postback"]["payload"]
    else:
        return 0


def process_command(id, command):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if command == "started":
        send_buttons(id, reply["started"], [buttons["rule"], buttons["timban"]])
        #create_user(id)
    if command == "timban":
        timban(id)
    elif command == "ketthuc":
        send_buttons(id, reply["confirm_ketthuc"], [buttons["confirm_ketthuc"]])
    elif command == "confirm_ketthuc":
        ketthuc(id)
    elif command == "report":
        report(id)


def timban(id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if user_data[id]["state"] == "connected":
        send_buttons(id, reply["timban-connected"], [buttons["ketthuc"]])
    elif user_data[id]["state"] == "waiting":
        send_text(id, reply["timban-waiting"])
    elif user_data[id]["state"] == "empty":
        find_partner(id)


def find_partner(id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if waiting_room["state"] == "empty":
        send_text(id, reply["timban-empty"])
        waiting_room["id"] = id
        waiting_room["state"] = "waiting"
        user_data[id]["state"] = "waiting"
    elif waiting_room["state"] == "waiting":
        send_text(id, reply["timban-empty"])
        connect(id, waiting_room["id"])


def connect(id1, id2):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    user_data[id1]["state"] = "connected"
    user_data[id1]["partner"] = id2
    user_data[id2]["state"] = "connected"
    user_data[id2]["partner"] = id1

    waiting_room["state"] = "empty"
    waiting_room["id"] = ""

    send_text(id1, reply["timban-empty-empty"])
    send_text(id2, reply["timban-empty-empty"])


def ketthuc(id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

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
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    partner_id = user_data[id]["partner"]

    user_data[id]["state"] = "empty"
    user_data[id]["partner"] = "empty"
    user_data[partner_id]["state"] = "empty"
    user_data[partner_id]["partner"] = "empty"

    send_buttons(id, reply["ketthuc-connected"], [buttons["phanhoi"], buttons["timban"]])
    send_buttons(partner_id, reply["ketthuc-connected"], [buttons["phanhoi"], buttons["timban"]])



def report(id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if user_data[id]["state"] == "connected":
        partner_id = user_data[id]["partner"]
        timezone = pytz.timezone('Asia/Saigon')
        now = datetime.now(timezone)
        date_time = now.strftime("%d/%m/%Y %H:%M")
        send_report_infor(user_data[id]["user_name"],
                          user_data[partner_id]["user_name"], date_time, id)

    else:
        send_buttons(id, reply["send_to_partner-empty"], [buttons["timban"]])


def send_report_infor(user_report, user_reported, report_data, id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if report_count == 1:
        infor = [["Người báo cáo", "Người bị báo cáo", "Thời gian"]]
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="report!A1", valueInputOption="USER_ENTERED",
                                        body={"values": infor}).execute()
    report_count = report_count + 1

    pos = "report!A" + str(report_count)
    infor = [[user_report, user_reported, report_data]]

    send_buttons(id, reply["report-connected"], [buttons["ketthuc"]])

    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=pos, valueInputOption="USER_ENTERED",
                                    body={"values": infor}).execute()

def send_connections(id1, id2):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if connection_count == 1:
        infor = [["User 1", "User 2", "Thời gian"]]
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="connection_history!A1", valueInputOption="USER_ENTERED",
                                        body={"values": infor}).execute()
    connection_count = connection_count + 1

    timezone = pytz.timezone('Asia/Saigon')
    now = datetime.now(timezone)
    date_time = now.strftime("%d/%m/%Y %H:%M")

    user_1 = user_data[id1]["user_name"]
    user_2 = user_data[id2]["user_name"]

    pos = "connection_history!A" + str(connection_count)
    infor = [[user_1, user_2, date_time]]


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


def get_message_text(event):
    message_type = "empty"
    message_data = "empty"
    if "text" in event["message"]:
        message_type = "text"
        message_data = event["message"]["text"]
    return message_type, message_data

def get_message_attachment(event):
    message_type = "empty"
    message_data = "empty"
    if "attachments" in event["message"]:
        message_type = event["message"]['attachments'][0]["type"]
        message_data = event["message"]['attachments'][0]["payload"]["url"]
        if message_type == "fallback":
            if not "text" in event["message"]:
                message_type = "text"
            else:
                return "empty", "empty"
        elif message_type == "video":
            message_type = "text"

    return message_type, message_data


def send_to_partner(id, message_data, message_type):
    if user_data[id]["state"] == "connected":
        if message_type == "text":
            send_text(user_data[id]["partner"], message_data)
        else:
            send_attachment(user_data[id]["partner"],
                            message_data, message_type)
    elif user_data[id]["state"] == "waiting":
        send_text(id, reply["timban-waiting"])
    else: send_buttons(id, reply["send_to_partner-empty"], [buttons["timban"]])


def is_seen(event):
    return (event.get('read'))

def create_user(id):
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    if id not in user_data:
        profile_URL = "https://graph.facebook.com/%s?fields=name&access_token=%s" % (
            id, PAGE_ACCESS_TOKEN)
        response = requests.get(profile_URL)

        #print(response.json())

        user_data[id] = {}
        user_data[id]["user_name"] = response.json()["name"]
        user_data[id]["state"] = "empty"
        user_data[id]["partner"] = "empty"


def load_data():
    global past_time
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    queryObject = {"Type": 'data'}
    query = mongo_data.find_one(queryObject)
    # print('------------------load-----------------')
    # print(query)
    query.pop('_id')

    data = query["Data"]

    user_data = data['user_data']
    waiting_room = data["waiting_room"]
    report_count = data["report_count"]
    connection_count = data["connection_count"]
    error_count = data["error_count"]


def save_data():
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data

    data["waiting_room"] = waiting_room
    data["user_data"] = user_data
    data["report_count"] = report_count

    # print('------------------save-----------------')
    # print(data)


    queryObject = {'Type': 'data'}
    updateObject = {"Data": data} 
    mongo_data.update_one(queryObject, {'$set': updateObject})

load_data()

app = Flask(__name__)
app.config["DEBUG"] = True

timezone = pytz.timezone('Asia/Saigon')
past_time = datetime.now(timezone)

@app.route("/webhook", methods=['GET', 'POST'])
def listen():
    global user_data
    global waiting_room
    global report_count
    global connection_count
    global error_count
    global data
    global past_time
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == "GET":
        return verify_webhook(request)

    if request.method == 'POST':
        #load_data()
        payload = request.json
        event = payload['entry'][0]['messaging']
        #print('-----------------start--------------------')
        #print(event)
        #print('-----------------end--------------------')

        

        try:
            for current_event in event:
                sender_id = event[0]['sender']['id']
                create_user(sender_id)

                if is_command(current_event):
                    # sender_id = current_event['sender']['id']
                    # create_user(sender_id)

                    send_action(sender_id, "typing_on")
                    command = current_event["postback"]["payload"]
                    process_command(sender_id, command)

                elif is_user_message(current_event):
                    # sender_id = current_event['sender']['id']
                    # create_user(sender_id)

                    message_type, message_data = get_message_text(current_event)
                    if message_type != "empty":
                        send_to_partner(sender_id, message_data, message_type)

                    message_type, message_data = get_message_attachment(current_event)
                    if message_type != "empty":
                        send_to_partner(sender_id, message_data, message_type)

                if is_seen(current_event):
                    # sender_id = current_event['sender']['id']
                    # create_user(sender_id)

                    if sender_id in user_data and user_data[sender_id]["state"] == "connected":
                        send_action(user_data[sender_id]["partner"], "mark_seen")
        except:
            save_data()
            print("!!!!!!!!!!!!!!!!Error!!!!!!!!!!!!!!!!!!!!")
            print('-----------------start--------------------')
            print(event)
            print('-----------------end--------------------')
            traceback.print_exc()
            return "error"

        current_time = datetime.now(timezone)

        time_delta = (current_time - past_time)
        total_seconds = time_delta.total_seconds()
        minutes = total_seconds/60

        if int(minutes) >= 1:
            print("----------------------------Save----------------------") 
            save_data()
            past_time = current_time

    return "ok"

@app.route("/", methods=['GET'])
def main():
    return jsonify(data)


if __name__ == "__main__":
    #app.run(threaded=True, port=5000)
    app.run(threaded=False, processes=1, port = 5000)
