#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能助手 - 统一GUI入口
Unified GUI Entry Point for Chinese Chess Intelligent Assistant
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 导入GUI模块
try:
    from src.ui.tkinter_gui.gui_chess_scanner import ChessScannerGUI
except ImportError:
    # 如果导入失败，尝试相对导入
    from tkinter_gui.gui_chess_scanner import ChessScannerGUI


class ChessAssistantApp:
    """中国象棋智能助手主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.root = None
        self.gui = None
    
    def create_gui(self):
        """创建GUI界面"""
        self.root = tk.Tk()
        
        # 设置窗口图标和标题
        self.root.title("🏯 中国象棋智能助手 🏯")
        
        # 创建主GUI界面
        self.gui = ChessScannerGUI(self.root)
        
        return self.root
    
    def run(self):
        """运行应用"""
        try:
            root = self.create_gui()
            print("🚀 启动中国象棋智能助手...")
            print("📱 GUI界面已加载")
            root.mainloop()
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            raise


def main():
    """主函数"""
    print("=" * 50)
    print("🏯 中国象棋智能助手 v3.1 Enhanced")
    print("Chinese Chess Intelligent Assistant")
    print("=" * 50)
    
    # 创建并运行应用
    app = ChessAssistantApp()
    app.run()


if __name__ == "__main__":
    main()