cmake_minimum_required(VERSION 2.8)
project(rosdoc_lite)
find_package(catkin REQUIRED)

catkin_package()

install(FILES DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}/cmake)

catkin_python_setup()

#----------------------------------------------------------------------
# customize uninstall target
#----------------------------------------------------------------------
configure_file(cmake_uninstall.cmake.in 
  "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
  IMMEDIATE @ONLY)

ADD_CUSTOM_TARGET(uninstall
  "${CMAKE_COMMAND}" -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")

