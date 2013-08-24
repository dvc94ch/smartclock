from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class TimePluginTestCase(PluginTestCase):

    settings = {
        'name': 'Time Plugin',
        'category': 'display'
    }

    def test_get_text(self):
        time = self.plugin.get_text()
        self.assertIsInstance(
            time, str, "Function get_text() must return a string.")
