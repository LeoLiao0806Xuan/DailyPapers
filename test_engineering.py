#!/usr/bin/env python3
"""
测试工程化后的项目结构
"""

import importlib
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块是否能正常导入"""
    print("测试模块导入...")
    try:
        # 测试包导入
        import dailypapers
        print(f"✅ 成功导入 dailypapers 包，版本: {dailypapers.__version__}")
        
        # 测试子模块导入
        from dailypapers import PaperCrawler, PaperFilter, PaperPusher, AbstractExtractor
        print("✅ 成功导入所有核心类")
        
        # 测试工具函数导入
        from dailypapers import setup_logger, validate_config
        print("✅ 成功导入工具函数")
        
        # 测试配置导入
        from dailypapers import config
        print("✅ 成功导入配置")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def test_package_structure():
    """测试包结构是否完整"""
    print("\n测试包结构...")
    try:
        # 检查必要的文件和目录
        required_files = [
            "dailypapers/__init__.py",
            "dailypapers/crawler.py",
            "dailypapers/filter.py",
            "dailypapers/pusher.py",
            "dailypapers/extractor.py",
            "dailypapers/utils.py",
            "dailypapers/config.py",
            "dailypapers/main.py",
            "setup.py",
            "requirements.txt",
            "run.py"
        ]
        
        all_exist = True
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} 存在")
            else:
                print(f"❌ {file_path} 不存在")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"❌ 测试包结构失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试工程化后的 DailyPapers 项目...")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("包结构", test_package_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n=== 测试: {test_name} ===")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            failed += 1
            print(f"❌ {test_name} 测试失败")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("🎉 所有测试通过！项目工程化成功。")
    else:
        print("⚠️  部分测试失败，可能需要进一步检查。")

if __name__ == "__main__":
    main()
