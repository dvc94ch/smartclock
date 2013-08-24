"""
[Core]
Name = Google Calendar Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Google Calendar Plugin
"""


import logging
from datetime import datetime, date, timedelta

from gdata.service import BadAuthentication, NotAuthenticated
from gdata.calendar.service import CalendarService, CalendarEventQuery

from smartclock.plugins.pluginlib import IEventCollectorPlugin, Event


class GoogleCalendarPlugin(IEventCollectorPlugin):

    default_settings = {
        'username': 'user@gmail.com',
        'password': 'password',
        'calendars': ['default']
    }

    def activate(self):
        IEventCollectorPlugin.activate(self)

        self.calendar_service = CalendarService()
        try:
            self.login()
        except Exception:  # pragma: no cover
            self.calendars = None
        else:
            self.calendars = [self.get_calendar_uri(calendar)
                              for calendar in self.settings['calendars']]

    def login(self, username=None, password=None):
        if username is None or password is None:
            username = self.settings['username']
            password = self.settings['password']

        try:
            self.calendar_service.ClientLogin(
                username=username, password=password,
                source='Alarmclock Plugin')
        except BadAuthentication:
            logging.getLogger(__name__).error(
                "Login failed: check username and password.")
            raise
        else:
            logging.getLogger(__name__).info(
                "Logged in to Google Calendar Webservice.")

    def get_calendar_uri(self, name):
        if name == 'default':
            return name

        try:
            feed = self.calendar_service.GetAllCalendarsFeed()
        except Exception as e:  # pragma: no cover
            logging.getLogger(__name__).info("Failed to resolve Calendar URI.")
            logging.getLogger(__name__).error(e)
            return

        # pylint: disable=maybe-no-member
        for calendar in feed.entry:
            if name in calendar.title.text:
                return calendar.content.src.split('/')[5].replace('%40', '@')

    def query(self, start_date, end_date, calendar='default'):
        query = CalendarEventQuery(calendar, 'private', 'full')
        query.start_min = str(start_date)
        query.start_max = str(end_date)

        logging.getLogger(__name__).info(
            "Querying Google Calendar %s." % calendar)

        try:
            return self.calendar_service.CalendarQuery(query)
        except NotAuthenticated:  # pragma: no cover
            try:
                self.login()
            except BadAuthentication:
                pass
            else:
                return self.query(start_date, end_date)

    def feed_to_events(self, feed):
        for event in feed.entry:
            for when in event.when:
                try:
                    start_time = datetime.strptime(
                        when.start_time.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    end_time = datetime.strptime(
                        when.end_time.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                except ValueError:  # pragma: no cover
                    # ValueError happens on parsing error. Parsing errors
                    # usually happen for "all day" events since they have
                    # not time, but we do not care about this events.
                    continue

                event_dict = {
                    'name': event.title.text,
                    'start_time': start_time,
                    'duration': end_time - start_time
                }

                reminders = []

                for reminder in when.reminder:
                    if reminder.method == "alert":
                        reminders.append(
                            timedelta(minutes=int(reminder.minutes)))

                if reminders:
                    reminders.sort()
                    event_dict['reminder'] = reminders[-1]

                for where in event.where:
                    if not where.value_string is None:
                        event_dict['location'] = where.value_string

                yield Event(**event_dict)

    def collect(self):
        if self.calendars is None:  # pragma: no cover
            logging.getLogger(__name__).info(
                "No Calendars to collect events from.")
            return

        for calendar in self.calendars:
            feed = self.query(calendar=calendar, start_date=str(
                date.today()), end_date=str(date.today() + timedelta(days=1)))
            for event in self.feed_to_events(feed):
                yield event
