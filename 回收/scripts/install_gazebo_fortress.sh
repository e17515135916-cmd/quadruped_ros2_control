#!/bin/bash
# Gazebo Fortress Installation Script
# This script installs Gazebo Fortress and ROS 2 bridge packages for Ubuntu 22.04 (Jammy)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gazebo Fortress Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Ubuntu version
echo -e "${YELLOW}Checking Ubuntu version...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$VERSION_ID" != "22.04" ]; then
        echo -e "${RED}Error: This script requires Ubuntu 22.04 (Jammy)${NC}"
        echo -e "${RED}Current version: $VERSION_ID${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ubuntu 22.04 detected${NC}"
else
    echo -e "${RED}Error: Cannot detect Ubuntu version${NC}"
    exit 1
fi

# Check ROS 2 Humble installation
echo -e "${YELLOW}Checking ROS 2 Humble installation...${NC}"
if [ -d "/opt/ros/humble" ]; then
    echo -e "${GREEN}✓ ROS 2 Humble found${NC}"
else
    echo -e "${RED}Error: ROS 2 Humble not found${NC}"
    echo -e "${RED}Please install ROS 2 Humble first${NC}"
    exit 1
fi

# Check internet connectivity
echo -e "${YELLOW}Checking internet connectivity...${NC}"
if ping -c 1 -W 2 8.8.8.8 &> /dev/null || ping -c 1 -W 2 packages.osrfoundation.org &> /dev/null; then
    echo -e "${GREEN}✓ Internet connection available${NC}"
else
    echo -e "${YELLOW}Warning: Cannot verify internet connection${NC}"
    echo -e "${YELLOW}Continuing anyway... installation may fail if offline${NC}"
fi

# Add repository key (new method for Ubuntu 22.04+)
echo -e "${YELLOW}Adding repository key...${NC}"
if [ ! -f "/usr/share/keyrings/gazebo-archive-keyring.gpg" ]; then
    wget https://packages.osrfoundation.org/gazebo.gpg -O - | sudo gpg --dearmor -o /usr/share/keyrings/gazebo-archive-keyring.gpg
    echo -e "${GREEN}✓ Key added${NC}"
else
    echo -e "${GREEN}✓ Key already exists${NC}"
fi

# Add Gazebo Fortress repository with signed-by
echo -e "${YELLOW}Adding Gazebo Fortress repository...${NC}"
REPO_FILE="/etc/apt/sources.list.d/gazebo-stable.list"
REPO_LINE="deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main"

if [ -f "$REPO_FILE" ]; then
    # Update existing repository file to use signed-by
    echo "$REPO_LINE" | sudo tee "$REPO_FILE" > /dev/null
    echo -e "${GREEN}✓ Repository updated with signed-by${NC}"
else
    # Create new repository file
    echo "$REPO_LINE" | sudo tee "$REPO_FILE" > /dev/null
    echo -e "${GREEN}✓ Repository added${NC}"
fi

# Update package list
echo -e "${YELLOW}Updating package list...${NC}"
sudo apt update
echo -e "${GREEN}✓ Package list updated${NC}"

# Install Gazebo Fortress
echo -e "${YELLOW}Installing Gazebo Fortress...${NC}"
if ! dpkg -l | grep -q "gz-fortress"; then
    sudo apt install -y gz-fortress
    echo -e "${GREEN}✓ Gazebo Fortress installed${NC}"
else
    echo -e "${GREEN}✓ Gazebo Fortress already installed${NC}"
fi

# Install ROS 2 Gazebo bridge packages
echo -e "${YELLOW}Installing ROS 2 Gazebo bridge packages...${NC}"
PACKAGES=(
    "ros-humble-ros-gz-sim"
    "ros-humble-ros-gz-bridge"
    "ros-humble-ros-gz"
)

for package in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "$package"; then
        echo -e "${YELLOW}Installing $package...${NC}"
        sudo apt install -y "$package"
        echo -e "${GREEN}✓ $package installed${NC}"
    else
        echo -e "${GREEN}✓ $package already installed${NC}"
    fi
done

# Verify gz command
echo ""
echo -e "${YELLOW}Verifying Gazebo Fortress installation...${NC}"
if command -v gz &> /dev/null; then
    GZ_VERSION=$(gz --version | head -n 1)
    echo -e "${GREEN}✓ gz command available: $GZ_VERSION${NC}"
else
    echo -e "${RED}Error: gz command not found${NC}"
    exit 1
fi

# Check for ign_ros2_control plugin
echo -e "${YELLOW}Checking for ign_ros2_control plugin...${NC}"
PLUGIN_PATHS=(
    "/opt/ros/humble/lib/libign_ros2_control-system.so"
    "/usr/lib/libign_ros2_control-system.so"
)

PLUGIN_FOUND=false
for path in "${PLUGIN_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo -e "${GREEN}✓ Plugin found at: $path${NC}"
        PLUGIN_FOUND=true
        break
    fi
done

if [ "$PLUGIN_FOUND" = false ]; then
    echo -e "${YELLOW}Warning: ign_ros2_control plugin not found${NC}"
    echo -e "${YELLOW}Attempting to install ros-humble-ign-ros2-control...${NC}"
    
    if sudo apt install -y ros-humble-ign-ros2-control 2>/dev/null; then
        echo -e "${GREEN}✓ ign_ros2_control installed${NC}"
    else
        echo -e "${YELLOW}Note: ros-humble-ign-ros2-control package not available${NC}"
        echo -e "${YELLOW}You may need to build it from source or use gz_ros2_control instead${NC}"
    fi
fi

# Test gz sim command
echo -e "${YELLOW}Testing gz sim command...${NC}"
if timeout 5 gz sim --version &> /dev/null; then
    echo -e "${GREEN}✓ gz sim command works${NC}"
else
    echo -e "${YELLOW}Warning: gz sim test timed out (this may be normal)${NC}"
fi

# Installation complete
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Gazebo Fortress has been successfully installed.${NC}"
echo ""
echo -e "${YELLOW}Verification commands:${NC}"
echo "  gz --version              # Check Gazebo version"
echo "  gz sim --help             # Check simulator help"
echo "  ros2 pkg list | grep gz   # List ROS 2 Gazebo packages"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Run URDF migration script: python3 scripts/migrate_urdf_to_fortress.py"
echo "  2. Run launch file migration script: python3 scripts/migrate_launch_to_fortress.py"
echo "  3. Test simulation: ros2 launch dog2_description <your_launch_file>"
echo ""
echo -e "${GREEN}For rollback instructions, see the design document.${NC}"
