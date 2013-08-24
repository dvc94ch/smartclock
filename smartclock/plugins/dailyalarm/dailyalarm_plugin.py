"""
[Core]
Name = Daily Alarm Plugin

[Documentation]
Author = David Craven
Version = 0.1
Website = http://www.craven.ch
Description = Allows to manually set alarms. Supports one time and weekday
              reoccuring alarms.
"""

from datetime import datetime, timedelta, date, time

from smartclock.plugins.pluginlib import IEventCollectorPlugin, Event


class DailyAlarmPlugin(IEventCollectorPlugin):

    default_settings = {
        "alarms": [{
            "enabled": True,
            "weekdays": [0, 1, 2, 3, 4, 5, 6],
            "time": (7, 0)
        }]
    }

    def collect(self):
        for alarm in self.settings['alarms']:
            if alarm['enabled'] and date.today().weekday() in alarm['weekdays']:  # pylint: disable=line-too-long
                start_time = datetime.combine(
                    date.today(), time(alarm['time'][0], alarm['time'][1]))
                yield Event(name="Daily Alarm", start_time=start_time,
                            reminder=timedelta(seconds=0))
