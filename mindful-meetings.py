# Interfaces with G Suite to manage a meeting's room resource.

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

import datetime

scopes = ['https://www.googleapis.com/auth/admin.directory.resource.calendar','https://www.googleapis.com/auth/calendar']

credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/eugene.kim/.credentials/mindful_meetings_private_key.json', scopes=scopes)

delegated_credentials = credentials.create_delegated('ekim@kenzyworld.com')

http_auth = delegated_credentials.authorize(Http())

cal = build('calendar', 'v3', http=http_auth)

now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

eventsResult = cal.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()

print eventsResult
