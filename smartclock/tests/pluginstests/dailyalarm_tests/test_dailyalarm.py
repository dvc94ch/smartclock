from datetime import datetime, date, time

from smartclock.plugins.pluginlib import Event
from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class DailyAlarmPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Daily Alarm Plugin',
        'category': 'eventcollector',
        'load_default_settings': True
    }

    def test_collect(self):
        start_time = datetime.combine(date.today(), time(8, 0))
        events = list(self.plugin.collect())

        self.assertTrue(events, "collect should return an event.")

        self.assertEquals(
            events[0], Event(name="Daily Alarm", start_time=start_time),
            "Should return an event with name Daily Alarm and start_time 8:00")
