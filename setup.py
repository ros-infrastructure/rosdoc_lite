#!/usr/bin/env python

from __future__ import print_function
from distutils.core import setup
import sys
from xml.etree.ElementTree import ElementTree

try:
    root = ElementTree(None, 'stack.xml')
    version = root.findtext('version')
except Exception as e:
    print('Could not extract version from your stack.xml:\n%s' % e, file=sys.stderr)
    sys.exit(-1)

sys.path.insert(0, 'src')

setup(name = 'rosdoc_lite',
      version = version,
      packages = ['rosdoc_lite'],
      package_dir = {'rosdoc_lite': 'src/rosdoc_lite'},
      install_requires = ['rospkg', 'genmsg'],
      scripts = ['scripts/rosdoc_lite'],
      package_data = {'rosdoc_lite': ['templates/*']},
      author = "Ken Conley, Eitan Marder-Eppstein",
      author_email = "kwc@willowgarage.com",
      url = "http://www.ros.org/wiki/rosdoc_lite",
      download_url = "http://pr.willowgarage.com/downloads/rosdoc_lite/",
      keywords = ["ROS"],
      classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License" ],
      description = "ROS documentation generation",
      long_description = """\
Library and scripts for generating documentation from ROS packages
""",
      license = "BSD"
      )
