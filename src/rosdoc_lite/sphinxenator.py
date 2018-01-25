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

from __future__ import print_function

import os
import sys
from . import python_paths
from subprocess import Popen, PIPE
import rospkg


def generate_sphinx(path, package, manifest, rd_config, output_dir, quiet):
    """
    Main entrypoint into creating Sphinx documentation
    :return [str]: list of packages that were successfully generated
    """
    try:
        # check to see which directory index.rst/conf.py are rooted in
        if 'sphinx_root_dir' in rd_config:
            base_dir = os.path.join(path, rd_config['sphinx_root_dir'])
        else:
            base_dir = path
        if os.access(os.path.join(base_dir, "conf.py"), os.R_OK):
            oldcwd = os.getcwd()
            os.chdir(base_dir)
            try:
                paths = python_paths.generate_python_path(package, rospkg.RosPack(), manifest)
                env = os.environ.copy()
                additional_packages = [p for p in paths if os.path.exists(p)]
                if additional_packages:
                    env['PYTHONPATH'] = "%s:%s" % (os.pathsep.join(additional_packages), env['PYTHONPATH'])
                print ("Sphinx python path is: %s" % env['PYTHONPATH'])

                html_dir = os.path.join(oldcwd, output_dir, rd_config.get('output_dir', '.'))
                command = ['sphinx-build', '-a', '-E', '-b', 'html', '.', html_dir]
                print("sphinx-building %s [%s]" % (package, ' '.join(command)))
                print("  cwd is", os.getcwd())
                com = Popen(command, stdout=PIPE, env=env).communicate()
                print('stdout:')
                print(com[0])
                print('stderr')
                print(com[1])
            finally:
                # restore cwd
                os.chdir(oldcwd)
        else:
            print("ERROR: no conf.py for sphinx build of [%s]"%package, file=sys.stderr)
    finally:
        pass
