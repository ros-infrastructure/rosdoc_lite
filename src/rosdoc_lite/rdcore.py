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

from catkin_pkg.package import Package, Export
import rospkg

#Helper object to pull the information rosdoc needs from both manifest and
#package objects

def convert_manifest_export(man_export):
    e = Export(man_export.tag, man_export.str)
    e.attributes = man_export.attrs
    return e

class PackageInformation(object):
    __slots__ = ['license', 'author', 'description', 'status', 'brief', 'url', 'is_catkin', 'exports', 'depends']

    def __init__(self, pkg_desc):
        if isinstance(pkg_desc, Package):
            self.create_from_package(pkg_desc)
        elif isinstance(pkg_desc, rospkg.Manifest):
            self.create_from_manifest(pkg_desc)

    def create_from_package(self, package):
        self.license = ', '.join(package.licenses)
        self.author =  ', '.join([('%s <%s>' % (a.name, a.email) if a.email is not None else a.name) for a in package.authors])
        self.description = package.description
        
        #we'll just use the first url with type website or the first URL of any type
        websites = [url.url for url in package.urls if url.type == 'website']
        if websites:
            self.url = websites[0]
        elif package.urls:
            self.url = package.urls[0].url

        self.is_catkin = True
        self.exports = package.exports
        self.status = None
        self.brief = None
        self.depends = []
        self.depends.extend([dep.name for dep in package.build_depends])
        self.depends.extend([dep.name for dep in package.buildtool_depends])
        self.depends.extend([dep.name for dep in package.run_depends])
        self.depends.extend([dep.name for dep in package.test_depends])

    def create_from_manifest(self, manifest):
        self.license = manifest.license
        self.author = manifest.author
        self.description = manifest.description
        self.status = manifest.status
        self.brief = manifest.brief
        self.url = manifest.url
        self.is_catkin = manifest.is_catkin
        self.exports = [convert_manifest_export(e) for e in manifest.exports]
        self.depends = [dep.name for dep in manifest.depends]
        self.depends.extend([dep.name for dep in manifest.rosdeps])

    def get_export(self, tag, attr):
        vals = [e.attributes[attr] for e in self.exports \
                if e.tagname == tag if e.attributes.has_key(attr)]
        return vals

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
import pkg_resources
import os

_TEMPLATES_DIR = 'templates'
_PACKAGE_NAME = 'rosdoc_lite'

def get_templates_dir():
    return pkg_resources.resource_filename(_PACKAGE_NAME, _TEMPLATES_DIR)

def load_tmpl(filename):
    filename = os.path.join(get_templates_dir(), filename)
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

