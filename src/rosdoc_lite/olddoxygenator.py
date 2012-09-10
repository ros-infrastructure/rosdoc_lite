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
# Revision $Id: doxygenator.py 16736 2012-05-29 17:17:32Z kwc $

from distutils.version import StrictVersion
from subprocess import Popen, PIPE
import shutil
import tempfile
import shutil 

## @param package str: package name
## @param rd_config dict: rosdoc configuration parameters for this doxygen build
## @param m Manifest : package manifest
## @param html_dir str: directory to store doxygen files                    
def create_package_template(package, rd_config, m, path, html_dir,
                            header_filename, footer_filename, example_path):
    # TODO: replace with general purpose key/value parser/substitution

    # set defaults for overridable keys
    file_patterns = '*.c *.cpp *.h *.cc *.hh *.hpp *.py *.dox *.java'
    excludes = '%s/build/'%path
    exclude_patterns = ''

    # last one wins
    for e in m.get_export('doxygen', 'excludes'):
        # prepend the packages path
        excludes = '%s/%s'%(path, e)

    # last one wins        
    for e in m.get_export('doxygen', 'file-patterns'):
        file_patterns = e

    # rd_config take precedence. default to empty dir so vars logic below works
    if not rd_config:
        rd_config = {}
       
    include_path = roslib.rospack.rospackexec(['cflags-only-I',package])

    # example path is where htmlinclude operates
    dvars = { '$INPUT':  path, '$PROJECT_NAME': package,
              '$EXAMPLE_PATH': "%s %s"%(path, example_path),
              '$EXCLUDE_PROP': rd_config.get('exclude', excludes),
              '$FILE_PATTERNS': rd_config.get('file_patterns', file_patterns),
              '$EXCLUDE_PATTERNS': rd_config.get('exclude_patterns', ''),
              '$HTML_OUTPUT': os.path.abspath(html_dir),
              '$HTML_HEADER': header_filename, '$HTML_FOOTER': footer_filename,
              '$OUTPUT_DIRECTORY': html_dir,
              '$INCLUDE_PATH': include_path,

              '$JAVADOC_AUTOBRIEF': rd_config.get('javadoc_autobrief', 'NO'),
              '$MULTILINE_CPP_IS_BRIEF': rd_config.get('multiline_cpp_is_brief', 'NO'),
              '$TAB_SIZE': rd_config.get('tab_size', '8'),
              '$ALIASES': rd_config.get('aliases', ''),
              '$EXAMPLE_PATTERNS': rd_config.get('example_patterns', ''),
              '$IMAGE_PATH': rd_config.get('image_path', path), #default to $INPUT
              '$EXCLUDE_SYMBOLS': rd_config.get('exclude_symbols', ''),
              }
    return instantiate_template(doxy_template, dvars)

## Processes manifest for package and then generates templates for
## header, footer, and manifest include file
## @param package: package to create templates for
## @type  package: str
## @param rd_config: rosdoc configuration dictionary
## @type  rd_config: dict
## @param path: file path to package
## @type  path: str
## @param m: package manifest or None
## @type  m: manifest.Manifest
## @return: header, footer, manifest
## @rtype: (str, str, str)
def load_manifest_vars(ctx, rd_config, package, path, docdir, package_htmldir, m):
    author = license = description = status = notes = li_vc = li_url = brief = ''
    
    # by default, assume that packages are on wiki
    home_url = 'http://ros.org/wiki/%s'%package

    if rd_config:
        if 'homepage' in rd_config:
            home_url = rd_config['homepage']
            
    project_link = '<a href="%s">%s</a>'%(home_url, package)
    if m is not None:
        license = m.license or ''
        author = m.author or ''
        description = m.description or ''
        status = m.status or ''
        notes = m.notes or ''

        if m.brief:
            brief = ": "+m.brief

        li_url = '<li>Homepage: <a href=\"%s\">%s</a></li>'%(m.url, m.url)
        if m.versioncontrol:
            vcurl = m.versioncontrol.url
            li_vc = '<li>Version Control (%s): <a href="%s">%s</a></li>'%(m.versioncontrol.type, vcurl, vcurl)
    else:
        print "no manifest [%s]"%(package)

    # include links to msgs/srvs
    msgs = roslib.msgs.list_msg_types(package, False)
    srvs = roslib.srvs.list_srv_types(package, False)
        
    return {'$package': package,
            '$projectlink': project_link, '$license': license,
            '$description': description, '$brief': brief,
            '$author': author, '$status':status, 
            '$notes':notes, '$li_vc': li_vc, '$li_url': li_url,
            }

## utility to write string data to files and handle unicode 
def _write_to_file(f, tmpl):
    try:
        if type(tmpl) == str:
            f.write(tmpl)
        else: #iso-8859-1 is the declared encoding of doxygen
            f.write(tmpl.encode('utf-8'))
        f.flush()
    except:
        print "ERROR, f[%s], tmpl[%s]"%(f, tmpl)
        raise
    
def get_doxygen_version():
    try:
        command = ['doxygen', '--version']
        version = Popen(command, stdout=PIPE, stderr=PIPE).communicate()[0].strip()
    except:
        version = None
    return version
        
# #3870: doxygen changed their template file syntax in a 'patch'
# version.  It's a bit ugly to inline this on import, but this entire
# generator needs to be rewritten.
def header_template_name():
    doxygen_version = get_doxygen_version()
    # doxygen not available
    if doxygen_version is None:
        return None
    doxygen_version_splitted = doxygen_version.split('.')
    major = doxygen_version_splitted[0]
    minor = doxygen_version_splitted[1]
    patch = doxygen_version_splitted[2]
    if len(doxygen_version_splitted) > 3:
        build = doxygen_version_splitted[3]
    # > 1.7.3 doxygen changed the template syntax
    if StrictVersion('%s.%s.%s'%(major, minor, patch)) > StrictVersion('1.7.3'):
        return 'header-1.7.4.html'
    else:
        return 'header.html'


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

## Main entrypoint into creating doxygen files
## @return [str]: list of directories in which documentation was generated (aka the list of successful packages)
def generate_doxygen(path):
    #TODO: Include tag files for external docs to do cross referencing
    
    # setup temp directory
    example_path = tempfile.mkdtemp(prefix='rosdoc_doxygen')

    success = []
    
    dir = ctx.docdir
    # dictionary mapping packages to paths
    packages = ctx.packages
    # list of packages that we are documenting
    doc_packages = ctx.doc_packages
    external_docs = ctx.external_docs
    rd_configs = ctx.rd_configs
    manifests = ctx.manifests

    tmpls = [header_template, footer_template, manifest_template]
    try:
        for package, path in packages.iteritems():
            if not package in doc_packages or \
                   not ctx.has_builder(package, 'doxygen'):
                continue

            # the logic for the doxygen builder is different from
            # others as doxygen is the default builder if no config is
            # declared
            rd_config = rd_configs.get(package, None)
            if rd_config:
                # currently only allow one doxygen build per package. This is not inherent, it
                # just requires rewriting higher-level logic
                rd_config = [d for d in ctx.rd_configs[package] if d['builder'] == 'doxygen'][0]

            # Configuration (all are optional)
            #
            # name: Documentation set name (e.g. C++ API)
            # output_dir: Directory to store files (default '.')
            # file_patterns: override FILE_PATTERNS
            # excludes: override EXCLUDES
            
            # doxygenator currently does some non-doxygen work.
            # pkg_doc_dir is the pointer to the directory for these non-doxygen
            # tools. html_dir is the path for doxygen
            pkg_doc_dir = html_path(package, ctx.docdir)
                
            # compute the html directory for doxygen
            html_dir = html_path(package, ctx.docdir)
            if rd_config and 'output_dir' in rd_config:
                html_dir = os.path.join(html_dir, rd_config['output_dir'])

            # have to makedirs for external packages
            if not os.path.exists(pkg_doc_dir):
                os.makedirs(pkg_doc_dir)
                    
            files = []
            try:
                header_file = tempfile.NamedTemporaryFile('w+')
                footer_file = tempfile.NamedTemporaryFile('w+')
                doxygen_file = tempfile.NamedTemporaryFile('w+')
                manifest_file = open(os.path.join(example_path, 'manifest.html'), 'w')
                files = [header_file, footer_file, manifest_file, doxygen_file]
                to_delete = [manifest_file]

                # create the doxygen templates and wiki header

                # - instantiate the templates
                manifest_ = manifests[package] if package in manifests else None

                vars = load_manifest_vars(ctx, rd_config, package, path, dir, html_dir, manifest_)
                header, footer, manifest_html = [instantiate_template(t, vars) for t in tmpls]

                if package not in external_docs:
                    doxy = \
                        create_package_template(package, rd_config, manifest_,
                                                path, html_dir,
                                                header_file.name, footer_file.name,
                                                example_path)
                    for f, tmpl in zip(files, [header, footer, manifest_html, doxy]):
                        _write_to_file(f, tmpl)
                    # doxygenate
                    run_doxygen(package, doxygen_file.name, quiet=quiet)
                        
                # support files (stylesheets)
                dstyles_in = os.path.join(ctx.template_dir, 'doxygen.css')
                dstyles_css = os.path.join(html_dir, 'doxygen.css')
                shutil.copyfile(dstyles_in, dstyles_css)

                success.append(package)
            except Exception as e:
                print >> sys.stderr, "ERROR: Doxygen of package [%s] failed: %s"%(package, str(e))
            finally:
                for f in files:
                    f.close()
    finally:
        shutil.rmtree(example_path)
    return success


doxy_template = load_tmpl('doxy.template')

header_template_filename = header_template_name()
if header_template_filename is None:
    raise Exception("Doxygen is not installed.  Please install it to continue.")
else:
    header_template = load_tmpl(header_template_filename)
    footer_template = load_tmpl('footer.html')
    manifest_template = load_tmpl('manifest.html')
