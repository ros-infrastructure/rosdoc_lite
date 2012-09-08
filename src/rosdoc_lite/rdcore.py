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
# Revision $Id: rdcore.py 16386 2012-02-25 18:54:45Z kwc $

import os
import traceback
import sys
from subprocess import Popen, PIPE
import yaml

import roslib.packages
import roslib.manifest 
import roslib.rospack 
import roslib.stacks
import roslib.stack_manifest

class RosdocContext(object):
    
    def __init__(self, name, docdir, package_filters=None, path_filters=None):
        self.name = name
        self.package_filters = package_filters
        self.path_filters = []
        if path_filters:
            for p in path_filters.split(os.pathsep):
                if not p:
                    continue
                if not p.endswith(os.sep):
                    p = p + os.sep
                self.path_filters.append(p)
        self.docdir = docdir

        # these will be initialized in init()
        self.packages = {}
        self.stacks = {}        
        self.external_docs = {}
        self.manifests = {}
        self.stack_manifests = {}

        # - generally suppress output
        self.quiet = False
        # - for profiling
        self.timings = {}

        # advanced per-package config
        self.rd_configs = {} 

        self.template_dir = None

    def has_builder(self, package, builder):
        """
        @return: True if package is configured to use builder. NOTE:
        if there is no config, package is assumed to define a doxygen
        builder
        @rtype: bool
        """
        rd_config = self.rd_configs.get(package, None)
        if not rd_config:
            return builder == 'doxygen'
        if type(rd_config) != list:
            sys.stderr.write("WARNING: package [%s] has an invalid rosdoc config\n"%(package))
            return False            
        try:
            return len([d for d in rd_config if d['builder'] == builder]) > 0
        except KeyError:
            sys.stderr.write("config file for [%s] is invalid, missing required 'builder' key\n"%(package))
            return False
        except:
            sys.stderr.write("config file for [%s] is invalid\n"%(package))
            return False
            
    def should_document(self, package):
        """
        @return: True if package should be documented
        @rtype: bool
        """
        if not package in self.packages:
            return False
        # package filters override all 
        if self.package_filters:
            return package in self.package_filters
        # don't document if not in path filters
        if self.path_filters:
            package_path = self.packages[package]
            if not [p for p in self.path_filters if package_path.startswith(p)]:
                return False
        # TODO: don't document if not in requested stack
        return True

    def init(self):
        if not self.quiet:
            print "initializing rosdoc context:\n\tpackage filters: %s\n\tpath filters: %s"%(self.package_filters, self.path_filters)
        
        rosdoc_dir = roslib.packages.get_pkg_dir('rosdoc')
        self.template_dir = os.path.join(rosdoc_dir, 'templates')

        # use 'rospack list' to locate all packages and store their paths in a dictionary
        rospack_list = roslib.rospack.rospackexec(['list']).split('\n')
        rospack_list = [x.split(' ') for x in rospack_list if ' ' in x]

        # I'm still debating whether or not to immediately filter
        # these. The problem is that a package that is within the
        # filter may reference packages outside that filter. I'm not
        # sure if this is an issue or not.
        packages = self.packages
        for package, path in rospack_list:
            packages[package] = path

        # cache all stack manifests due to issue with empty stacks not being noted by _crawl_deps
        stack_manifests = self.stack_manifests
        rosstack_list = roslib.rospack.rosstackexec(['list']).split('\n')
        rosstack_list = [x.split(' ') for x in rosstack_list if ' ' in x]
        for stack, path in rosstack_list:

            f = os.path.join(path, roslib.stack_manifest.STACK_FILE)
            try:
                stack_manifests[stack] = roslib.stack_manifest.parse_file(f)
            except:
                traceback.print_exc()
                print >> sys.stderr, "WARN: stack '%s' does not have a valid stack.xml file, manifest information will not be included in docs"%stack

        self.doc_packages = [p for p in packages if self.should_document(p)]
        self._crawl_deps()
        
    def _crawl_deps(self):
        """
        Crawl manifest.xml dependencies
        """
        external_docs = self.external_docs
        manifests = self.manifests
        rd_configs = self.rd_configs

        stacks = self.stacks = {}

        # keep track of packages with invalid manifests so we can unregister them
        bad = []
        for package, path in self.packages.iteritems():

            # find stacks to document on demand
            if self.should_document(package):
                if not self.quiet:
                    print "+package[%s]"%(package)
                stack = roslib.stacks.stack_of(package) or ''
                if stack and stack not in stacks:
                    #print "adding stack [%s] to documentation"%stack
                    try:
                        p = roslib.stacks.get_stack_dir(stack)
                        stacks[stack] = p
                    except:
                        sys.stderr.write("cannot locate directory of stack [%s]\n"%(stack))
                
            f = os.path.join(path, roslib.manifest.MANIFEST_FILE)
            try:
                manifests[package] = m = roslib.manifest.parse_file(f)

                if self.should_document(package):
                    #NOTE: the behavior is undefined if the users uses
                    #both config and export properties directly

                    # #1650 for backwards compatibility, we read the old
                    # 'doxymaker' tag, which is deprecated
                    #  - this is a loop but we only accept one value
                    for e in m.get_export('doxymaker', 'external'):
                        external_docs[package] = e
                    for e in m.get_export('rosdoc', 'external'):
                        external_docs[package] = e

                    # load in any external config files
                    # TODO: check for rosdoc.yaml by default
                    for e in m.get_export('rosdoc', 'config'):
                        try:
                            e = e.replace('${prefix}', path)
                            config_p = os.path.join(path, e)
                            with open(config_p, 'r') as config_f:
                                rd_configs[package] = yaml.load(config_f)
                        except Exception as e:
                            sys.stderr.write("ERROR: unable to load rosdoc config file [%s]: %s\n"%(config_p, str(e)))
                    
            except:
                if self.should_document(package):
                    sys.stderr.write("WARN: Package '%s' does not have a valid manifest.xml file, manifest information will not be included in docs\n"%(package))
                bad.append(package)

        for b in bad:
            if b in self.packages:
                del self.packages[b]
        stack_manifests = self.stack_manifests
        for stack, path in stacks.iteritems():
            if not self.quiet:
                print "+stack[%s]"%(stack)

def compute_relative(src, target):
    s1, s2 = [p.split(os.sep) for p in [src, target]]
    #filter out empties
    s1, s2 = filter(lambda x: x, s1), filter(lambda x: x, s2)
    i = 0
    while i < min(len(s1), len(s2)):
        if s1[i] != s2[i]:
            break
        i+=1
    rel = ['..' for d in s1[i:]] + s2[i:]
    return os.sep.join(rel)

def html_path(package, docdir):
    return os.path.join(docdir, package, 'html')


################################################################################
# TEMPLATE ROUTINES

_TEMPLATES_DIR = 'templates'

def load_tmpl(filename):
    filename = os.path.join(roslib.packages.get_pkg_dir('rosdoc'), _TEMPLATES_DIR, filename)
    if not os.path.isfile(filename):
        sys.stderr.write("Cannot locate template file '%s'\n"%(filename))
        sys.exit(1)
    with open(filename, 'r') as f:
        str = f.read()
        if not str:
            sys.stderr.write("Template file '%s' is empty\n"%(filename))
            sys.exit(1)
        return str

def instantiate_template(tmpl, vars):
    for k, v in vars.iteritems():
        tmpl = tmpl.replace(k, str(v).encode('utf-8'))
    return tmpl

