cmake_minimum_required(VERSION 3.0.2)
project(rosdoc_lite)
find_package(catkin REQUIRED)

catkin_package()

install(FILES DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}/cmake)

catkin_python_setup()

if(CATKIN_ENABLE_TESTING)
  catkin_add_nosetests(test/test_doxygenator.py)
endif()

