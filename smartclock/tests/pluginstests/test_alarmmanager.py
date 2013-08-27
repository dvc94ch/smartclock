from unittest import TestCase
from mock import MagicMock

from datetime import datetime, timedelta

from smartclock.plugins.alarmmanager import AlarmManager
from smartclock.hardware.bedsensor import Bedsensor
from smartclock.plugins.pluginlib import Event


mockevent = Event(
    name="Mock Event", start_time=datetime.now(), reminder=timedelta(hours=0))


class MockEventCollector(object):

    def collect(self):
        yield mockevent


class MockEventProcessor(object):

    def process(self, event):
        event.mock = True
        return event


class AlarmManagerTestCase(TestCase):

    def setUp(self):
        self.alarm_manager = AlarmManager(
            self.mock_get_plugins, MagicMock(return_value=Bedsensor.PRESSED))
        self.alarm = MagicMock()
        self.alarm.begin = MagicMock(name="begin")
        self.alarm.play = MagicMock(name="play")
        self.alarm.pause = MagicMock(name="pause")
        self.alarm.interval = MagicMock(name="interval")
        self.alarm.end = MagicMock(name="end")

    def mock_get_plugins(self, category):
        if category == 'eventcollector':
            yield MockEventCollector()
        elif category == 'eventprocessor':
            yield MockEventProcessor()
        elif category == 'alarm':
            yield self.alarm

    def test_collect_events(self):
        events = list(event for event in self.alarm_manager.collect_events())
        self.assertEquals(
            len(events), 1, "MockEventCollector only yields one event.")
        self.assertEquals(events[0], mockevent)

    def test_process_event(self):
        event = self.alarm_manager.process_event(mockevent)
        self.assertEquals(event.mock, True)

    def test_begin_alarms(self):
        self.alarm_manager.begin_alarms(mockevent)
        self.alarm.begin.assert_called_once_with(mockevent)
        self.alarm.play.assert_called_once_with()

    def test_play_alarms(self):
        self.alarm_manager.play_alarms()
        self.alarm.play.assert_called_once_with()

    def test_pause_alarms(self):
        self.alarm_manager.pause_alarms()
        self.alarm.pause.assert_called_once_with()

    def test_interval_alarms(self):
        self.alarm_manager.interval_alarms()
        self.alarm.interval.assert_called_once_with()

    def test_end_alarms(self):
        self.alarm_manager.end_alarms()
        self.alarm.end.assert_called_once_with()
