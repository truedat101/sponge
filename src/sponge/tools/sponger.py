#!/usr/bin/env python
# encoding: utf-8
#
#Sponger.py
#
#Created by David J. Kordsmeier on 2009-01-30.
#Copyright (c) 2009 Razortooth Communications, LLC. All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification,
#are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
#    * Neither the name of Razortooth Communications, LLC, nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Sponger handles the process of loading the plugins used to track Project Vitality,
generate a report, and store the results.

The backing store format for the Project Vitality Report is as follows:
XXX TBD CSV is easiest for out of the box, and can be backed up anywhere as a flat file
either to git iteself, sqlite, CouchDB, mysql, or simply to local hard drive.

It is expected the Project Vitality Report will be used a website to publish the data
in a graph form for easier visualization.  Something like this should work great:
http://www.liquidx.net/plotkit/
There is also Open Flash Charts http://teethgrinder.co.uk/open-flash-chart/  which look
great but I think I can't hang with the flash stuff.  Too many browser problems.

"""
import sys
import os
import unittest
import string
import re
import getopt
import types
import sponge.plugins.simplegithub


class Sponger:

    spongeProjectEnv = {}
    spongeDatasourceEnv = {}
    spongeReportEnv = {}
    spongeBackingstoreEnv = {}
    spongeDatasourcePlugins = {}
    envFile = 0 # XXX Will I ever need this again after init?  I don't plan to modify the *Env

    def __init__(self):
        print "sponger is sponging...scrub scrub soak soak"
    def initEnv(self, projectConfigFilePath):
        envFile = open(projectConfigFilePath, 'rU')
        lines = envFile.readlines()
        if envFile:
            # read it in
            print envFile
            for line in lines:
                # Discard comments
                # split each line into key, tuple
                # XXX Based on luffa issues, need to review best approach
                # for stripping control characters from the input before
                # I store them into the *Env
                if line[0].find("#", 0) == -1:
                    line = line.split('=')
                    if line[0].find("project") > -1:
                        self.spongeProjectEnv[line[0]] = line[1]
                    elif line[0].find("datasource") > -1:
                        self.spongeDatasourceEnv[line[0]] = line[1]
                    elif line[0].find("report") > -1:
                       self.spongeProjectEnv[line[0]] = line[1]
                    elif line[0].find("backingstore") > -1:
                       self.spongeProjectEnv[line[0]] = line[1]
                    else:
                       print "Ignoring env property %s" % line
            envFile.close()
            #
            # Process plugin keys
            #
            # 1. Get the pluginclassname.
            # 2. Load the Module and Class named in pluginclassname via __import__
            #    see reference: http://code.activestate.com/recipes/223972/
            #    also: http://www.canonical.org/~kragen/isinstance/
            #    also: http://www.ibm.com/developerworks/library/l-pyint.html
            #    also: http://effbot.org/zone/python-getattr.htm
            #    also: http://www.gamedev.net/community/forums/topic.asp?topic_id=445037
            #    also: http://docs.python.org/library/new.html
            #    also: http://diveintopython.org/power_of_introspection/getattr.html#d0e9194
            # 3. Add the pluginclassname as the key in spongeDatasourcePlugins, so as to avoid
            #    any namespace collision, and store the Class reference
            # Of course, if there is some problem loading the class, I think this should bomb
            # rather than continue trying to load the other plugins.  If you intend to load a
            # plugin, don't ignore errors loading the plugin.  XXX For now, use this approach
            # And revisit after major debugging is done
            for aKey in self.spongeDatasourceEnv.keys():
                if aKey.find("pluginclassname") > -1:
                    pluginclassname = self.spongeDatasourceEnv.get(aKey).rstrip()
                    print "add the key to the plugin list"
                    pluginmodule = self.dynamicModuleImport(pluginclassname)
                    pluginClassRef = self.dynamicClassImport(pluginmodule, pluginclassname)
                    self.spongeDatasourcePlugins[pluginclassname, pluginClassRef]
        else:
            print "Error: Cannot open file $s" % siteFile
        return (len(self.spongeDatasourceEnv) + len(self.spongeProjectEnv) + len(self.spongeReportEnv) + len(self.spongeBackingstoreEnv))
    def soak(self): # XXX What should this return?
        if (len(self.spongeDatasourcePlugins) > 0): # Check for existence of data source plugins
            plugin = 0
            #
            # Use Default
            # should normally loop through and process all of the data source plugins
            # and only fail with exit if there are no plugins available
            # even if plugins don't work, they should return error info to stderr/stdout
            # and should not commit results to backing store if any plugin fails.
            #
            # Example Plugin init: plugin = GithubDatasourcePlugin()
            #          self.spongeDatasourcePlugins['GithubDatasourcePlugin':plugin]
            #
            # Process data sources
            #
            for datasource in self.spongDatasourcePlugins.keys():
                print "Processing data source"

        else:
            print "Couldn't load any plugins for datasources, exiting"
            sys.exit(1)

    def dynamicModuleImport(self, modulename):
        if modulename is not None:
            try:
                modulePackageWithClass = string.rsplit(modulename, '.', 1)
                dmod = __import__(modulePackageWithClass[0], globals(), locals(), [''])
                sys.modules = dmod
                print "Successfully imported module " + dmod.__name__
            except ImportError:
                return None
            return dmod

    def dynamicClassImport(self, module, className):
        if module is not None:
            if className is None:
                className = "Plugin" # If no classname is given, then default to Plugin
            try:
                dclass = getattr(module, className)
                print "Successfully imported name " + dclass.__name__
            except ImportError:
                return None
            return dclass

class spongerTests(unittest.TestCase):
    aSponger = 0
    def setUp(self):
        print "Setting up"
        self.aSponger = Sponger()
    def testInitEnv(self):
        count = self.aSponger.initEnv("../../../examples/spongesite.conf")
        print "# of props read=%d" % (count)
        self.assert_(count == 9)
    def testSoak(self):
        self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aSponger.soak()
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main() # From within the IDE or from the shell, we'll run tests automatically
else:
    pass # Module Imported by another module, which is what we want mostly

