cmake_minimum_required(VERSION 2.8)
project(rosdoc_lite)
find_package(catkin REQUIRED)

catkin_package()

install(FILES DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}/cmake)

catkin_python_setup()
catkin_add_nosetests(test/test_doxygenator.py)
