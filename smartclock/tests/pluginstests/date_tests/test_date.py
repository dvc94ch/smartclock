from smartclock.tests.pluginstests.plugintestcase import PluginTestCase


class DatePluginTestCase(PluginTestCase):

    settings = {
        'name': 'Date Plugin',
        'category': 'display'
    }

    def test_get_text(self):
        date = self.plugin.get_text()
        self.assertIsInstance(
            date, str, "Function get_text() must return a string.")
