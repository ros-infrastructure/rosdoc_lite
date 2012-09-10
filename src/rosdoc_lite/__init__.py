#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id: __init__.py 16386 2012-02-25 18:54:45Z kwc $

import sys
import os
import time
import traceback
from subprocess import Popen, PIPE

NAME='rosdoc_lite'

from . import upload

#TODO Come back to support each plugin one by one
#from . import msgenator
#from . import epyenator
#from . import sphinxenator
#from . import landing_page
from . import doxygenator

import roslib

def get_optparse(name):
    """
    Retrieve default option parser for rosdoc. Useful if building an
    extended rosdoc tool with additional options.
    """
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] [paths]", prog=name)
    parser.add_option("-n", "--name",metavar="NAME",
                      dest="name", default="docs", 
                      help="Name for documentation set")
    parser.add_option("-q", "--quiet",action="store_true", default=False,
                      dest="quiet",
                      help="Suppress doxygen errors")
    parser.add_option("-o",metavar="OUTPUT_DIRECTORY",
                      dest="docdir", default='doc', 
                      help="directory to write documentation to")
    parser.add_option("--tags", metavar="TAGS", dest="tags", default=None,
                      help="Any tag file arguments to pass on to Doxygen")
    return parser
    
def generate_docs(path, package, manifest, output_dir, quiet=True):
    artifacts = []
    
    #plugins = [
    #    ('doygen', doxygenator.generate_doxygen),
    #    ('epydoc', epyenator.generate_epydoc),
    #    ('sphinx', sphinxenator.generate_sphinx),
    #    ('msg', msgenator.generate_msg_docs),
    #    ('landing-page', landing_page.generate_landing_page)
    #           ]

    plugins = [
        ('doygen', doxygenator.generate_doxygen)
               ]

    #TODO: Real values for this stuff
    rd_config = {}

    for plugin_name, plugin in plugins:
        start = time.time()
        try:
            artifacts.append(plugin(path, package, manifest, rd_config, output_dir))
        except Exception, e:
            traceback.print_exc()
            print >> sys.stderr, "plugin [%s] failed"%(plugin_name)
        timing = time.time() - start
            
    # support files
    # TODO: convert to plugin
    #start = time.time()
    #import shutil
    #for f in ['styles.css', 'msg-styles.css']:
    #    styles_in = os.path.join(ctx.template_dir, f)
    #    styles_css = os.path.join(ctx.docdir, f)
    #    print "copying",styles_in, "to", styles_css
    #    shutil.copyfile(styles_in, styles_css)
    #    artifacts.append(styles_css)
    #timings['support_files'] = time.time() - start

    return artifacts


def main():
    parser = get_optparse(NAME)
    options, args = parser.parse_args()

    if len(args) != 1:
        print "Please give %s exactly one path" % NAME
        parser.print_usage()
        sys.exit(1)

    path = args[0]

    manifest_path = os.path.join(path, 'manifest.xml')

    #Check to make sure that the path is a ROS package
    if not os.path.isfile(manifest_path):
        print "This tool is only meant to document ROS packages and requires that a manifest.xml file be present"
        print "Did not find %s" % manifest_path
        sys.exit(1)

    print "Found %s" % manifest_path
    manifest = roslib.manifest.parse_file(manifest_path)
    package = os.path.basename(path)
    print package

    try:
        artifacts = generate_docs(path, package, manifest, "docs")

        #start = time.time()
        #if options.upload:
        #    upload.upload(ctx, artifacts, options.upload)
        #ctx.timings['upload'] = time.time() - start

        #print "Timings"
        #for k, v in ctx.timings.iteritems():
        #    print " * %.2f %s"%(v, k)

    except:
        traceback.print_exc()
        sys.exit(1)
