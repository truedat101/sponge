#!/usr/bin/env python
# encoding: utf-8
#
# Attribution:
# Linked from http://docs.python.org/library/shelve.html to
# Recipe 576642: DBM with Dict-speed accesses and Multiple standard file formats
# http://code.activestate.com/recipes/576642/
#
# License is not known, but we'll provide the  attribution, and
# look forward to maybe re-implementing this at some point with
# additional file formats, though (including a SQLite), but for now
# it is clean and hard to improve.
#
'''Alternate DB based on a dict subclass

Runs like gdbm's fast mode (all writes all delayed until close).
While open, the whole dict is kept in memory.  Start-up and
close time's are potentially long because the whole dict must be
read or written to disk.

Input file format is automatically discovered.
Output file format is selectable between pickle, json, and csv.
All three are backed by fast C implementations.

=========
CHANGELOG
=========
djk - change module name to lowercase dictdb, per PEP008
djk - add unittest and modify default handling to load the unit test
    if __main__, otherwise, move import as a regular package
djk - fixed a few 2.6-isms, mark as a todo item for later

'''

import pickle
# XXX TODO: enable once I get python2.6 working in EasyEclipse for Python
# import json
import csv
import os, shutil
import unittest

class DictDB(dict):

    def __init__(self, filename, flag=None, mode=None, format=None, *args, **kwds):
        self.flag = flag or 'c'             # r=readonly, c=create, or n=new
        self.mode = mode                    # None or octal triple like 0x666
        self.format = format or 'csv'       # csv, json, or pickle
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            # XXX This line is broken
            # 2.6 supported? file = __builtins__.open(filename, 'rb')
            file = open(filename, 'rb')
            try:
                self.load(file)
            finally:
                file.close()
        self.update(*args, **kwds)

    def sync(self):
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        # XXX: This line was broken
        # file = __builtins__.open(tempname, 'wb')
        file = open(tempname, 'wb')
        try:
            self.dump(file)
        except Exception:
            file.close()
            os.remove(tempname)
            raise
        file.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def dump(self, file):
        if self.format == 'csv':
            csv.writer(file).writerows(self.iteritems())
        elif self.format == 'json':
            # XXX renable with 2.6
            # json.dump(self, file, separators=(',', ':'))
            raise NotImplementedError('Unknown format: %r' % self.format)
        elif self.format == 'pickle':
            pickle.dump(self.items(), file, -1)
        else:
            raise NotImplementedError('Unknown format: %r' % self.format)

    def load(self, file):
        # try formats from most restrictive to least restrictive
        # XXX: Implement json with 2.6
        # for loader in (pickle.load, json.load, csv.reader):
        for loader in (pickle.load, csv.reader):

            file.seek(0)
            try:
                return self.update(loader(file))
            except Exception:
                pass
        raise ValueError('File not in recognized format')


def dbopen(filename, flag=None, mode=None, format=None):
    return DictDB(filename, flag, mode, format)

class dictdbTests(unittest.TestCase):
    dbref = 0
    def setUp(self):
        print "Setting up"
        # dbref = DictDB({})
    def testDryRun(self):
        import random
        os.chdir('/tmp')
        print(os.getcwd())
        s = dbopen('tmp.shl', 'c', format='csv')
        self.assert_(s is not None)
        print(s, 'start')
        s['abc'] = '123'
        s['rand'] = random.randrange(10000)
        s.close()
        # XXX This line was broken
        # f = __builtins__.open('tmp.shl', 'rb')
        f = open('tmp.shl', 'rb')
        self.assert_(f is not None)
        print (f.read())
        f.close()


if __name__ == '__main__':
    unittest.main() # From within the IDE or from the shell, we'll run tests automatically
else:
    pass # Module Imported by another module, which is what we want mostly