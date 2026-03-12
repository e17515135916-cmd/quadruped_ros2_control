#!/usr/bin/env python3
"""
verify_installation.py - 验证所有依赖是否正确安装
"""
import sys

def test_eigen():
    try:
        import subprocess
        result = subprocess.run(['pkg-config', '--modversion', 'eigen3'], 
                                capture_output=True, text=True)
        version = result.stdout.strip()
        if version:
            print(f"✓ Eigen3: 版本 {version}")
            return True
        else:
            print("✗ Eigen3: 未找到")
            return False
    except Exception as e:
        print(f"✗ Eigen3: 检查失败 - {e}")
        return False

def test_pinocchio():
    try:
        import pinocchio as pin
        print(f"✓ Pinocchio: 版本 {pin.__version__}")
        
        # 测试加载URDF
        try:
            urdf_path = "/home/dell/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf"
            model = pin.buildModelFromUrdf(urdf_path)
            print(f"  └─ 成功加载Dog2 URDF (nq={model.nq})")
        except Exception as e:
            print(f"  └─ 警告: 无法加载Dog2 URDF - {e}")
        
        return True
    except ImportError:
        print("✗ Pinocchio: 未安装")
        print("  └─ 安装命令: pip3 install pin")
        return False

def test_osqp():
    try:
        import osqp
        import numpy as np
        from scipy import sparse
        
        # 快速测试求解一个小QP问题
        P = sparse.csc_matrix([[4., 1.], [1., 2.]])
        q = np.array([1., 1.])
        A = sparse.csc_matrix([[1., 1.]])
        l = np.array([1.])
        u = np.array([1.])
        
        prob = osqp.OSQP()
        prob.setup(P, q, A, l, u, verbose=False)
        result = prob.solve()
        
        if result.info.status == 'solved':
            print(f"✓ OSQP: 已安装并可正常工作")
            return True
        else:
            print(f"✗ OSQP: 安装但求解失败")
            return False
    except ImportError:
        print("✗ OSQP: 未安装")
        print("  └─ 安装命令: pip3 install osqp")
        return False
    except Exception as e:
        print(f"✗ OSQP: 测试失败 - {e}")
        return False

def test_hpp_fcl():
    try:
        import hppfcl
        import numpy as np
        
        # 简单测试
        sphere = hppfcl.Sphere(0.1)
        print(f"✓ HPP-FCL: 已安装")
        return True
    except ImportError:
        print("✗ HPP-FCL: 未安装")
        print("  └─ 需要从源码编译安装")
        return False
    except Exception as e:
        print(f"✗ HPP-FCL: 测试失败 - {e}")
        return False

def test_qpoases():
    import os
    import subprocess
    
    # 检查头文件
    header_paths = [
        "/usr/local/include/qpOASES.hpp",
        "/usr/local/include/qpOASES/qpOASES.hpp",
        "/usr/include/qpOASES.hpp",
        "/usr/include/qpOASES/qpOASES.hpp"
    ]
    
    found = False
    for path in header_paths:
        if os.path.exists(path):
            print(f"✓ qpOASES: 已安装 ({path})")
            found = True
            break
    
    if not found:
        # 检查库文件
        try:
            result = subprocess.run(['ldconfig', '-p'], 
                                    capture_output=True, text=True)
            if 'libqpOASES' in result.stdout:
                print("✓ qpOASES: 已安装 (库文件已找到)")
                return True
        except:
            pass
        
        print("✗ qpOASES: 未安装")
        print("  └─ 需要从源码编译安装")
        return False
    
    return found

def test_scipy():
    try:
        import scipy
        print(f"✓ SciPy: 版本 {scipy.__version__}")
        return True
    except ImportError:
        print("✗ SciPy: 未安装")
        print("  └─ 安装命令: pip3 install scipy")
        return False

def test_numpy():
    try:
        import numpy as np
        print(f"✓ NumPy: 版本 {np.__version__}")
        return True
    except ImportError:
        print("✗ NumPy: 未安装")
        print("  └─ 安装命令: pip3 install numpy")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("        Dog2 MPC+WBC 依赖验证")
    print("=" * 60)
    print()
    
    results = {}
    
    print("[1/7] 检查NumPy...")
    results['numpy'] = test_numpy()
    print()
    
    print("[2/7] 检查SciPy...")
    results['scipy'] = test_scipy()
    print()
    
    print("[3/7] 检查Eigen3...")
    results['eigen'] = test_eigen()
    print()
    
    print("[4/7] 检查Pinocchio...")
    results['pinocchio'] = test_pinocchio()
    print()
    
    print("[5/7] 检查OSQP...")
    results['osqp'] = test_osqp()
    print()
    
    print("[6/7] 检查HPP-FCL...")
    results['hpp_fcl'] = test_hpp_fcl()
    print()
    
    print("[7/7] 检查qpOASES...")
    results['qpoases'] = test_qpoases()
    print()
    
    # 汇总
    print("=" * 60)
    print("汇总结果:")
    print("-" * 60)
    
    total = len(results)
    passed = sum(results.values())
    
    for name, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {name}")
    
    print("-" * 60)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print()
        print("🎉 所有依赖安装成功！")
        print("可以开始开发Dog2 MPC+WBC控制器了！")
        print()
        print("下一步:")
        print("  1. 阅读使用指南: cat MPC_WBC_TOOLS_GUIDE.md")
        print("  2. 查看架构设计: cat DOG2_MPC_WBC_ARCHITECTURE.md")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("⚠️  部分依赖缺失")
        print("请运行安装脚本:")
        print("  cd ~/aperfect/carbot_ws")
        print("  ./install_mpc_wbc_deps.sh")
        print("=" * 60)
        sys.exit(1)

