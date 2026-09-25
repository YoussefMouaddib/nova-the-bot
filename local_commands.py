import os.path
import pickle
from datetime import datetime, timedelta
from notion_client import Client
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config

notion = Client(auth=config.NOTION_API_KEY)

def get_calendar_service():
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        with open(config.TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def add_project(data):
    notion.pages.create(
        parent={"database_id": config.NOTION_PROJECTS_DB_ID},
        properties={
            "Project Name": {"title": [{"text": {"content": data["Project Name"]}}]},
            "Tag": {"multi_select": [{"name": tag} for tag in data.get("Tags", [])]},
            "Last Step": {"rich_text": [{"text": {"content": data.get("Last Step", "")}}]},
            "Next Step": {"rich_text": [{"text": {"content": data.get("Next Step", "")}}]},
            "Summary": {"rich_text": [{"text": {"content": data.get("Summary", "")}}]},
            "Status": {"status": {"name": data.get("Status", "Not Started")}}
        }
    )
    print(f"🧠 Project added: {data['Project Name']}")

def schedule_gcal_event(title, start_time_str, duration_minutes=60):
    service = get_calendar_service()
    start_dt = datetime.fromisoformat(start_time_str)
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': config.TIMEZONE},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': config.TIMEZONE},
        'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 0}]}
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"📅 Event created: {event.get('htmlLink')}")

def add_task(data):
    notion.pages.create(
        parent={"database_id": config.NOTION_TASKS_DB_ID},
        properties={
            "Name": {"title": [{"text": {"content": data["Name"]}}]},
            "Done": {"checkbox": data.get("Done", False)}
        }
    )
    print(f"✅ Task added: {data['Name']}")

def check_task(data):
    task_title = data["title"]
    query = notion.databases.query(
        database_id=config.NOTION_TASKS_DB_ID,
        filter={"property": "Name", "title": {"equals": task_title}}
    )
    if query["results"]:
        page_id = query["results"][0]["id"]
        notion.pages.update(page_id=page_id, properties={"Done": {"checkbox": True}})
        print(f"✅ Task checked: {task_title}")
    else:
        print(f"⚠️ Task not found: {task_title}")

def update_project(data):
    proj_name = data["project"]
    new_value = data["value"]
    query = notion.databases.query(
        database_id=config.NOTION_PROJECTS_DB_ID,
        filter={"property": "Project Name", "title": {"equals": proj_name}}
    )
    if query["results"]:
        page_id = query["results"][0]["id"]
        notion.pages.update(
            page_id=page_id,
            properties={"Last Step": {"rich_text": [{"text": {"content": new_value}}]}}
        )
        print(f"✅ Project updated: {proj_name} → Last Step = \"{new_value}\"")
    else:
        print(f"⚠️ Project not found: {proj_name}")