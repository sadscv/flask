#!/usr/bin/env python3
"""
测试运行器
运行所有单元测试并生成报告
"""

import unittest
import sys
import os
from io import StringIO

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """运行所有测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    # 创建测试运行器
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        descriptions=True,
        failfast=False
    )

    # 运行测试
    result = runner.run(suite)

    # 输出结果
    output = stream.getvalue()
    print(output)

    # 生成测试报告
    generate_test_report(result, output)

    return result.wasSuccessful()

def generate_test_report(result, output):
    """生成测试报告"""
    report = f"""
# 测试报告

## 测试概览
- 运行测试数量: {result.testsRun}
- 成功: {result.testsRun - len(result.failures) - len(result.errors)}
- 失败: {len(result.failures)}
- 错误: {len(result.errors)}
- 跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}
- 成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%

## 测试结果详情
{output}

"""

    # 保存报告到文件
    report_file = os.path.join(os.path.dirname(__file__), 'test_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n测试报告已保存到: {report_file}")

def run_specific_test_module(module_name):
    """运行特定模块的测试"""
    try:
        suite = unittest.TestLoader().loadTestsFromName(module_name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"运行测试模块 {module_name} 时出错: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定模块的测试
        module_name = sys.argv[1]
        print(f"运行测试模块: {module_name}")
        success = run_specific_test_module(module_name)
    else:
        # 运行所有测试
        print("运行所有测试...")
        success = run_all_tests()

    # 退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()