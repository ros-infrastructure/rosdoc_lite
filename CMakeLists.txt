cmake_minimum_required(VERSION 2.8)
project(rosdoc_lite)
find_package(catkin REQUIRED)

catkin_stack()
catkin_project(rosdoc_lite)

install(FILES DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}/cmake)

catkin_python_setup()

#catkin_add_nosetests(${PROJECT_SOURCE_DIR})
