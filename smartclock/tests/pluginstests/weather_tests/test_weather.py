from datetime import datetime

from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class WeatherPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Weather Plugin',
        'category': 'display'
    }

    def test_update_cache(self):
        if self.plugin.cache is None:
            self.plugin.update_cache()
        self.assertIsNot(
            self.plugin.cache, None, "Weather cache wasn't updated.")
        self.assertIsInstance(
            self.plugin.cache_time, datetime,
            "Cache time stamp cache_time isn't set.")

    def test_get_text(self):
        weather = self.plugin.get_text()
        self.assertIsInstance(
            weather, str, "get_text() must return a string.")
