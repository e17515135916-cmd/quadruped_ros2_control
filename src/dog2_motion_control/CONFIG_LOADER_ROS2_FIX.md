# Config Loader ROS 2 路径修复

## 问题描述

在初始实现中，`config_loader.py` 使用了相对路径来查找配置文件：

```python
current_dir = Path(__file__).parent
config_path = current_dir.parent / 'config' / 'gait_params.yaml'
```

这种方法在纯 Python 项目中完美工作，但在 ROS 2 的 `ament_python` 构建体系下会失败。

## 根本原因

当执行 `colcon build` 后，ROS 2 会将文件安装到不同的位置：

- **Python 代码**：`install/dog2_motion_control/lib/python3.10/site-packages/dog2_motion_control/`
- **配置文件**：`install/dog2_motion_control/share/dog2_motion_control/config/`

此时，`current_dir.parent` 根本找不到 `config` 文件夹，导致：
- 加载器触发异常
- 回退到默认参数
- 用户的配置调整完全失效

## 解决方案

使用 ROS 2 提供的 **Ament Index** 机制来优雅地查找资源：

```python
from ament_index_python.packages import get_package_share_directory

def __init__(self, config_path: Optional[str] = None):
    if config_path is None:
        try:
            # 通过 ament_index 查询 share 目录
            share_dir = get_package_share_directory('dog2_motion_control')
            config_path = os.path.join(share_dir, 'config', 'gait_params.yaml')
        except Exception as e:
            print(f"Warning: Package not found in ament index: {e}")
            # Fallback 到本地开发路径（仅用于测试）
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / 'config' / 'gait_params.yaml'
    
    self.config_path = Path(config_path)
```

## 优势

1. **生产环境安全**：在 `colcon build` 后的安装环境中正确工作
2. **开发环境友好**：在源码目录中直接运行测试时也能工作（fallback 机制）
3. **符合 ROS 2 最佳实践**：使用官方推荐的资源查找方式
4. **跨平台兼容**：不依赖特定的文件系统结构

## setup.py 配置

确保 `setup.py` 中正确配置了配置文件的安装：

```python
data_files=[
    # ... 其他配置 ...
    (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
]
```

## 测试验证

修复后，所有测试仍然通过：

```bash
python3 -m pytest test/test_config_loader.py -v
```

## 参考资料

- [ROS 2 Ament Index Documentation](https://docs.ros.org/en/humble/Tutorials/Intermediate/Ament-CMake-Documentation.html)
- [ROS 2 Python Packages](https://docs.ros.org/en/humble/How-To-Guides/Ament-CMake-Python-Documentation.html)
