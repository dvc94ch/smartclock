"""
[Core]
Name = Hue Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = When the bedsensor state changes to occupated, it turns the
              lights off.
"""


import logging

from smartclock.hardware.lightsensor import Lightsensor
from smartclock.plugins.pluginlib import IBedsensorPlugin
from smartclock.plugins.hue.phue import Bridge


class BedsensorHuePlugin(IBedsensorPlugin):

    default_settings = {
        'ip': '192.168.1.57',
        'username': '1b3cbc1e720be71e4cf232137e820b',
        'rcl-threshold': 1500,
        'off-group': 0,
        'on-group': 'Bedroom'
    }

    def activate(self):
        IBedsensorPlugin.activate(self)

        self.bridge = None
        self.lightsensor = Lightsensor()

    def get_brightness(self):  # pragma: no cover
        if self.lightsensor.read() < self.settings['rcl-threshold']:
            return False
        return True

    def bedsensor_changed(self, state):  # pragma: no cover
        logging.getLogger(__name__).info("Hue callback started.")

        if self.bridge is None:
            try:
                self.bridge = Bridge(
                    ip=self.settings['ip'], username=self.settings['username'])
            except Exception as e:
                logging.getLogger(__name__).error(e)
                return

        self.bridge.connect()

        if state == self.PRESSED:
            logging.getLogger(__name__).info("Turning lights off.")
            self.bridge.set_group(self.settings['off-group'], 'on', False)
        elif self.get_brightness():
            logging.getLogger(__name__).info("Turning lights on.")
            self.bridge.set_group(self.settings['on-group'], 'on', True)
