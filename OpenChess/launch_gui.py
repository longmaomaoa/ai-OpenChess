#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的GUI启动脚本
"""

import sys
import os
from pathlib import Path

# 确保能导入项目模块
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """主函数"""
    try:
        import tkinter as tk
        from src.ui.tkinter_gui.gui_chess_scanner import ChessScannerGUI
        
        print("正在启动GUI...")
        
        # 创建Tkinter根窗口
        root = tk.Tk()
        
        # 设置全局异常处理器
        def handle_exception(exc, val, tb):
            import traceback
            print(f"全局异常处理: {exc.__name__}: {val}")
            print("".join(traceback.format_tb(tb)))
            # 不让异常导致应用崩溃
        
        root.report_callback_exception = handle_exception
        
        # 创建应用
        try:
            app = ChessScannerGUI(root)
        except Exception as e:
            print(f"创建应用失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 显示错误对话框
            try:
                from tkinter import messagebox
                messagebox.showerror("启动错误", f"应用初始化失败:\n{e}\n\n请检查日志获取详细信息。")
            except:
                pass
            return
        
        # 设置窗口关闭处理
        def on_closing():
            try:
                if hasattr(app, 'scanning') and app.scanning:
                    app.stop_ai_monitoring()
            except:
                pass
            
            try:
                root.destroy()
            except:
                pass
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动主循环
        try:
            print("GUI启动成功，进入主循环...")
            root.mainloop()
            print("GUI已关闭")
        except KeyboardInterrupt:
            print("用户中断程序")
            on_closing()
        except Exception as e:
            print(f"主循环异常: {e}")
            import traceback
            traceback.print_exc()
            on_closing()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖都已安装")
        print("运行 'python scripts/install_requirements.py' 安装依赖")
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试显示错误对话框
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("严重错误", f"应用启动失败:\n{e}")
            root.destroy()
        except:
            pass

if __name__ == '__main__':
    main()