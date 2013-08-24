import imp
import os
import sys
import ConfigParser
from cStringIO import StringIO

from yapsy import log
from yapsy import PLUGIN_NAME_FORBIDEN_STRING
from yapsy.PluginFileLocator import PluginFileAnalyzerWithInfoFile


class PluginFileAnalyzerWithDocString(PluginFileAnalyzerWithInfoFile):
    def __init__(self, name):
        PluginFileAnalyzerWithInfoFile.__init__(self, name, extensions="py")

    def isValidPlugin(self, filename):
        if filename.endswith('_plugin.py'):
            return True
        return False

    def getInfosDictFromPlugin(self, dirpath, filename):
        path = os.path.join(dirpath, filename)
        key = "%s_get_docstring" % os.path.splitext(filename)[0]
        log.debug(path)

        module = None
        infos = None, None
        try:
            module = imp.load_source(key, path)
            docstring = module.__doc__
            infos = PluginFileAnalyzerWithInfoFile.getInfosDictFromPlugin(
                self, path, StringIO(docstring))
        except Exception as e:
            log.debug(e)
        finally:
            if not module is None:
                del module
            if key in sys.modules:
                del sys.modules[key]
        return infos

    def _extractCorePluginInfo(self, candidate_infofile, stream):
        name, config_parser = self.getPluginNameAndModuleFromStream(
            stream, candidate_infofile)

        if (name, config_parser) == (None, None):
            return (None, None)
        infos = {"name": name, "path": candidate_infofile}
        return infos, config_parser

    def getPluginNameAndModuleFromStream(self, infoFileObject,
                                         candidate_infofile=None):
        # parse the information buffer to get info about the plugin
        config_parser = ConfigParser.SafeConfigParser()
        try:
            config_parser.readfp(infoFileObject)
        except Exception, e:
            log.debug(
                "Could not parse the plugin file '%s' (exception raised was '%s')",  # pylint: disable=line-too-long
                candidate_infofile, e)
            return (None, None)
        # check if the basic info is available
        if not config_parser.has_section("Core"):
            log.debug(
                "Plugin info file has no 'Core' section (in '%s')",
                candidate_infofile)
            return (None, None)
        if not config_parser.has_option("Core", "Name"):
            log.debug(
                "Plugin info file has no 'Name' or 'Module' section (in '%s')",
                candidate_infofile)
            return (None, None)
        # check that the given name is valid
        name = config_parser.get("Core", "Name")
        name = name.strip()
        if PLUGIN_NAME_FORBIDEN_STRING in name:
            log.debug(
                "Plugin name contains forbiden character: %s (in '%s')",
                PLUGIN_NAME_FORBIDEN_STRING, candidate_infofile)
            return (None, None)
        return (name, config_parser)
