import logging
from datetime import datetime, timedelta

from apscheduler.scheduler import Scheduler

from smartclock.hardware.bedsensor import Bedsensor
from smartclock.plugins.pluginlib import Event


class AlarmManager(object):

    def __init__(self, get_plugins, read_bedsensor):
        self.get_plugins = get_plugins
        self.read_bedsensor = read_bedsensor
        self.sched = Scheduler(daemonic=True)
        self.sched.start()
        self.sched.add_interval_job(self.check_events, hours=1)
        self.check_events()

    def check_events(self):
        """Gets called every hour and after an alarm ended to collect, process
        and schedule the next event.
        """

        logging.getLogger(__name__).info("Checking for events.")

        events = []
        for event in self.collect_events():
            events.append(event)

        if events:
            events.sort()
            now = datetime.now()
            next_event_collection = now + timedelta(hours=1)

            for event in events:

                if event.get_alarm_time() < now:
                    continue

                self.process_event(event)

                if event.get_alarm_time() > next_event_collection:
                    return

                self.schedule_alarm(event)

    def collect_events(self):
        """Collects events from all eventcollector plugins. Returns a list
        of events. Shedules an alarm if it's alarm_time is before the next
        event collection.
        """

        logging.getLogger(__name__).info("Collecting events.")

        for plugin in self.get_plugins("eventcollector"):
            for event in plugin.collect():
                yield event

    def process_event(self, event):
        """Passes an Event through every eventprocessor plugin to make
        modifications.
        """

        for plugin in self.get_plugins("eventprocessor"):
            plugin.process(event)
        return event

    def schedule_alarm(self, event):  # pragma: no cover
        """Shedules an alarm if alarm_time hasn't passed yet."""

        if event.get_alarm_time() > datetime.now():
            alarm_time = event.get_alarm_time()
            logging.info("Sheduling alarm for {0}.".format(alarm_time))
            self.sched.add_date_job(self.begin_alarms, alarm_time, [event])
            self.sched.add_date_job(self.end_alarms, event.end_time)

    def bedsensor_changed(self, state):  # pragma: no cover
        if state == Bedsensor.PRESSED:
            self.play_alarms()
        else:
            self.pause_alarms()

    def begin_alarms(self, event):
        logging.info("Begining alarms.")
        for plugin in self.get_plugins("alarm"):
            plugin.begin(event)

        if self.read_bedsensor() == Bedsensor.PRESSED:
            self.play_alarms()

    def play_alarms(self):
        logging.info("Bedsensor is pressed, playing alarms.")
        for plugin in self.get_plugins("alarm"):
            plugin.play()

    def pause_alarms(self):
        logging.info("Bedsensor is released, pausing alarms.")
        for plugin in self.get_plugins("alarm"):
            plugin.pause()

    def end_alarms(self):
        logging.info("Ending alarms.")
        for plugin in self.get_plugins("alarm"):
            plugin.end()

    def interval_alarms(self):
        for plugin in self.get_plugins("alarm"):
            plugin.interval()

    def test_alarm(self):  # pragma: no cover
        event = Event(
            name="Some Event", reminder=timedelta(hours=0),
            start_time=datetime.now() + timedelta(seconds=2),
            duration=timedelta(seconds=30))
        self.schedule_alarm(event)
        self.sched.add_date_job(
            self.play_alarms, event.get_alarm_time() + timedelta(seconds=1))
