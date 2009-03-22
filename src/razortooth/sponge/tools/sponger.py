#!/usr/bin/env python
# encoding: utf-8
"""
spongerpy

Created by David J. Kordsmeier on 2009-01-30.
Copyright (c) 2009 Razortooth Communications, LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of Razortooth Communications, LLC, nor the names of its
      contributors may be used to endorse or promote products derived from this
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import sys
import os
import unittest

class Sponger:
    spongeProjectEnv = {}
    spongeDatasourceEnv = {}
    spongeReportEnv = {}
    envFile = 0
    lines = 0
    def __init__(self):
        print "sponger is sponging..."
    def initEnv(self, siteFile):
        envFile = open(siteFile, 'rU')
        lines = envFile.readlines()
        if envFile:
            # read it in
            print envFile
            for line in lines:
                # Discard comments
                # split each line into key, tuple
                if line[0].find("#", 0) == -1:
                    line = line.split('=')
                    if line[0].find("project") > -1:
                        self.spongeProjectEnv[line[0]] = line[1]
                    elif line[0].find("datasource") > -1:
                        self.spongeDatasourceEnv[line[0]] = line[1]
                    elif line[0].find("report") > -1:
                       self.spongeProjectEnv[line[0]] = line[1]
                    else:
                       print "Ignoring env property %s" % line
            envFile.close()
        else:
            print "Error: Cannot open file $s" % siteFile
        return (len(self.spongeDatasourceEnv) + len(self.spongeProjectEnv) + len(self.spongeReportEnv))
    def soak(self):
        if (1): # Check for existence of data source plugins
            # Use Default

class spongerTests(unittest.TestCase):
    aSponger = 0
    def setUp(self):
        print "Setting up"
        self.aSponger = Sponger()
    def testInitEnv(self):
        print "# of props read=%d" % self.aSponger.initEnv("/Users/dkords/dev/projects/sponge/examples/spongesite.conf")
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()