from datetime import datetime

from smartclock.plugins.pluginlib import Event
from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class DisplayNotificationPluginTestCase(PluginTestCase):

    settings = {
        'name': 'Display Notification Plugin',
        'category': 'display',
        'load_default_settings': True
    }

    def test_get_text_backlight(self):
        notification = self.plugin.get_text()
        self.assertIs(
            notification, None, "get_text must return None if alarm isn't on.")
        backlight = self.plugin.backlight()
        self.assertIs(
            backlight, None, "backlight must return None if alarm isn't on.")
        self.plugin.begin(Event(name="Some Event", start_time=datetime.now()))
        self.plugin.play()
        notification = self.plugin.get_text()
        self.assertIsInstance(
            notification, str,
            "get_text must return a string when alarm is on.")
        backlight = self.plugin.backlight()
        backlight2 = self.plugin.backlight()
        self.assertIsNot(
            backlight, backlight2, "backlight should toggle when alarm is on.")
