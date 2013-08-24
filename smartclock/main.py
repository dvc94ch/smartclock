#!/usr/bin/python
import logging
import os
import site
import sys
import time
from datetime import datetime, timedelta

from apscheduler.scheduler import Scheduler


try:
    import smartclock
except ImportError:  # pragma: no cover
    # Add smartclock package to sys.path if it isn't already.
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
else:  # pragma: no cover
    del smartclock


try:
    from daemon import runner  # pylint: disable-msg=import-error
except ImportError:  # pragma: no cover
    start_daemon = False
else:  # pragma: no cover
    start_daemon = True


def get_log_conf_files():
    if os.name == 'nt':
        return '.log', 'plugins.conf'
    return '/var/log/smartclock.log', '/etc/smartclock.conf'


def get_plugin_places():
    plugins = os.path.join(site.getsitepackages()[0], 'smartclock', 'plugins')
    if os.path.exists(plugins):
        return plugins
    return 'plugins'


def configure_logger(logfile, loglevel=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    filehandler = logging.FileHandler(logfile)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return filehandler


logfile, conffile = get_log_conf_files()


from smartclock.plugins.pluginlib import Event
from smartclock.plugins.pluginmanager import PluginManager
from smartclock.hardware.bedsensor import Bedsensor
from smartclock.hardware.lcd import LCD


class SmartClock(object):

    # pylint: disable=too-many-instance-attributes

    def __init__(self, debug=False):
        """Prepare daemon runner."""

        # set settings for daemon runner
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/var/log/smartclock_stderr.log'
        self.pidfile_path = '/var/run/smartclock.pid'
        self.pidfile_timeout = 5

        self.debug = debug

        if self.debug:
            logging.getLogger(__name__).info(
                "Running smartclock in test mode.")

    def setup(self):  # pragma: no cover
        """Loads plugins and settings, initializes the Bedsensor and LCD and
        schedules event checking.
        """

        self.manager = PluginManager(conffile, [get_plugin_places()])

        self.bedsensor = Bedsensor()
        self.bedsensor.add_callback(self.bedsensor_changed)

        for plugin in self.manager.get_plugins("bedsensor"):
            self.bedsensor.add_callback(plugin.bedsensor_changed)

        self.lcd = LCD()

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

        for plugin in self.manager.get_plugins("eventcollector"):
            for event in plugin.collect():
                yield event

    def process_event(self, event):
        """Passes an Event through every eventprocessor plugin to make
        modifications.
        """

        for plugin in self.manager.get_plugins("eventprocessor"):
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
        for plugin in self.manager.get_plugins("alarm"):
            plugin.begin(event)

        if self.bedsensor.read() == Bedsensor.PRESSED:
            self.play_alarms()

    def play_alarms(self):
        logging.info("Bedsensor is pressed, playing alarms.")
        for plugin in self.manager.get_plugins("alarm"):
            plugin.play()

    def pause_alarms(self):
        logging.info("Bedsensor is released, pausing alarms.")
        for plugin in self.manager.get_plugins("alarm"):
            plugin.pause()

    def end_alarms(self):
        logging.info("Ending alarms.")
        for plugin in self.manager.get_plugins("alarm"):
            plugin.end()

    def interval_alarms(self):
        for plugin in self.manager.get_plugins("alarm"):
            plugin.interval()

    def display(self):  # pragma: no cover
        line_1 = self.get_text("Display Notification Plugin")

        if line_1 is None:
            line_1 = self.get_text("Time Plugin")

        line_2 = "%s %s" % (
            self.get_text("Date Plugin"), self.get_text("Weather Plugin"))

        self.lcd.set_text(line_1, line_2)
        self.lcd.display()

        backlight_value = True
        for plugin in self.manager.get_plugins("display"):
            backlight = plugin.backlight()
            if backlight is not None:
                backlight_value = backlight
        self.lcd.backlight(backlight_value)

    def get_text(self, plugin_name):  # pragma: no cover
        return self.manager.get_plugin(
            plugin_name, category="display").get_text()

    def run(self):  # pragma: no cover
        self.setup()

        loops = 100
        if self.debug:
            self.test_alarm()
            loops = 10

        logging.getLogger(__name__).info("Running...")

        while True:
            self.interval_alarms()
            # pylint: disable=unused-variable
            for i in xrange(loops):
                self.display()
                time.sleep(0.4)

    def test_alarm(self):  # pragma: no cover
        event = Event(
            name="Some Event", reminder=timedelta(hours=0),
            start_time=datetime.now() + timedelta(seconds=2),
            duration=timedelta(seconds=30))
        self.schedule_alarm(event)
        self.sched.add_date_job(
            self.play_alarms, event.get_alarm_time() + timedelta(seconds=1))


if __name__ == "__main__":  # pragma: no cover
    if start_daemon:
        logfile = configure_logger(logfile)
        clock = SmartClock()
        daemon_runner = runner.DaemonRunner(clock)
        daemon_runner.daemon_context.files_preserve = [logfile.stream]
        daemon_runner.do_action()
    else:
        logfile = configure_logger(logfile, logging.DEBUG)
        clock = SmartClock(debug=True)
        clock.run()
