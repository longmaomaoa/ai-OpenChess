#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能对弈助手 - Enhanced GUI版本
现代化的图形用户界面，提供直观的中国象棋对弈体验
集成AI分析功能，提供实时走法推荐、胜率分析和智能对弈建议
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import os
import threading
import math
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.vision.region_selector import RegionSelector

class ChessScannerGUI:
    """中国象棋智能对弈助手 - GUI主类
    
    提供可视化界面，集成扫描器和AI助手功能
    上方显示为对手，下方显示为玩家
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏯 中国象棋智能对弈助手 v3.2 Enhanced - 四列布局版 🏯")
        self.root.geometry("1875x850")    # 调整窗口尺寸以适应四列布局（650+300+425+450+边距，750+标题+边距）
        self.root.minsize(1875, 850)      # 设置最小尺寸以适应四列布局
        
        # 现代化中国风主题色彩 - 1920x1080优化版
        self.colors = {
            'bg_primary': '#f8f6f0',       # 温润米白
            'bg_secondary': '#6b4423',      # 深棕色
            'wood_light': '#e8d7c3',        # 浅木色
            'wood_dark': '#8b7355',         # 深木色
            'gold': '#d4af37',              # 古典金
            'red_chinese': '#c8102e',       # 中国红
            'black_ink': '#1c1c1c',         # 墨黑
            'green_jade': '#22c55e',        # 现代翡翠绿
            'blue_porcelain': '#1e40af',    # 青花蓝
            'text_primary': '#1f2937',      # 主文字色
            'text_secondary': '#6b7280',    # 次文字色
            'accent_light': '#fef3c7',      # 浅强调色
            'accent_dark': '#92400e',       # 深强调色
            'success': '#10b981',           # 成功色
            'warning': '#f59e0b',           # 警告色
            'danger': '#ef4444',            # 危险色
            'border': '#d1d5db',            # 边框色
            'hover': '#f3f4f6',             # 悬浮色
            # AI视觉反馈专用色彩
            'ai_excellent': '#059669',      # 极佳走法 (深绿)
            'ai_good': '#10b981',           # 良好走法 (绿色)
            'ai_normal': '#f59e0b',         # 一般走法 (橙色)
            'ai_poor': '#ef4444',           # 差劲走法 (红色)
            'ai_highlight': '#fbbf24',      # AI推荐高亮
            'move_from': '#3b82f6',         # 起始位置
            'move_to': '#10b981',           # 目标位置
            'threat': '#ef4444',            # 威胁标记
            'opportunity': '#22c55e',       # 机会标记
            'win_rate_high': '#059669',     # 高胜率
            'win_rate_mid': '#f59e0b',      # 中等胜率
            'win_rate_low': '#dc2626',      # 低胜率
            'confidence_high': '#1e40af',   # 高置信度
            'confidence_mid': '#7c3aed',    # 中等置信度
            'confidence_low': '#9333ea'     # 低置信度
        }
        
        # 配置根窗口样式
        self.root.configure(bg=self.colors['bg_primary'])
        
        # 现代化字体配置 - 1920x1080优化
        self.fonts = {
            'title': ('华文行楷', 28, 'bold'),         # 标题字体 (增大)
            'subtitle': ('微软雅黑', 16, 'bold'),      # 副标题 (增大)
            'heading': ('微软雅黑', 14, 'bold'),       # 小标题 (增大)
            'normal': ('微软雅黑', 11),               # 正文 (增大)
            'button': ('微软雅黑', 10, 'bold'),       # 按钮 (增大)
            'piece': ('华文行楷', 16, 'bold'),        # 棋子字体 (增大)
            'status': ('Consolas', 10),               # 状态字体 (增大)
            'large': ('微软雅黑', 18, 'bold'),        # 大号字体 (增大)
            'small': ('微软雅黑', 9),                 # 小号字体 (增大)
            'code': ('Consolas', 10),                 # 代码字体 (增大)
            'win_rate': ('微软雅黑', 32, 'bold'),     # 胜率显示专用 (新增)
            'ai_recommendation': ('微软雅黑', 12),     # AI推荐专用 (新增)
            'piece_large': ('华文行楷', 18, 'bold'),  # 大号棋子字体 (新增)
            'board_label': ('华文行楷', 20, 'bold')   # 棋盘标签专用 (新增)
        }
        
        # 扫描器实例
        self.scanner = None
        self.ai_assistant = None  # AI助手实例
        self.scanning = False
        self.scan_thread = None
        
        # 棋盘状态
        self.board_state = [[None for _ in range(9)] for _ in range(10)]
        self.init_chess_board()  # 初始化为标准象棋开局
        
        # AI可视化增强
        self.highlighted_moves = []          # 高亮显示的推荐走法
        self.threat_positions = []           # 威胁位置标记
        self.opportunity_positions = []      # 机会位置标记
        self.last_ai_analysis = None         # 上次AI分析结果
        self.move_animation_active = False   # 走法动画状态
        self.confidence_indicators = {}      # 置信度指示器
        
        # 区域选择器和当前扫描区域
        self.region_selector = RegionSelector()
        self.current_scan_region = None  # 当前使用的扫描区域 (x, y, width, height)
        self.region_name_var = tk.StringVar(value="全屏")  # 当前区域名称
        
        # 配置样式
        self.configure_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化所有显示模块
        self.root.after(500, self.init_all_display_modules)  # 延迟500ms确保界面完全加载
        
        # 初始化扫描器
        self.init_scanner()
    
    def configure_styles(self):
        """配置现代化中国风样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('MainFrame.TLabelframe', 
                       background=self.colors['bg_primary'],
                       relief='flat',
                       borderwidth=0,
                       padding=15)
        style.configure('MainFrame.TLabelframe.Label',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['heading'])
        
        # 卡片样式框架
        style.configure('Card.TLabelframe', 
                       background='white',
                       relief='solid',
                       borderwidth=1,
                       padding=20)
        style.configure('Card.TLabelframe.Label',
                       background='white',
                       foreground=self.colors['text_primary'],
                       font=self.fonts['heading'])
        
        # 控制面板样式
        style.configure('Control.TLabelframe', 
                       background=self.colors['accent_light'],
                       relief='solid',
                       borderwidth=1,
                       padding=15)
        style.configure('Control.TLabelframe.Label',
                       background=self.colors['accent_light'],
                       foreground=self.colors['accent_dark'],
                       font=self.fonts['heading'])
        
        # 主要按钮样式
        style.configure('Primary.TButton',
                       background=self.colors['blue_porcelain'],
                       foreground='white',
                       font=self.fonts['button'],
                       relief='flat',
                       borderwidth=0,
                       padding=(12, 8))
        style.map('Primary.TButton',
                 background=[('active', '#1d4ed8'),
                           ('pressed', '#1e3a8a')])
        
        # 成功按钮样式（AI相关）
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       font=self.fonts['button'],
                       relief='flat',
                       borderwidth=0,
                       padding=(12, 8))
        style.map('Success.TButton',
                 background=[('active', '#059669'),
                           ('pressed', '#047857')])
        
        # 次要按钮样式
        style.configure('Secondary.TButton',
                       background=self.colors['wood_light'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['button'],
                       relief='solid',
                       borderwidth=1,
                       padding=(10, 6))
        style.map('Secondary.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['border'])])
        
        # 危险按钮样式
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       font=self.fonts['button'],
                       relief='flat',
                       borderwidth=0,
                       padding=(10, 6))
        style.map('Danger.TButton',
                 background=[('active', '#dc2626'),
                           ('pressed', '#b91c1c')])
        
        # 标签样式
        style.configure('Primary.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['normal'])
        
        style.configure('Card.TLabel',
                       background='white',
                       foreground=self.colors['text_primary'],
                       font=self.fonts['normal'])
        
        # 进度条样式
        style.configure('WinRate.Horizontal.TProgressbar',
                       background=self.colors['success'],
                       troughcolor=self.colors['border'],
                       borderwidth=0,
                       lightcolor=self.colors['success'],
                       darkcolor=self.colors['success'])
    
    def create_widgets(self):
        """创建现代化GUI组件 - 1920x1080优化的四区域布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 现代化标题区域
        self.create_header(main_container)
        
        # 主要内容区域 - 四列水平布局 (棋盘-控制-AI分析-日志)
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 配置网格权重 - 四列布局
        content_frame.columnconfigure(0, weight=0)  # 左侧固定宽度 (棋盘: 650)
        content_frame.columnconfigure(1, weight=0)  # 中间固定宽度 (控制: 300)
        content_frame.columnconfigure(2, weight=0)  # AI分析面板 (固定宽度: 425，原850的一半)
        content_frame.columnconfigure(3, weight=0)  # 右侧日志面板 (固定宽度: 450)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧：棋盘面板 (650x750)
        self.create_chess_board_panel(content_frame)
        
        # 中间：控制面板 (300x750)
        self.create_control_center_panel(content_frame)
        
        # 第三列：AI分析面板 (425x750，宽度减半)
        self.create_right_panel(content_frame)
        
        # 右侧：状态日志面板 (450x750，从底部移到右侧)
        self.create_status_log_panel(content_frame)
    
    def create_header(self, parent):
        """创建现代化标题区域"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 16))
        header_frame.pack_propagate(False)
        
        # 标题容器
        title_container = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_container.pack(expand=True, fill='both')
        
        # 主标题
        title_label = tk.Label(title_container, 
                             text="中国象棋智能对弈助手", 
                             font=self.fonts['title'],
                             fg=self.colors['red_chinese'],
                             bg=self.colors['bg_primary'])
        title_label.pack(pady=(8, 0))
        
        # 版本和副标题
        subtitle_frame = tk.Frame(title_container, bg=self.colors['bg_primary'])
        subtitle_frame.pack(pady=(4, 0))
        
        version_label = tk.Label(subtitle_frame, text="v3.1 Enhanced", 
                                font=self.fonts['small'],
                                fg=self.colors['blue_porcelain'],
                                bg=self.colors['bg_primary'])
        version_label.pack(side=tk.LEFT)
        
        separator_label = tk.Label(subtitle_frame, text=" • ", 
                                  font=self.fonts['small'],
                                  fg=self.colors['text_secondary'],
                                  bg=self.colors['bg_primary'])
        separator_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(subtitle_frame, text="AI 驱动的现代象棋助手", 
                                 font=self.fonts['small'],
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack(side=tk.LEFT)
        
        # AI状态标签
        ai_separator = tk.Label(subtitle_frame, text=" • ", 
                               font=self.fonts['small'],
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_primary'])
        ai_separator.pack(side=tk.LEFT)
        
        self.ai_status_label = tk.Label(subtitle_frame, text="AI助手: 初始化中...", 
                                      font=self.fonts['small'],
                                      fg='orange',
                                      bg=self.colors['bg_primary'])
        self.ai_status_label.pack(side=tk.LEFT)
    
    def create_chess_board_panel(self, parent):
        """创建棋盘面板 - 按要求调整为650x750尺寸"""
        # 左侧棋盘面板 - 按用户要求调整为650x750
        chess_board_frame = tk.Frame(parent, bg=self.colors['bg_primary'], 
                                    width=650, height=750)
        chess_board_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        chess_board_frame.pack_propagate(False)
        chess_board_frame.grid_propagate(False)
        
        # 棋盘标题卡片
        board_card = ttk.LabelFrame(chess_board_frame, text="🏯 棋盘局势", style='Card.TLabelframe')
        board_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 对弈双方标示 - 调整位置避免与棋盘重叠
        players_frame = tk.Frame(board_card, bg='white')
        players_frame.pack(fill='x', pady=(5, 10))
        
        # 调整玩家标签位置：黑方稍微左移，红方稍微右移
        black_label = tk.Label(players_frame, text="⚫ 黑方 (对手)", 
                              bg='white', fg=self.colors['black_ink'], 
                              font=self.fonts['normal'])
        black_label.pack(side=tk.LEFT, padx=(5, 10))  # 左移5px
        
        red_label = tk.Label(players_frame, text="🔴 红方 (玩家)", 
                            bg='white', fg=self.colors['red_chinese'], 
                            font=self.fonts['normal'])
        red_label.pack(side=tk.RIGHT, padx=(10, 5))  # 右移5px
        
        # 棋盘画布容器
        canvas_container = tk.Frame(board_card, bg='white')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 创建棋盘画布 - 550x550精确尺寸
        self.board_canvas = tk.Canvas(canvas_container, width=550, height=550, 
                                    bg='white', relief='flat', bd=0,
                                    highlightthickness=0)
        self.board_canvas.pack(expand=True)  # 居中显示
        
        # 绑定点击事件用于AI交互
        self.board_canvas.bind("<Button-1>", self.on_board_click)
        
        # 绘制棋盘网格和初始棋子
        self.draw_modern_board_grid()
        self.update_modern_board_display()
    
    def create_control_center_panel(self, parent):
        """创建控制面板 - 按要求调整为300x750尺寸"""
        # 中间控制面板 - 按用户要求调整为300x750
        control_center_frame = tk.Frame(parent, bg=self.colors['bg_primary'], 
                                       width=300, height=750)
        control_center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        control_center_frame.pack_propagate(False)
        control_center_frame.grid_propagate(False)
        
        # 控制面板标题卡片
        control_card = ttk.LabelFrame(control_center_frame, text="🎛️ 控制面板", style='Control.TLabelframe')
        control_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动容器来处理内容过多的问题
        canvas_frame = tk.Frame(control_card, bg=self.colors['accent_light'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['accent_light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['accent_light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 按钮容器 - 垂直排列（现在在可滚动框架内）
        buttons_container = scrollable_frame
        
        # 基础功能组
        basic_group = tk.LabelFrame(buttons_container, text="基础功能", 
                                   bg=self.colors['accent_light'], 
                                   fg=self.colors['accent_dark'],
                                   font=self.fonts['normal'])
        basic_group.pack(fill='x', pady=(0, 8))
        
        ttk.Button(basic_group, text="校准棋盘", command=self.calibrate_board, 
                  style='Primary.TButton').pack(fill='x', padx=5, pady=2)
        ttk.Button(basic_group, text="单次扫描", command=self.single_scan, 
                  style='Secondary.TButton').pack(fill='x', padx=5, pady=2)
        ttk.Button(basic_group, text="创建模板", command=self.create_template, 
                  style='Secondary.TButton').pack(fill='x', padx=5, pady=2)
        
        # 区域功能组
        region_group = tk.LabelFrame(buttons_container, text="区域选择", 
                                    bg=self.colors['accent_light'], 
                                    fg=self.colors['accent_dark'],
                                    font=self.fonts['normal'])
        region_group.pack(fill='x', pady=(0, 8))
        
        ttk.Button(region_group, text="选择区域", command=self.select_scan_region, 
                  style='Primary.TButton').pack(fill='x', padx=5, pady=2)
        ttk.Button(region_group, text="管理区域", command=self.manage_regions, 
                  style='Secondary.TButton').pack(fill='x', padx=5, pady=2)
        
        # 当前区域显示
        region_info_frame = tk.Frame(region_group, bg=self.colors['accent_light'])
        region_info_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Label(region_info_frame, text="当前区域:", 
                bg=self.colors['accent_light'], 
                fg=self.colors['text_primary'], 
                font=self.fonts['small']).pack(anchor='w')
        tk.Label(region_info_frame, textvariable=self.region_name_var, 
                bg=self.colors['accent_light'], 
                fg=self.colors['blue_porcelain'], 
                font=self.fonts['normal']).pack(anchor='w', padx=(10, 0))
        
        # AI功能组
        ai_group = tk.LabelFrame(buttons_container, text="AI 助手", 
                                bg=self.colors['accent_light'], 
                                fg=self.colors['accent_dark'],
                                font=self.fonts['normal'])
        ai_group.pack(fill='x', pady=(0, 8))
        
        ttk.Button(ai_group, text="启动 AI 助手", command=self.start_ai_monitoring, 
                  style='Success.TButton').pack(fill='x', padx=5, pady=2)
        ttk.Button(ai_group, text="停止监控", command=self.stop_ai_monitoring, 
                  style='Danger.TButton').pack(fill='x', padx=5, pady=2)
        ttk.Button(ai_group, text="获取推荐", command=self.get_ai_recommendation, 
                  style='Success.TButton').pack(fill='x', padx=5, pady=2)
        
        # AI分析功能组
        ai_analysis_group = tk.LabelFrame(buttons_container, text="AI 分析", 
                                         bg=self.colors['accent_light'], 
                                         fg=self.colors['accent_dark'],
                                         font=self.fonts['normal'])
        ai_analysis_group.pack(fill='x', pady=(0, 8))
        
        ttk.Button(ai_analysis_group, text="高亮推荐", command=self.highlight_recommendations, 
                  style='Success.TButton').pack(fill='x', padx=5, pady=1)
        ttk.Button(ai_analysis_group, text="清除高亮", command=self.clear_highlights, 
                  style='Secondary.TButton').pack(fill='x', padx=5, pady=1)
        ttk.Button(ai_analysis_group, text="威胁分析", command=self.show_threats, 
                  style='Danger.TButton').pack(fill='x', padx=5, pady=1)
        ttk.Button(ai_analysis_group, text="机会分析", command=self.show_opportunities, 
                  style='Success.TButton').pack(fill='x', padx=5, pady=1)
        
        # 系统功能组
        system_group = tk.LabelFrame(buttons_container, text="系统功能", 
                                   bg=self.colors['accent_light'], 
                                   fg=self.colors['accent_dark'],
                                   font=self.fonts['normal'])
        system_group.pack(fill='x', pady=(0, 8))
        
        ttk.Button(system_group, text="刷新面板", command=self.refresh_all_panels, 
                  style='Secondary.TButton').pack(fill='x', padx=5, pady=1)
        ttk.Button(system_group, text="高级模式", command=self.toggle_advanced_mode, 
                  style='Primary.TButton').pack(fill='x', padx=5, pady=1)
    
    def create_left_panel(self, parent):
        """创建左侧面板（控制和棋盘）- 1920x1080优化"""
        left_panel = tk.Frame(parent, bg=self.colors['bg_primary'])
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_panel.rowconfigure(1, weight=1)  # 棋盘区域占主要空间
        
        # 控制面板
        self.create_control_panel(left_panel)
        
        # 棋盘面板
        self.create_board_panel(left_panel)
    
    def create_control_panel(self, parent):
        """创建现代化控制面板"""
        control_card = ttk.LabelFrame(parent, text="控制面板", style='Control.TLabelframe')
        control_card.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # 基础功能区
        basic_frame = tk.Frame(control_card, bg=self.colors['accent_light'])
        basic_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Button(basic_frame, text="校准棋盘", command=self.calibrate_board, 
                  style='Primary.TButton').grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(basic_frame, text="单次扫描", command=self.single_scan, 
                  style='Secondary.TButton').grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(basic_frame, text="创建模板", command=self.create_template, 
                  style='Secondary.TButton').grid(row=0, column=2, padx=4, pady=4)
        
        # 区域选择功能
        region_frame = tk.Frame(control_card, bg=self.colors['accent_light'])
        region_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Button(region_frame, text="选择区域", command=self.select_scan_region, 
                  style='Primary.TButton').grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(region_frame, text="管理区域", command=self.manage_regions, 
                  style='Secondary.TButton').grid(row=0, column=1, padx=4, pady=4)
        
        # 当前区域显示
        region_info = tk.Frame(region_frame, bg=self.colors['accent_light'])
        region_info.grid(row=0, column=2, padx=(8, 0), pady=4, sticky="w")
        
        tk.Label(region_info, text="当前区域:", bg=self.colors['accent_light'], 
                fg=self.colors['text_primary'], font=self.fonts['small']).pack(side=tk.LEFT)
        tk.Label(region_info, textvariable=self.region_name_var, 
                bg=self.colors['accent_light'], fg=self.colors['blue_porcelain'], 
                font=self.fonts['normal']).pack(side=tk.LEFT, padx=(4, 0))
        
        # AI控制功能
        ai_frame = tk.Frame(control_card, bg=self.colors['accent_light'])
        ai_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(ai_frame, text="启动 AI 助手", command=self.start_ai_monitoring, 
                  style='Success.TButton').grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(ai_frame, text="停止监控", command=self.stop_ai_monitoring, 
                  style='Danger.TButton').grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(ai_frame, text="获取推荐", command=self.get_ai_recommendation, 
                  style='Success.TButton').grid(row=0, column=2, padx=4, pady=4)
    
    def create_board_panel(self, parent):
        """创建棋盘面板"""
        board_card = ttk.LabelFrame(parent, text="棋盘局势", style='Card.TLabelframe')
        board_card.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        board_card.columnconfigure(0, weight=1)
        board_card.rowconfigure(1, weight=1)
        
        # 对弈双方标示 - 优化布局确保在可视区域内
        players_frame = tk.Frame(board_card, bg='white')
        players_frame.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        
        # 使用网格布局更好地控制位置
        players_frame.columnconfigure(0, weight=1)
        players_frame.columnconfigure(1, weight=1)
        
        black_label = tk.Label(players_frame, text="⚫ 黑方 (对手)", 
                              bg='white', fg=self.colors['black_ink'], 
                              font=self.fonts['normal'])
        black_label.grid(row=0, column=0, pady=4, padx=10, sticky='w')
        
        red_label = tk.Label(players_frame, text="🔴 红方 (玩家)", 
                            bg='white', fg=self.colors['red_chinese'], 
                            font=self.fonts['normal'])
        red_label.grid(row=0, column=1, pady=4, padx=10, sticky='e')
        
        # 创建现代化棋盘显示
        self.create_modern_board_display(board_card)
    
    def create_right_panel(self, parent):
        """创建AI分析面板 - 宽度减半为425x750尺寸"""
        right_panel = tk.Frame(parent, bg=self.colors['bg_primary'], width=425, height=750)
        right_panel.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        right_panel.pack_propagate(False)
        right_panel.grid_propagate(False)
        right_panel.rowconfigure(0, weight=0, minsize=180)  # 胜率卡片固定高度180px
        right_panel.rowconfigure(1, weight=1, minsize=280)  # 推荐走法卡片最小280px
        right_panel.rowconfigure(2, weight=1, minsize=280)  # 局面分析卡片最小280px
        right_panel.columnconfigure(0, weight=1)
        
        # 胜率显示卡片
        self.create_win_rate_card(right_panel)
        
        # 推荐走法卡片
        self.create_recommendations_card(right_panel)
        
        # 局面分析卡片
        self.create_analysis_card(right_panel)
    
    def create_win_rate_card(self, parent):
        """创建胜率显示卡片 - 1920x1080优化"""
        win_rate_card = ttk.LabelFrame(parent, text="🎯 AI 胜率分析", style='Card.TLabelframe')
        win_rate_card.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 主胜率显示区域 - 紧凑布局
        rate_display_frame = tk.Frame(win_rate_card, bg='white')
        rate_display_frame.pack(fill='x', pady=(5, 5))
        
        # 大号胜率数字
        self.win_rate_label = tk.Label(rate_display_frame, text="---%", 
                                     font=self.fonts['win_rate'],
                                     bg='white',
                                     fg=self.colors['success'])
        self.win_rate_label.pack()
        
        # 胜率状态描述
        self.win_rate_status = tk.Label(rate_display_frame, text="等待分析中...", 
                                      font=self.fonts['normal'],
                                      bg='white',
                                      fg=self.colors['text_secondary'])
        self.win_rate_status.pack(pady=(5, 0))
        
        # 增强的胜率进度条
        progress_frame = tk.Frame(win_rate_card, bg='white')
        progress_frame.pack(fill='x', pady=(0, 5))
        
        self.win_rate_progress = ttk.Progressbar(progress_frame, 
                                               style='WinRate.Horizontal.TProgressbar',
                                               mode='determinate', length=300)
        self.win_rate_progress.pack(fill='x', pady=5)
        
        # 胜率详细信息
        detail_frame = tk.Frame(win_rate_card, bg='white')
        detail_frame.pack(fill='x')
        
        # 左侧：优势方
        self.advantage_label = tk.Label(detail_frame, text="", 
                                      font=self.fonts['small'],
                                      bg='white', fg=self.colors['text_secondary'])
        self.advantage_label.pack(side=tk.LEFT)
        
        # 右侧：置信度
        self.confidence_label = tk.Label(detail_frame, text="", 
                                       font=self.fonts['small'],
                                       bg='white', fg=self.colors['text_secondary'])
        self.confidence_label.pack(side=tk.RIGHT)
    
    def create_recommendations_card(self, parent):
        """创建推荐走法卡片 - 1920x1080优化"""
        rec_card = ttk.LabelFrame(parent, text="🚀 AI 推荐走法", style='Card.TLabelframe')
        rec_card.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        rec_card.columnconfigure(0, weight=1)
        rec_card.rowconfigure(1, weight=1)
        
        # 推荐控制按钮区域
        control_frame = tk.Frame(rec_card, bg='white')
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        
        ttk.Button(control_frame, text="高亮显示", 
                  command=self.highlight_recommendations,
                  style='Success.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="清除高亮", 
                  command=self.clear_highlights,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="自动走法", 
                  command=self.auto_execute_move,
                  style='Primary.TButton').pack(side=tk.RIGHT)
        
        # 推荐文本区域 - 增大尺寸
        text_frame = tk.Frame(rec_card, bg='white')
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.recommendation_text = tk.Text(text_frame, height=10, width=30,
                                         bg='#fafafa', fg=self.colors['text_primary'],
                                         font=self.fonts['ai_recommendation'], relief='flat', bd=0,
                                         padx=8, pady=6, wrap=tk.WORD)
        self.recommendation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        rec_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                     command=self.recommendation_text.yview)
        rec_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.recommendation_text.configure(yscrollcommand=rec_scrollbar.set)
        
        # 初始化推荐文本显示
        self.update_recommendation_display()
    
    def create_analysis_card(self, parent):
        """创建局面分析卡片 - 1920x1080优化"""
        analysis_card = ttk.LabelFrame(parent, text="🔍 深度局面分析", style='Card.TLabelframe')
        analysis_card.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        analysis_card.columnconfigure(0, weight=1)
        analysis_card.rowconfigure(1, weight=1)
        
        # 分析控制区域
        analysis_control_frame = tk.Frame(analysis_card, bg='white')
        analysis_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        
        ttk.Button(analysis_control_frame, text="威胁分析", 
                  command=self.show_threats,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(analysis_control_frame, text="机会分析", 
                  command=self.show_opportunities,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(analysis_control_frame, text="详细报告", 
                  command=self.generate_detailed_report,
                  style='Primary.TButton').pack(side=tk.RIGHT)
        
        # 分析文本区域 - 增大尺寸
        analysis_frame = tk.Frame(analysis_card, bg='white')
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
        
        self.analysis_text = tk.Text(analysis_frame, height=8, width=30,
                                   bg='#fafafa', fg=self.colors['text_primary'],
                                   font=self.fonts['ai_recommendation'], relief='flat', bd=0,
                                   padx=8, pady=6, wrap=tk.WORD)
        self.analysis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, 
                                         command=self.analysis_text.yview)
        analysis_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        
        # 初始化分析文本显示
        self.update_analysis_display()
    
    def create_status_log_panel(self, parent):
        """创建右侧状态日志面板 - 450x750尺寸"""
        # 右侧日志面板 - 从底部移到第四列
        log_panel = tk.Frame(parent, bg=self.colors['bg_primary'], width=450, height=750)
        log_panel.grid(row=0, column=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0))
        log_panel.pack_propagate(False)
        log_panel.grid_propagate(False)
        
        status_card = ttk.LabelFrame(log_panel, text="📊 系统状态与日志", style='Card.TLabelframe')
        status_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态文本区域 - 适应右侧列布局
        status_frame = tk.Frame(status_card, bg='white')
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 调整文本区域尺寸以适应450px宽度
        self.status_text = tk.Text(status_frame, height=35, width=50,
                                 bg='#f8f9fa', fg=self.colors['text_primary'], 
                                 font=self.fonts['code'], relief='flat', bd=0,
                                 padx=10, pady=8, wrap=tk.WORD,
                                 insertbackground=self.colors['blue_porcelain'])
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, 
                                       command=self.status_text.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        # 添加现代化欢迎信息 - 四列布局版本
        welcome_msg = """🏯 中国象棋智能对弈助手 - Enhanced v3.2 - 四列布局版 🏯

✨ 全新四列界面布局，系统已就绪！

📋 界面布局（按用户要求定制）：
  • 第一列：棋盘局势模块 (650x750) - 棋盘画布居中显示
  • 第二列：控制面板 (300x750) - 垂直排列的功能按钮
  • 第三列：AI分析面板 (425x750) - 胜率分析、推荐走法、局面分析
  • 第四列：系统日志模块 (450x750) - 从底部移至右侧列

🎯 快速开始：
  1. 点击"校准棋盘"设置扫描区域
  2. 使用"选择区域"功能精确定位棋盘
  3. 启动"AI 助手"开始智能分析

🚀 1920x1080版本特色：
  • 四区域布局设计：顶部标题 + 三列内容 + 底部日志
  • 棋盘画布精确调整为550x550像素，网格大小52px
  • 控制面板宽度扩展至320px，按钮布局优化
  • 状态日志面板完全恢复，高度增至8行
  • AI分析面板保持可扩展性，适应大屏显示
  • 所有边距和间距针对1920x1080分辨率优化

🚀 AI增强功能：
  • 实时棋盘识别与状态监控
  • AI 智能走法推荐与胜率分析
  • 威胁与机会智能识别
  • 详细局面分析报告
  • 多区域扫描支持，适应不同对弈场景

准备好在全新优化的1920x1080界面上开始您的象棋AI之旅了吗？
"""
        self.status_text.insert(tk.END, welcome_msg)
    
    def create_modern_board_display(self, parent):
        """创建现代化棋盘显示 - 1920x1080优化"""
        # 棋盘画布容器
        canvas_container = tk.Frame(parent, bg='white')
        canvas_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        canvas_container.columnconfigure(0, weight=1)
        canvas_container.rowconfigure(0, weight=1)
        
        # 创建适中的现代化棋盘画布 - 确保完整可见
        self.board_canvas = tk.Canvas(canvas_container, width=720, height=800, 
                                    bg='white', relief='flat', bd=0,
                                    highlightthickness=0)
        self.board_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        
        # 绑定点击事件用于AI交互
        self.board_canvas.bind("<Button-1>", self.on_board_click)
        
        # 绘制现代化棋盘网格
        self.draw_modern_board_grid()
        
        # 显示初始棋子位置
        self.update_modern_board_display()
    
    def draw_modern_board_grid(self):
        """绘制现代化棋盘网格 - 适配550x550画布"""
        self.board_canvas.delete("all")
        
        # 现代化棋盘参数 - 适配550x550画布
        margin = 40
        cell_size = 52  # 调整为适合550x550的网格大小
        start_x = margin
        start_y = margin
        
        # 获取画布尺寸
        canvas_width = 550
        canvas_height = 550
        
        # 绘制清新的背景
        self.board_canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='#fafafa', outline='')
        
        # 绘制棋盘边框
        border_x1 = start_x - 15
        border_y1 = start_y - 15
        border_x2 = start_x + 8 * cell_size + 15
        border_y2 = start_y + 9 * cell_size + 15
        
        self.board_canvas.create_rectangle(border_x1, border_y1, border_x2, border_y2, 
                                         fill=self.colors['wood_light'], 
                                         outline=self.colors['wood_dark'], width=3)
        
        # 绘制主要网格线（横线）- 1920x1080优化，增加线条粗细
        for i in range(10):
            y = start_y + i * cell_size
            line_color = self.colors['black_ink'] if i in [0, 9] else '#4a5568'
            line_width = 3 if i in [0, 9] else 2
            
            self.board_canvas.create_line(start_x, y, start_x + 8 * cell_size, y, 
                                        fill=line_color, width=line_width, capstyle='round')
        
        # 绘制竖线 - 1920x1080优化
        for i in range(9):
            x = start_x + i * cell_size
            line_color = self.colors['black_ink'] if i in [0, 8] else '#4a5568'
            line_width = 3 if i in [0, 8] else 2
            
            # 上半部分
            self.board_canvas.create_line(x, start_y, x, start_y + 4 * cell_size, 
                                        fill=line_color, width=line_width, capstyle='round')
            # 下半部分
            self.board_canvas.create_line(x, start_y + 5 * cell_size, x, start_y + 9 * cell_size, 
                                        fill=line_color, width=line_width, capstyle='round')
        
        # 绘制九宫格对角线
        self.draw_modern_palace_diagonals(start_x, start_y, cell_size)
        
        # 绘制位置标记点
        self.draw_modern_position_markers(start_x, start_y, cell_size)
        
        # 绘制楚河汉界
        self.draw_modern_river(start_x, start_y, cell_size)
    
    def draw_modern_palace_diagonals(self, start_x, start_y, cell_size):
        """绘制现代化九宫格对角线 - 1920x1080优化"""
        # 上方九宫
        palace_x1 = start_x + 3 * cell_size
        palace_x2 = start_x + 5 * cell_size
        palace_y1 = start_y
        palace_y2 = start_y + 2 * cell_size
        
        self.board_canvas.create_line(palace_x1, palace_y1, palace_x2, palace_y2, 
                                    fill='#4a5568', width=2, capstyle='round')
        self.board_canvas.create_line(palace_x2, palace_y1, palace_x1, palace_y2, 
                                    fill='#4a5568', width=2, capstyle='round')
        
        # 下方九宫
        palace_y1 = start_y + 7 * cell_size
        palace_y2 = start_y + 9 * cell_size
        
        self.board_canvas.create_line(palace_x1, palace_y1, palace_x2, palace_y2, 
                                    fill='#4a5568', width=2, capstyle='round')
        self.board_canvas.create_line(palace_x2, palace_y1, palace_x1, palace_y2, 
                                    fill='#4a5568', width=2, capstyle='round')
    
    def draw_modern_position_markers(self, start_x, start_y, cell_size):
        """绘制现代化位置标记点 - 1920x1080优化"""
        positions = [
            (0, 3), (2, 3), (4, 3), (6, 3), (8, 3),  # 上方兵点
            (1, 2), (7, 2),  # 上方炮点
            (0, 6), (2, 6), (4, 6), (6, 6), (8, 6),  # 下方兵点
            (1, 7), (7, 7)   # 下方炮点
        ]
        
        for col, row in positions:
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            
            # 绘制增大的圆点标记 - 1920x1080优化
            self.board_canvas.create_oval(x-4, y-4, x+4, y+4, 
                                        fill='#6b7280', outline='')
    
    def draw_modern_river(self, start_x, start_y, cell_size):
        """绘制现代化楚河汉界 - 1920x1080优化"""
        river_y = start_y + 4.5 * cell_size
        
        # 楚河汉界区域 - 1920x1080优化，增大尺寸
        self.board_canvas.create_rectangle(start_x + 1 * cell_size, river_y - 25,
                                         start_x + 7 * cell_size, river_y + 25,
                                         fill='#f0f9ff', outline=self.colors['blue_porcelain'], 
                                         width=2)
        
        # 楚河文字 - 1920x1080优化，增大字体
        self.board_canvas.create_text(start_x + 2.5 * cell_size, river_y, 
                                    text="楚河", font=self.fonts['board_label'], 
                                    fill=self.colors['red_chinese'])
        
        # 汉界文字 - 1920x1080优化，增大字体
        self.board_canvas.create_text(start_x + 5.5 * cell_size, river_y, 
                                    text="汉界", font=self.fonts['board_label'], 
                                    fill=self.colors['black_ink'])
    
    def update_modern_board_display(self):
        """更新现代化棋盘显示 - 适配550x550画布"""
        # 清除棋子和AI标记
        self.board_canvas.delete("piece")
        self.board_canvas.delete("ai_highlight")
        self.board_canvas.delete("ai_marker")
        
        # 棋盘参数 - 适配550x550画布
        margin = 40
        cell_size = 52
        start_x = margin
        start_y = margin
        
        # 绘制AI可视化标记（在棋子下方）
        self.draw_ai_visualizations(start_x, start_y, cell_size)
        
        # 绘制棋子 - 1920x1080优化，增大尺寸
        for row in range(10):
            for col in range(9):
                piece = self.board_state[row][col]
                if piece is not None:
                    x = start_x + col * cell_size
                    y = start_y + row * cell_size
                    
                    # 现代化棋子样式 - 增大尺寸
                    is_red = "red" in piece
                    
                    # 棋子阴影 - 适配550x550画布，稍小尺寸
                    self.board_canvas.create_oval(x-18, y-18, x+18, y+18, 
                                                fill='#e5e7eb', outline='', tags="piece")
                    
                    # 棋子背景 - 适配550x550画布
                    bg_color = '#ffffff'
                    border_color = self.colors['red_chinese'] if is_red else self.colors['black_ink']
                    
                    self.board_canvas.create_oval(x-16, y-16, x+16, y+16, 
                                                fill=bg_color, 
                                                outline=border_color, 
                                                width=2, tags="piece")
                    
                    # 棋子文字 - 使用更大字体
                    piece_text = self.get_piece_text(piece)
                    text_color = self.colors['red_chinese'] if is_red else self.colors['black_ink']
                    
                    self.board_canvas.create_text(x, y, text=piece_text, 
                                                fill=text_color, 
                                                font=self.fonts['piece_large'], tags="piece")
    
    def draw_ai_visualizations(self, start_x, start_y, cell_size):
        """绘制AI可视化标记 - 推荐走法、威胁、机会等"""
        # 绘制推荐走法高亮
        for move in self.highlighted_moves:
            from_row, from_col, to_row, to_col = move
            
            # 起始位置标记 - 适配550x550画布
            from_x = start_x + from_col * cell_size
            from_y = start_y + from_row * cell_size
            self.board_canvas.create_rectangle(from_x-20, from_y-20, from_x+20, from_y+20,
                                             outline=self.colors['move_from'], width=2,
                                             fill='', tags="ai_highlight")
            
            # 目标位置标记 - 适配550x550画布
            to_x = start_x + to_col * cell_size
            to_y = start_y + to_row * cell_size
            self.board_canvas.create_rectangle(to_x-20, to_y-20, to_x+20, to_y+20,
                                             outline=self.colors['move_to'], width=2,
                                             fill='', tags="ai_highlight")
            
            # 绘制移动箭头
            self.board_canvas.create_line(from_x, from_y, to_x, to_y,
                                        fill=self.colors['ai_highlight'], width=4,
                                        arrow=tk.LAST, arrowshape=(16, 20, 6),
                                        tags="ai_highlight")
        
        # 绘制威胁位置 - 适配550x550画布
        for row, col in self.threat_positions:
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            self.board_canvas.create_oval(x-22, y-22, x+22, y+22,
                                        outline=self.colors['threat'], width=2,
                                        fill='', tags="ai_marker")
            # 添加威胁图标
            self.board_canvas.create_text(x-26, y-26, text="⚠", 
                                        fill=self.colors['threat'],
                                        font=('Arial', 12, 'bold'), tags="ai_marker")
        
        # 绘制机会位置 - 适配550x550画布
        for row, col in self.opportunity_positions:
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            self.board_canvas.create_oval(x-22, y-22, x+22, y+22,
                                        outline=self.colors['opportunity'], width=2,
                                        fill='', tags="ai_marker")
            # 添加机会图标
            self.board_canvas.create_text(x-26, y-26, text="★", 
                                        fill=self.colors['opportunity'],
                                        font=('Arial', 12, 'bold'), tags="ai_marker")
    
    def on_board_click(self, event):
        """处理棋盘点击事件 - AI交互功能"""
        if not hasattr(self, 'board_canvas'):
            return
            
        # 获取点击位置对应的棋盘坐标 - 适配550x550画布
        margin = 40
        cell_size = 52
        start_x = margin
        start_y = margin
        
        # 计算点击的格子位置
        col = round((event.x - start_x) / cell_size)
        row = round((event.y - start_y) / cell_size)
        
        # 检查是否在棋盘范围内
        if 0 <= row < 10 and 0 <= col < 9:
            # 显示位置信息（可以扩展为更多AI交互功能）
            position_info = f"点击位置: 第{row+1}行, 第{col+1}列"
            piece = self.board_state[row][col]
            if piece:
                piece_text = self.get_piece_text(piece)
                position_info += f" - {piece_text}"
            
            self.log_message(position_info)
    
    # 保持原有的古木棋盘显示方法以确保兼容性
    def create_board_display(self, parent):
        """创建古木棋盘显示"""
        # 棋盘框架
        board_canvas_frame = tk.Frame(parent, bg=self.colors['wood_light'])
        board_canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建古木风格棋盘画布 - 增大尺寸以显示完整棋盘
        self.board_canvas = tk.Canvas(board_canvas_frame, width=600, height=650, 
                                    bg=self.colors['wood_light'], relief='raised', bd=5,
                                    highlightthickness=0)
        self.board_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 配置网格权重
        board_canvas_frame.columnconfigure(0, weight=1)
        board_canvas_frame.rowconfigure(0, weight=1)
        
        # 绘制古木棋盘网格
        self.draw_board_grid()
        
        # 显示初始棋子位置
        self.update_board_display()
    
    def draw_board_grid(self):
        """绘制古木风格棋盘网格"""
        self.board_canvas.delete("all")
        
        # 棋盘参数 - 调整以适应更大的画布，确保完整显示
        margin = 60
        cell_size = 55
        start_x = margin
        start_y = margin
        
        # 绘制古木纹背景效果
        self.draw_wood_texture()
        
        # 绘制精美的棋盘网格线（去除简陋的下划线风格）
        # 绘制主要网格线（横线）
        for i in range(10):
            y = start_y + i * cell_size
            # 使用渐变色彩和阴影效果
            if i == 0 or i == 9:  # 边界线
                self.board_canvas.create_line(start_x - 5, y, start_x + 8 * cell_size + 5, y, 
                                            fill='#654321', width=4, capstyle='round')
            else:
                self.board_canvas.create_line(start_x, y, start_x + 8 * cell_size, y, 
                                            fill='#8B4513', width=2, capstyle='round')
        
        # 绘制竖线
        for i in range(9):
            x = start_x + i * cell_size
            if i == 0 or i == 8:  # 边界线
                # 上半部分
                self.board_canvas.create_line(x, start_y - 5, x, start_y + 4 * cell_size, 
                                            fill='#654321', width=4, capstyle='round')
                # 下半部分
                self.board_canvas.create_line(x, start_y + 5 * cell_size, x, start_y + 9 * cell_size + 5, 
                                            fill='#654321', width=4, capstyle='round')
            else:
                # 上半部分
                self.board_canvas.create_line(x, start_y, x, start_y + 4 * cell_size, 
                                            fill='#8B4513', width=2, capstyle='round')
                # 下半部分
                self.board_canvas.create_line(x, start_y + 5 * cell_size, x, start_y + 9 * cell_size, 
                                            fill='#8B4513', width=2, capstyle='round')
        
        # 绘制九宫格对角线（优化样式）
        self.draw_palace_diagonals(start_x, start_y, cell_size)
        
        # 绘制精美的位置标记点
        self.draw_position_markers(start_x, start_y, cell_size)
        
        # 绘制楚河汉界 (新的位置和样式)
        river_y = start_y + 4.5 * cell_size
        
        # 精美的楚河汉界区域
        river_rect = self.board_canvas.create_rectangle(start_x + 1 * cell_size, river_y - 18,
                                         start_x + 7 * cell_size, river_y + 18,
                                         fill='#F5DEB3', outline='#8B4513', width=3,
                                         activefill='#FFEFD5')
        
        # 添加装饰性边框
        self.board_canvas.create_rectangle(start_x + 1 * cell_size + 5, river_y - 15,
                                         start_x + 7 * cell_size - 5, river_y + 15,
                                         fill='', outline='#DAA520', width=1)
        
        # 楚河文字 (左侧) - 使用更大更美的字体
        self.board_canvas.create_text(start_x + 2.5 * cell_size, river_y, 
                                    text="楚 河", font=('SimHei', 16, 'bold'), 
                                    fill=self.colors['red_chinese'])
        
        # 汉界文字 (右侧)
        self.board_canvas.create_text(start_x + 5.5 * cell_size, river_y, 
                                    text="汉 界", font=('SimHei', 16, 'bold'), 
                                    fill=self.colors['black_ink'])
    
    def draw_wood_texture(self):
        """绘制精美的木纹背景效果"""
        width = 600  # 匹配新的画布尺寸
        height = 650
        
        # 主背景色
        self.board_canvas.create_rectangle(0, 0, width, height, 
                                         fill=self.colors['wood_light'], outline="")
        
        # 绘制细腻的木纹纹理（水平纹理）
        for i in range(0, height, 8):
            alpha = 0.1 if i % 16 == 0 else 0.05
            color = '#8B7355' if (i // 8) % 2 == 0 else '#DEB887'
            self.board_canvas.create_rectangle(0, i, width, i + 4, fill=color, outline="")
        
        # 添加垂直的木纹细节
        for i in range(0, width, 25):
            color = '#CD853F' if (i // 25) % 3 == 0 else '#D2B48C'
            self.board_canvas.create_rectangle(i, 0, i + 1, height, fill=color, outline="")
    
    def draw_palace_diagonals(self, start_x, start_y, cell_size):
        """绘制九宫格对角线"""
        # 上方九宫
        palace_x1 = start_x + 3 * cell_size
        palace_x2 = start_x + 5 * cell_size
        palace_y1 = start_y
        palace_y2 = start_y + 2 * cell_size
        
        # 上方九宫对角线（精美样式）
        self.board_canvas.create_line(palace_x1, palace_y1, palace_x2, palace_y2, 
                                    fill='#8B4513', width=3, capstyle='round')
        self.board_canvas.create_line(palace_x2, palace_y1, palace_x1, palace_y2, 
                                    fill='#8B4513', width=3, capstyle='round')
        
        # 下方九宫
        palace_y1 = start_y + 7 * cell_size
        palace_y2 = start_y + 9 * cell_size
        
        # 下方九宫对角线（精美样式）
        self.board_canvas.create_line(palace_x1, palace_y1, palace_x2, palace_y2, 
                                    fill='#8B4513', width=3, capstyle='round')
        self.board_canvas.create_line(palace_x2, palace_y1, palace_x1, palace_y2, 
                                    fill='#8B4513', width=3, capstyle='round')
    
    def draw_position_markers(self, start_x, start_y, cell_size):
        """绘制兵点标记点"""
        # 兵点位置
        pawn_positions = [
            (0, 3), (2, 3), (4, 3), (6, 3), (8, 3),  # 上方兵点
            (1, 2), (7, 2),  # 上方炮点
            (0, 6), (2, 6), (4, 6), (6, 6), (8, 6),  # 下方兵点
            (1, 7), (7, 7)   # 下方炮点
        ]
        
        # 绘制精美的位置标记点
        for col, row in pawn_positions:
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            
            # 绘制小圆点标记（增强视觉效果）
            # 外圈
            self.board_canvas.create_oval(x-4, y-4, x+4, y+4, 
                                        fill='#CD853F', outline='#8B4513', width=1)
            # 内圈
            self.board_canvas.create_oval(x-2, y-2, x+2, y+2, 
                                        fill='#8B4513', outline="")
    
    def update_board_display(self):
        """更新棋盘显示 - 使用现代化版本"""
        self.update_modern_board_display()
    
    def get_piece_text(self, piece):
        """获取棋子显示文字"""
        # 优化的棋子映射，使用更正统的中国象棋字体
        piece_map = {
            'red_king': '帅',
            'red_advisor': '仕', 
            'red_elephant': '相',
            'red_horse': '马',
            'red_chariot': '车',
            'red_cannon': '炮',
            'red_pawn': '兵',
            'black_king': '将',
            'black_advisor': '士',
            'black_elephant': '象',
            'black_horse': '马',
            'black_chariot': '车',
            'black_cannon': '炮',
            'black_pawn': '卒'
        }
        return piece_map.get(piece, '?')
    
    def init_chess_board(self):
        """初始化为标准象棋开局状态"""
        # 清空棋盘
        self.board_state = [[None for _ in range(9)] for _ in range(10)]
        
        # 黑方棋子（上方，第0-4行）
        # 第0行：车马相士将士相马车
        black_pieces_row0 = ['black_chariot', 'black_horse', 'black_elephant', 'black_advisor', 'black_king', 
                             'black_advisor', 'black_elephant', 'black_horse', 'black_chariot']
        for col, piece in enumerate(black_pieces_row0):
            self.board_state[0][col] = piece
        
        # 第2行：炮
        self.board_state[2][1] = 'black_cannon'
        self.board_state[2][7] = 'black_cannon'
        
        # 第3行：卒
        for col in [0, 2, 4, 6, 8]:
            self.board_state[3][col] = 'black_pawn'
        
        # 红方棋子（下方，第5-9行）
        # 第6行：兵
        for col in [0, 2, 4, 6, 8]:
            self.board_state[6][col] = 'red_pawn'
        
        # 第7行：炮
        self.board_state[7][1] = 'red_cannon'
        self.board_state[7][7] = 'red_cannon'
        
        # 第9行：车马相仕帅仕相马车
        red_pieces_row9 = ['red_chariot', 'red_horse', 'red_elephant', 'red_advisor', 'red_king',
                           'red_advisor', 'red_elephant', 'red_horse', 'red_chariot']
        for col, piece in enumerate(red_pieces_row9):
            self.board_state[9][col] = piece
        
        print("已初始化标准象棋开局")
    
    def init_scanner(self):
        """异步初始化扫描器和AI助手，避免阻塞GUI"""
        def init_thread():
            try:
                self.log_message("正在初始化扫描器...")
                from ...core.scanner.advanced_chess_scanner import AdvancedChessScanner
                self.scanner = AdvancedChessScanner()
                self.log_message("扫描器初始化成功")
                
                # 初始化AI助手
                self.log_message("正在初始化AI助手...")
                from ...core.ai_engine.chess_ai_assistant import ChessAIAssistant
                self.ai_assistant = ChessAIAssistant(player_color='red')
                self.log_message("AI助手初始化成功")
                
                # 更新UI状态
                self.root.after(0, lambda: self.update_ai_status(True))
                
            except Exception as e:
                error_msg = f"系统初始化失败: {e}"
                self.log_message(error_msg)
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                self.root.after(0, lambda: self.update_ai_status(False))
        
        # 在后台线程中运行初始化，避免阻塞GUI
        import threading
        init_thread = threading.Thread(target=init_thread, daemon=True)
        init_thread.start()
        
    def update_ai_status(self, initialized):
        """更新AI状态显示"""
        if hasattr(self, 'ai_status_label'):
            if initialized:
                status = "已初始化"
                color = self.colors['green_jade']
            else:
                status = "未初始化"
                color = self.colors['red_chinese']
            self.ai_status_label.config(text=f"AI助手: {status}", fg=color)
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def calibrate_board(self):
        """校准棋盘"""
        if not self.scanner:
            messagebox.showerror("错误", "扫描器未初始化")
            return
        
        self.log_message("开始棋盘校准...")
        
        # 在新线程中执行校准
        def calibrate_thread():
            try:
                self.scanner.calibrate_board()
                self.log_message("棋盘校准完成")
            except Exception as e:
                self.log_message(f"校准失败: {e}")
        
        threading.Thread(target=calibrate_thread, daemon=True).start()
    
    def single_scan(self):
        """单次扫描"""
        if not self.scanner:
            messagebox.showerror("错误", "扫描器未初始化")
            return
        
        self.log_message("开始单次扫描...")
        
        def scan_thread():
            try:
                # 设置扫描区域
                if self.current_scan_region:
                    self.scanner.set_scan_region(self.current_scan_region)
                else:
                    self.scanner.set_scan_region(None)  # 全屏扫描
                
                board = self.scanner.scan_board()
                self.board_state = board
                
                # 更新显示
                self.root.after(0, self.update_board_display)
                self.root.after(0, lambda: self.log_message("扫描完成"))
                
                # 检查胜负
                winner = self.scanner.check_win_condition()
                if winner:
                    winner_text = "红方胜利！" if winner == 'red' else "黑方胜利！"
                    self.root.after(0, lambda: messagebox.showinfo("胜负判定", f"恭喜！{winner_text}"))
                    
            except Exception as e:
                error_msg = f"扫描失败: {e}"
                self.root.after(0, lambda msg=error_msg: self.log_message(msg))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def start_monitoring(self):
        """开始监控"""
        if not self.scanner:
            messagebox.showerror("错误", "扫描器未初始化")
            return
        
        if self.scanning:
            messagebox.showwarning("警告", "监控已在运行中")
            return
        
        self.scanning = True
        self.log_message("开始持续监控...")
        
        def monitor_thread():
            try:
                while self.scanning:
                    board = self.scanner.scan_board()
                    self.board_state = board
                    
                    # 更新显示
                    self.root.after(0, self.update_board_display)
                    
                    # 检查胜负
                    winner = self.scanner.check_win_condition()
                    if winner:
                        winner_text = "红方胜利！" if winner == 'red' else "黑方胜利！"
                        self.root.after(0, lambda: messagebox.showinfo("胜负判定", f"恭喜！{winner_text}"))
                        self.root.after(0, self.stop_monitoring)
                        break
                    
                    time.sleep(2)  # 扫描间隔
                    
            except Exception as e:
                error_msg = f"监控失败: {e}"
                self.root.after(0, lambda msg=error_msg: self.log_message(msg))
                self.root.after(0, self.stop_monitoring)
        
        self.scan_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.scan_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.scanning = False
        self.log_message("监控已停止")
    
    def start_ai_monitoring(self):
        """启动AI助手监控"""
        if not self.ai_assistant:
            messagebox.showerror("错误", "AI助手未初始化")
            return
        
        if self.scanning:
            messagebox.showwarning("警告", "AI监控已在运行中")
            return
        
        self.scanning = True
        self.log_message("启动AI智能监控...")
        
        def ai_monitor_thread():
            try:
                while self.scanning:
                    # 设置扫描区域
                    if self.current_scan_region:
                        self.scanner.set_scan_region(self.current_scan_region)
                    else:
                        self.scanner.set_scan_region(None)  # 全屏扫描
                    
                    # 扫描棋盘
                    board = self.scanner.scan_board()
                    self.board_state = board
                    
                    # AI分析
                    analysis = self.ai_assistant.update_board_state(board)
                    
                    # 更新GUI显示
                    self.root.after(0, self.update_board_display)
                    self.root.after(0, lambda: self.update_ai_display(analysis))
                    
                    time.sleep(2)  # 扫描间隔
                    
            except Exception as e:
                error_msg = f"AI监控失败: {e}"
                self.root.after(0, lambda msg=error_msg: self.log_message(msg))
                self.root.after(0, self.stop_ai_monitoring)
        
        self.scan_thread = threading.Thread(target=ai_monitor_thread, daemon=True)
        self.scan_thread.start()
    
    def stop_ai_monitoring(self):
        """停止AI助手监控"""
        self.scanning = False
        self.log_message("AI监控已停止")
    
    def get_ai_recommendation(self):
        """获取AI推荐"""
        if not self.ai_assistant:
            messagebox.showerror("错误", "AI助手未初始化")
            return
        
        if not self.board_state or not any(any(row) for row in self.board_state):
            messagebox.showwarning("警告", "请先扫描棋盘")
            return
        
        self.log_message("获取AI推荐中...")
        
        def get_recommendation_thread():
            try:
                # 设置扫描区域
                if self.current_scan_region:
                    self.scanner.set_scan_region(self.current_scan_region)
                else:
                    self.scanner.set_scan_region(None)  # 全屏扫描
                
                # 重新扫描获取最新状态
                board = self.scanner.scan_board()
                self.board_state = board
                
                analysis = self.ai_assistant.update_board_state(self.board_state)
                self.root.after(0, lambda: self.update_ai_display(analysis))
                self.root.after(0, lambda: self.log_message("AI推荐获取完成"))
            except Exception as e:
                error_msg = f"获取AI推荐失败: {e}"
                self.root.after(0, lambda msg=error_msg: self.log_message(msg))
        
        threading.Thread(target=get_recommendation_thread, daemon=True).start()
    
    def update_ai_display(self, analysis):
        """更新现代化AI显示界面 - 重新设计版本"""
        try:
            # 保存分析结果用于其他功能
            self.last_ai_analysis = analysis
            
            # 更新胜率显示
            win_rate = analysis.current_evaluation['win_probability'] * 100
            confidence = "高" if hasattr(analysis, 'confidence') and analysis.confidence > 0.8 else "中" if hasattr(analysis, 'confidence') and analysis.confidence > 0.6 else "低"
            
            # 更新胜率颜色和状态 - 增强版
            if win_rate >= 70:
                status = "优势明显"
                advantage = "红方大优"
            elif win_rate >= 55:
                status = "略有优势"
                advantage = "红方小优"
            elif win_rate >= 45:
                status = "势均力敌"
                advantage = "双方均势"
            elif win_rate >= 30:
                status = "处于劣势"
                advantage = "黑方小优"
            else:
                status = "劣势明显"
                advantage = "黑方大优"
            
            # 使用统一的胜率更新方法
            self.update_win_rate_display(win_rate, status, advantage, confidence)
            
            # 更新推荐走法文本区域
            if hasattr(self, 'recommendation_text') and analysis.recommendations:
                self.recommendation_text.delete(1.0, tk.END)
                
                rec_text = "🚀 AI 推荐走法分析\n\n"
                rec_text += f"📊 当前胜率: {win_rate:.1f}% ({status})\n"
                rec_text += f"🎯 分析时间: {time.strftime('%H:%M:%S')}\n\n"
                
                for i, rec in enumerate(analysis.recommendations[:5], 1):
                    move_str = self.ai_assistant.move_detector.format_move(rec.move) if hasattr(self.ai_assistant, 'move_detector') else "走法"
                    confidence_pct = rec.confidence * 100 if hasattr(rec, 'confidence') else 75
                    
                    level_text = "💎强烈推荐" if confidence_pct >= 80 else "⭐推荐" if confidence_pct >= 60 else "💡备选"
                    
                    rec_text += f"{i}. {level_text}\n"
                    rec_text += f"   走法: {move_str}\n"
                    rec_text += f"   置信度: {confidence_pct:.1f}%\n"
                    
                    if hasattr(rec, 'reasoning'):
                        rec_text += f"   理由: {rec.reasoning}\n"
                    rec_text += "\n"
                
                self.recommendation_text.insert(tk.END, rec_text)
            
            # 更新分析文本区域
            if hasattr(self, 'analysis_text'):
                self.analysis_text.delete(1.0, tk.END)
                
                analysis_text = "🔍 深度局面分析\n\n"
                analysis_text += f"📈 分析结果 ({time.strftime('%H:%M:%S')})\n"
                analysis_text += "=" * 40 + "\n\n"
                
                # 局面评估
                eval_data = analysis.current_evaluation
                analysis_text += f"🎯 当前胜率: {win_rate:.1f}%\n"
                analysis_text += f"⚖️ 局面评分: {eval_data.get('score', 0):.2f}\n"
                analysis_text += f"🏁 优势方: {advantage}\n"
                analysis_text += f"📊 置信度: {confidence}\n\n"
                
                # 威胁分析
                if hasattr(analysis, 'threats') and analysis.threats:
                    analysis_text += "⚠️ 威胁分析:\n"
                    for threat in analysis.threats[:3]:
                        analysis_text += f"  • {threat}\n"
                    analysis_text += "\n"
                
                # 机会分析
                if hasattr(analysis, 'opportunities') and analysis.opportunities:
                    analysis_text += "🌟 机会分析:\n"
                    for opportunity in analysis.opportunities[:3]:
                        analysis_text += f"  • {opportunity}\n"
                    analysis_text += "\n"
                
                analysis_text += "📝 分析完成。使用控制面板按钮进行更多分析。"
                
                self.analysis_text.insert(tk.END, analysis_text)
            
            # 在状态栏显示推荐走法信息
            if analysis.recommendations:
                rec = analysis.recommendations[0]  # 显示最佳推荐
                move_str = self.ai_assistant.move_detector.format_move(rec.move) if hasattr(self.ai_assistant, 'move_detector') else "走法"
                confidence_pct = rec.confidence * 100 if hasattr(rec, 'confidence') else 75
                
                level_text = "强烈推荐" if confidence_pct >= 80 else "推荐" if confidence_pct >= 60 else "备选"
                
                recommendation_msg = f"🎯 AI推荐: {move_str} ({level_text}, 置信度: {confidence_pct:.1f}%)"
                if hasattr(rec, 'reasoning'):
                    recommendation_msg += f" - {rec.reasoning}"
                
                self.log_message(recommendation_msg)
                
        except Exception as e:
            self.log_message(f"更新AI显示失败: {e}")
            import traceback
            traceback.print_exc()
    
    def highlight_recommendations(self):
        """高亮显示AI推荐走法"""
        if not self.last_ai_analysis or not self.last_ai_analysis.recommendations:
            self.log_message("暂无AI推荐可以高亮显示")
            return
        
        # 清除之前的高亮
        self.highlighted_moves.clear()
        
        # 添加前3个推荐走法到高亮列表
        for i, rec in enumerate(self.last_ai_analysis.recommendations[:3]):
            if hasattr(rec, 'move') and rec.move:
                self.highlighted_moves.append(rec.move)
        
        # 更新棋盘显示
        self.update_modern_board_display()
        self.log_message(f"已高亮显示 {len(self.highlighted_moves)} 个推荐走法")
    
    def clear_highlights(self):
        """清除所有高亮标记"""
        self.highlighted_moves.clear()
        self.threat_positions.clear()
        self.opportunity_positions.clear()
        self.update_modern_board_display()
        self.log_message("已清除所有高亮标记")
    
    def auto_execute_move(self):
        """自动执行最佳推荐走法（仅演示，实际应用需要谨慎）"""
        if not self.last_ai_analysis or not self.last_ai_analysis.recommendations:
            messagebox.showwarning("警告", "暂无推荐走法可执行")
            return
        
        best_move = self.last_ai_analysis.recommendations[0]
        move_text = self.ai_assistant.move_detector.format_move(best_move.move) if hasattr(best_move, 'move') else "未知走法"
        
        result = messagebox.askyesno("确认执行", f"是否执行推荐走法：{move_text}？\n\n注意：这仅为演示功能，实际对弈请手动操作。")
        
        if result:
            self.log_message(f"演示执行推荐走法：{move_text}")
            self.log_message("注意：这仅为演示功能，实际棋盘状态未改变")
    
    def show_threats(self):
        """显示威胁分析并标记在棋盘上"""
        if not self.last_ai_analysis or not self.last_ai_analysis.threats:
            self.log_message("暂无威胁分析数据")
            return
        
        # 示例威胁位置（实际应从AI分析中获取）
        self.threat_positions = [(1, 4), (7, 4)]  # 示例威胁位置
        self.update_modern_board_display()
        self.log_message(f"已标记 {len(self.threat_positions)} 个威胁位置")
    
    def show_opportunities(self):
        """显示机会分析并标记在棋盘上"""
        if not self.last_ai_analysis or not self.last_ai_analysis.opportunities:
            self.log_message("暂无机会分析数据")
            return
        
        # 示例机会位置（实际应从AI分析中获取）
        self.opportunity_positions = [(2, 1), (6, 7)]  # 示例机会位置
        self.update_modern_board_display()
        self.log_message(f"已标记 {len(self.opportunity_positions)} 个机会位置")
    
    def generate_detailed_report(self):
        """生成详细分析报告"""
        if not self.last_ai_analysis:
            self.log_message("暂无分析数据，无法生成报告")
            return
        
        # 生成详细报告
        report = "🔍 详细分析报告\n"
        report += "=" * 40 + "\n\n"
        report += f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if hasattr(self.last_ai_analysis, 'current_evaluation'):
            eval_data = self.last_ai_analysis.current_evaluation
            report += f"当前胜率: {eval_data.get('win_probability', 0) * 100:.1f}%\n"
            report += f"局面评估: {eval_data.get('score', 0):.2f}\n\n"
        
        if self.last_ai_analysis.recommendations:
            report += "推荐走法详情:\n"
            for i, rec in enumerate(self.last_ai_analysis.recommendations[:5], 1):
                move_str = self.ai_assistant.move_detector.format_move(rec.move) if hasattr(rec, 'move') else "未知"
                report += f"{i}. {move_str} (置信度: {rec.confidence*100:.1f}%)\n"
                if hasattr(rec, 'reasoning'):
                    report += f"   理由: {rec.reasoning}\n"
            report += "\n"
        
        report += "分析完成。\n"
        
        # 显示报告
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, report)
        self.log_message("已生成详细分析报告")
    
    def create_template(self):
        """创建模板"""
        if not self.scanner:
            messagebox.showerror("错误", "扫描器未初始化")
            return
        
        # 创建模板对话框
        template_dialog = tk.Toplevel(self.root)
        template_dialog.title("创建棋子模板")
        template_dialog.geometry("300x150")
        template_dialog.transient(self.root)
        template_dialog.grab_set()
        
        # 居中显示
        template_dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # 输入框
        ttk.Label(template_dialog, text="请输入棋子名称:").pack(pady=10)
        entry = ttk.Entry(template_dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def create_template_action():
            piece_name = entry.get().strip()
            if not piece_name:
                messagebox.showwarning("警告", "请输入棋子名称")
                return
            
            template_dialog.destroy()
            self.log_message(f"开始创建模板: {piece_name}")
            
            def create_thread():
                try:
                    self.scanner.create_template_from_screenshot(piece_name)
                    self.log_message(f"模板创建完成: {piece_name}")
                except Exception as e:
                    self.log_message(f"模板创建失败: {e}")
            
            threading.Thread(target=create_thread, daemon=True).start()
        
        # 按钮
        button_frame = ttk.Frame(template_dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="确定", command=create_template_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=template_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 回车键绑定
        entry.bind('<Return>', lambda e: create_template_action())
    
    def select_scan_region(self):
        """选择扫描区域"""
        self.log_message("请在屏幕上框选扫描区域...")
        
        def region_selection_thread():
            try:
                def on_region_selected(region):
                    if region:
                        self.current_scan_region = region
                        x, y, w, h = region
                        region_info = f"{x}, {y}, {w}x{h}"
                        self.region_name_var.set(f"自定义区域")
                        
                        # 使用线程安全的方式更新UI
                        self.root.after(0, lambda: self.log_message(f"扫描区域已设置: {region_info}"))
                
                # 设置回调函数
                self.region_selector.callback = on_region_selected
                
                # 启动区域选择（这会阻塞直到选择完成）
                try:
                    selected_region = self.region_selector.select_region()
                    
                    if selected_region:
                        x, y, w, h = selected_region
                        self.root.after(0, lambda: self.log_message(f"区域选择完成: {x}, {y}, {w}x{h}"))
                        
                        # 询问是否保存区域
                        self.root.after(0, lambda: self.prompt_save_region(selected_region))
                    else:
                        self.root.after(0, lambda: self.log_message("区域选择已取消"))
                        
                except Exception as e:
                    error_msg = f"区域选择过程出错: {e}"
                    self.root.after(0, lambda msg=error_msg: self.log_message(msg))
                    # 重置区域选择器状态
                    try:
                        self.region_selector._cleanup_resources()
                    except:
                        pass
                    
            except Exception as e:
                error_msg = f"区域选择线程失败: {e}"
                self.root.after(0, lambda msg=error_msg: self.log_message(msg))
                import traceback
                traceback.print_exc()
        
        try:
            threading.Thread(target=region_selection_thread, daemon=True).start()
        except Exception as e:
            self.log_message(f"启动区域选择线程失败: {e}")
    
    def prompt_save_region(self, region):
        """提示保存区域"""
        result = messagebox.askyesno("保存区域", "是否保存这个扫描区域以便将来使用？")
        if result:
            self.save_region_dialog(region)
    
    def save_region_dialog(self, region):
        """保存区域对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("保存扫描区域")
        dialog.geometry("300x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # 输入框
        ttk.Label(dialog, text="请输入区域名称:").pack(pady=10)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def save_action():
            region_name = entry.get().strip()
            if not region_name:
                messagebox.showwarning("警告", "请输入区域名称")
                return
            
            try:
                self.region_selector.save_region(region_name, region)
                self.region_name_var.set(region_name)
                self.log_message(f"区域 '{region_name}' 已保存")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="保存", command=save_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 回车键绑定
        entry.bind('<Return>', lambda e: save_action())
    
    def manage_regions(self):
        """管理已保存的区域"""
        regions = self.region_selector.get_saved_regions()
        
        if not regions:
            messagebox.showinfo("信息", "尚未保存任何扫描区域")
            return
        
        # 创建区域管理对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("管理扫描区域")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # 区域列表
        ttk.Label(dialog, text="已保存的扫描区域:").pack(pady=10)
        
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        listbox = tk.Listbox(listbox_frame)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充区域列表
        for region in regions:
            listbox.insert(tk.END, region)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def load_region():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请选择一个区域")
                return
            
            region_name = listbox.get(selection[0])
            region = self.region_selector.load_region(region_name)
            
            if region:
                self.current_scan_region = region
                self.region_name_var.set(region_name)
                self.log_message(f"已加载区域: {region_name}")
                dialog.destroy()
            else:
                messagebox.showerror("错误", "加载区域失败")
        
        def delete_region():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请选择一个区域")
                return
            
            region_name = listbox.get(selection[0])
            result = messagebox.askyesno("确认删除", f"确定要删除区域 '{region_name}' 吗？")
            
            if result:
                try:
                    # 这里需要实现删除功能
                    import json
                    config_file = "scan_regions.json"
                    
                    if os.path.exists(config_file):
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        if region_name in config:
                            del config[region_name]
                            
                            with open(config_file, 'w', encoding='utf-8') as f:
                                json.dump(config, f, indent=2, ensure_ascii=False)
                            
                            listbox.delete(selection[0])
                            self.log_message(f"区域 '{region_name}' 已删除")
                            
                            # 如果删除的是当前使用的区域，重置为全屏
                            if self.region_name_var.get() == region_name:
                                self.reset_to_fullscreen()
                        
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {e}")
        
        def preview_region():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请选择一个区域")
                return
            
            region_name = listbox.get(selection[0])
            region = self.region_selector.load_region(region_name)
            
            if region:
                preview_image = self.region_selector.preview_region(region)
                if preview_image is not None:
                    cv2.imshow(f"区域预览 - {region_name}", preview_image)
                    cv2.waitKey(3000)  # 显示3秒
                    cv2.destroyAllWindows()
            else:
                messagebox.showerror("错误", "预览失败")
        
        def reset_fullscreen():
            self.reset_to_fullscreen()
            dialog.destroy()
        
        # 按钮
        ttk.Button(button_frame, text="加载区域", command=load_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="预览区域", command=preview_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除区域", command=delete_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置全屏", command=reset_fullscreen).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def reset_to_fullscreen(self):
        """重置为全屏扫描"""
        self.current_scan_region = None
        self.region_name_var.set("全屏")
        self.log_message("已重置为全屏扫描模式")
    
    def update_recommendation_display(self):
        """更新推荐走法显示区域"""
        if hasattr(self, 'recommendation_text'):
            self.recommendation_text.delete(1.0, tk.END)
            
            initial_text = """🚀 AI 推荐走法分析

📋 功能说明:
  • 高亮显示 - 在棋盘上标记推荐走法
  • 清除高亮 - 移除所有棋盘标记
  • 自动走法 - 演示功能（仅供参考）

🎯 使用方法:
  1. 点击"获取推荐"按钮进行AI分析
  2. 系统将显示最佳走法建议
  3. 可通过高亮功能在棋盘上查看
  4. 每个推荐包含置信度和理由分析

💡 当前状态: 等待AI分析...

提示：启动AI助手并扫描棋盘后，此区域将显示：
• 最佳推荐走法（前3个）
• 每步走法的置信度评分
• AI分析的具体理由
• 预期收益评估
"""
            self.recommendation_text.insert(tk.END, initial_text)
    
    def update_analysis_display(self):
        """更新深度局面分析显示区域"""
        if hasattr(self, 'analysis_text'):
            self.analysis_text.delete(1.0, tk.END)
            
            initial_text = """🔍 深度局面分析

📊 分析功能:
  • 威胁分析 - 识别对方的攻击威胁
  • 机会分析 - 发现我方的进攻机会
  • 详细报告 - 生成完整的局面评估

🎯 分析维度:
  • 材料平衡 - 双方棋子价值对比
  • 位置优势 - 棋子的位置价值
  • 王安全性 - 将帅的安全程度
  • 控制力 - 对关键位置的控制

📈 评估指标:
  • 胜率百分比 - 基于当前局面的获胜概率
  • 优势评估 - 量化的局面优势值
  • 威胁等级 - 面临威胁的严重程度
  • 机会评分 - 进攻机会的价值评估

🔄 实时更新:
启动AI监控后，本区域将实时显示：
• 当前局面的综合评估
• 双方优劣势分析
• 关键威胁和机会标记
• 战术建议和策略指导

💡 当前状态: 等待棋盘数据...
"""
            self.analysis_text.insert(tk.END, initial_text)
    
    def update_win_rate_display(self, win_rate=None, status=None, advantage=None, confidence=None):
        """更新胜率显示模块"""
        if win_rate is None:
            win_rate = 50.0  # 默认50%
        if status is None:
            status = "等待分析..."
        if advantage is None:
            advantage = "势均力敌"
        if confidence is None:
            confidence = "分析中..."
        
        # 更新胜率数字
        if hasattr(self, 'win_rate_label'):
            self.win_rate_label.config(text=f"{win_rate:.1f}%")
            
            # 根据胜率设置颜色
            if win_rate >= 70:
                color = self.colors['win_rate_high']
            elif win_rate >= 55:
                color = self.colors['success']
            elif win_rate >= 45:
                color = self.colors['win_rate_mid']
            elif win_rate >= 30:
                color = self.colors['warning']
            else:
                color = self.colors['win_rate_low']
            
            self.win_rate_label.config(fg=color)
        
        # 更新状态文本
        if hasattr(self, 'win_rate_status'):
            self.win_rate_status.config(text=status)
        
        # 更新进度条
        if hasattr(self, 'win_rate_progress'):
            self.win_rate_progress['value'] = win_rate
        
        # 更新详细信息
        if hasattr(self, 'advantage_label'):
            self.advantage_label.config(text=f"优势: {advantage}")
        
        if hasattr(self, 'confidence_label'):
            self.confidence_label.config(text=f"置信度: {confidence}")
    
    def init_all_display_modules(self):
        """初始化所有显示模块的默认内容"""
        # 初始化胜率显示
        self.update_win_rate_display()
        
        # 初始化推荐走法显示
        if hasattr(self, 'update_recommendation_display'):
            self.update_recommendation_display()
        
        # 初始化分析显示
        if hasattr(self, 'update_analysis_display'):
            self.update_analysis_display()
        
        self.log_message("所有显示模块已初始化")
    
    def refresh_all_panels(self):
        """刷新所有面板显示"""
        try:
            # 刷新棋盘显示
            self.update_modern_board_display()
            
            # 刷新胜率显示
            self.update_win_rate_display()
            
            # 刷新AI分析面板
            if self.last_ai_analysis:
                self.update_ai_display(self.last_ai_analysis)
            
            self.log_message("所有面板已刷新")
        except Exception as e:
            self.log_message(f"刷新面板时出错: {e}")
    
    def toggle_advanced_mode(self):
        """切换高级模式显示（显示更多AI分析细节）"""
        if not hasattr(self, 'advanced_mode'):
            self.advanced_mode = False
        
        self.advanced_mode = not self.advanced_mode
        
        if self.advanced_mode:
            self.log_message("已开启高级分析模式 - 显示详细AI数据")
            # 可以在这里添加更多高级显示元素
        else:
            self.log_message("已关闭高级分析模式 - 简化显示")
        
        # 刷新显示
        self.refresh_all_panels()

def main():
    """主函数"""
    root = tk.Tk()
    app = ChessScannerGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.scanning:
            app.stop_ai_monitoring()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main()
