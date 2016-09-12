# Software License Agreement (BSD License)
#
# Copyright (c) 2016, Yujin Robot
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

import errno
import fnmatch
import json
import os
import re
import shutil
import tempfile
import termcolor
import yaml

from . import exceptions


def generate_swagger(path, package, manifest, rd_config, output_dir, quiet):
    """
    Main entrypoint into creating Swagger documentation
    """
    ######################
    # Configuration
    ######################
    env_resources_directory = os.environ.get('ROSDOC_SWAGGER_RESOURCES_DIR')  # returns None if not found
    if 'destination_directory' in rd_config:
        base_dir = os.path.join(path, rd_config['destination_directory']) if 'destination_directory' in rd_config else path
    else:
        base_dir = path
    if env_resources_directory is not None:
        resources_directory = env_resources_directory
    elif 'resources_directory' in rd_config:
        resources_directory = rd_config['resources_directory']
    else:
        resources_directory = os.path.join(os.path.dirname(__file__), 'templates', 'swagger-ui')
        if not os.path.isfile(os.path.join(resources_directory, 'dist', 'index.html')):
            raise exceptions.PluginException("swagger resources haven't been downloaded, did you 'git clone --recursive?'".format(resources_directory))

    ######################
    # Debugging
    ######################
    if not quiet:
        print("")
        termcolor.cprint("Generate Swagger", 'white', attrs=['bold'])
        print("")
        pretty_print_key_value("Package", package, indent=2)
        pretty_print_key_value("Path", path, indent=2)
        pretty_print_key_value("Manifest", manifest, indent=2)
        pretty_print_key_value("Rosdoc config", rd_config, indent=2)
        pretty_print_key_value("Output Dir", output_dir, indent=2)
        pretty_print_key_value("Resources Dir", resources_directory, indent=2)

    ######################
    # Checks
    ######################
    if not os.path.isdir(resources_directory):
        raise exceptions.PluginException("'{0}' does not exist.".format(resources_directory))

    if not os.path.isfile(os.path.join(resources_directory, 'dist', 'index.html')):
        raise exceptions.PluginException("'{0}' does not seem to be a valid clone/copy of the swagger-ui repository.".format(resources_directory))

    yaml_filename_list = find_swagger_yaml_definitions(path)
    ######################
    # YAML Hunting
    ######################
    for yaml_filename in yaml_filename_list:
        if not quiet:
            pretty_print_key_value("REST API Spec", yaml_filename, indent=2)

        ######################
        # YAML 2 JSON
        ######################
        with open(yaml_filename, 'r') as yaml_file:
            yaml_file_text = yaml_file.read().replace("'", "")
            python_content = yaml.load(yaml_file_text)  # store yaml content into a dictionary
            name = os.path.splitext(os.path.basename(yaml_filename))[0]
        json_content = json.dumps(python_content)

        ######################
        # Generating Swagger
        ######################
        destination_directory = os.path.join(os.path.join(base_dir, 'html'), name)
        create_swagger_documentation_folder(destination_directory, resources_directory)

        index_html_path = os.path.join(destination_directory, 'index.html')

        title_pattern = re.compile("<title>.*</title>")
        new_title = '<title>{0}</title>'.format(name).title()
        tmp_index_html_filehandle, tmp_index_html_path = tempfile.mkstemp()
        with open(tmp_index_html_path, 'w') as new_html_file:
            with open(index_html_path, 'r') as old_html_file:
                for line in old_html_file:
                    line = re.sub(title_pattern, new_title, line)
                    if "dom_id" in line:
                        new_html_file.write("        spec: JSON.parse($('#json_rest_api').html()),")
                    if "<head>" in line:
                        new_html_file.write('  <script id="json_rest_api" type="application/json">{0}</script>'.format(json_content))
                    new_html_file.write(line)

        os.close(tmp_index_html_filehandle)
        os.remove(index_html_path)
        shutil.move(tmp_index_html_path, index_html_path)
        os.chmod(index_html_path, 0664)
    if not quiet:
        print("")


def is_swagger_yaml(filename):
    """
    Quite a poor man's check to see whether the yaml is a swagger file or not.
    """
    contents = yaml.load(open(filename))
    return (isinstance(contents, dict) and 'swagger' in contents.keys())


def find_swagger_yaml_definitions(package_dir):
    """
    Walk a specified directory and its subdirectories looking for swagger
    definition files. These are identified by:

    :param str package_dir:
    :returns [filenames]: list of swagger yaml definition filenames (absolute paths)
    """

    matches = []
    for root, unused_dirnames, filenames in os.walk(package_dir):
        for filename in fnmatch.filter(filenames, '*.yaml'):
            yaml_filename = os.path.join(root, filename)
            if is_swagger_yaml(yaml_filename):
                matches.append(yaml_filename)
    return matches


def create_swagger_documentation_folder(destination_directory, resources_directory):
    """
    Copy all the swagger files in the templates 'swagger-ui' subfolder across to the target
    directory (eventual doc directory).
    :param str destination_directory: usually something like 'doc/<name of yaml>'.
    """
    # only use the resources from the swagger-ui dist directory
    dist_directory = os.path.join(resources_directory, 'dist')
    mkdir_p(destination_directory)
    for root, dirnames, filenames in os.walk(dist_directory):
        for d in dirnames:
            mkdir_p(os.path.join(destination_directory, d))
        for filename in filenames:
            full_filename = os.path.join(root, filename)
            if (os.path.isfile(full_filename)):
                shutil.copy(full_filename, os.path.join(destination_directory, os.path.relpath(root, dist_directory)))


def pretty_print_key_value(key, value, indent):
    pretty_print_key_value_with_attributes(key, value, indent, attrs=[])


def pretty_print_key_value_with_attributes(key, value, indent, attrs):
    print(termcolor.colored(" " * indent + "{0: <{width}}".format(key, width=(17 - indent)), 'cyan', attrs=attrs) + ": " + termcolor.colored("{0}".format(value), 'yellow'))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
