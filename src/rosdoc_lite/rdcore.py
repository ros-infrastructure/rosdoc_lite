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

