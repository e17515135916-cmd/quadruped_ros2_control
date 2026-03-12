#!/bin/bash
# Dog2 MPC+WBC 依赖安装脚本
# ROS 2 Humble + Ubuntu 22.04

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Dog2 MPC+WBC 依赖安装"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 安装基础数学库
echo -e "\n${YELLOW}[1/6] 安装基础数学库 (Eigen3)...${NC}"
sudo apt install -y libeigen3-dev

# 2. 安装Pinocchio刚体动力学库
echo -e "\n${YELLOW}[2/6] 安装Pinocchio刚体动力学库...${NC}"
sudo apt install -y \
    robotpkg-py3*-pinocchio \
    robotpkg-pinocchio \
    robotpkg-hpp-fcl \
    || echo "尝试从ROS源安装..."

# 如果robotpkg不可用，从ROS源安装
if ! dpkg -l | grep -q pinocchio; then
    sudo apt install -y \
        ros-humble-pinocchio \
        libboost-all-dev \
        liburdfdom-dev
fi

# 3. 安装OSQP优化求解器（用于MPC）
echo -e "\n${YELLOW}[3/6] 安装OSQP优化求解器...${NC}"
sudo apt install -y \
    libosqp-dev \
    osqp-python3 \
    cmake

# 4. 安装qpOASES求解器（用于WBC）
echo -e "\n${YELLOW}[4/6] 安装qpOASES求解器...${NC}"
cd /tmp
if [ ! -d "qpOASES" ]; then
    git clone https://github.com/coin-or/qpOASES.git
fi
cd qpOASES
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
sudo ldconfig

# 5. 安装HPP-FCL碰撞检测库（用于避障）
echo -e "\n${YELLOW}[5/6] 安装HPP-FCL碰撞检测库...${NC}"
sudo apt install -y liboctomap-dev
cd /tmp
if [ ! -d "hpp-fcl" ]; then
    git clone --recursive https://github.com/humanoid-path-planner/hpp-fcl.git
fi
cd hpp-fcl
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON_INTERFACE=ON
make -j$(nproc)
sudo make install
sudo ldconfig

# 6. 安装Python依赖
echo -e "\n${YELLOW}[6/6] 安装Python依赖...${NC}"
pip3 install --user \
    numpy \
    scipy \
    osqp \
    quadprog \
    matplotlib \
    pinocchio

# 验证安装
echo -e "\n${GREEN}=========================================="
echo "验证安装..."
echo "==========================================${NC}"

echo -n "Eigen3: "
if [ -f "/usr/include/eigen3/Eigen/Core" ]; then
    echo -e "${GREEN}✓ 已安装${NC}"
else
    echo -e "✗ 未找到"
fi

echo -n "OSQP: "
if ldconfig -p | grep -q libosqp; then
    echo -e "${GREEN}✓ 已安装${NC}"
else
    echo -e "✗ 未找到"
fi

echo -n "qpOASES: "
if [ -f "/usr/local/include/qpOASES.hpp" ] || [ -f "/usr/local/include/qpOASES/qpOASES.hpp" ]; then
    echo -e "${GREEN}✓ 已安装${NC}"
else
    echo -e "✗ 未找到"
fi

echo -n "Pinocchio (Python): "
if python3 -c "import pinocchio" 2>/dev/null; then
    echo -e "${GREEN}✓ 已安装${NC}"
else
    echo -e "✗ 未找到"
fi

echo -n "HPP-FCL: "
if ldconfig -p | grep -q libhpp-fcl; then
    echo -e "${GREEN}✓ 已安装${NC}"
else
    echo -e "✗ 未找到"
fi

echo -e "\n${GREEN}=========================================="
echo "安装完成！"
echo "==========================================${NC}"
echo ""
echo "请运行以下命令查看使用说明："
echo "  cat ~/aperfect/carbot_ws/MPC_WBC_TOOLS_GUIDE.md"

