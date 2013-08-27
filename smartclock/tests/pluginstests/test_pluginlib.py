from unittest import TestCase
from datetime import datetime, timedelta

from mock import MagicMock

from smartclock.plugins.pluginlib import Event, IAlarmPlugin, ITravelTimePlugin


class TestITravelTimePlugin(TestCase):

    def setUp(self):
        self.plugin = ITravelTimePlugin()

    def test_calculate_walking_time(self):
        origin = (47.2454078, 7.9716352)  # Hauptstrasse 32 Reiden 6260
        destination = (47.241445, 7.9688353)  # Bahnhofstrasse 12 Reiden 6260
        walking_time = self.plugin.calculate_walking_time(origin, destination)
        self.assertTrue(walking_time < timedelta(minutes=10))

    def test_geocode(self):
        lat, lng = self.plugin.geocode('Hauptstrasse 32 Reiden 6260')
        self.assertTrue(lat > 45.0 and lat < 48.0)
        self.assertTrue(lng > 7.0 and lng < 10.0)


class TestIAlarmPlugin(TestCase):

    # pylint: disable-msg=protected-access

    def setUp(self):
        self.plugin = IAlarmPlugin()
        self.plugin._play = MagicMock()
        self.plugin._pause = MagicMock()
        self.plugin._interval = MagicMock()
        self.event = Event(name="Some Event", start_time=datetime.now())

    def test_begin_end(self):
        self.assertEquals(
            self.plugin.status, False, "status is true before calling begin.")
        self.plugin.begin(self.event)
        self.assertEquals(
            self.plugin.status, True, "begin() didn't set status to true")
        self.assertEquals(
            self.plugin.event, self.event, "begin() didn't set event.")
        self.plugin.end()
        self.assertEquals(
            self.plugin.status, False, "end() didn't set status to false")

    def test_play_pause(self):
        self.plugin.begin(self.event)
        self.assertEquals(
            self.plugin.playing, False)
        self.plugin.play()
        self.assertEquals(
            self.plugin.playing, True)
        self.plugin._play.assert_called_once_with()
        self.plugin.pause()
        self.assertEquals(self.plugin.playing, False)
        self.plugin._pause.assert_called_once_with()
        self.plugin.end()

    def test_interval(self):
        self.plugin.begin(self.event)
        self.plugin.play()
        self.plugin.interval()
        self.plugin._interval.assert_called_once_with()
        self.plugin.end()
        self.plugin._pause.assert_called_once_with()


class TestEvent(TestCase):

    def setUp(self):
        self.starttime = datetime(year=2013, month=3, day=5)
        self.before = datetime(year=2013, month=3, day=4)
        self.after = datetime(year=2013, month=3, day=6)
        self.event_without_reminder = Event(
            name="Some Event", start_time=self.starttime)
        self.event_with_reminder = Event(
            name="Some Event", start_time=self.starttime,
            reminder=timedelta(minutes=45))

    def test_to_string(self):
        val = self.event_without_reminder.__str__()
        if not isinstance(val, str):
            self.fail("Not a String.")  # pragma: no cover
        if not str(self.event_without_reminder):
            self.fail("String is empty.")  # pragma: no cover

    def test_compare_events(self):
        smaller = Event(name="Some Event", start_time=self.before)
        bigger = Event(name="Some Event", start_time=self.after)
        equal = Event(name="Some Event", start_time=self.before)

        if not smaller < bigger:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: <")

        if not bigger > smaller:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: >")

        if not smaller == equal:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: ==")

        if not smaller <= bigger:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: <=")

        if not bigger >= smaller:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: >=")

        if not smaller != bigger:
            self.fail(  # pragma: no cover
                "Events don't compare properly. Operator: !=")
