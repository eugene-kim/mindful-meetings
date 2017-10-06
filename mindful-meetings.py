# Interfaces with G Suite to manage a meeting's room resource.

from gpiozero import MotionSensor
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

import os
import pprint
import iso8601
import time
import datetime
import config
import mindfulmail

pp = pprint.PrettyPrinter(indent=4)

def getCalendarService():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ["G_APPS_PRIVATE_KEY_PATH"], scopes=config.api_scopes)
  delegated_credentials = credentials.create_delegated(config.impersonated_user_email)
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
  pir = MotionSensor(config.gpio_pin)
  
  calendarService = getCalendarService()
  meetings = getTodaysRoomMeetings(config.room_email, calendarService)

  while True:

    # TODO: Make this smarter...
    currentMeeting = getCurrentMeeting(meetings)

    # A meeting is starting now
    if currentMeeting is not None:
      currentMeeting = getCurrentMeeting(meetings)

      try:
        print "Scheduled meeting \"{0}\" is starting now.\n".format(currentMeeting['summary'])
      except KeyError, e:
        print "Scheduled meeting is starting now.\n"

      # Wait for the stragglers to leave.
      print "Waiting {0} seconds for the room to clear of previous inhabitants.\n".format(config.meeting_started_sleep_length)
      time.sleep(config.meeting_started_sleep_length)

      startTime = time.time()
      
      while True: 
        if pir.motion_detected:
          startTime = time.time()

          print '---------------------------------------------------------------------------------'
          print 'Human presence has been detected in the meeting room. Thank you for being mindful.'
          print '---------------------------------------------------------------------------------'
          
          break
        else:
          organizer = currentMeeting['organizer']
          organizerEmail = organizer['email']
          endTime = time.time()
          totaltime = endTime-startTime

          if int(totaltime) == 50:
            print('No motion detected and maximum time reached. Freeing up the room for others to reserve.')
            removeRoomFromMeeting(config.room_email, currentMeeting, calendarService)
            mindfulmail.emailuser(organizerEmail, 15)
            time.sleep(.5)
            break
          if int(totaltime) == 30:
            print('No motion detected. Sending reminder email #2 to {0}.\n'.format(
              organizerEmail
            ))
            mindfulmail.emailuser(organizerEmail, 10)
            time.sleep(.5)
          if int(totaltime) == 10:
            print('No motion detected. Sending reminder email #1 to {0}.\n'.format(
              organizerEmail
            ))
            mindfulmail.emailuser(organizerEmail, 5)
            time.sleep(.5)
    else:
      print 'No meeting is starting now. Sleeping for {0} seconds.\n'.format(config.no_meeting_timeout)
      time.sleep(config.no_meeting_timeout)

      meetings = getTodaysRoomMeetings(config.room_email, calendarService)

start()
