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
import yaml
from subprocess import Popen, PIPE

NAME='rosdoc_lite'

from . import upload

#TODO Come back to support each plugin one by one
#from . import msgenator
from . import epyenator
#from . import sphinxenator
#from . import landing_page
from . import doxygenator

import rospkg

def get_optparse(name):
    """
    Retrieve default option parser for rosdoc. Useful if building an
    extended rosdoc tool with additional options.
    """
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] [paths]", prog=name)
    parser.add_option("-q", "--quiet",action="store_true", default=False,
                      dest="quiet",
                      help="Suppress doxygen errors")
    parser.add_option("-o",metavar="OUTPUT_DIRECTORY",
                      dest="docdir", default='docs', 
                      help="directory to write documentation to")
    parser.add_option("--tags", metavar="TAGS", dest="tags", default=None,
                      help="Any tag file arguments to pass on to Doxygen")
    return parser

def load_rd_config(path, manifest):
    #load in any external config files
    rd_config = {}
    exported_configs = manifest.get_export('rosdoc', 'config')
    if exported_configs:
        #This just takes the last listed config export
        for exported_config in manifest.get_export('rosdoc', 'config'):
            try:
                exported_config = exported_config.replace('${prefix}', path)
                config_path = os.path.join(path, exported_config)
                with open(config_path, 'r') as config_file:
                    rd_config = yaml.load(config_file)
            except Exception as e:
                sys.stderr.write("ERROR: unable to load rosdoc config file [%s]: %s\n" % (config_path, str(e)))
    #we'll check if a 'rosdoc.yaml' file exists in the directory
    elif os.path.isfile(os.path.join(path, 'rosdoc.yaml')):
        with open(os.path.join(path, 'rosdoc.yaml'), 'r') as config_file:
            rd_config = yaml.load(config_file)

    return rd_config

def generate_build_params(rd_config, package):
    build_params = {}
    #if there's no config, we'll just build doxygen with the defaults
    if not rd_config:
        build_params['doxygen'] = {}
    #make sure that we have a valid rd_config
    elif type(rd_config) != list:
        sys.stderr.write("WARNING: package [%s] had an invalid rosdoc config\n"%(package))
        build_params['doxygen'] = {}
    #generate build parameters for the different types of builders
    else:
        try:
            for target in rd_config:
                print target
                build_params[target['builder']] = target
        except KeyError:
            sys.stderr.write("config file for [%s] is invalid, missing required 'builder' key\n"%(package))
        except:
            sys.stderr.write("config file for [%s] is invalid\n"%(package))
            raise

    return build_params
    
def generate_docs(path, package, manifest, output_dir, quiet=True):
    results = {}
    
    #plugins = [
    #    ('doygen', doxygenator.generate_doxygen),
    #    ('epydoc', epyenator.generate_epydoc),
    #    ('sphinx', sphinxenator.generate_sphinx),
    #    ('msg', msgenator.generate_msg_docs),
    #    ('landing-page', landing_page.generate_landing_page)
    #           ]

    plugins = [
        ('doxygen', doxygenator.generate_doxygen),
        ('epydoc', epyenator.generate_epydoc)
               ]

    #load any rosdoc configuration files
    rd_config = load_rd_config(path, manifest)

    #put the rd_config into a form that's easier to use with plugins
    build_params = generate_build_params(rd_config, package)

    print build_params

    for plugin_name, plugin in plugins:
        #check to see if we're supposed to build each plugin
        if plugin_name in build_params:
            start = time.time()
            try:
                plugin(path, package, manifest, build_params[plugin_name], output_dir, quiet)
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

def main():
    parser = get_optparse(NAME)
    options, args = parser.parse_args()

    if len(args) != 1:
        print "Please give %s exactly one path" % NAME
        parser.print_usage()
        sys.exit(1)

    path = args[0]

    manifest = rospkg.manifest.parse_manifest_file(path, 'manifest.xml')
    package = os.path.basename(path.strip('/'))
    print package

    try:
        generate_docs(path, package, manifest, options.docdir, options.quiet)

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
