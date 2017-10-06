# Interfaces with G Suite to manage a meeting's room resource.

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

import os
import pprint
import iso8601
import time
import datetime

pp = pprint.PrettyPrinter(indent=4)


roomEmail = "kenzyworld.com_3837373936323438313637@resource.calendar.google.com"
apiScopes = ['https://www.googleapis.com/auth/admin.directory.resource.calendar','https://www.googleapis.com/auth/calendar']

# Sleep times are in seconds

# Time to sleep if there isn't a meeting going on right now.
noMeetingSleepLength = 10

# Amount of time to give people who are in the previous meeting to leave the room.
meetingStartedSleepLength = 1

# Amount of time give people from the previous room to leave the room.
noMotionSleepLength = 1

def getCalendarService():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ["G_APPS_PRIVATE_KEY_PATH"], scopes=apiScopes)
  delegated_credentials = credentials.create_delegated('ekim@kenzyworld.com')
  http_auth = delegated_credentials.authorize(Http())
  calendar = build('calendar', 'v3', http=http_auth)

  print 'Retrieving the Calendar API Object.\n'

  return calendar

# Returns all the meetings that meet under a resource for the current day
def getTodaysRoomMeetings(roomEmail, calendarService):
  meetings = calendarService.events().list(calendarId=roomEmail, alwaysIncludeEmail=True).execute()['items']

  return filter(filterMeetingFromToday, meetings)

# Returns true if the meeting met today.
def filterMeetingFromToday(meeting):
  now = datetime.datetime.now()
  meetingStartDateTimeString = meeting['start']['dateTime']
  meetingStartDateTime = getDatetimeFromDatetimeString(meetingStartDateTimeString)

  return (
    now.year == meetingStartDateTime.year and
    now.month == meetingStartDateTime.month and
    now.day == meetingStartDateTime.day
  )

# Converts a Datetime string in RFC3339 format to a datetime object.
def getDatetimeFromDatetimeString(datetimeString):
  return iso8601.parse_date(datetimeString)

def removeRoomFromMeeting(roomEmail, meeting, calendarService):
  pp.pprint(meeting)

  try:
    calendarService.events().delete(calendarId=roomEmail, eventId=meeting['id']).execute()
  except Exception, e:
    print e

def getCurrentMeeting(meetings):
  now = datetime.datetime.now()
  hour = now.hour
  minute = now.minute

  for meeting in meetings:
    meetingStartDateTimeString = meeting['start']['dateTime']
    meetingStartDatetime = getDatetimeFromDatetimeString(meetingStartDateTimeString)

    if (meetingStartDatetime.hour == hour and meetingStartDatetime.minute == minute):
      return meeting

  return None

def wasMotionDetected():
  return False

def start():
  calendarService = getCalendarService()
  meetings = getTodaysRoomMeetings(roomEmail, calendarService)

  while True:
    print 'Checking if a meeting is started now.'

    # TODO: Make this smarter...
    currentMeeting = getCurrentMeeting(meetings)

    # A meeting is starting now
    if currentMeeting is not None:
      currentMeeting = getCurrentMeeting(meetings)

      try:
        print "Scheduled meeting \"{0}\" is starting now.".format(currentMeeting['summary'])
      except KeyError, e:
        print "Scheduled meeting is starting now."

      print "Waiting {0} seconds for the room to clear of previous inhabitants.".format(meetingStartedSleepLength)
      time.sleep(meetingStartedSleepLength)

      if (wasMotionDetected()):
        print 'Human presence has been detected in the meeting room. Thank you for being mindful.'
      else:
        loopCount = 1
        while (wasMotionDetected() is False):
          organizer = currentMeeting['organizer']
          organizerEmail = organizer['email']

          if (loopCount == 4):
            print('No motion detected and maximum time reached. Freeing up the room for others to reserve.')

            removeRoomFromMeeting(roomEmail, currentMeeting, calendarService)
            break
          else:
            print('No motion detected. Sending reminder email #{0} to {1}.\nSleeping for {2} seconds.'.format(loopCount, organizerEmail, noMotionSleepLength))
            # Send email

            loopCount += 1

    else:
      print 'No meeting is starting now. Sleeping for {0} seconds.'.format(noMeetingSleepLength)

      time.sleep(noMeetingSleepLength)


start()
