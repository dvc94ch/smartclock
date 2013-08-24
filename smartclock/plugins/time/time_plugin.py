"""
[Core]
Name = Time Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Returns a locale formatted time.
"""


from datetime import datetime

from smartclock.plugins.pluginlib import IDisplayPlugin


class TimePlugin(IDisplayPlugin):

    default_settings = {
        'format': '!H:!M:!S !Z'
    }

    def activate(self):
        IDisplayPlugin.activate(self)
        self.format = self.settings['format'].replace('!', '%')

    def get_text(self):
        return datetime.now().strftime(self.format)
