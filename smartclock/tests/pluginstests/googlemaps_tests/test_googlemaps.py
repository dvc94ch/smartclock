from datetime import datetime, timedelta

from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class MapsPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Google Maps Plugin'
    }

    def test_get_departure_time(self):
        arrival_time = datetime.now()

        departure_time = self.plugin.get_departure_time(
            travel_mode='DRIVING', origin='Reiden', destination='Ballwil',
            arrival_time=arrival_time)

        travel_time = arrival_time - departure_time
        self.assertTrue(
            travel_time > timedelta(minutes=20) and
            travel_time < timedelta(minutes=60), "Event wasn't processed.")
