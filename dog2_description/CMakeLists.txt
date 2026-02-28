cmake_minimum_required(VERSION 3.8)
project(dog2_description)

find_package(ament_cmake REQUIRED)

# Find xacro for URDF generation
find_program(XACRO xacro)
if(NOT XACRO)
  message(WARNING "xacro not found. URDF will not be auto-generated from Xacro.")
else()
  # Generate URDF from Xacro at build time - TEMPORARILY DISABLED
  # set(XACRO_FILE "${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf.xacro")
  # set(URDF_FILE "${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf")
  
  # add_custom_command(
  #   OUTPUT ${URDF_FILE}
  #   COMMAND ${XACRO} ${XACRO_FILE} -o ${URDF_FILE}
  #   DEPENDS ${XACRO_FILE}
  #   COMMENT "Generating URDF from Xacro: dog2.urdf.xacro -> dog2.urdf"
  # )
  
  # add_custom_target(generate_urdf ALL DEPENDS ${URDF_FILE})
  
  # # Validate URDF after generation
  # find_program(PYTHON3 python3)
  # if(PYTHON3)
  #   set(VALIDATE_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/../scripts/validate_urdf_limits.py")
  #   if(EXISTS ${VALIDATE_SCRIPT})
  #     add_custom_command(
  #       TARGET generate_urdf POST_BUILD
  #       COMMAND ${PYTHON3} ${VALIDATE_SCRIPT} ${URDF_FILE}
  #       COMMENT "Validating generated URDF joint limits"
  #     )
  #   endif()
  # endif()
endif()

install(
  DIRECTORY urdf meshes launch rviz config scripts
  DESTINATION share/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS
)

# Install Python scripts as executables
install(
  PROGRAMS
    scripts/auto_stand_node.py
    scripts/spider_joint_smoke_test.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
