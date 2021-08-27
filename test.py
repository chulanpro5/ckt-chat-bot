import requests
from flask import Flask, request,jsonify, request
from flask_cors import CORS
import json
from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from flask import jsonify
import pytz 
import pymongo
import certifi
import os
import traceback
import time
timezone = pytz.timezone('Asia/Saigon')
time1 = datetime.now(timezone)

time.sleep(70)

time2 = datetime.now(timezone)

time_delta = (time2 - time1)
total_seconds = time_delta.total_seconds()
minutes = total_seconds/60

print(int(minutes))