from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Add these constants near the top of your file
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service-account.json'  # Path to your service account key file

# Add this function to handle Google Calendar authentication
def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

def new_calendar_event(event_data):
    # Extract event details from form data
    event = {
        'summary': event_data.get('summary', 'New Event'),
        'location': event_data.get('location', ''),
        'description': event_data.get('description', ''),
        'start': {
            'dateTime': event_data.get('start_time'),
            'timeZone': event_data.get('timezone', 'UTC'),
        },
        'end': {
            'dateTime': event_data.get('end_time'),
            'timeZone': event_data.get('timezone', 'UTC'),
        },
    }

    try:
        service = get_calendar_service()
        event_result = service.events().insert(calendarId='calendar@group.calendar.google.com', body=event).execute()
        return {"message": "Event created", "event_id": event_result['id']}
    except Exception as e:
        return {"error": str(e)}
