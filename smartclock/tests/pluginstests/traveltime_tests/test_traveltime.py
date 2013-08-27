from datetime import datetime, date, time

from smartclock.plugins.pluginlib import ITravelTimePlugin, Event
from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class TransportOpendataPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Travel Time Plugin',
        'category': 'eventprocessor',
        'load_default_settings': True
    }

    def test_get_travel_plugin(self):
        self.assertIsInstance(
            self.plugin.get_travel_plugin('TRANSIT'), ITravelTimePlugin)

    def test_parse_location_and_travel_mode(self):
        location, travel_mode = self.plugin.parse_location_and_travel_mode(
            'Hauptstrasse 32 DRIVING Reiden 6260')
        self.assertEquals(travel_mode, 'DRIVING')
        self.assertEquals(location, 'Hauptstrasse 32 Reiden 6260')

    def process(self):
        event = Event(
            name="some event", location="Ballwil",
            start_time=datetime.combine(date.today(), time(hour=9)))
        self.plugin.process(event)
        self.assertEqual(event.departure_time, datetime.combine(
            date.today(), time(hour=7, minute=50)))
