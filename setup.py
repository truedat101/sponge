#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

import sys
import os

import sponge.PkgInfo

if float("%d.%d" % sys.version_info[:2]) < 2.5:
	sys.stderr.write("Your Python version %d.%d.%d is not supported.\n" % sys.version_info[:3])
	sys.stderr.write("sponge requires Python 2.5 or newer.\n")
	sys.exit(1)

try:
	## Remove 'MANIFEST' file to force
	## distutils to recreate it.
	## Only in "sdist" stage. Otherwise
	## it makes life difficult to packagers.
	if sys.argv[1] == "sdist":
		os.unlink("MANIFEST")
except:
	pass

## Don't install manpages and docs when $sponge_PACKAGING is set
## This was a requirement of Debian package maintainer.
if not os.getenv("sponge_PACKAGING"):
	man_path = os.getenv("sponge_INSTPATH_MAN") or "share/man"
	doc_path = os.getenv("sponge_INSTPATH_DOC") or "share/doc/packages"
	data_files = [
		(doc_path+"/sponge", [ "README", "INSTALL", "NEWS" ]),
		(man_path+"/man1", [ "spongex.1" ] ),
	]
else:
	data_files = None

## XXX TODO: Fix the Topic
classifiers = [
    'Development Status :: 3 - Alpha'
  , 'Environment :: Console'
  , 'Intended Audience :: Developers'
  , 'License :: OSI Approved :: BSD License'
  , 'Natural Language :: English'
  , 'Operating System :: MacOS :: MacOS X'
  , 'Operating System :: POSIX'
  , 'Programming Language :: Python'
  , 'Topic :: Internet :: WWW/HTTP :: WSGI :: Server'
   ]

## Main distutils info
setup(
	## Content description
	name = sponge.PkgInfo.package,
	version = sponge.PkgInfo.version,
	## packages = [ 'sponge', 'sponge.tools' ],
	packages = find_packages(),
	scripts = ['spongex'],
	data_files = data_files,

	## Packaging details
	author = "David J. kordsmeier",
	author_email = "dkords@gmail.com",
	url = sponge.PkgInfo.url,
	license = sponge.PkgInfo.license,
	description = sponge.PkgInfo.short_description,
	long_description = """
%s

Authors:
--------
    David J. Kordsmeier <dkords@gmail.com>
""" % (sponge.PkgInfo.long_description)
	)
