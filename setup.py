#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rosdoc_lite'],
    package_dir={'': 'src'},
    scripts=['scripts/rosdoc_lite'],
    package_data={'rosdoc_lite': ['templates/*',
                                  'templates/swagger-ui/*',
                                  'templates/swagger-ui/dist/*',
                                  'templates/swagger-ui/dist/css/*',
                                  'templates/swagger-ui/dist/fonts/*',
                                  'templates/swagger-ui/dist/langs/*',
                                  'templates/swagger-ui/dist/images/*',
                                  'templates/swagger-ui/dist/lib/*'
                                  # skipping other swagger dirs, they are not needed
                                  ]
                  }
)

setup(**d)
