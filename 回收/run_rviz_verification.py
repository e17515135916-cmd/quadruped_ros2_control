#!/usr/bin/env python3
"""
RViz 自动化验证脚本。

此脚本自动化 RViz 验证过程：
1. 验证 URDF 文件有效性
2. 验证髋关节轴向配置
3. 验证视觉模型保持不变
4. 生成验证报告
5. 可选：启动 RViz 进行手动验证

验证需求：6.1, 6.2
"""

import subprocess
import os
import sys
import time
from datetime import datetime


class RVizVerification:
    """RViz 验证类。"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'xacro_compilation': False,
            'urdf_validation': False,
            'hip_axis_check': False,
            'visual_model_check': False,
            'overall_success': False
        }
        self.report_lines = []
    
    def log(self, message, level='INFO'):
        """记录日志消息。"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {level}: {message}"
        print(log_line)
        self.report_lines.append(log_line)
    
    def run_command(self, cmd, description):
        """运行命令并返回结果。"""
        self.log(f"执行: {description}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                shell=isinstance(cmd, str)
            )
            self.log(f"✓ {description} 成功", 'SUCCESS')
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"✗ {description} 失败", 'ERROR')
            self.log(f"  错误: {e.stderr}", 'ERROR')
            return False, e.stderr
    
    def step1_compile_xacro(self):
        """步骤 1: 编译 xacro 文件。"""
        self.log("\n" + "="*70)
        self.log("步骤 1: 编译 xacro 文件")
        self.log("="*70)
        
        xacro_path = 'src/dog2_description/urdf/dog2.urdf.xacro'
        output_path = '/tmp/dog2_verification.urdf'
        
        success, output = self.run_command(
            ['xacro', xacro_path],
            f"编译 {xacro_path}"
        )
        
        if success:
            # 保存 URDF 到临时文件
            with open(output_path, 'w') as f:
                f.write(output)
            self.log(f"URDF 已保存到: {output_path}")
            self.results['xacro_compilation'] = True
        
        return success
    
    def step2_validate_urdf(self):
        """步骤 2: 验证 URDF 有效性。"""
        self.log("\n" + "="*70)
        self.log("步骤 2: 验证 URDF 有效性")
        self.log("="*70)
        
        urdf_path = '/tmp/dog2_verification.urdf'
        
        success, output = self.run_command(
            ['check_urdf', urdf_path],
            f"验证 {urdf_path}"
        )
        
        if success:
            self.results['urdf_validation'] = True
        
        return success
    
    def step3_check_hip_axis(self):
        """步骤 3: 检查髋关节轴向。"""
        self.log("\n" + "="*70)
        self.log("步骤 3: 检查髋关节轴向配置")
        self.log("="*70)
        
        success, output = self.run_command(
            ['python3', 'verify_visual_unchanged.py'],
            "验证髋关节轴向和视觉模型"
        )
        
        if success:
            self.results['hip_axis_check'] = True
            self.results['visual_model_check'] = True
        
        return success
    
    def step4_generate_report(self):
        """步骤 4: 生成验证报告。"""
        self.log("\n" + "="*70)
        self.log("步骤 4: 生成验证报告")
        self.log("="*70)
        
        # 确定总体成功状态
        self.results['overall_success'] = all([
            self.results['xacro_compilation'],
            self.results['urdf_validation'],
            self.results['hip_axis_check'],
            self.results['visual_model_check']
        ])
        
        # 生成报告
        report_path = f'rviz_verification_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RViz 髋关节轴向修改验证报告\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"验证时间: {self.results['timestamp']}\n")
            f.write(f"验证人员: 自动化脚本\n\n")
            
            f.write("验证项目:\n")
            f.write("-"*70 + "\n")
            f.write(f"1. Xacro 编译:        {'✓ 通过' if self.results['xacro_compilation'] else '✗ 失败'}\n")
            f.write(f"2. URDF 验证:         {'✓ 通过' if self.results['urdf_validation'] else '✗ 失败'}\n")
            f.write(f"3. 髋关节轴向检查:    {'✓ 通过' if self.results['hip_axis_check'] else '✗ 失败'}\n")
            f.write(f"4. 视觉模型检查:      {'✓ 通过' if self.results['visual_model_check'] else '✗ 失败'}\n")
            f.write("-"*70 + "\n\n")
            
            f.write("总体结果:\n")
            f.write("-"*70 + "\n")
            if self.results['overall_success']:
                f.write("✓ 所有验证项目通过\n\n")
                f.write("确认事项:\n")
                f.write("- 髋关节 (j11, j21, j31, j41) 轴向已更新为 X 轴 (1 0 0)\n")
                f.write("- 视觉模型保持不变\n")
                f.write("- URDF 文件有效且可以正常加载\n")
            else:
                f.write("✗ 部分验证项目失败\n")
                f.write("请检查上述失败项目\n")
            f.write("-"*70 + "\n\n")
            
            f.write("详细日志:\n")
            f.write("-"*70 + "\n")
            for line in self.report_lines:
                f.write(line + "\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("报告结束\n")
            f.write("="*70 + "\n")
        
        self.log(f"验证报告已生成: {report_path}")
        return report_path
    
    def run_verification(self):
        """运行完整的验证流程。"""
        self.log("\n" + "="*70)
        self.log("RViz 髋关节轴向修改验证")
        self.log("="*70)
        self.log(f"开始时间: {self.results['timestamp']}\n")
        
        # 执行验证步骤
        steps = [
            self.step1_compile_xacro,
            self.step2_validate_urdf,
            self.step3_check_hip_axis,
        ]
        
        for step in steps:
            if not step():
                self.log("\n验证失败，停止后续步骤", 'ERROR')
                break
        
        # 生成报告
        report_path = self.step4_generate_report()
        
        # 打印总结
        self.log("\n" + "="*70)
        self.log("验证总结")
        self.log("="*70)
        
        if self.results['overall_success']:
            self.log("✓ 所有验证通过", 'SUCCESS')
            self.log("髋关节轴向已成功从 Z 轴改为 X 轴", 'SUCCESS')
        else:
            self.log("✗ 验证失败", 'ERROR')
            self.log("请查看报告了解详情", 'ERROR')
        
        self.log(f"\n完整报告: {report_path}")
        self.log("="*70 + "\n")
        
        return self.results['overall_success']


def launch_rviz_manual_test():
    """启动 RViz 进行手动测试。"""
    print("\n" + "="*70)
    print("启动 RViz 进行手动验证")
    print("="*70)
    print("\n正在启动 RViz...")
    print("请在 RViz 中手动验证以下内容：")
    print("1. 使用 joint_state_publisher_gui 调整髋关节角度")
    print("2. 观察髋关节是否绕 X 轴旋转（前后摆动）")
    print("3. 确认视觉外观与修改前一致")
    print("\n按 Ctrl+C 停止 RViz\n")
    
    try:
        subprocess.run(
            ['ros2', 'launch', 'verify_hip_axis_rviz.py'],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nRViz 已停止")
    except subprocess.CalledProcessError as e:
        print(f"\n启动 RViz 失败: {e}")


def main():
    """主函数。"""
    print("\n" + "="*70)
    print("RViz 髋关节轴向修改验证工具")
    print("="*70)
    print("\n选项:")
    print("1. 运行自动化验证（推荐）")
    print("2. 启动 RViz 手动验证")
    print("3. 两者都运行")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\n请选择 (1/2/3，默认 1): ").strip() or "1"
    
    verifier = RVizVerification()
    
    if choice in ['1', '3']:
        success = verifier.run_verification()
        
        if not success:
            print("\n自动化验证失败，建议修复问题后再进行手动验证")
            return 1
    
    if choice in ['2', '3']:
        print("\n")
        input("按 Enter 键启动 RViz 进行手动验证...")
        launch_rviz_manual_test()
    
    return 0


if __name__ == '__main__':
    exit(main())
