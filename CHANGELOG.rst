Change history
==============

0.2.6 (2016-04-12)
------------------
* Support SEARCHENGINE option for doxygen
  Closes `#56 <https://github.com/ros-infrastructure/rosdoc_lite/issues/56>`_
* Contributors: Jack O'Quin, Kentaro Wada

0.2.5 (2015-02-28)
------------------

* Add autodoc to sphinx config.
* Use generator specific output folder.
* Move import to local scope, since when the new API is being invoked
  from jenkins_scripts genmsg is not on the Python path.
* Add API to provide generator specific output folders.
* Run epydoc in the package folder.
* Print output from epydoc invocation (fix `#50
  <https://github.com/ros-infrastructure/rosdoc_lite/issues/50>`_).
* Update doxygen template to disable external groups and pages.
* Update doxygen template to 1.8.6.
* Contributors: Dirk Thomas, Jack O'Quin, Jonathan Bohren

0.2.4 (2014-04-22)
------------------

* Groovy, Hydro and Indigo release.
* Introduce doxygen PREDEFINED tag (`#47`_).  Thanks to Fabien
  Spindler.
* Bugfix to enable devel space usage of rosdoc-lite, fixes `#44
  <https://github.com/ros-infrastructure/rosdoc_lite/issues/44>`_.
  Thanks to Daniel Stonier.
* Delete upload script which is not used anymore.  Its functionality
  is in `jenkins_scripts doc_stack.py`_
* Merge pull request `#41
  <https://github.com/ros-infrastructure/rosdoc_lite/issues/41>`_ to
  disable doxygen searchengine and latex generation.
* Update ros.org urls.
* Add list of actions to manifest.yaml after documenting them.
* Order list of documented msgs/srvs/actions.
* Add debug information to epyenator.
* Contributors: Daniel Stonier, Dirk Thomas, Fabien Spindler, Jack O'Quin, Tully Foote

0.2.3 (2013-08-02)
------------------

* Groovy and Hydro release.
* Working version of action documentation.
* Restore support for raw message comments in docs (`#29`_).

0.2.2 (2013-01-28)
------------------

* Groovy and Hydro release.
* Write information on deprecated packages to manifest.yaml.
* Updated package.xml with new <buildtool_depend>catkin<...>
  requirement.
* Now writes information about package maintainers to the manifest
  generated for the wiki.
* Adding bugtracker and repo_url fields to manifest generation.
* Adding a missing dep on python-catkin-pkg.
* Switching to python kitchen for unicode support to get around edge
  cases.
* Switching from abspath to realpath to make sure to handle symlinks
  correctly.
* Add docstrings.

0.2.1 (2012-10-24)
------------------

* Groovy release
* Updating so that dependencies are only listed once, regardless of
  how many times they appear in package.xml
* Updating so that ros-theme can be found
* Updating description in package.xml to be a bit more informative
* Adding proper export to rosdoc_lite
* Changing default doc directory to be doc
* Adding docs for rosdoc_lite

0.2.0 (2012-10-05)
------------------

* Initial Groovy release.
* Message generation now links to the proper place, but expansion
  commented out.
* Write manifest.yaml files for the wiki to use.
* Support both new package.xml and the old manifest.xml on Groovy.
* Port to Groovy catkin.

0.1.3 (2012-10-24)
------------------

* Fuerte release.
* Only list dependencies once, regardless of how many times they
  appear in package.xml.
* Updating so that ros-theme can be found.
* Adding proper export to manifest.xml.
* Changing default doc directory to be doc.
* For Fuerte, we need to pull the version of the package from
  stack.xml instead of package.xml.
* Refactoring so that epydoc and sphinx share the same Python path
  manipulation code.

0.1.2 (2012-10-05)
------------------

* Fuerte release.
* Message generation now links to the proper place, but commenting out
  expansion for now, also work towards writing manifest.yaml files for
  the wiki to use.
* Fixing a bug in converting from package.xml to rosdoc manifest format
* Just treat catkin stuff as non-catkin on Fuerte since those packages
  still have a manifest.  Fuerte catkin stacks do need to be on
  ``$ROS_PACKAGE_PATH`` to document.

0.1.1 (2012-09-28)
------------------

* minor Fuerte release.
* Fixing a bug with the way the python path was built for
  epydoc. Also, skipping documentation for messages that can't be
  found.
* Now handles when a given URL does not exist for a specified tagfile.

0.1.0 (2012-09-20)
------------------

* Initial release to Fuerte.
* Fix for rospkg dependency problem (`#1`_).
* Updating help to be more useful.
* Allow users to specify the location of tagfile output if they choose.
* Add support for tagfiles.
* Working towards catkinizing this stack.
* Removing leftover package dependencies, including roslib.
* Version of the message documentation that doesn't depend on roslib.
* Switching to package names for calling rosdoc_lite.
* Renaming ``rosdoc`` script to ``rosdoc_lite``.
* Making a ROS package, need some tools for message generation.

.. _`jenkins_scripts doc_stack.py`:
   https://github.com/ros-infrastructure/jenkins_scripts/blob/master/doc_stack.py
.. _`#1`: https://github.com/ros-infrastructure/rosdoc_lite/issues/1
.. _`#29`: https://github.com/ros-infrastructure/rosdoc_lite/issues/29
.. _`#47`: https://github.com/ros-infrastructure/rosdoc_lite/issues/47
