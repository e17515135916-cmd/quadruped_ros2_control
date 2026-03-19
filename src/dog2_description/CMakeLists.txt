cmake_minimum_required(VERSION 3.8)
project(dog2_description)

find_package(ament_cmake REQUIRED)

option(DOG2_ENABLE_URDF_SHIFT_BOUNDARY_CHECK "Enable URDF shift boundary validation test" ON)

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
    scripts/spider_keyboard_control.py
    scripts/spider_ik_stand.py
    scripts/spider_basic_motion_controller.py
    scripts/check_urdf_shift_boundary.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING AND DOG2_ENABLE_URDF_SHIFT_BOUNDARY_CHECK)
  find_program(PYTHON3_EXECUTABLE python3)
  find_program(XACRO_EXECUTABLE xacro)

  if(PYTHON3_EXECUTABLE AND XACRO_EXECUTABLE)
    add_test(
      NAME dog2_urdf_shift_boundary_check
      COMMAND
        ${PYTHON3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/scripts/check_urdf_shift_boundary.py
        ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf.xacro
        --strict
    )
  else()
    message(WARNING "Skip dog2_urdf_shift_boundary_check: python3 or xacro not found")
  endif()
endif()

ament_package()
