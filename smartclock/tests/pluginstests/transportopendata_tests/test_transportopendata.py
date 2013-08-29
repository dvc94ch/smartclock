from datetime import datetime, date, time

from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class TransportOpendataPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Transport Opendata Plugin'
    }

    def test_get_departure_time(self):
        arrival_time = datetime.combine(date.today(), time(hour=9))
        departure_time = datetime.combine(
            date.today(), time(hour=7, minute=38))

        result = self.plugin.get_departure_time(
            travel_mode='TRANSIT', origin='Reiden', destination='Ballwil',
            arrival_time=arrival_time)

        self.assertEquals(result, departure_time)
