# Dog2机器人模型文件列表

## 📁 所有STL文件路径

### 机身
```
~/aperfect/carbot_ws/src/dog2_description/meshes/base_link.STL
```

### 左前腿 (Leg 1)
```
~/aperfect/carbot_ws/src/dog2_description/meshes/l1.STL      # 髋关节
~/aperfect/carbot_ws/src/dog2_description/meshes/l11.STL     # 大腿
~/aperfect/carbot_ws/src/dog2_description/meshes/l111.STL    # 小腿
```

### 右前腿 (Leg 2)
```
~/aperfect/carbot_ws/src/dog2_description/meshes/l2.STL      # 髋关节
~/aperfect/carbot_ws/src/dog2_description/meshes/l21.STL     # 大腿
~/aperfect/carbot_ws/src/dog2_description/meshes/l211.STL    # 小腿
```

### 左后腿 (Leg 3)
```
~/aperfect/carbot_ws/src/dog2_description/meshes/l3.STL      # 髋关节
~/aperfect/carbot_ws/src/dog2_description/meshes/l31.STL     # 大腿
~/aperfect/carbot_ws/src/dog2_description/meshes/l311.STL    # 小腿
```

### 右后腿 (Leg 4)
```
~/aperfect/carbot_ws/src/dog2_description/meshes/l4.STL      # 髋关节
~/aperfect/carbot_ws/src/dog2_description/meshes/l41.STL     # 大腿
~/aperfect/carbot_ws/src/dog2_description/meshes/l411.STL    # 小腿
```

## 🎯 快速修改流程

### 修改单个部件（推荐）

1. **打开Blender**
```bash
blender
```

2. **删除默认立方体**
   - 选中立方体
   - 按 `X` → Delete

3. **导入STL**
   - File → Import → STL (.stl)
   - 选择要修改的文件（例如 `base_link.STL`）

4. **修改模型**
   - 按 `Tab` 进入编辑模式
   - 进行修改
   - 按 `Tab` 退出编辑模式

5. **导出STL**
   - File → Export → STL (.stl)
   - 覆盖原文件

6. **测试**
```bash
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description
source install/setup.bash
ros2 launch dog2_description view_dog2.launch.py
```

## 📝 修改建议

### 如果你想修改：

**机身外形** → 修改 `base_link.STL`
**腿部长度** → 修改 `l111.STL`, `l211.STL`, `l311.STL`, `l411.STL` (小腿)
**腿部粗细** → 修改 `l11.STL`, `l21.STL`, `l31.STL`, `l41.STL` (大腿)
**关节部分** → 修改 `l1.STL`, `l2.STL`, `l3.STL`, `l4.STL` (髋关节)

## ⚠️ 重要提示

1. **修改前备份**
```bash
cp ~/aperfect/carbot_ws/src/dog2_description/meshes/base_link.STL \
   ~/aperfect/carbot_ws/src/dog2_description/meshes/base_link.STL.backup
```

2. **同时更新碰撞模型**
```bash
cp ~/aperfect/carbot_ws/src/dog2_description/meshes/base_link.STL \
   ~/aperfect/carbot_ws/src/dog2_description/meshes/collision/base_link_collision.STL
```

3. **保持文件名不变**
   - 导出时必须使用原文件名
   - 大小写要一致

## 🔍 在Blender中查看多个部件

如果你想同时看多个部件（不需要正确的装配位置）：

1. 导入第一个STL
2. File → Import → STL (.stl) 导入第二个
3. 重复导入其他部件
4. 所有部件会堆叠在一起
5. 选择任意部件，按 `G` 移动到合适位置查看

这样你可以对比不同部件的大小和形状。
