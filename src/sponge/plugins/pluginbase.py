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

"""Abstract Base class to easily implement a Plugin for Sponge.  All methods are
abstract.  Develop a concrete implementation of this class, and add an
associated plugin into the conf file for your project.  This class cannot
be used directly.

XXX TODO: Document, define in docs the expected return types, purpose

Inspired by implementation of markupbase.ParserBase.py in 2.5

"""
import sys
import os

class PluginBase:

    def __init__(self, projectdict):
        if self.__class__ is PluginBase:
            raise RuntimeError(
                "sponge.plugins.PluginBase must be subclassed")
    def get_plugin_metadata(self):
        raise NotImplementedError(
            "subclasses of PluginBase must override error()") # XXX Can also pass...what makes most sense?
    def get_datasource_metadata(self):
        raise NotImplementedError(
            "subclasses of PluginBase must override error()")
    def fetch_data(self, plugindict):
        raise NotImplementedError(
            "subclasses of PluginBase must override error()")

    #
    # XXX This is convenient to have here, but think about moving
    # it into a utility module under sponge.utils
    #
    #
    def removeDirUtil(self, top):
        # Only do the cleanup inside of the workDir
        if top.find(self.workDir) > -1:
            print "Blowing away working dir " + self.workDir
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

