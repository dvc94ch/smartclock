"""
[Core]
Name = Transport Opendata Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Transport Opendata Plugin
"""


import logging
from datetime import datetime

from smartclock.plugins.pluginlib import ITravelTimePlugin
from smartclock.plugins.transportopendata.transportopendata import TransportOpendata  # pylint: disable=line-too-long


class TransportOpendataPlugin(ITravelTimePlugin):

    def activate(self):
        ITravelTimePlugin.activate(self)
        self.opendata = TransportOpendata()

    def get_travel_modes(self):
        return ['TRANSIT']

    def get_departure_time(self, travel_mode, arrival_time,
                           origin, destination):
        try:
            station_origin = self.opendata.get_locations(query=origin)[0].uid
            station_dst = self.opendata.get_locations(query=destination)[0].uid
            departure_time = self.opendata.get_connections(
                origin=station_origin, destination=station_dst, limit=1,
                date=arrival_time.date(), time=arrival_time.time(),
                isArrivalTime=True)['connections'][0]['from']['departure']
            return datetime.strptime(departure_time[:-5], "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            logging.getLogger(__name__).info(e)
