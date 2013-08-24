from unittest import TestCase

from smartclock.main import conffile, get_plugin_places
from smartclock.plugins.pluginmanager import PluginManager

_manager = PluginManager(conffile, [get_plugin_places()], debug=True)


class PluginTestCase(TestCase):

    settings = {}

    def setUp(self):
        if not 'category' in self.settings:
            self.settings['category'] = 'configurable'
        if not 'load_default_settings' in self.settings:
            self.settings['load_default_settings'] = False

        self.plugin = _manager.get_plugin(
            self.settings['name'], self.settings['category'])

        if self.settings['load_default_settings']:
            self.plugin.settings = self.plugin.default_settings
