#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能对弈助手 - 主启动程序 (简化版)
Chinese Chess (Xiangqi) Intelligent Assistant - Main Launcher (Simple)
"""

import sys
import os
from pathlib import Path

# 确保能导入项目模块
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """主函数"""
    print("=" * 62)
    print("    中国象棋智能对弈助手 v3.2.0")
    print("    Chinese Chess (Xiangqi) Intelligent Assistant")
    print("=" * 62)
    print()
    
    try:
        # 导入GUI应用
        from src.ui.main_gui import ChessAssistantApp
        
        print("启动GUI模式...")
        
        # 创建并运行应用
        app = ChessAssistantApp()
        app.run()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有必要的模块都已正确安装")
        print("运行 'python scripts/install_requirements.py' 安装依赖")
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n程序结束")

if __name__ == '__main__':
    main()