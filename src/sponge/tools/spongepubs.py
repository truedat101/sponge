#!/usr/bin/env python
# encoding: utf-8
#
# spongepubs.py
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

r"""The idea behind Project Sponge is to provide some tools to measure an OSS project’s
vitality. The concept I will use is similar to an APGAR test when a baby is born. An
APGAR test checks the vitals several times after the birth (at birth, and then
throughout the next hour or two of life). For an OSS project, you should be checking
what I will call the Project Vitality: The vital stats and data showing how well an OSS
project is doing at a given point in time. Since Project Vitality can be a relative measure,
it is important to be able to compare the Project Vitality to past measurements. The Vitality
Dashboard is the visual report of Project Vitality over time. This is targeted at OSS project
leads, and specifically, to help commercial open source types to justify the open source approach
to management by promises to track progress using some reasonable metrics for success and signs
of life. Ideally, sponge can evolve into a sort of OSS Project Analytics tool.

python spongepubs.py -c [config file path]
    spongepubs reads in the config file and first generates a Sponger.soak() request to pull
    from various analytics sources.  It then generates a Sponger.squeeze() request to extract
    the analytics data and push it into the default publisher.  This is currently the only
    supported mode of execution.
examples:

    * python ScanReport.py ../../../../examples/spongesite.conf

"""
import sys
import getopt
from sponge.tools import sponger

class SpongePubs:

    def __init__(self):
        print "Executing Sponger for project"

    def main(argv):
        config = "../../../../examples/spongesite.conf" # Change this to any name by command line arg
        try:
            opts, args = getopt.getopt(argv, "hc:d", ["help", "config="])
        except getopt.GetoptError:
            print __doc__
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print __doc__
                sys.exit()
            elif opt == '-d':
                global _debug
                _debug = 1
            elif opt in ("-c","--config"):
                config = arg
        command = "".join(args) # We don't currently need this, but may use it later, putting it here before I forget
        mainSponger = sponger.Sponger()
        propsRead = mainSponger.initEnv(config)
        if (propsRead > 0):
            mainSponger.soak()
            mainSponger.squeeze()
        else:
            print "ERROR: No properties were read.  Go find out why."
    if __name__ == '__main__':
      main(sys.argv[1:])
    else:
      # This will be executed in case the
      #    source has been imported as a
      #    module.
      print "ERROR: Module should be run as a command line"
      system.exit(2)