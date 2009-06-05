import sys
import os
import unittest

class GithubDatasourcePlugin:
    dataDict = {}
    dataSpec = {} # I'm thinking to use this to define what the data definition looks like
    workDir = "/tmp"
    #
    # TODO: Define Plugin Metadata
    #
    # At this point in time, the github api is limited.  I am trying to find out if there are
    # more private apis that can be used.
    #
    def __init__(self):
        print "Init GithubDatasourcePlugin..."
        #
        # TODO: Initialize Plugin Metadata
        #
    def get_plugin_metadata(self):
        return {'guid':1,'name':'GithubDataSourcePlugin', 'license':'gplv3'}
    def get_datasource_metadata(self):
        return {'field1':['watchers','integer']}
    def fetch_data(self, gitcloneurl):
        print "Fetching data"
        os.execv("git", ["clone", gitcloneurl, "/tmp/githubdatasource.git"])
        os.chdir("/tmp/githubdatasource.git")
        f = os.popen('git rev-list --all --reverse')
        dataDict["totalcommits"] = len(f);
        os.rmdir("/tmp/githubdatasource.git")
        return dataDict
class githubDatasourcePluginTests(unittest.TestCase):
    def setUp(self):
        print "Setting up"
    def testInitEnv(self):
        print "foo"
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()