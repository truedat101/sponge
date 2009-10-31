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
import string
import urllib2
import unittest
from sponge.plugins import pluginbase
from sponge.tools import sponger

# XXX This should extend a base class defining the basic method signatures required
class GithubDatasource(pluginbase.PluginBase):
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
    baseDir = os.path.abspath(os.curdir) # The current work dir on execution
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
        print "initialzed baseDir = %s"%(self.baseDir)
    def get_plugin_metadata(self):
        return {'guid':1,'name':'GithubDatasource', 'license':'bsd 3-clause'}
    def get_datasource_metadata(self):
        return {1:['commitcount', 'integer'],
                2:['watchercount','integer'],
                3:['forkcount', 'integer'],
                4:['collaborators', 'integer'],
                5:['tagcount', 'integer'],
                6:['branchcount', 'integer'],
                7:['issuecount', 'integer'],
                8:['lastcommit', 'timestamp']
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
        # XXX rename plugindict to something else
        gitcloneurl = 0
        githubRepoName = 0
        githubUsername = 0
        githubApiURI = 0
        print "Fetching data"
        if plugindict is not None:
            print plugindict
            gitcloneurl = plugindict.get('datasource.github.scm.uri')
            githubRepoName = plugindict.get('datasource.github.reponame')
            githubUsername = plugindict.get('datasource.github.username')
            githubApiURI = plugindict.get('datasource.github.api.uri')
        os.chdir(self.workDir)
        #
        # Double check to see if the previous work was not cleaned
        # and remove the directory first
        if os.access(self.workDir + "/githubdatasource.git", os.R_OK):
            self.removeDirUtil(self.workDir + "/githubdatasource.git")
            os.rmdir(self.workDir + "/githubdatasource.git")

        #
        # field1 - commitcount
        #
        # Could probably use github api, it was worth the effort to
        # do a local clone so we have a general way to query a git
        # repo
        #
        print "about to run %s %s %s" %(self.binPath + "/git", gitcloneurl, self.workDir)
        subprocess.check_call([self.binPath + "/git", "clone", gitcloneurl, self.workDir + "/githubdatasource.git"])
        os.chdir(self.workDir + "/githubdatasource.git")
        subprocess.check_call(self.binPath + "/git rev-list --all --reverse 2>&1 | wc -l >" + self.workDir + "/githubdatasource.git/gitcommits.out", shell=True)
        commitFile = open(self.workDir + "/githubdatasource.git/gitcommits.out", 'rU')
        if commitFile:
            lines = commitFile.readlines()
            if lines:
                self.dataDict["commitcount"] = lines[0].lstrip().rstrip()
                commitFile.close()

        #
        # Use Github API repos
        #
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/repos/show/' + githubUsername + '/' + githubRepoName)


        #
        # field2 - watchercount
        #
        # curl http://github.com/api/v2/yaml/repos/show/truedat101/sponge
        #
        # XXX Need to catch exceptions through here
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        print githubapiResp # XXX Debug output
        self.dataDict["watchercount"] = [string.lstrip(string.split(elem, ':')[2]) for elem in githubapiResp if elem.find(":watchers") > -1][0]

        #
        # field3 - forkcount XXX This might be a problem.  Need to see if this forkcount is working
        #
        self.dataDict["forkcount"] = [string.lstrip(string.split(elem, ':')[2]) for elem in githubapiResp if elem.find(":forks") > -1][0]

        #
        # field4 - collaborators
        #
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/repos/show/' + githubUsername + '/' + githubRepoName + '/collaborators')
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        self.dataDict["collaborators"] = len(githubapiResp)-2 # Discard the ---- and the branches: text

        #
        # field5 - tagcount
        #
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/repos/show/' + githubUsername + '/' + githubRepoName + '/tags')
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        self.dataDict["tagcount"] = len(githubapiResp)-2 # Discard the ---- and the branches: text

        #
        # field6 - branchcount
        # curl http://github.com/api/v2/yaml/repos/show/schacon/ruby-git/branches
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/repos/show/' + githubUsername + '/' + githubRepoName + '/branches')
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        self.dataDict["branchcount"] = len(githubapiResp)-2 # Discard the ---- and the branches: text

        #
        # field7 - issuecount
        #
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/issues/list/' + githubUsername + '/' + githubRepoName + '/open')
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        self.dataDict["issuecount"] = len([elem for elem in githubapiResp if elem.find("number:") > -1])

        #
        # field8 - lastcommit
        # XXX This is kind of sucky and inefficient, and only shows commits on master
        githubapiReq = urllib2.urlopen('http://github.com' + githubApiURI + '/commits/list/' + githubUsername + '/' + githubRepoName + '/master')
        githubapiResp = [string.strip(elem) for elem in string.rsplit(githubapiReq.read(), '\n')]
        self.dataDict["lastcommit"] = string.replace(string.split([elem for elem in githubapiResp if elem.find("committed_date:") > -1][0])[1], '"', '')

        # Only clean this up after we are sure we are finished
        # grabbing data from the local clone
        # This won't work unless the directory in question is empty
        # utility method helps walk through and remove leaf nodes first
        # See: http://docs.python.org/library/os.html#os.rmdir
        self.removeDirUtil(self.workDir + "/githubdatasource.git")
        os.rmdir(self.workDir + "/githubdatasource.git")
        print "self.baseDir = %s"%(self.baseDir)
        os.chdir(self.baseDir) # Do this to get back to our original working directory
        print self.dataDict
        return self.dataDict

    def removeDirUtil(self, top):
        # Only do the cleanup inside of the workDir
        if top.find(self.workDir) > -1:
            print "Blowing away working dir " + self.workDir + "/" + top
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    joinedpath = os.path.join(root, name)
                    if os.path.islink(joinedpath):
                        os.remove(joinedpath)
                    else:
                        os.rmdir(joinedpath)

class githubDatasourcePluginTests(unittest.TestCase):
    aSponger = 0
    aDatasource = 0
    def setUp(self):
        print "Setting up"
        self.aSponger = sponger.Sponger()
        count = self.aSponger.initEnv("../../../examples/spongesite.conf")
        self.aDatasource = GithubDatasource(self.aSponger.spongeProjectEnv)
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