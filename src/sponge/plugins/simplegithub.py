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
        return {'field1':['watchers','integer']}
    def fetch_data(self, plugindict):
        print "Fetching data"
        if plugindict is not None:
            gitcloneurl = plugindict['datasource.github.scm.uri']
        os.chdir(self.workDir)
        # Really need to decide if the host PATH should be used
        # or whether to pass this in as an argument
        print "about to run %s %s %s" %(self.binPath, gitcloneurl, self.workDir)
        subprocess.check_call([self.binPath + "/git", "clone", gitcloneurl, self.workDir + "/githubdatasource.git"])
        os.chdir(self.workDir + "/githubdatasource.git")
        commitCount = subprocess.call([self.binPath + "/git", "rev-list","--all","--reverse", ">", "/tmp/gitcommits.out"])
        # commitfile = os.open(self.workDir + "/githubdatasource.git/gitcommits.out", 'rU')
        # lines = commitFile.readlines()
        # if lines:
        #     self.dataDict["totalcommits"] = len(lines);
        # os.close(commitFile)
        self.dataDict["totalcommits"] = commitCount

        # XXX This won't work unless the directory in question is empty
        # See: http://docs.python.org/library/os.html#os.rmdir
        # os.rmdir(self.workDir + "/githubdatasource.git")
        print self.dataDict
        return self.dataDict
class githubDatasourcePluginTests(unittest.TestCase):
    def setUp(self):
        print "Setting up"
    def testInitEnv(self):
        print "foo"
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()