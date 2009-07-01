#!/usr/bin/env python
# encoding: utf-8
#
# simplegithub.py
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

"""A Simple Freshmeat.net Datasource for sponge.  Should eventually
use freshmeat Data API: http://help.freshmeat.net/faqs/api-7/data-api-intro
but may page scrape XML initially in order to simplify effort around
acquiring a Developer API Key.

"""
import sys
import os
import string
import urllib2
from sponge.plugins import pluginbase
import unittest
from sponge.tools import sponger

# XXX This should extend a base class defining the basic method signatures required
class FreshmeatDotNetDatasource(pluginbase.PluginBase):
    dataDict = {}  # Contains the database of our current result set
                   # XXX It's possible this won't stay around for long if data sets are very
                   # large, in which case we will page them in as needed
                   # For now, we are trying to deal with data snapshots and should avoid
                   # manipulating tomes of data

    dataModel = {} # XXX I'm thinking to use this to define what the data definition looks like
                   # Problem is complexity.  The reason for knowing what the Data Model looks like
                   # is for 2 reasons: (1) the api user can know what is in the data returned
                   # and parse appropriately, and (2) a renderer can introspect and automatically
                   # know how to handle rendering
                   # To avoid complexity at this point, simply name the fields as the key, and
                   # offer a description in the value field.
                   #
                   # KEY = String name of the field
                   # VALUE = String description of the field contents
                   #
                   # It is difficult to do better than this at the moment without adopting
                   # some ORM dependency or getting into trying ourselves to an actual
                   # database
    workDir = "/tmp" # XXX This won't work on winders.  Shux.  Need to maybe move this to the
                     # common config file used for the project and allow all plugins to
                     # share the use of the workDir

    def __init__(self, projectdict):
        print "Init FreshmeatDotNetDatasourcePlugin..."
        #
        # TODO: Initialize Plugin Metadata
        #
        self.workDir = projectdict['project.work.dir']
        print "initialized workDir variable = " + self.workDir
    def get_plugin_metadata(self):
        return {'guid':2,'name':'FreshmetDotNetDatasource', 'license':'bsd 3-clause'}
    def get_datasource_metadata(self):
        return {'field' + repr(1):['votescore', 'integer'],
                'field' + repr(2):['popularity','float'],
                'field' + repr(3):['vitality', 'float'],
                'field' + repr(4):['subscribers', 'integer'],
                }
    def fetch_data(self, plugindict):
        #
        #
        # XXX rename plugindict to something else
        apirooturl = 0
        apikey = 0
        apiuri = "/projects/"
        permalink = 0
        print "Fetching data"
        if plugindict is not None:
            print plugindict
            apirooturl = plugindict.get('datasource.freshmeat.api.root.uri')
            apikey = plugindict.get('datasource.freshmeat.apikey')
            permalink = plugindict.get('datasource.freshmeat.permalink')

        #
        # field1 - votescore
        #
        # Use Freshmeat.net Data API - Project, fetch as JSON
        #
        print "calling Freshmeat.net api: " + apirooturl + apiuri + permalink + '.json' + '?auth_code=' + apikey

        apiReq = urllib2.urlopen(apirooturl + apiuri + permalink + '.json' + '?auth_code=' + apikey)

        #
        # XXX This sucks.  I need a real JSON parser
        #
        apiResp = [string.strip(elem) for elem in string.rsplit(apiReq.read(), ',')]
        print apiResp # XXX Debug output

        self.dataDict["votescore"] = [string.lstrip(string.split(elem, ':')[1]) for elem in apiResp if elem.find("vote_score") > -1][0]

        #
        # field2 - popularity
        #
        self.dataDict["popularity"] = [string.lstrip(string.split(elem, ':')[1]) for elem in apiResp if elem.find("popularity") > -1][0]

        #
        # field3 - vitality
        #
        self.dataDict["vitality"] = [string.lstrip(string.split(elem, ':')[1]) for elem in apiResp if elem.find("vitality") > -1][0]

        #
        # field4 - subscribers
        #
        self.dataDict["subscribers"] = [string.lstrip(string.split(elem, ':')[1]) for elem in apiResp if elem.find("subscriptions_count") > -1][0]

        print self.dataDict
        return self.dataDict



class freshmeatDotNetDatasourcePluginTests(unittest.TestCase):
    aSponger = 0
    aDatasource = 0
    def setUp(self):
        print "Setting up"
        self.aSponger = sponger.Sponger()
        count = self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aDatasource = FreshmeatDotNetDatasource(self.aSponger.spongeProjectEnv)
    def testGetPluginMetadata(self):
        pluginMetadataDict = self.aDatasource.get_plugin_metadata()
        self.assert_(pluginMetadataDict is not None)
        print pluginMetadataDict
    def testGetDatasourceMetadata(self):
        datasourceMetadataDict = self.aDatasource.get_datasource_metadata()
        self.assert_(datasourceMetadataDict is not None)
        print datasourceMetadataDict
    def testFetchData(self):
        dataDict = self.aDatasource.fetch_data(self.aSponger.spongeDatasourceEnv)
        self.assert_(dataDict is not None)
        print dataDict
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()