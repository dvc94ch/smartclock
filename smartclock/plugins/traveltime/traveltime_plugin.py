"""
[Core]
Name = Travel Time Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Computes the departure time for an event.
"""

from smartclock.plugins.pluginlib import (
    IEventProcessorPlugin, PluginMasterMixin)


class TravelTimePlugin(IEventProcessorPlugin, PluginMasterMixin):
    """If the location of the Event is specified then it will add a
    travel_mode, process the location and calculate the departure_time.
    Starting address is allways home because if you're not home you don't
    hear the alarm anyway.
    """

    default_settings = {
        'default-travelmode': 'TRANSIT',
        'home-address': 'Hauptstrasse 32 6260 Reiden',
        'plugin-mapping': {
            'TRANSIT': 'Transport Opendata Plugin',
            'DRIVING': 'Google Maps Plugin',
            'BICYCLING': None,
            'WALKING': 'Google Maps Plugin'
        }
    }

    def get_travel_plugin(self, travel_mode):
        # pylint: disable=no-member
        try:
            plugin_name = self.settings['plugin-mapping'][travel_mode]
            plugin = self.get_plugin(
                name=plugin_name, category='traveltime')
            if (travel_mode in plugin.get_travel_modes()):
                return plugin
        except Exception:
            return

    def process(self, event):
        if event.location is None:
            return

        travel_mode = self.settings['default-travelmode']
        if 'TRANSIT' in event.location:
            travel_mode = 'TRANSIT'
        elif 'DRIVING' in event.location:
            travel_mode = 'DRIVING'
        elif 'BICYCLING' in event.location:
            travel_mode = 'BICYCLING'
        elif 'WALKING' in event.location:
            travel_mode = 'WALKING'

        event.location = ' '.join(
            event.location.replace(travel_mode, '').split())
        event.travel_mode = travel_mode

        plugin = self.get_travel_plugin(travel_mode)
        if plugin is not None:
            departure_time = plugin.get_departure_time(
                travel_mode=travel_mode, arrival_time=event.start_time,
                origin=self.settings['home-address'],
                destination=event.location)

            if departure_time is not None:
                event.departure_time = departure_time
