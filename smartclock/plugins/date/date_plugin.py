"""
[Core]
Name = Date Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Returns a locale formatted date.
"""


from datetime import datetime

from smartclock.plugins.pluginlib import IDisplayPlugin


class DatePlugin(IDisplayPlugin):

    default_settings = {
        'format': '!a, !d !b !Y'
    }

    def activate(self):
        IDisplayPlugin.activate(self)
        self.format = self.settings['format'].replace('!', '%')

    def get_text(self):
        return datetime.now().strftime(self.format)
