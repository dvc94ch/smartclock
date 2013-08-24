"""
[Core]
Name = Display Notification Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Flashes the LCD backlight and displays an upcomming alarm.
"""

import logging

from smartclock.plugins.pluginlib import (
    IConfigurablePlugin, IAlarmPlugin, IDisplayPlugin)


class DisplayNotification(IAlarmPlugin, IDisplayPlugin):
    """This Alarm starts flashing the LCD and displays the name of the
    Event.
    """

    default_settings = {
        'flash_backlight': True
    }

    def activate(self):
        IConfigurablePlugin.activate(self)
        self.flash = True

    def _play(self):
        pass

    def _pause(self):
        pass

    def _interval(self):
        pass

    def get_text(self):
        if self.status and self.playing:
            return "Alarm for %s" % self.event.name

    def backlight(self):
        if self.status and self.playing and self.settings['flash_backlight']:
            self.flash = not self.flash
            logging.getLogger(__name__).info("Flashing backlight.")
            return self.flash
