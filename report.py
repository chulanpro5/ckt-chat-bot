from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import date, datetime

	

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'key.json'
credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# If modifying these scopes, delete the file token.json.

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1461y4vKxSoPwaDV6wUuLAqObNXwEWZ3Hmq27pKywbt0'
 
service = build('sheets', 'v4', credentials=credentials)

count = 0
sheet = service.spreadsheets()

# Call the Sheets API
def send_report_infor(user_report, user_reported, data):
        global count

        if count == 0:
                infor = [["Người báo cáo", "Người bị báo cáo","Thời gian"]]
                request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range = "test!A1", valueInputOption = "USER_ENTERED",
                                        body = {"values": infor}).execute()
        count = count + 1
        

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M")
        print(date_time)

        infor = [user_report, user_reported, data]
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range = "test!A%s"%(count), valueInputOption = "USER_ENTERED",
                                body = {"values": infor}).execute()
        

