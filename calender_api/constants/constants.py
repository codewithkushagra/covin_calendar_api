from django.conf import settings


# Constants for Google OAuth2
GOOGLE_AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v1/userinfo'
GOOGLE_CALENDAR_ENDPOINT = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'

CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = "http://127.0.0.1:8000/rest/v1/calendar/redirect"