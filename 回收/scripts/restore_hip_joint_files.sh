#!/bin/bash
# Restore script for hip joint axis change
# This script restores files from a backup created by backup_hip_joint_files.sh
# Usage: ./scripts/restore_hip_joint_files.sh <backup_directory>

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup directory is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup directory specified${NC}"
    echo "Usage: $0 <backup_directory>"
    echo ""
    echo "Available backups:"
    ls -1d backups/hip_joint_axis_change_* 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_DIR="$1"

# Check if backup directory exists
if [ ! -d "${BACKUP_DIR}" ]; then
    echo -e "${RED}Error: Backup directory not found: ${BACKUP_DIR}${NC}"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Hip Joint Axis Change - Restore Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Restoring from: ${BACKUP_DIR}"
echo ""

# Show backup manifest if it exists
if [ -f "${BACKUP_DIR}/BACKUP_MANIFEST.txt" ]; then
    echo -e "${YELLOW}Backup Manifest:${NC}"
    cat "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
    echo ""
fi

# Ask for confirmation
read -p "Are you sure you want to restore from this backup? (yes/no): " confirm
if [ "${confirm}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi
echo ""

# Restore URDF file
echo -e "${YELLOW}Restoring URDF file...${NC}"
if [ -f "${BACKUP_DIR}/urdf/dog2.urdf.xacro" ]; then
    cp "${BACKUP_DIR}/urdf/dog2.urdf.xacro" "src/dog2_description/urdf/dog2.urdf.xacro"
    echo -e "${GREEN}✓ URDF restored: dog2.urdf.xacro${NC}"
else
    echo -e "${RED}✗ URDF backup not found!${NC}"
    exit 1
fi
echo ""

# Restore hip link visual mesh files
echo -e "${YELLOW}Restoring hip link visual meshes...${NC}"
VISUAL_MESHES=("l11.STL" "l21.STL" "l31.STL" "l41.STL")
for mesh in "${VISUAL_MESHES[@]}"; do
    if [ -f "${BACKUP_DIR}/meshes/visual/${mesh}" ]; then
        cp "${BACKUP_DIR}/meshes/visual/${mesh}" "src/dog2_description/meshes/${mesh}"
        echo -e "${GREEN}✓ Visual mesh restored: ${mesh}${NC}"
    else
        echo -e "${RED}✗ Visual mesh backup not found: ${mesh}${NC}"
        exit 1
    fi
done
echo ""

# Restore hip link collision mesh files
echo -e "${YELLOW}Restoring hip link collision meshes...${NC}"
COLLISION_MESHES=("l11_collision.STL" "l21_collision.STL" "l31_collision.STL" "l41_collision.STL")
for mesh in "${COLLISION_MESHES[@]}"; do
    if [ -f "${BACKUP_DIR}/meshes/collision/${mesh}" ]; then
        cp "${BACKUP_DIR}/meshes/collision/${mesh}" "src/dog2_description/meshes/collision/${mesh}"
        echo -e "${GREEN}✓ Collision mesh restored: ${mesh}${NC}"
    else
        echo -e "${RED}✗ Collision mesh backup not found: ${mesh}${NC}"
        exit 1
    fi
done
echo ""

# Restore kinematics solver files
echo -e "${YELLOW}Restoring kinematics solver files...${NC}"
KINEMATICS_FILES=(
    "dog2_kinematics/leg_ik_4dof.py:src/dog2_kinematics/dog2_kinematics/leg_ik_4dof.py"
    "src/leg_ik_4dof.cpp:src/dog2_kinematics/src/leg_ik_4dof.cpp"
    "include/leg_ik_4dof.hpp:src/dog2_kinematics/include/dog2_kinematics/leg_ik_4dof.hpp"
)
for file_pair in "${KINEMATICS_FILES[@]}"; do
    backup_path=$(echo ${file_pair} | cut -d: -f1)
    restore_path=$(echo ${file_pair} | cut -d: -f2)
    
    if [ -f "${BACKUP_DIR}/kinematics/${backup_path}" ]; then
        cp "${BACKUP_DIR}/kinematics/${backup_path}" "${restore_path}"
        echo -e "${GREEN}✓ Kinematics file restored: ${restore_path}${NC}"
    else
        echo -e "${YELLOW}⚠ Kinematics file backup not found (may not have existed): ${backup_path}${NC}"
    fi
done
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Restore completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Files have been restored from: ${BACKUP_DIR}"
echo ""
echo "Next steps:"
echo "1. Rebuild the workspace: colcon build"
echo "2. Test the robot in RViz or Gazebo"
echo ""
