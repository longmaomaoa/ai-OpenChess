#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区域选择功能测试脚本
测试多棋盘场景下的区域选择和扫描功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import time
import threading
from region_selector import RegionSelector
from advanced_chess_scanner import AdvancedChessScanner

class RegionTestGUI:
    """区域选择功能测试GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("区域选择功能测试")
        self.root.geometry("800x600")
        
        # 组件
        self.region_selector = RegionSelector()
        self.scanner = AdvancedChessScanner()
        self.current_regions = {}  # 存储多个区域
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self.root, text="多棋盘区域选择测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 控制面板
        control_frame = ttk.LabelFrame(self.root, text="区域管理", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="选择棋盘区域1", command=lambda: self.select_region("棋盘1")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="选择棋盘区域2", command=lambda: self.select_region("棋盘2")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="选择棋盘区域3", command=lambda: self.select_region("棋盘3")).pack(side=tk.LEFT, padx=5)
        
        # 测试面板
        test_frame = ttk.LabelFrame(self.root, text="扫描测试", padding="10")
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(test_frame, text="测试扫描棋盘1", command=lambda: self.test_scan("棋盘1")).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text="测试扫描棋盘2", command=lambda: self.test_scan("棋盘2")).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text="测试扫描棋盘3", command=lambda: self.test_scan("棋盘3")).pack(side=tk.LEFT, padx=5)
        
        # 区域信息显示
        info_frame = ttk.LabelFrame(self.root, text="区域信息", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 区域列表
        self.region_listbox = tk.Listbox(info_frame)
        self.region_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 操作按钮
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="预览选中区域", command=self.preview_selected_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除选中区域", command=self.delete_selected_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存所有区域", command=self.save_all_regions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载已保存区域", command=self.load_saved_regions).pack(side=tk.LEFT, padx=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(self.root, text="测试日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def log_message(self, message):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def select_region(self, region_name):
        """选择指定名称的区域"""
        self.log_message(f"开始选择区域: {region_name}")
        
        def region_selection_thread():
            try:
                def on_region_selected(region):
                    self.current_regions[region_name] = region
                    x, y, w, h = region
                    region_info = f"{region_name}: ({x}, {y}) {w}x{h}"
                    
                    # 更新区域列表显示
                    self.root.after(0, lambda: self.update_region_list())
                    self.root.after(0, lambda: self.log_message(f"区域 {region_name} 选择完成: {w}x{h}"))
                
                # 设置回调函数
                self.region_selector.callback = on_region_selected
                
                # 启动区域选择
                selected_region = self.region_selector.select_region()
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"区域选择失败: {e}"))
        
        threading.Thread(target=region_selection_thread, daemon=True).start()
    
    def update_region_list(self):
        """更新区域列表显示"""
        self.region_listbox.delete(0, tk.END)
        for name, region in self.current_regions.items():
            x, y, w, h = region
            info = f"{name}: ({x}, {y}) {w}x{h}"
            self.region_listbox.insert(tk.END, info)
    
    def test_scan(self, region_name):
        """测试扫描指定区域"""
        if region_name not in self.current_regions:
            messagebox.showwarning("警告", f"请先选择区域: {region_name}")
            return
        
        self.log_message(f"开始测试扫描: {region_name}")
        
        def scan_thread():
            try:
                region = self.current_regions[region_name]
                
                # 设置扫描区域
                self.scanner.set_scan_region(region)
                
                # 执行扫描
                start_time = time.time()
                board_state = self.scanner.scan_board()
                scan_time = time.time() - start_time
                
                # 统计扫描结果
                piece_count = sum(1 for row in board_state for cell in row if cell is not None)
                
                # 显示结果
                result_msg = f"{region_name} 扫描完成: 耗时 {scan_time:.2f}s, 识别到 {piece_count} 个棋子"
                self.root.after(0, lambda: self.log_message(result_msg))
                
                # 显示扫描区域预览
                preview_image = self.region_selector.preview_region(region)
                if preview_image is not None:
                    cv2.imshow(f"扫描结果 - {region_name}", preview_image)
                    cv2.waitKey(3000)
                    cv2.destroyAllWindows()
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"扫描失败 {region_name}: {e}"))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def preview_selected_region(self):
        """预览选中的区域"""
        selection = self.region_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个区域")
            return
        
        # 获取选中的区域名称
        selected_text = self.region_listbox.get(selection[0])
        region_name = selected_text.split(":")[0]
        
        if region_name in self.current_regions:
            region = self.current_regions[region_name]
            preview_image = self.region_selector.preview_region(region)
            if preview_image is not None:
                cv2.imshow(f"区域预览 - {region_name}", preview_image)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()
                self.log_message(f"预览区域: {region_name}")
            else:
                self.log_message(f"预览失败: {region_name}")
    
    def delete_selected_region(self):
        """删除选中的区域"""
        selection = self.region_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个区域")
            return
        
        selected_text = self.region_listbox.get(selection[0])
        region_name = selected_text.split(":")[0]
        
        if region_name in self.current_regions:
            del self.current_regions[region_name]
            self.update_region_list()
            self.log_message(f"已删除区域: {region_name}")
    
    def save_all_regions(self):
        """保存所有区域"""
        if not self.current_regions:
            messagebox.showinfo("信息", "没有区域需要保存")
            return
        
        try:
            saved_count = 0
            for name, region in self.current_regions.items():
                self.region_selector.save_region(f"测试_{name}", region)
                saved_count += 1
            
            self.log_message(f"已保存 {saved_count} 个区域")
            messagebox.showinfo("成功", f"已保存 {saved_count} 个区域")
            
        except Exception as e:
            self.log_message(f"保存区域失败: {e}")
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_saved_regions(self):
        """加载已保存的区域"""
        try:
            saved_regions = self.region_selector.get_saved_regions()
            if not saved_regions:
                messagebox.showinfo("信息", "没有已保存的区域")
                return
            
            # 显示选择对话框
            self.show_load_dialog(saved_regions)
            
        except Exception as e:
            self.log_message(f"加载区域失败: {e}")
            messagebox.showerror("错误", f"加载失败: {e}")
    
    def show_load_dialog(self, saved_regions):
        """显示加载区域对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("加载已保存区域")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="选择要加载的区域:").pack(pady=10)
        
        # 区域列表
        listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for region in saved_regions:
            listbox.insert(tk.END, region)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def load_selected():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("警告", "请选择区域")
                return
            
            loaded_count = 0
            for index in selected_indices:
                region_name = listbox.get(index)
                region = self.region_selector.load_region(region_name)
                if region:
                    # 去掉"测试_"前缀
                    display_name = region_name.replace("测试_", "")
                    self.current_regions[display_name] = region
                    loaded_count += 1
            
            if loaded_count > 0:
                self.update_region_list()
                self.log_message(f"已加载 {loaded_count} 个区域")
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="加载选中", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def run_auto_test(self):
        """运行自动化测试"""
        self.log_message("开始自动化测试...")
        
        # 这里可以添加自动化测试逻辑
        # 比如：加载预设区域，执行批量扫描等
        
        self.log_message("自动化测试功能待实现...")

def main():
    """主函数"""
    print("区域选择功能测试")
    print("=" * 50)
    
    root = tk.Tk()
    app = RegionTestGUI(root)
    
    # 添加菜单
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    test_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="测试", menu=test_menu)
    test_menu.add_command(label="自动测试", command=app.run_auto_test)
    test_menu.add_separator()
    test_menu.add_command(label="退出", command=root.quit)
    
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="帮助", menu=help_menu)
    help_menu.add_command(label="使用说明", command=lambda: messagebox.showinfo(
        "使用说明",
        "1. 点击'选择棋盘区域'按钮框选不同的棋盘\n"
        "2. 点击'测试扫描'按钮验证区域扫描功能\n"
        "3. 使用'预览区域'查看选择的区域\n"
        "4. '保存所有区域'可以保存当前区域配置\n"
        "5. '加载已保存区域'可以加载之前的配置\n\n"
        "适用场景：多个象棋软件同时运行时，可以为每个棋盘选择独立的扫描区域"
    ))
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main()