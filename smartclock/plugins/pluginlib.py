import ast
import logging
from datetime import timedelta

from yapsy.IPlugin import IPlugin

from smartclock.hardware.bedsensor import Bedsensor


class IConfigurablePlugin(IPlugin):
    """Manages settings for plugins."""

    # pylint: disable=no-member

    # settings will be saved to file on exit and restored on start.
    settings = {}

    # Override default_settings in your plugin.
    default_settings = {}

    def activate(self):
        IPlugin.activate(self)
        self._load_settings()

    def _load_settings(self):
        """Restores settings dict from conf file or loads default_settings
        and saves them to conf file so that the user can customize.
        """

        if self.hasConfigOption("settings"):
            try:
                self.settings = ast.literal_eval(
                    self.getConfigOption("settings"))
            except Exception as e:
                logging.getLogger(__name__).error(
                    "Failed to load settings: %s" % e)
        else:
            logging.getLogger(__name__).info("Using default settings.")
            self.settings = self.default_settings
            self._save_settings()

    def _save_settings(self):
        """Writes settings dict to conf file if it's not empty."""

        if self.settings:
            self.setConfigOption("settings", str(self.settings))
            logging.getLogger(__name__).info("Saved settings.")


class IEventCollectorPlugin(IConfigurablePlugin):
    """Base class for all Event Collection type plugins."""

    def collect(self):
        """Returns a list of Events from today."""

        raise NotImplementedError()  # pragma: no cover


class IEventProcessorPlugin(IConfigurablePlugin):
    """Base class for all Event Processing type plugins."""

    def process(self, event):
        """Is used for modifying events."""

        raise NotImplementedError()  # pragma: no cover


class ITravelTimePlugin(IConfigurablePlugin):
    """Base class for travel_time/departure_time calculators."""

    def get_departure_time(self, travel_mode, arrival_time, origin,
                           destination):
        """Calculates the departure_time. Returns datetime or None."""

        raise NotImplementedError()  # pragma: no cover

    def get_travel_modes(self):
        """Returns a list of travelmodes this plugin supports. Possible
        travelmodes are TRANSIT, DRIVING, BICYCLING, WALKING.
        """

        return ['TRANSIT', 'DRIVING', 'BICYCLING', 'WALKING']


class IAlarmPlugin(IConfigurablePlugin):
    """Use this class to implement an Alarm. Implement _play(), _pause(),
    _interval(). The purpose of play() and pause() is to prevent people from
    getting out of bed to turn the alarm off and then go back to sleep so
    their task is to mute and unmute the alarm. begin() and end() are
    responsable for turning the alarm on and off.

    _play() gets called if the bedsensor is pressed at event.alarm_time
    or gets pressed between event.alarm_time and event.end_time.

    _pause() gets called when the bedsensor is released between
    event.alarm_time and event.end_time.

    _interval() gets called every 30 seconds while status and playing
    equal True. It's purpose is to do tasks like fade wake up music volume
    or small electric shocks to get the subject out of bed.
    """

    def __init__(self):
        """Initializes alarm state."""

        IConfigurablePlugin.__init__(self)
        self.status = False
        self.playing = False
        self.event = None

    def begin(self, event):
        """This function gets called at event.alarm_time."""

        self.status = True
        self.event = event
        logging.getLogger(__name__).info(
            "Alarm for %s has started." % self.event.name)

    def play(self):
        """This function gets called when the bedsensor gets pressed of after
        begin() gets called if the bedsensor is pressed."""

        if self.status:
            self.playing = True
            self._play()

    def _play(self):
        raise NotImplementedError()  # pragma: no cover

    def interval(self):
        """This function gets called every 30 seconds while self.playing
        equals True.
        """

        if self.status and self.playing:
            self._interval()

    def _interval(self):
        raise NotImplementedError()  # pragma: no cover

    def pause(self):
        """This function gets called when the bedsensor is released.
        """

        self.playing = False
        self._pause()

    def _pause(self):
        raise NotImplementedError()

    def end(self):
        """This function gets called at event.end_time."""

        if self.playing:
            self.pause()

        self.status = False
        logging.getLogger(__name__).info(
            "Alarm for %s has ended." % self.event.name)


class IDisplayPlugin(IConfigurablePlugin):
    """Use this baseclass to display text when the display gets refreshed or
    to switch the backlight on/off.
    """

    def get_text(self):
        """Returns the text to be displayed on lcd. Returns None if there is
        nothing to be displayed."""

        raise NotImplementedError()  # pragma: no cover

    def backlight(self):
        """Asks the plugin for an opinion on the backlight status. Can return
        None, True, False.
        """

        return None  # pragma: no cover


class IBedsensorPlugin(IConfigurablePlugin):
    """Use this baseclass to respond to bedsensor state changes."""

    PRESSED = Bedsensor.PRESSED
    RELEASED = Bedsensor.RELEASED

    def bedsensor_changed(self, state):
        """Gets called when some one gets in or out of bed."""

        raise NotImplementedError()  # pragma: no cover


class PluginMasterMixin(object):
    pass


class ComparableMixin(object):
    """Mixin to simplify classes that need comparison operators."""

    def _compare(self, other, method):
        try:
            # pylint: disable=protected-access
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):  # pragma: no cover
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)


class Event(ComparableMixin):
    """Holds the relevant information for an event."""

    # pylint: disable=too-many-arguments
    def __init__(self, name, start_time, duration=timedelta(hours=1),
                 reminder=timedelta(hours=1), location=None):
        """The location will determine the travel_time, the duration will
        determine the end_time. The start_time, travel_time and reminder an
        will be used to determine the alarm_time.
        """

        if not isinstance(reminder, timedelta):  # pragma: no cover
            raise TypeError("reminder must be instance of timedelta.")

        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.end_time = start_time + duration
        self.reminder = reminder
        self.location = location
        self.departure_time = start_time

    def get_alarm_time(self):
        """Calculates the alarm_time based on departure_time and
        reminder that defaults to 1 hour.
        """

        return self.departure_time - self.reminder

    def _cmpkey(self):
        """Returns the alarm_time. Is used to compare and sort Events."""

        return self.get_alarm_time()

    def __str__(self):
        return ("name: %s, start_time: %s, departure_time: %s, reminder: %s, "
                "alarm_time: %s" % (self.name, self.start_time,
                                    self.departure_time, self.reminder,
                                    self.get_alarm_time()))
