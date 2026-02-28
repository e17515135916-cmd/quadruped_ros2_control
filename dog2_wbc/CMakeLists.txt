cmake_minimum_required(VERSION 3.8)
project(dog2_wbc)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -std=c++17)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# Include directories
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
)

# WBC Controller library
add_library(wbc_controller
  src/wbc_controller.cpp
)
target_include_directories(wbc_controller PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(wbc_controller
  Eigen3
)

# Simple WBC Node executable
add_executable(wbc_node_simple
  src/wbc_node_simple.cpp
)
ament_target_dependencies(wbc_node_simple
  rclcpp
  std_msgs
  sensor_msgs
  Eigen3
)

# Complete WBC Node executable
add_executable(wbc_node_complete
  src/wbc_node_complete.cpp
)
target_link_libraries(wbc_node_complete
  wbc_controller
)
ament_target_dependencies(wbc_node_complete
  rclcpp
  std_msgs
  sensor_msgs
  Eigen3
)

# Install libraries
install(TARGETS wbc_controller
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install executables
install(TARGETS wbc_node_simple wbc_node_complete
  DESTINATION lib/${PROJECT_NAME}
)

# Install header files
install(DIRECTORY include/
  DESTINATION include
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
