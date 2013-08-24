"""
[Core]
Name = Google Maps Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Google Maps Plugin
"""


import logging
from datetime import timedelta

from smartclock.plugins.pluginlib import ITravelTimePlugin
from smartclock.plugins.googlemaps.googlemaps import (
    GoogleMaps, GoogleMapsError)


class GoogleMapsPlugin(ITravelTimePlugin):

    def activate(self):
        ITravelTimePlugin.activate(self)
        self.maps = GoogleMaps("AIzaSyB35q09EmgCRKixpKxIyzDZWeIZmJV8noQ")

    def get_travel_modes(self):
        # deprecated google maps api v2 only supports driving directions.
        return ['DRIVING', 'WALKING']

    def get_departure_time(self, travel_mode, arrival_time,
                           origin, destination):
        try:
            dirs = self.maps.directions(
                origin, destination,
                **{'travelMode': travel_mode})
        except GoogleMapsError as e:  # pragma: no cover
            logging.getLogger(__name__).error(str(e))
        else:
            return arrival_time - timedelta(
                seconds=dirs['Directions']['Duration']['seconds'])
