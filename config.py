#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration for Mindful Meetings.
"""

# Email for the room resource. This is also the value to use for 'calendarId'
room_email = 'kenzyworld.com_3837373936323438313637@resource.calendar.google.com'

# The APIs we're hitting.
api_scopes = ['https://www.googleapis.com/auth/admin.directory.resource.calendar','https://www.googleapis.com/auth/calendar']

# Sleep times are in seconds.
# Time to sleep if there isn't a meeting going on right now.
no_meeting_timeout = 10

# Amount of time to give people who are in the previous meeting to leave the room.
meeting_started_sleep_length = 10

# GPIO Pin number that output is connected to
gpio_pin = 4

impersonated_user_email = 'ekim@kenzyworld.com'
