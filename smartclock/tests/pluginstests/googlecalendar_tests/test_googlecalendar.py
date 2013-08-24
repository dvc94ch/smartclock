from datetime import datetime, date, timedelta

import gdata

from smartclock.plugins.pluginlib import Event
from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class CalendarPluginTestCase(PluginTestCase):
    """Calendar has to have one and only one entry on 5.3.13

    name: some event
    start_time: 12:00
    end_time: 13:00
    reminders: 45min, 15min
    location: some place
    """

    settings = {
        'name': 'Google Calendar Plugin',
        'category': 'eventcollector',
        'load_default_settings': False
    }

    def test_login(self):
        try:
            self.bad_login()
        except gdata.service.BadAuthentication:
            self.plugin.login()
        else:
            self.fail("Unable to login to google calendar. Try changing "
                      "default username and password.")  # pragma: no cover

    def bad_login(self):
        self.plugin.login(username=self.plugin.settings['username'] + "bad",
                          password=self.plugin.settings['password'])

    def test_collect(self):
        events = list(self.plugin.collect())
        if events:  # pragma: no cover
            self.assertIsInstance(
                events[0], Event, "collect should yield a list of Event.")

    def test_query(self):
        events = []
        feed = self.plugin.query(start_date=date(year=2013, month=3, day=5),
                                 end_date=date(year=2013, month=3, day=6))
        for event in self.plugin.feed_to_events(feed):
            events.append(event)

        self.assertEquals(
            len(events), 1,
            "Must be one and only one calendar event on 5.3.13.")

        self.assertEquals(
            events[0].name, "some event", "Event name must be 'some event'.")

        self.assertEquals(
            events[0].start_time, datetime(year=2013, month=3, day=5, hour=12),
            "Event start_time must be 12:00")

        self.assertEquals(
            events[0].end_time, datetime(year=2013, month=3, day=5, hour=13),
            "Event end_time must be 13:00.")

        self.assertEquals(
            events[0].reminder, timedelta(minutes=45),
            "Event reminder should be 45min.")

        self.assertEquals(
            events[0].location, "some place",
            "Event location should be 'some place'.")
