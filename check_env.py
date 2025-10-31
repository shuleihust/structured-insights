#!/usr/bin/env python3
"""
环境检测脚本
检查 API Key 配置和依赖库安装情况
"""

import os
import sys
import json
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print(f"     需要 Python 3.7+")
        return False


def check_config_file():
    """检查配置文件"""
    print("\n🔍 检查配置文件...")
    config_file = Path(__file__).parent / "config.json"
    
    if not config_file.exists():
        print("  ❌ config.json 不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("  ✅ config.json 格式正确")
        return True
    except json.JSONDecodeError as e:
        print(f"  ❌ config.json 格式错误: {e}")
        return False


def check_dependencies():
    """检查依赖库"""
    print("\n🔍 检查依赖库...")
    
    results = {}
    
    # 检查 OpenAI
    try:
        import openai
        print(f"  ✅ openai ({openai.__version__})")
        results['openai'] = True
    except ImportError:
        print("  ⚠️  openai 未安装 (pip install openai)")
        results['openai'] = False
    
    # 检查 Anthropic
    try:
        import anthropic
        print(f"  ✅ anthropic ({anthropic.__version__})")
        results['anthropic'] = True
    except ImportError:
        print("  ⚠️  anthropic 未安装 (pip install anthropic)")
        results['anthropic'] = False
    
    if not results['openai'] and not results['anthropic']:
        print("\n  ❌ 至少需要安装一个 LLM 客户端库")
        return False
    
    return True


def check_api_keys():
    """检查 API Keys"""
    print("\n🔍 检查 API Keys...")
    
    keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    }
    
    found_any = False
    for key_name, key_value in keys.items():
        if key_value:
            # 隐藏大部分密钥，只显示前后几位
            masked = key_value[:8] + '...' + key_value[-4:] if len(key_value) > 12 else '***'
            print(f"  ✅ {key_name}: {masked}")
            found_any = True
        else:
            print(f"  ⚠️  {key_name}: 未设置")
    
    if not found_any:
        print("\n  ❌ 未找到任何 API Key")
        print("     请设置至少一个:")
        print("     export OPENAI_API_KEY='your-key'")
        print("     export ANTHROPIC_API_KEY='your-key'")
        print("     export DEEPSEEK_API_KEY='your-key'")
        return False
    
    return True


def check_directories():
    """检查目录结构"""
    print("\n🔍 检查目录结构...")
    
    base_dir = Path(__file__).parent
    required_files = [
        'extractor.py',
        'extraction-prompt.md',
        'config.json',
        'README.md',
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} 不存在")
            all_exist = False
    
    # 检查输出目录
    output_dir = base_dir / 'output'
    if output_dir.exists():
        print(f"  ✅ output/ 目录")
    else:
        print(f"  ⚠️  output/ 目录不存在（将自动创建）")
    
    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("文案结构化提炼工具 - 环境检测")
    print("=" * 60)
    
    checks = [
        ("Python 版本", check_python_version()),
        ("配置文件", check_config_file()),
        ("依赖库", check_dependencies()),
        ("API Keys", check_api_keys()),
        ("目录结构", check_directories()),
    ]
    
    print("\n" + "=" * 60)
    print("检测结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:.<20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 环境检测全部通过！可以开始使用工具了。")
        print("\n快速开始:")
        print("  python extractor.py -i example_input.txt")
        print("\n或查看帮助:")
        print("  python extractor.py --help")
        return 0
    else:
        print("\n⚠️  部分检查未通过，请按照提示修复问题。")
        print("\n查看文档:")
        print("  cat README.md")
        print("  cat QUICKSTART.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())

