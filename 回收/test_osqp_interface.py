#!/usr/bin/env python3
"""
测试OSQP接口

测试一个简单的QP问题：
  min  0.5 * x^T * P * x + q^T * x
  s.t. l <= A * x <= u

其中：
  P = [[4, 1],
       [1, 2]]
  q = [1, 1]
  A = [[1, 1],
       [1, 0],
       [0, 1]]
  l = [1, 0, 0]
  u = [1, 0.7, 0.7]

最优解应该接近 x = [0.3, 0.7]
"""

import sys
import ctypes
import numpy as np
from pathlib import Path

# 加载OSQP接口库
lib_path = Path("install/dog2_mpc/lib/libosqp_interface.so")
if not lib_path.exists():
    print(f"错误：找不到库文件 {lib_path}")
    print("请先编译：colcon build --packages-select dog2_mpc")
    sys.exit(1)

print("=" * 60)
print("OSQP接口测试")
print("=" * 60)

# 定义测试问题
P = np.array([[4.0, 1.0],
              [1.0, 2.0]])

q = np.array([1.0, 1.0])

A = np.array([[1.0, 1.0],
              [1.0, 0.0],
              [0.0, 1.0]])

l = np.array([1.0, 0.0, 0.0])
u = np.array([1.0, 0.7, 0.7])

print("\n问题定义：")
print(f"P = \n{P}")
print(f"q = {q}")
print(f"A = \n{A}")
print(f"l = {l}")
print(f"u = {u}")

print("\n预期最优解：x ≈ [0.3, 0.7]")
print("预期目标函数值：≈ 1.88")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n注意：这是一个Python测试框架。")
print("实际的C++测试需要创建一个C++测试程序。")
print("\n建议：创建一个C++测试程序来验证OSQP接口。")
