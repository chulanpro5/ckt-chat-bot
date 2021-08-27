from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import certifi

connection_url = 'mongodb+srv://nxhieu1302:NjYZbMYvOUtQS7s8@cluster0.ikjyi.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(connection_url, tlsCAFile=certifi.where())

# Database
Database = client.get_database('ckt-chat-bot')
# Table
SampleTable = Database.User_data

sample_data = {
    "waiting_room": {
        "state": "empty",
        "id": ""
    },
    "user_data": {},
    "count": 1
}


def load_data():
    queryObject = {"Type": 'data'}
    query = SampleTable.find_one(queryObject)
    query.pop('_id')
    print(query["Data"])


def insertOne(data):
    queryObject = {
        'Type': 'data',
        'Data': data
    }
    query = SampleTable.insert_one(queryObject)
    return "Query inserted...!!!"

insertOne(sample_data)
