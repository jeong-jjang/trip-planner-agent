# ───── [1] Google Calendar API ────────────────────────────────────────────────
# service_account_calendar.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from langchain.tools import tool
from typing import List, Dict
import datetime

import os
from dotenv import load_dotenv

# 상대 경로로 .env 불러오기
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

CAL_ID = os.getenv("CAL_ID")
KEY_FILE = os.getenv("GOOGLE_KEY_FILE", "app/service/google_service_account.json")

SCOPES   = ['https://www.googleapis.com/auth/calendar']

@tool
def create_event(calendar_id: str, summary: str,
                 start_dt: str, end_dt: str,
                 description: str = None, location: str = None) -> dict:
    """
    구글 캘린더에 이벤트를 생성합니다.
    - calendar_id: 공유한 캘린더 이메일.
    - summary: 일정 제목
    - start_dt, end_dt: 시작 및 종료 시간 (datetime 객체가 아닌 ISO 문자열)
    - description: 일정 설명
    - location: 일정 장소
    """
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    service   = build('calendar','v3',credentials=creds)
    event = {
      'summary': summary,
      'location': location,
      'description': description,
      'start':   {'dateTime': start_dt, 'timeZone':'Asia/Seoul'},
      'end':     {'dateTime': end_dt,   'timeZone':'Asia/Seoul'},
    }
    # print(f"Creating event: {event}")
    if not calendar_id:
        calendar_id = CAL_ID
    # print(f"Using calendar ID: {calendar_id}")  

    return service.events().insert(calendarId=calendar_id, body=event).execute()


@tool
def create_multiple_events(events: List[Dict]) -> str:
    """
    여러 개의 일정을 Google Calendar에 한 번에 생성합니다.

    각 이벤트는 다음 필드를 포함해야 합니다:
    - summary: 일정 제목
    - start_dt: 시작 시간 (datetime 객체가 아닌 ISO 문자열, 예: '2025-06-12T09:00:00+09:00')
    - end_dt: 종료 시간 (datetime 객체가 아닌 ISO 문자열)s
    - description: 일정 설명 (선택)
    - location: 장소 (선택)
    - calendar_id: 캘린더 ID (선택, 없으면 기본값 사용)

    모든 이벤트는 개별적으로 처리되며, 성공/실패 메시지를 하나의 문자열로 반환합니다.
    """

    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    
    results = []
    for i, event in enumerate(events, 1):
        try:
            calendar_id = event.get("calendar_id", CAL_ID)
            print(f"[{i}] Using calendar ID: {calendar_id}")
            body = {
                "summary": event["summary"],
                "start": {"dateTime": event["start_dt"], "timeZone": "Asia/Seoul"},
                "end": {"dateTime": event["end_dt"], "timeZone": "Asia/Seoul"},
                "description": event.get("description"),
                "location": event.get("location"),
            }
            service.events().insert(calendarId=calendar_id, body=body).execute()
            results.append(f"✅ {i}번 일정 등록 완료: {event['summary']}")
        except Exception as e:
            results.append(f"❌ {i}번 일정 등록 실패: {e}")
    return "\n".join(results)


@tool
def list_events(calendar_id: str,
                time_min: str = None,
                time_max: str = None,
                max_results: int = 30) -> list:
    """
    구글 캘린더에 등록된 일정을 조회합니다.
    - calendar_id: 공유한 캘린더 이메일.
    - time_min: 조회 시작 시간 (ISO 8601 형식).
    - time_max: 조회 종료 시간 (ISO 8601 형식).
    - max_results: 최대 조회 개수
    - return: 일정 목록 (JSON 형태)
    """
    print(f"Using calendar ID: {calendar_id}")
    if not calendar_id:
        calendar_id = CAL_ID
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    service   = build('calendar','v3',credentials=creds)
    params = {
      'calendarId': calendar_id,
      'maxResults': max_results,
      'singleEvents': True,
      'orderBy': 'startTime'
    }
    if time_min: params['timeMin'] = time_min
    if time_max: params['timeMax'] = time_max
    return service.events().list(**params).execute().get('items', [])


@tool
def update_event(calendar_id: str, event_id: str, updates: dict) -> dict:
    """
    구글 캘린더에 등록된 일정을 수정합니다.
    - calendar_id: 공유한 캘린더 이메일.
    - event_id: 수정할 일정 ID
    - updates: 수정할 내용 (JSON 형태)
    - return: 수정된 일정 (JSON 형태)

    """
    print(f"Using calendar ID: {calendar_id}")
    if not calendar_id:
        calendar_id = CAL_ID
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    service = build('calendar','v3',credentials=creds)
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event.update(updates)
    return service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()


@tool
def delete_event(calendar_id: str, event_id: str) -> str:
    """
    구글 캘린더에 등록된 일정을 삭제합니다.
    - calendar_id: 공유한 캘린더 이메일.
    - event_id: 삭제할 일정 ID
    - return: 삭제된 일정 ID
    """
    print(f"Using calendar ID: {calendar_id}")
    if not calendar_id:
        calendar_id = CAL_ID
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    service = build('calendar','v3',credentials=creds)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return f"Deleted {event_id}"