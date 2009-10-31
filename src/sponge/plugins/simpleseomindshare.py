#!/usr/bin/env python
# encoding: utf-8
#
# simpleseomindshare.py
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

"""A Simple SEO Pagerank scraper which will pull from the most popular
   search engines.  It can be said this is a bit of an indicator of
   adoption and marketing efforts based on uptake of the project and
   general mindshare on the Internet.  Focus is likely on English
   language sources at this point.

   Search Engines and metrics are:
       - Google (pagerank, backlinks, search term hits less false postives)
            * googlepagerank: http://seopen.com/seopen-tools/pagerank.php?url=http://xmpp.org
                             This works well too, more restful: http://www.trynt.com/google-pagerank-api/v1/?u=
            * googlebacklinks: curl -e http://www.my-ajax-site.com  'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=link:http%3A//www.yahoo.com/&callback=processResults'
            * googlesearchtermhits: curl -e http://www.my-ajax-site.com  'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%2B"content+centric+networking"&callback=processResults'
              vs. http://www.google.com/#hl=en&q=%2B%22content+centric+networking%22&aq=f&oq=&aqi=&fp=Xmf0jJ9P_V0
             http://code.google.com/apis/ajaxsearch/documentation/#fonje
       - Yahoo (inlinks, search term hits less false positives)
           * yahooinlinks: XXX This is only good for one shot curl -e http://my-ajax-site.com 'http://search.yahooapis.com/SiteExplorerService/V1/inlinkData?appid=YahooDemo&query=http://search.yahoo.com&results=2'
           * yahoosearchtermhits: XXX TODO...need a web api, use BOSS http://developer.yahoo.com/search/
                        this is cool, but doesn't get stats curl -e http://my-ajax-site.com 'http://search.twitter.com/search.json?q=google+android&amp;rpp=60&amp;lang=en'
                        curl -e http://my-ajax-site.com 'http://boss.yahooapis.com/ysearch/web/v1/xmpp?appid=Cn4p77bV34ErE0krAqPrhfgS1xpX_DzN1vWzXZZIjRVNefU6jpFJ0TXsEDuhO_97kz795A--&format=xml'
       -Bing (search term hits less false positives)
           * bingsearchtermhits: curl -e http://myajaxsite.com \
"http://api.bing.net/json.aspx?AppId=MYAPPID&Version=2.2&Market=en-US&Query=testing&Sources=web&Web.Count=1&JsonType=raw"
            Note, their terms of service may not be friendly
       - Alexa (alexarank, alexainlinks)
            * alexarank, alexainlinks: curl -e http://myajaxsite.com http://www.alexa.com/siteinfo/yahoo.com [Scrape first occurence of 'data steady'
            /images/icons/globe-sm.jpg + 46 chars = pagerank
            /site/linksin/yahoo.com + 3 chars = inlinks
        -Delcio.us (deliciouslinks, delicioustags)
            * deliciouslinks: XXX TODO
            * delicioustags: XXX TODO

        This site can provide some inspiration: http://www.pr.jbi.in/index.php

"""
import sys
import os
import string
import urllib2
import urllib
import cookielib
import base64
import HTMLParser
from sponge.plugins import pluginbase
import unittest
from sponge.tools import sponger


parsedResults = [] # Used for storing parsed data

class SEOMindshareDatasource(pluginbase.PluginBase):
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
        print "Init SEOMindshareDatasource Plugin..."
        #
        # TODO: Initialize Plugin Metadata
        #
        self.workDir = projectdict['project.work.dir']
        print "initialized workDir variable = " + self.workDir
    def get_plugin_metadata(self):
        return {'guid':3,'name':'SEOPagerankDatasource', 'license':'bsd 3-clause'}
    def get_datasource_metadata(self):
        return {1:['googlepagerank', 'integer'],
                2:['googlebacklinks','integer'],
                3:['googlesearchtermhits', 'integer'],
                4:['yahooinlinks', 'integer'],
                5:['yahoosearchtermhits', 'integer'],
                6:['alexarank', 'integer'],
                7:['alexainlinks', 'integer'],
                8:['bingsearchtermhits', 'integer']
                }

    def fetch_data(self, plugindict):
        #
        #
        apirooturl = 0
        apikey = 0
        apiuri = 0
        query = 0

        print "Fetching seomindshare data"
        if plugindict is not None:
            print plugindict # XXX Debug
            apirooturl = plugindict.get('datasource.seomindshare.google.pagerank.api.root.uri')
            query = plugindict.get('datasource.seomindshare.query.1')

        print "getting google page rank: root url " + apirooturl


        #
        # query 1 - googlepagerank
        #
        # XXX Refactor this block into urlencode_query_data
        adict = {}
        adict[query.split(' ')[0]] = query.split(' ')[1];

        querydata = urllib.urlencode(adict)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)

        #
        # just look for a line containing "PageRank:" and save this string
        #
        #
        pageRankParser = SEOMindsharePagerankParser()
        rawHTML = apiResp.read()
        # print rawHTML
        pageRankParser.feed(rawHTML)
        print parsedResults # XXX Debug output
        self.dataDict['googlepagerank'] = parsedResults[0]


        #
        # query 2 - googlebacklinks
        #
        apirooturl = plugindict.get('datasource.seomindshare.google.search.api.root.uri')
        query = plugindict.get('datasource.seomindshare.query.2')
        querydata = self.urlencode_query_string(query)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)
        rawJSON = apiResp.read()
        resultCountIndex = rawJSON.find("estimatedResultCount") + len("estimatedResultCount")
        backlinkCount = -1;
        if resultCountIndex > -1:
            # Sorry this sucks...I am lame.  I lazily do not want to require a JSON library to run this
            # so we parse everything in an ugly way.  It's brittle as a cracker.  For now, I'm trying to
            # get something useful out quickly, and optimize, fix, cleanup later.
            backlinkCount = rawJSON[resultCountIndex + 3:string.find(rawJSON, ",", resultCountIndex) -1]
        print "simpleseomindshare found " + backlinkCount + " backlinks from Google"
        self.dataDict['googlebacklinks'] = str(backlinkCount)

        #
        # query 3 - googlesearchtermhits
        #
        apirooturl = plugindict.get('datasource.seomindshare.google.search.api.root.uri')
        query = plugindict.get('datasource.seomindshare.query.3')
        querydata = self.urlencode_query_string(query)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)
        rawJSON = apiResp.read()
        resultCountIndex = rawJSON.find("estimatedResultCount") + len("estimatedResultCount")
        searchtermhitCount = -1;
        if resultCountIndex > -1:
            # Sorry this sucks...I am lame.  I lazily do not want to require a JSON library to run this
            # so we parse everything in an ugly way.  It's brittle as a cracker.  For now, I'm trying to
            # get something useful out quickly, and optimize, fix, cleanup later.
            searchtermhitCount = rawJSON[resultCountIndex + 3:string.find(rawJSON, ",", resultCountIndex) -1]
        print "simpleseomindshare found " + searchtermhitCount + " search term hit from Google"
        self.dataDict['googlesearchtermhits'] = str(searchtermhitCount)

        #
        # query 4 - yahooinlinks
        #
        apirooturl = plugindict.get('datasource.seomindshare.yahoo.api.root.uri')
        query = plugindict.get('datasource.seomindshare.yahoo.query.1')
        querydata = self.urlencode_query_string(query)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)
        rawXML= apiResp.read()
        resultCountIndex = rawXML.find("totalResultsAvailable") + len("totalResultsAvailable")
        yahooinlinksCount = -1;
        if resultCountIndex > -1:
            yahooinlinksCount = rawXML[resultCountIndex + 2:string.find(rawXML, "\"", resultCountIndex + 2)]
        print "yahooinlinks found " + yahooinlinksCount + " inlinks from yahoo"
        self.dataDict['yahooinlinks'] = str(yahooinlinksCount)

        #
        # query 5 - yahoosearchtermhits
        #
        apirooturl = plugindict.get('datasource.seomindshare.yahoo.bossapi.root.uri') + plugindict.get('datasource.seomindshare.yahoo.query.2a')
        query = plugindict.get('datasource.seomindshare.yahoo.query.2b')
        querydata = self.urlencode_query_string(query)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)
        rawXML= apiResp.read()
        resultCountIndex = rawXML.find("totalhits") + len("totalhits")
        yahoosearchtermhitsCount = -1;
        if resultCountIndex > -1:
            yahoosearchtermhitsCount = rawXML[resultCountIndex + 2:string.find(rawXML, "\"", resultCountIndex + 2)]
        print "yahoosearchtermhits found " + yahoosearchtermhitsCount
        self.dataDict['yahoosearchtermhits'] = str(yahoosearchtermhitsCount)

        #
        # query 6 - bingsearchtermhits
        #
        apirooturl = plugindict.get('datasource.seomindshare.bing.api.root.uri')
        query = plugindict.get('datasource.seomindshare.bing.query.1')
        querydata = self.urlencode_query_string(query)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl + "?" + querydata)
        rawXML= apiResp.read()
        resultCountIndex = rawXML.find("Total") + len("Total")
        bingsearchtermhitsCount = -1;
        if resultCountIndex > -1:
            bingsearchtermhitsCount = rawXML[resultCountIndex + 2:string.find(rawXML, ",", resultCountIndex + 2)]
        print "bingsearchtermhits found " + bingsearchtermhitsCount
        self.dataDict['bingsearchtermhits'] = str(bingsearchtermhitsCount)

        #
        # query 7 - alexarank XXX BUG: Need to coerce the string result to in
        #
        alexaquery = plugindict.get('datasource.seomindshare.alexa.query.1')
        apirooturl = plugindict.get('datasource.seomindshare.alexa.api.root.uri') + alexaquery

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        apiResp = urllib2.urlopen(apirooturl)
        rawHTML= apiResp.read()
        resultCountIndex = rawHTML.find("/images/icons/globe-sm.jpg") + len("/images/icons/globe-sm.jpg")
        alexarank = -1;
        if resultCountIndex > -1:
            alexarank = rawHTML[resultCountIndex + 45:string.find(rawHTML, "<", resultCountIndex + 45)]
        print "alexarank found " + alexarank
        strtoint = string.split(alexarank, ',')
        self.dataDict['alexarank'] = string.atoi(strtoint[0] + strtoint[1])

        #
        # query 8 - alexainlinks XXX BUG: Need to coerce the string result to in
        #
        # Reuse result for query 7
        alexaquery = string.strip(alexaquery, "www.") # hack to deal with alexa chopping this off in the results page
        resultCountIndex = rawHTML.find("/site/linksin/" + alexaquery) + len("/site/linksin/" + alexaquery)
        alexainlinks = -1;
        if resultCountIndex > -1:
            alexainlinks = rawHTML[resultCountIndex + 2:string.find(rawHTML, "<", resultCountIndex + 2)]
        print "alexainlinks found " + alexainlinks
        strtoint = string.split(alexainlinks, ',')
        self.dataDict['alexainlinks'] = string.atoi(strtoint[0] + strtoint[1])


        print self.dataDict
        return self.dataDict

    def urlencode_query_string(self, query):
        #
        # This sucks.  Todo: XXX Make this handle queries that may have whitespace
        #
        adict = {}
        print query
        querylist = query.split(' ')
        size = len(querylist)
        idx = 0
        while idx < size:
            adict[querylist[idx]] = querylist[idx+1];
            idx += 2
        encodedquerydata = urllib.urlencode(adict)
        print encodedquerydata
        return encodedquerydata
class SEOMindsharePagerankParser(HTMLParser.HTMLParser):
#    def handle_starttag(self, tag, attrs):
#            if tag == 'center':
#                for name, value in attrs:
#                    if value.find("PageRank:") > -1:
#                        print "Found PageRank = " + value
#                        parsedResults = value
    def handle_data(self, data):
            if data.find("PageRank:") > -1:
                print "Found pagerank data = " + data
                # print data.split(" ")
                # parsedResults = (data.split(" ")[1])[0]
                parsedResults.append(data.split(" ")[1].rstrip("\""))
class seoMindshareDatasourcePluginTests(unittest.TestCase):
    aSponger = 0
    aDatasource = 0
    def setUp(self):
        print "Setting up"
        self.aSponger = sponger.Sponger()
        count = self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aDatasource = SEOMindshareDatasource(self.aSponger.spongeProjectEnv)
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