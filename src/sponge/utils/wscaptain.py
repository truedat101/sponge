#!/usr/bin/env python
# encoding: utf-8
#
# wscaptain.py
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

"""WSCaptain is short for Web Service Captain.  As the name implies, the WSCaptain aims to help you when
you need to interact with various Web Services.  The only purpose of this class is as a utility for
taking common code for calling up web pages and handling authentication, and putting it into a single
location.  The methods defined here are static methods to handle general things you will need to do
frequently.  If a change needs to be made in HTTP handling, it is better to change it in one place
rather than cut-n-paste code everywhere.

XXX TODO: Refactor entire code base and put common items for accessing web services and page scraping
here.  Sigh, scraping sucks.  Oh, woe is me brittle software.  I'll add a JSON parser and XML parser
to the project in some future version.

References:
* Inspiration here: http://www.voidspace.org.uk/python/articles/authentication.shtml

"""

import sys
import os
import string
import urllib2
import urllib
import cookielib
import base64
import HTMLParser
import unittest
import exceptions


class WSCaptain():
    def __init__(self):
        pass

    def createHTTPBasicAuthenticationOpenerContext(self, username, password, toplevel_url):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, toplevel_url, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        return opener

    def createRequest(self, some_url, some_data, some_headers):
        return urllib2.Request(some_url, some_data, some_headers)

    def openPage(self, some_url):
        try:
            # XXX This would be a good place to maybe check for SSL support in your
            # python install.  In 2.6, check for import ssl, in 2.5 check for python socket ssl wrapper
            handler = urllib2.urlopen(some_url)
            page = handler.read()
            return page
        except IOError, e:
            if hasattr(e, 'code'):
                print e.code
            elif hasattr(e,'headers'):
                print e.headers
                print e.headers['www-authenticate']
            else:
                print e

class wscaptainTests(unittest.TestCase):
    aWSCaptain = 0
    def setUp(self):
        print "Setting up"
        self.aWSCaptain = WSCaptain()
    def testCreateHTTPBasicAuthenticationOpenerContext(self):
        self.assert_(self.aWSCaptain is not None)
        aURL = 'https://timetric.com/series/bdb10YFeSA-rQkNEVD1rUA/'
        anOpener = self.aWSCaptain.createHTTPBasicAuthenticationOpenerContext('YOURAPPID','YOURSECRET', aURL)
        self.assert_(anOpener is not None)
        try:
            aRequest = urllib2.urlopen(aURL)
            self.assert_(aRequest is not None)
            page = aRequest.read()
            self.assert_(page is not None)
            print page
        except IOError, e:
            if hasattr(e, 'code'):
                print e.code
                self.fail(e.code)
            elif hasattr(e,'headers'):
                print e.headers
                print e.headers['www-authenticate']
            else:
                print e

    def testCreateRequest(self):
        self.assert_(self.aWSCaptain is not None)
        aURL = 'https://timetric.com/series'
        data = {'foo1':'foo1', 'foo2':'foo2'}
        headers = {'Content-Type':'text/html'}
        encodedData = ""
        for key in data:
            encodedData = encodedData + key + "," + data[key] + "\r\n"
        print encodedData
        req = self.aWSCaptain.createRequest(aURL, encodedData, headers)
        self.assert_(req is not None)
        print req
    def testOpenPage(self):
        self.assert_(self.aWSCaptain is not None)
        aURL = 'https://timetric.com/series'
        anOpener = self.aWSCaptain.createHTTPBasicAuthenticationOpenerContext('YOURAPPID','YOURSECRET', aURL)
        self.assert_(anOpener is not None)
        aPage = self.aWSCaptain.openPage('https://timetric.com/series/bdb10YFeSA-rQkNEVD1rUA/')
        self.assert_(aPage is not None)
        aURL2 = 'https://timetric.com/series/bdb10YFeSA-rQkNEVD1rUA/'
        aPage2 = self.aWSCaptain.openPage(aURL2)
        self.assert_(aPage2 is not None)
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()