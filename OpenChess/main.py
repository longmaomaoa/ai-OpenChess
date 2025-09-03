#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能对弈助手 - 主启动程序
Chinese Chess (Xiangqi) Intelligent Assistant - Main Launcher
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 确保能导入项目模块
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import setup_logging, PROJECT_ROOT
from src.ui.main_gui import ChessAssistantApp

def setup_argument_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='中国象棋智能对弈助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 启动GUI版本
  python main.py --console          # 启动控制台版本
  python main.py --debug           # 启动调试模式
  python main.py --region-selector # 启动区域选择工具
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['gui', 'console', 'region-selector'],
        default='gui',
        help='运行模式 (默认: gui)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='指定配置文件路径'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='中国象棋智能对弈助手 v3.2.0'
    )
    
    return parser

def check_dependencies():
    """检查必要的依赖包是否已安装"""
    required_packages = [
        'cv2', 'numpy', 'pyautogui', 'pytesseract', 
        'PIL', 'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("× 缺少必要的依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("   python install_requirements.py")
        print("   或")
        print("   pip install -r requirements.txt")
        return False
    
    print("√ 所有必要的依赖包已安装")
    return True

def check_tesseract():
    """检查Tesseract OCR是否正确安装和配置"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"√ Tesseract OCR 版本: {version}")
        return True
    except Exception as e:
        print(f"× Tesseract OCR 配置有问题: {e}")
        print("\n请确保:")
        print("1. 已安装 Tesseract OCR")
        print("2. 已安装中文语言包")
        print("3. 系统PATH中包含tesseract.exe")
        print("4. 或在config.py中正确配置TESSERACT_PATH")
        return False

def run_gui_mode(debug=False):
    """运行GUI模式"""
    try:
        import tkinter as tk
        from src.ui.main_gui import ChessAssistantApp
        
        print("启动GUI模式...")
        
        app = ChessAssistantApp()
        root = app.create_gui()
        
        if debug:
            print("🔍 调试模式已启用")
        
        # 设置窗口关闭事件
        def on_closing():
            if hasattr(app, 'cleanup'):
                app.cleanup()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        print(f"× 导入错误: {e}")
        print("请确保所有GUI相关模块都已正确安装")
    except Exception as e:
        logging.error(f"GUI模式运行时错误: {e}")
        print(f"× 运行错误: {e}")

def run_console_mode():
    """运行控制台模式"""
    try:
        from src.core.scanner.advanced_chess_scanner import AdvancedChessScanner
        
        print("🚀 启动控制台模式...")
        print("按 Ctrl+C 退出程序")
        
        scanner = AdvancedChessScanner()
        scanner.run()
        
    except ImportError as e:
        print(f"× 导入错误: {e}")
        print("请确保所有扫描器模块都已正确配置")
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        logging.error(f"控制台模式运行时错误: {e}")
        print(f"× 运行错误: {e}")

def run_region_selector():
    """运行区域选择工具"""
    try:
        from src.core.vision.region_selector import RegionSelector
        
        print("🚀 启动区域选择工具...")
        
        selector = RegionSelector()
        region = selector.select_region()
        
        if region:
            print(f"✅ 选定区域: {region}")
        else:
            print("❌ 未选择区域")
            
    except ImportError as e:
        print(f"× 导入错误: {e}")
        print("请确保区域选择模块已正确配置")
    except Exception as e:
        logging.error(f"区域选择工具运行时错误: {e}")
        print(f"× 运行错误: {e}")

def main():
    """主函数"""
    # 解析命令行参数
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # 设置日志
    try:
        setup_logging(level=args.log_level, debug=args.debug)
        logging.info("程序启动")
    except Exception as e:
        print(f"警告: 日志配置失败 - {e}")
    
    # 显示欢迎信息
    try:
        print("🏯" + "="*58 + "🏯")
        print("    中国象棋智能对弈助手 v3.2.0")
        print("    Chinese Chess (Xiangqi) Intelligent Assistant")
        print("🏯" + "="*58 + "🏯\n")
    except UnicodeEncodeError:
        print("=" * 62)
        print("    中国象棋智能对弈助手 v3.2.0")
        print("    Chinese Chess (Xiangqi) Intelligent Assistant")
        print("=" * 62 + "\n")
    
    # 检查系统环境
    try:
        print("🔍 正在检查系统环境...")
    except UnicodeEncodeError:
        print("正在检查系统环境...")
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_tesseract():
        print("\n⚠️  OCR功能可能无法正常工作，但其他功能仍可使用")
    
    print()
    
    # 根据模式运行程序
    try:
        if args.mode == 'gui':
            run_gui_mode(debug=args.debug)
        elif args.mode == 'console':
            run_console_mode()
        elif args.mode == 'region-selector':
            run_region_selector()
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        logging.error(f"程序运行错误: {e}")
        print(f"❌ 程序运行出错: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        logging.info("程序结束")
        print("\n👋 再见!")

if __name__ == '__main__':
    main()