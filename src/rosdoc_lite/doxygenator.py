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
import tempfile
import shutil

from . import rdcore

def run_doxygen(package, doxygen_file, quiet=False):
    try:
        command = ['doxygen', doxygen_file]
        if quiet:
            Popen(command, stdout=PIPE, stderr=PIPE).communicate()
        else:
            print "doxygen-ating %s [%s]"%(package, ' '.join(command))
            Popen(command, stdout=PIPE).communicate()            
    except OSError, (errno, strerr):
        #fatal        
        print """\nERROR: It appears that you do not have doxygen installed.
If you are on Ubuntu/Debian, you can install doxygen by typing:

   sudo apt-get install doxygen
"""
        sys.exit(1) 

## utility to write string data to files and handle unicode 
def write_to_file(f, tmpl):
    try:
        if type(tmpl) == str:
            f.write(tmpl)
        else: #iso-8859-1 is the declared encoding of doxygen
            f.write(tmpl.encode('utf-8'))
        f.flush()
    except:
        print "ERROR, f[%s], tmpl[%s]"%(f, tmpl)
        raise

def load_manifest_vars(rd_config, package, manifest):
    author = license = description = status = brief = ''
    
    # by default, assume that packages are on wiki
    home_url = 'http://ros.org/wiki/%s'%package
    home_url = rd_config.get('homepage', home_url)

    project_link = '<a href="%s">%s</a>'%(home_url, package)
    if manifest is not None:
        license = manifest.license or ''
        author = manifest.author or ''
        description = manifest.description or ''
        status = manifest.status or ''

        if manifest.brief:
            brief = ": "+manifest.brief
    else:
        print "no manifest [%s]"%(package)

    return {'$package': package,
            '$projectlink': project_link, '$license': license,
            '$description': description, '$brief': brief,
            '$author': author, '$status':status
            }

def package_doxygen_template(template, rd_config, path, package, html_dir, header_filename, footer_filename):
    # set defaults for overridable keys
    file_patterns = '*.c *.cpp *.h *.cc *.hh *.hpp *.py *.dox *.java'
    excludes = '%s/build/'%path

    # example path is where htmlinclude operates
    dvars = { '$INPUT':  path, '$PROJECT_NAME': package,
              '$EXCLUDE_PROP': rd_config.get('exclude', excludes),
              '$FILE_PATTERNS': rd_config.get('file_patterns', file_patterns),
              '$EXCLUDE_PATTERNS': rd_config.get('exclude_patterns', ''),
              '$HTML_OUTPUT': os.path.abspath(html_dir),
              '$HTML_HEADER': header_filename, '$HTML_FOOTER': footer_filename,
              '$OUTPUT_DIRECTORY': html_dir,
              '$JAVADOC_AUTOBRIEF': rd_config.get('javadoc_autobrief', 'NO'),
              '$MULTILINE_CPP_IS_BRIEF': rd_config.get('multiline_cpp_is_brief', 'NO'),
              '$TAB_SIZE': rd_config.get('tab_size', '8'),
              '$ALIASES': rd_config.get('aliases', ''),
              '$EXAMPLE_PATTERNS': rd_config.get('example_patterns', ''),
              '$IMAGE_PATH': rd_config.get('image_path', path), #default to $INPUT
              '$EXCLUDE_SYMBOLS': rd_config.get('exclude_symbols', ''),
              }
    return rdcore.instantiate_template(template, dvars)

## Main entrypoint into creating Doxygen documentation
## @return bool: True if documentation was successful, false otherwise
def generate_doxygen(path, package, manifest, rd_config, html_dir):
    success = True
    #TODO Check if user wants to run this builder

    # Configuration Properties (all optional):
    #
    # html_dir: directory_name (default: '.')
    # name: Documentation Set Name (default: Doxygen API)
    files = []
    #try:
    if not os.path.isdir(html_dir):
        os.makedirs(html_dir)

    #Create files to write for doxygen generation
    header_file = tempfile.NamedTemporaryFile('w+')
    footer_file = tempfile.NamedTemporaryFile('w+')
    doxygen_file = tempfile.NamedTemporaryFile('w+')
    files = [header_file, footer_file, doxygen_file]

    #Generate our Doxygen templates and fill them in with the right info
    doxy_template = rdcore.load_tmpl('doxy.template')
    doxy = package_doxygen_template(doxy_template, rd_config, path, package, html_dir, header_file.name, footer_file.name)

    header_template = rdcore.load_tmpl('header.html')
    footer_template = rdcore.load_tmpl('footer.html')
    manifest_vars = load_manifest_vars(rd_config, package, manifest)
    header, footer = [rdcore.instantiate_template(t, manifest_vars) for t in [header_template, footer_template]]

    #Actually write files to disk so that doxygen can find them and use them
    for f, tmpl in zip(files, [header, footer, doxy]):
        write_to_file(f, tmpl)

    # doxygenate
    run_doxygen(package, doxygen_file.name)

    #except Exception, e:
    #    print >> sys.stderr, "ERROR: Doxygen of package [%s] failed: %s"%(package, str(e))
    #    raise e
    #    success = False
    #finally:
    #    for f in files:
    #        f.close()

    return success
