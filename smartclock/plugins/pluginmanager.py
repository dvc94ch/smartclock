import os
from ConfigParser import SafeConfigParser

from yapsy.PluginManager import PluginManagerSingleton
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.VersionedPluginManager import VersionedPluginManager

from smartclock.plugins import pluginlib
from smartclock.plugins.pluginfileanalyzerwithdocstring import PluginFileAnalyzerWithDocString  # pylint: disable=line-too-long


PluginManagerSingleton.setBehaviour(
    [ConfigurablePluginManager, VersionedPluginManager])
_manager = PluginManagerSingleton.get()


class PluginManager(object):

    def __init__(self, conffile, plugin_places, debug=False):
        """Configures the PluginManager, loads plugins and settings."""

        activate_plugins = not os.path.exists(conffile) or debug

        if debug:
            write_config = lambda: None
        else:
            write_config = lambda: self.write_config(parser, conffile)

        parser = SafeConfigParser()
        parser.read(conffile)

        _manager.setConfigParser(parser, write_config)  # pylint: disable=maybe-no-member

        _manager.getPluginLocator().setAnalyzers(
            [PluginFileAnalyzerWithDocString(name="doc_string")])
        _manager.setPluginPlaces(plugin_places)
        _manager.setCategoriesFilter({
            "configurable": pluginlib.IConfigurablePlugin,
            "eventcollector": pluginlib.IEventCollectorPlugin,
            "eventprocessor": pluginlib.IEventProcessorPlugin,
            "traveltime": pluginlib.ITravelTimePlugin,
            "alarm": pluginlib.IAlarmPlugin,
            "bedsensor": pluginlib.IBedsensorPlugin,
            "display": pluginlib.IDisplayPlugin
        })
        _manager.collectPlugins()

        if activate_plugins:
            self.activate_plugins()

        for plugin_info in _manager.getPluginsOfCategory("configurable"):
            if isinstance(
                    plugin_info.plugin_object, pluginlib.PluginMasterMixin):
                plugin_info.plugin_object.get_plugin = self.get_plugin

    def activate_plugins(self):
        for plugin_info in _manager.getPluginsOfCategory("configurable"):
            _manager.activatePluginByName(
                plugin_name=plugin_info.name, category_name="configurable")

    def write_config(self, parser, conffile):
        with open(conffile, "w+") as f:
            parser.write(f)

    def get_plugin(self, name, category):
        plugin_info = _manager.getPluginByName(name, category)
        if plugin_info.is_activated:
            return plugin_info.plugin_object

    def get_plugins(self, category):
        for plugin_info in _manager.getPluginsOfCategory(category):
            if plugin_info.is_activated:
                yield plugin_info.plugin_object
