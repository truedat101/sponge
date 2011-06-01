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

It is expected the Project Vitality Report will be used on a website to publish the data
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
import new
import datetime
import urllib2
from sponge.utils import wscaptain
from sponge.utils.dictdb import dbopen
from sponge.utils.dictdb import dbexists

class Sponger:
    spongeProjectEnv = {}
    spongeDatasourceEnv = {}
    spongeReportEnv = {}
    spongeBackingstoreEnv = {}
    spongeDatasourcePlugins = {}
    envFile = 0 # XXX Will I ever need this again after init?  I don't plan to modify the *Env
    baseDir = os.path.abspath(os.curdir) # The current work dir on execution

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
                if line[0].find("#", 0) == -1: # XXX This probably is a bug...would throw out any line containing a comment, even an inline comment, which should be valid
                    line = line.split('=') # XXX There is nothing wrong with this, but I don't know what the behavior is for split when a line ends with an =, which should just be an edge case, but I still need to cover this
                    if line[0].find("project") > -1:
                        self.spongeProjectEnv[line[0]] = line[1].rstrip()
                    elif line[0].find("datasource") > -1:
                        self.spongeDatasourceEnv[line[0]] = line[1].rstrip()
                    elif line[0].find("report") > -1:
                       self.spongeProjectEnv[line[0]] = line[1].rstrip()
                    elif line[0].find("backingstore") > -1:
                       self.spongeProjectEnv[line[0]] = line[1].rstrip()
                    elif line[0].find("publisher") > -1:
                       self.spongeProjectEnv[line[0]] = line[1].rstrip() # XXX: Probably want to put this into a different dict
                    else:
                       # print "Ignoring env property %s" % line
                       None
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
                    pluginmodule = self.dynamicModuleImport(pluginclassname)
                    pluginClassRef = self.dynamicClassImport(pluginmodule, pluginclassname)
                    print "add the key to the plugin list for key " + pluginclassname + " = " + pluginClassRef.__name__
                    self.spongeDatasourcePlugins[pluginclassname] = pluginClassRef
        else:
            print "Error: Cannot open file $s" % siteFile
        return (len(self.spongeDatasourceEnv) + len(self.spongeProjectEnv) + len(self.spongeReportEnv) + len(self.spongeBackingstoreEnv))
    def soak(self): # XXX What should this return?
        if (len(self.spongeDatasourcePlugins) > 0): # Check for existence of data source plugins
            fooPlugin = 0
            #
            # Use Default
            # should normally loop through and process all of the data source plugins
            # and only fail with exit if there are no plugins available
            # even if plugins don't work, they should return error info to stderr/stdout
            # and should not commit results to backing store if any plugin fails.
            # XXX: TODO Need to see if I actually honor this
            #
            # Example Plugin init: plugin = GithubDatasourcePlugin()
            #          self.spongeDatasourcePlugins['GithubDatasourcePlugin':plugin]
            #
            # Process data sources
            # 1. get the data source instance
            # 2. get the results
            # 3. get the metadata
            # 4. persist the results into various formats
            for datasourceKey in self.spongeDatasourcePlugins.keys():
                datasource = self.spongeDatasourcePlugins[datasourceKey]
                # print "Processing data source" + datasourceKey + " and datasource = " +
                # fooPlugin = datasource.__init__(self)
                fooPlugin = new.instance(datasource)
                fooPlugin.__init__(self.spongeProjectEnv)
                metadata = fooPlugin.get_plugin_metadata()
                ds_col_labels = fooPlugin.get_datasource_metadata()
                print metadata
                rowResults = fooPlugin.fetch_data(self.spongeDatasourceEnv)
                dbname = datasourceKey

                os.chdir(self.spongeProjectEnv['project.db.dir'])

                #
                # XXX: TODO This section of persistence approaches should be handled by configurable
                # plugins
                # For now, inline each approach
                #
                #
                # import csv
                #
                # Persist Method 1
                # Persist to a .csv with results in row records, human readable
                # This yields one .csv per Plugin
                # This is better for crunching data on a single sheet
                isNewDB = False
                if (dbexists(dbname + ".csv") is not True):
                    isNewDB = True
                fdb = open(dbname + ".csv", 'ab')
                rowdata = None
                if isNewDB:
                    rowdata = "Date"
                    for label in ds_col_labels.values():
                        rowdata = rowdata + ",%s"%(label)
                    fdb.write(rowdata + "\n")
                rowdata = datetime.datetime.now().ctime() # This needs to be ISO
                print "time now is %s"%(rowdata)
                for data in rowResults.values():
                    rowdata = rowdata + ",%s"%(data)
                fdb.write(rowdata + "\n")
                fdb.close()

                #
                # Persist Method 2
                # For each series, put into a separate csv file
                # format should be
                # ISO DateTime Data, row data
                # This yields 1 .csv per Plugin-Column combo
                # Naming follows this  convension
                # for label in ds_col_labels.value():
                for key,value in rowResults.items():
                    db = dbopen(dbname + "." + key + ".csv", flag='c', format='csv')
                    if (db is not None):
                        # XXX May want to change how this mapped so that each key/value pair is comma-sep
                        db[datetime.datetime.isoformat(datetime.datetime.now())] = value # Warning: time is in ISO, need to convert when displaying
                        db.close()
                    else:
                        print "Couldn't create or open DB name = " + dbname + "." + key + '.csv'
                    db.close()
                print rowResults # XXX Debug
                print fooPlugin # XXX Debug
            os.chdir(self.baseDir) # Do this to get back to our original working directory
        else:
            print "Couldn't load any plugins for datasources, exiting"
            sys.exit(1)

    def squeeze(self):
        if (len(self.spongeDatasourcePlugins) > 0): # Check for existence of data source plugins
            fooPlugin = 0
            #
            # Here we will define the concept of a publisher.  A publisher is an abstraction for any
            # site, service, or component that handles the publication of data in a way that it can be
            # accessed, consumed, and understood by interested and authorized parties.  Our publisher
            # model is only conceptual at the moment, but we will define the concepts now.  We will not
            # define what ways data can be accessed, consumed, or understood.  We will discuss the concepts
            # for each of these action verbs.
            #
            # Publishers can make data accessible by exposing it over a network, typically published
            # on a web page or via a programatic web service interface.
            #
            # Publishers can allow data to be consumed, by making it possible for interested parties to
            # export the data as it has been published.  In other words, if I publish a data series, my
            # publisher should not only allow you to view the data, but also pull or export the data
            # as I have published it, and use it for other purposes.
            #
            # Publishers present data in such a way that it can be understood.  The best way to do this
            # is to provide the data a graphical representation, a bar graph, line graph, or some other
            # form of graph to best represent your data.  For analytics data, we probably care most about
            # data over time.  If graphics are not practical, then presenting summary data that has
            # been analyzed, with highlights, or more
            #
            #
            #
            # Process data sources
            # 0. Setup the HTTP Basic Authentication for the timetric web service
            # 1. Loop through the existing data sources, and attempt to find all of the .csv backingstores.
            # 2. get the datasource metadata
            # 3. push the existing data series store in the default backing store (currently .csv files) into
            # a publisher.
            # 4. email me when the complete set of data series have been uploaded. XXX: TODO: change how
            # to handle this notification so this is pluggable.
            #
            wsCaptain = wscaptain.WSCaptain()

            publisherURL = self.spongeProjectEnv['publisher.service.timetric.update.url']
            apitokenKey = self.spongeProjectEnv['publisher.service.timetric.apitoken.key']
            apitokenSecret = self.spongeProjectEnv['publisher.service.timetric.apitoken.secret']
            seriesDict = eval(self.spongeProjectEnv['publisher.service.timetric.series'])

            # XXX: I need to verify if the authentication actually worked and avoid publishing if it did not + report error
            anOpener = wsCaptain.createHTTPBasicAuthenticationOpenerContext(apitokenKey, apitokenSecret, publisherURL)

            for datasourceKey in self.spongeDatasourcePlugins.keys():
                datasource = self.spongeDatasourcePlugins[datasourceKey]
                fooPlugin = new.instance(datasource)
                fooPlugin.__init__(self.spongeProjectEnv)
                # We only want the datasource metadata, not to soak data from the datasources.
                ds_col_labels = fooPlugin.get_datasource_metadata()
                dbname = datasourceKey
                os.chdir(self.spongeProjectEnv['project.db.dir'])

                for col in ds_col_labels.keys(): # XXX What is the best way to iterate over the values?
                    label = ds_col_labels[col][0]
                    dbcsv = dbname + "." + label + ".csv"
                    if (dbexists(dbcsv) is True):
                        db = dbopen(dbcsv, flag='c', format='csv')
                        if (db is not None):
                            seriesID = seriesDict[datasourceKey][col-1]
                            seriesURL = publisherURL + "/" + seriesID + "/"
                            print "Publishing " + dbcsv + " to URL = " + seriesURL
                            headers = {'Content-Type':'text/csv'}
                            data = ""
                            for key in db:
                                data = data + key + "," + db[key] + "\r\n"
                            request = wsCaptain.createRequest(seriesURL, data, headers)
                            try:
                                response = urllib2.urlopen(request)
                            except urllib2.HTTPError, e:
                                print e
                            page = wsCaptain.openPage(seriesURL)
                        else:
                            print "Couldn't open DB name = " + dbcsv
                        db.close()
                    else:
                        # Do this if you can't find the actual .csv source file
                        print "Skipping publish of " + dbcsv
            os.chdir(self.baseDir) # Do this to get back to our original working directory

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
            if className.find(".") > -1:
                className = (string.rsplit(className, '.', 1))[1]
            elif className is None:
                className = "Plugin" # If no classname is given, then default to Plugin
            try:
                dclass = getattr(module, className)
                print "Successfully loaded class reference for " + dclass.__name__
            except AttributeError: # Catch this or just let it fail?
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
        self.assert_(count == 42)

    def testSoak(self):
        self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aSponger.soak()

    def testSqueeze(self):
        self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aSponger.squeeze()

    def testPublisher(self):
        self.aSponger.initEnv("../../../examples/spongesite.conf")
        publisherURL = self.aSponger.spongeProjectEnv['publisher.service.timetric.update.url']
        self.assert_(publisherURL is not None)
        apitokenKey = self.aSponger.spongeProjectEnv['publisher.service.timetric.apitoken.key']
        self.assert_(apitokenKey is not None)
        apitokenSecret = self.aSponger.spongeProjectEnv['publisher.service.timetric.apitoken.secret']
        self.assert_(apitokenSecret is not None)
        seriesDict = eval(self.aSponger.spongeProjectEnv['publisher.service.timetric.series'])
        self.assert_(seriesDict)
        print seriesDict
        seriesList = seriesDict['sponge.plugins.simplefreshmeat.FreshmeatDotNetDatasource']
        self.assert_(seriesList is not None)
        print seriesList
        self.assert_(len(seriesList) == 4)
        wsCaptain = wscaptain.WSCaptain()
        anOpener = wsCaptain.createHTTPBasicAuthenticationOpenerContext(apitokenKey, apitokenSecret, publisherURL)
        self.assert_(anOpener is not None)
        seriesURL = publisherURL + "/bdb10YFeSA-rQkNEVD1rUA/"
        page = wsCaptain.openPage(seriesURL)
        self.assert_(page is not None)

    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main() # From within the IDE or from the shell, we'll run tests automatically
else:
    pass # Module Imported by another module, which is what we want mostly

