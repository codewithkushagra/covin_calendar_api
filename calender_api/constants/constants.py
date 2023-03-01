from django.conf import settings


# Constants for Google OAuth2
GOOGLE_AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v1/userinfo'
GOOGLE_CALENDAR_ENDPOINT = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'


CLIENT_ID = "112358493438-edfr9undt7k89q3k49532nd1k0r04oph.apps.googleusercontent.com"
# CLIENT_ID = "112358493438-q3bvo7skq7toisuolu8qcbda0bvck6qn.apps.googleusercontent.com"
CLIENT_SECRET = "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"
# CLIENT_SECRET = "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"
REDIRECT_URI = "https://api.kushagraagarwal.software/rest/v1/calendar/redirect"
# REDIRECT_URI = "http://127.0.0.1:8000/rest/v1/calendar/redirect"
