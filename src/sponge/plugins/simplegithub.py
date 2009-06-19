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
import sys
import os
import subprocess
import unittest

# XXX This should extend a base class defining the basic method signatures required
class GithubDatasource:
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

    binPath = "/usr/bin" # where to find the git binaries

    #
    # TODO: Define Plugin Metadata
    #
    # At this point in time, the github api is limited.  I am trying to find out if there are
    # more private apis that can be used.
    #
    def __init__(self, projectdict):
        print "Init GithubDatasourcePlugin..."
        #
        # TODO: Initialize Plugin Metadata
        #
        self.workDir = projectdict['project.work.dir']
        self.binPath = projectdict['project.host.binarypath']
        print "initialized workDir variable = " + self.workDir
        print "initialized binPath = " + self.binPath
    def get_plugin_metadata(self):
        return {'guid':1,'name':'GithubDatasource', 'license':'gplv3'}
    def get_datasource_metadata(self):
        return {'field' + 1:['commits', 'integer'],
                'field' + 2:['watchers','integer'],
                'field' + 3:['forks', 'integer'],
                'field' + 4:['collaborators', 'integer'],
                'field' + 5:['tagcount', 'integer'],
                'field' + 6:['branchcount', 'integer'],
                'field' + 7:['issuecount', 'integer'],
                'field' + 8:['lastactivity', 'timestamp']
                }
    def fetch_data(self, plugindict):
        #
        # The Github API v2 is available
        #
        # However, it is focused on repository metadata for generating
        # a repo page, but no real ranking or stats.  The choice to use
        # the api, or use a local copy of the remote, or both.
        # For this one, I will grab what I can from the local, and get
        # what I can from the remote via the api
        #

        print "Fetching data"
        if plugindict is not None:
            gitcloneurl = plugindict['datasource.github.scm.uri']
        os.chdir(self.workDir)
        # Really need to decide if the host PATH should be used
        # or whether to pass this in as an argument
        print "about to run %s %s %s" %(self.binPath, gitcloneurl, self.workDir)
        subprocess.check_call([self.binPath + "/git", "clone", gitcloneurl, self.workDir + "/githubdatasource.git"])
        os.chdir(self.workDir + "/githubdatasource.git")
        subprocess.check_call(self.binPath + "/git rev-list --all --reverse 2>&1 | wc -l >" + self.workDir + "/githubdatasource.git/gitcommits.out", shell=True)
        commitFile = open(self.workDir + "/githubdatasource.git/gitcommits.out", 'rU')
        if commitFile:
            lines = commitFile.readlines()
            if lines:
                self.dataDict["totalcommits"] = lines[0].lstrip().rstrip()
                commitFile.close()

        # This won't work unless the directory in question is empty
        # utility method helps walk through and remove leaf nodes first
        # See: http://docs.python.org/library/os.html#os.rmdir
        self.removeDirUtil(self.workDir + "/githubdatasource.git")
        os.remove(self.workDir + "/githubdatasource.git")
        print self.dataDict
        return self.dataDict

    def removeDirUtil(self, top):
        # Only do the cleanup inside of the workDir
        if top.find(self.workDir) > -1:
            print "Blowing away working dir " + self.workDir
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

class githubDatasourcePluginTests(unittest.TestCase):
    def setUp(self):
        print "Setting up"
    def testInitEnv(self):
        print "foo"
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()