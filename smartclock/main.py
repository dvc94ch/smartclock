#!/usr/bin/python
import logging
import os
import site
import sys
import time


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


from smartclock.plugins.pluginmanager import PluginManager
from smartclock.plugins.alarmmanager import AlarmManager
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
        schedules event checking. Setup is delayed from __init__ so that
        deamonization has completed before setup.
        """

        self.bedsensor = Bedsensor()
        self.lcd = LCD()

        self.manager = PluginManager(conffile, [get_plugin_places()])
        self.alarm_manager = AlarmManager(
            self.manager.get_plugins, self.bedsensor.read)

        # add callbacks for bedsensor_changed
        self.bedsensor.add_callback(self.alarm_manager.bedsensor_changed)
        for plugin in self.manager.get_plugins("bedsensor"):
            self.bedsensor.add_callback(plugin.bedsensor_changed)

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

        if self.debug:
            self.alarm_manager.test_alarm()
            loops = 10
        else:
            loops = 100

        logging.getLogger(__name__).info("Running...")

        while True:
            self.alarm_manager.interval_alarms()
            # pylint: disable=unused-variable
            for i in xrange(loops):
                self.display()
                time.sleep(0.4)


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
