"""
[Core]
Name = Weather Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Returns the weather report.
"""


import logging
import string
from datetime import datetime, timedelta

from smartclock.plugins.pluginlib import IDisplayPlugin
from smartclock.plugins.weather import pywapi


class WeatherPlugin(IDisplayPlugin):

    default_settings = {
        'location_name': u'Emmenbr\xf5cke',
        'location_id': 'SZXX0011'
    }

    def activate(self):
        IDisplayPlugin.activate(self)
        self.cache = None
        self.cache_time = None

    def update_cache(self):
        logging.getLogger(__name__).info("Updating weather cache from yahoo.")
        self.cache = pywapi.get_weather_from_yahoo(
            self.settings['location_id'])
        self.cache_time = datetime.now()

    def get_text(self):
        if self.cache is None or (self.cache_time +
                                  timedelta(hours=1) < datetime.now()):
            self.update_cache()

        try:
            condition = string.lower(self.cache['condition']['text'])
            temp = self.cache['condition']['temp']
        except KeyError:  # pragma: no cover
            logging.getLogger(__name__).info(
                "Error while updating weather cache.")
            self.cache = None
            condition = "Unknown"
            temp = "-"

        return (u"%s and %s\xdfC now in %s." % (
            condition, temp, self.settings['location_name'])).encode('latin-1')
