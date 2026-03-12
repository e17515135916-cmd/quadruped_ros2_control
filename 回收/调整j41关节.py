#!/usr/bin/env python3
"""
微调j41关节的origin位置
用于修正第四条腿（右后腿）的对齐问题
"""

import sys

def show_current_config():
    """显示当前j41的配置"""
    print("=" * 70)
    print("当前j41关节配置（第四条腿 - 右后腿）")
    print("=" * 70)
    print()
    print("在URDF中，Leg 4的配置：")
    print("  hip_joint_xyz: 0.0116 0.0199 0.055")
    print("  hip_joint_rpy: 3.1416 0 1.5708")
    print()
    print("这个参数控制l41（髋关节）相对于l4（滑轨）的位置")
    print()

def suggest_adjustments():
    """建议可能的调整方向"""
    print("=" * 70)
    print("调整建议")
    print("=" * 70)
    print()
    print("从图片看，蓝色部件（l41）和灰色部件（l4）之间有轻微错位")
    print()
    print("可能的调整方向：")
    print()
    print("1. X方向调整（前后）：")
    print("   - 增加X值：向前移动（远离base）")
    print("   - 减少X值：向后移动（靠近base）")
    print("   当前值：0.0116")
    print("   建议范围：0.010 ~ 0.015")
    print()
    print("2. Y方向调整（上下）：")
    print("   - 增加Y值：向上移动")
    print("   - 减少Y值：向下移动")
    print("   当前值：0.0199")
    print("   建议范围：0.018 ~ 0.022")
    print()
    print("3. Z方向调整（左右）：")
    print("   - 增加Z值：向右移动")
    print("   - 减少Z值：向左移动")
    print("   当前值：0.055")
    print("   建议范围：0.053 ~ 0.057")
    print()

def interactive_adjust():
    """交互式调整"""
    print("=" * 70)
    print("交互式调整j41关节位置")
    print("=" * 70)
    print()
    
    current_x = 0.0116
    current_y = 0.0199
    current_z = 0.055
    
    print(f"当前值：X={current_x}, Y={current_y}, Z={current_z}")
    print()
    print("请输入新的值（直接回车保持不变）：")
    print()
    
    # X方向
    x_input = input(f"X值 (当前: {current_x}): ").strip()
    new_x = float(x_input) if x_input else current_x
    
    # Y方向
    y_input = input(f"Y值 (当前: {current_y}): ").strip()
    new_y = float(y_input) if y_input else current_y
    
    # Z方向
    z_input = input(f"Z值 (当前: {current_z}): ").strip()
    new_z = float(z_input) if z_input else current_z
    
    print()
    print("=" * 70)
    print("新的配置")
    print("=" * 70)
    print()
    print(f"hip_joint_xyz=\"{new_x} {new_y} {new_z}\"")
    print()
    print("修改步骤：")
    print("1. 打开文件：src/dog2_description/urdf/dog2.urdf.xacro")
    print("2. 找到 Leg 4 的定义（搜索 'Leg 4: Rear Right'）")
    print("3. 修改 hip_joint_xyz 参数")
    print("4. 保存文件")
    print("5. 重新编译：colcon build --packages-select dog2_description")
    print("6. 在RViz中查看：ros2 launch dog2_description view_dog2.launch.py")
    print()
    
    # 询问是否自动修改
    confirm = input("是否自动修改URDF文件？(y/n): ").strip().lower()
    
    if confirm == 'y':
        return new_x, new_y, new_z
    else:
        return None

def modify_urdf(new_x, new_y, new_z):
    """修改URDF文件"""
    import os
    import shutil
    
    urdf_path = os.path.expanduser("~/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf.xacro")
    
    if not os.path.exists(urdf_path):
        print(f"❌ URDF文件不存在: {urdf_path}")
        return False
    
    # 备份
    backup_path = urdf_path + ".backup_j41_adjust"
    shutil.copy2(urdf_path, backup_path)
    print(f"✅ 已备份到: {backup_path}")
    
    # 读取文件
    with open(urdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换Leg 4的hip_joint_xyz
    # 查找模式：在Leg 4定义中的hip_joint_xyz参数
    import re
    
    # 匹配Leg 4的整个定义块
    leg4_pattern = r'(<!-- Leg 4: Rear Right.*?<xacro:leg leg_num="4".*?hip_joint_xyz=")([^"]+)(")'
    
    def replace_hip_xyz(match):
        return match.group(1) + f"{new_x} {new_y} {new_z}" + match.group(3)
    
    new_content = re.sub(leg4_pattern, replace_hip_xyz, content, flags=re.DOTALL)
    
    if new_content == content:
        print("❌ 未找到匹配的配置，请手动修改")
        return False
    
    # 保存
    with open(urdf_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ URDF文件已修改")
    print()
    print("下一步：")
    print("1. colcon build --packages-select dog2_description")
    print("2. source install/setup.bash")
    print("3. ros2 launch dog2_description view_dog2.launch.py")
    
    return True

def main():
    """主函数"""
    show_current_config()
    suggest_adjustments()
    
    result = interactive_adjust()
    
    if result:
        new_x, new_y, new_z = result
        modify_urdf(new_x, new_y, new_z)

if __name__ == "__main__":
    main()
