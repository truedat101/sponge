import sys
import os
import unittest

class GithubDatasourcePlugin:
    #
    # TODO: Define Plugin Metadata
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
    def fetch_data(self):
        print "Fetching data"

class githubDatasourcePluginTests(unittest.TestCase):
    def setUp(self):
        print "Setting up"
    def testInitEnv(self):
        print "foo"
    def tearDown(self):
        print "tearing down"
if __name__ == '__main__':
    unittest.main()