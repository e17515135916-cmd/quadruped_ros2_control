#!/usr/bin/env python3
"""
移除小腿的collision标签
"""

import re

urdf_file = "src/dog2_description/urdf/dog2.urdf.xacro"

# 读取文件
with open(urdf_file, 'r') as f:
    content = f.read()

# 备份
backup_file = urdf_file + '.backup_remove_shin_collision'
with open(backup_file, 'w') as f:
    f.write(content)
print(f"✅ 已备份到: {backup_file}")

# 移除小腿collision块
# 匹配模式：在小腿visual之后，link结束之前的collision块
pattern = r'(<!-- Shin link.*?<visual>.*?</visual>)\s*<collision>.*?</collision>'

new_content = re.sub(pattern, r'\1\n    <!-- Collision disabled for shin - foot handles all ground contact -->\n    <!-- This prevents collision conflicts between shin and foot -->', content, flags=re.DOTALL)

# 写回文件
with open(urdf_file, 'w') as f:
    f.write(new_content)

print(f"✅ 已移除小腿collision标签")
print(f"✅ 已保存到: {urdf_file}")
