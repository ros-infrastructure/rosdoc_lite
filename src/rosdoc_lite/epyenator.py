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

from __future__ import with_statement

import os, sys
from subprocess import Popen, PIPE
import rospkg

def get_non_catkin_depends(package, rospack):
    vals = rospack.get_depends(package, implicit=True)
    return [v for v in vals if not rospack.get_manifest(v).is_catkin]

def append_package_paths(manifest, paths, pkg_dir):
    """
    Added paths for package to paths
    :param manifest_: package manifest, ``Manifest``
    :param pkg_dir: package's filesystem directory path, ``str``
    :param paths: list of paths, ``[str]``
    """
    exports = manifest.get_export('python','path')
    if exports:
        for export in exports:
            if ':' in export:
                export = export.split(':')
            else:
                export = [export]
            for e in export:
                paths.append(e.replace('${prefix}', pkg_dir))
    else:
        dirs = [os.path.join(pkg_dir, d) for d in ['src', 'lib']]
        paths.extend([d for d in dirs if os.path.isdir(d)])
    
def generate_python_path(pkg, rospack):
    """
    Recursive subroutine for building dependency list and python path
    :raises: :exc:`rospkg.ResourceNotFound` If an error occurs while attempting to load package or dependencies
    """
    # short-circuit if this is a catkin-ized package
    m = rospack.get_manifest(pkg)
    if m.is_catkin:
        return []

    packages = get_non_catkin_depends(pkg, rospack) 
    packages.append(pkg)

    paths = []
    try:
        for p in packages:
            m = rospack.get_manifest(p)
            d = rospack.get_path(p)
            append_package_paths(m, paths, d)
    except:
        raise
    return paths

## Main entrypoint into creating Epydoc documentation
def generate_epydoc(path, package, manifest, rd_config, output_dir, quiet):
    #make sure that we create docs in a subdirectory if requested
    html_dir = os.path.join(output_dir, rd_config.get('output_dir', '.'))

    try:
        if not os.path.isdir(html_dir):
            os.makedirs(html_dir)
            
        command = ['epydoc', '--html', package, '-o', html_dir]
        if 'exclude' in rd_config:
            for s in rd_config['exclude']:
                command.extend(['--exclude', s])

        if 'config' in rd_config:
            command.extend(['--config', os.path.join(path, rd_config['config']) ])
        else:
            # default options
            command.extend(['--inheritance', 'included', '--no-private'])
        
        # determine the python path of the package
        paths = generate_python_path(package, rospkg.RosPack())
        env = os.environ.copy()
        additional_packages = [p for p in paths if os.path.exists(p)]
        if additional_packages:
            env['PYTHONPATH'] = "%s:%s" % (os.pathsep.join(additional_packages), env['PYTHONPATH'])

        if not quiet:
            print "epydoc-building %s [%s]"%(package, ' '.join(command))
        Popen(command, stdout=PIPE, env=env).communicate()
    except Exception, e:
        print >> sys.stderr, "Unable to generate epydoc for [%s]. This is probably because epydoc is not installed.\nThe exact error is:\n\t%s"%(package, str(e))
        raise
