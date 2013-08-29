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

from smartclock.plugins.pluginlib import ITravelTimePlugin
from smartclock.plugins.transportopendata.transportopendata import TransportOpendata  # pylint: disable=line-too-long


class TransportOpendataPlugin(ITravelTimePlugin):

    def activate(self):
        ITravelTimePlugin.activate(self)
        self.opendata = TransportOpendata()

    def get_travel_modes(self):
        return ['TRANSIT']

    def get_train_stations(self, coordinates):
        lat, lng = coordinates
        for station in self.opendata.get_locations(x=lat, y=lng):
            if not ',' in station.name or 'Bahnhof' in station.name:
                yield station

    def get_nearest_train_station(self, coordinates):
        stations = [
            station for station in self.get_train_stations(coordinates)]
        for station in stations:
            station.distance = self.distance(
                station.get_coordinates(), coordinates)
        logging.getLogger(__name__).debug(stations)
        return sorted(stations, key=lambda station: station.distance)[0]

    def get_departure_time(self, travel_mode, arrival_time,
                           origin, destination):
        try:
            origin = self.geocode(origin)
            destination = self.geocode(destination)

            # get train stations nearest to origin and destination
            station_origin = self.get_nearest_train_station(origin)
            station_dst = self.get_nearest_train_station(destination)

            logging.getLogger(__name__).debug(
                "station origin: %s", station_origin)
            logging.getLogger(__name__).debug(
                "station destination: %s", station_dst)

            # calculate arrival time based on walking time from destination
            # train station to destination
            walking_time = self.calculate_walking_time(
                station_dst.get_coordinates(), destination)
            arrival_time = arrival_time - walking_time

            logging.getLogger(__name__).debug("arrival time: %s", arrival_time)

            # get connection and parse departure time, limit=1 doesn't
            # always return the best connection
            connections = self.opendata.get_connections(
                origin=station_origin.uid, destination=station_dst.uid,
                limit=3, date=arrival_time.date(), time=arrival_time.time(),
                isArrivalTime=True, fields='connections/from/departure')

            # find best connection
            departure_times = [
                self.opendata.strp_datetime(conn['from']['departure'])
                for conn in connections]
            departure_times.sort()

            # walking time to train station from origin is part of the
            # reminder.
            return departure_times[-1]
        except Exception as e:
            logging.getLogger(__name__).error(e)
