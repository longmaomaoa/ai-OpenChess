#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - Configuration Module
中国象棋智能对弈助手的全局配置设置
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
TEMPLATES_DIR = ASSETS_DIR / "chess_templates"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

def find_tesseract_path() -> Optional[str]:
    """智能查找Tesseract可执行文件路径"""
    # 常见的Tesseract安装路径
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract'
    ]
    
    # 首先检查环境变量
    env_path = os.environ.get('TESSERACT_PATH')
    if env_path and Path(env_path).exists():
        return env_path
    
    # 尝试通过which/where命令查找
    tesseract_cmd = shutil.which('tesseract')
    if tesseract_cmd:
        return tesseract_cmd
    
    # 检查常见路径
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None

# Tesseract路径配置（自动检测）
TESSERACT_PATH = find_tesseract_path()

# 扫描配置
SCAN_INTERVAL = 2.0  # 扫描间隔（秒）
CONFIDENCE_THRESHOLD = 0.7  # 模板匹配置信度阈值
OCR_CONFIDENCE_THRESHOLD = 60  # OCR识别置信度阈值

# 棋盘配置
BOARD_WIDTH = 9  # 棋盘宽度（列数）
BOARD_HEIGHT = 10  # 棋盘高度（行数）
GRID_PADDING = 10  # 网格边距（像素）

# AI助手配置
PLAYER_COLOR = 'red'  # 玩家颜色（red=红方/下方，black=黑方/上方）
AI_SEARCH_DEPTH = 3   # AI搜索深度
MAX_RECOMMENDATIONS = 5  # 最大推荐走法数
AI_THINKING_TIME = 1.0  # AI思考时间（秒）

# 图像处理配置
PIECE_SIZE_THRESHOLD = (15, 15)  # 最小棋子尺寸
MAX_PIECE_SIZE = (80, 80)  # 最大棋子尺寸
EDGE_DETECTION_THRESHOLD = (50, 150)  # Canny边缘检测阈值

# 颜色配置（HSV格式）
RED_COLOR_RANGE = {
    'lower': [0, 100, 100],
    'upper': [10, 255, 255]
}

RED_COLOR_RANGE_ALT = {  # 备用红色范围（处理色调环绕）
    'lower': [170, 100, 100],
    'upper': [180, 255, 255]
}

BLACK_COLOR_RANGE = {
    'lower': [0, 0, 0],
    'upper': [180, 255, 30]
}

# GUI配置
DEFAULT_WINDOW_SIZE = (1400, 900)
GUI_UPDATE_INTERVAL = 100  # GUI更新间隔（毫秒）

# 中国风主题色彩
GUI_COLORS = {
    'bg_primary': '#f5f5dc',      # 米色背景
    'bg_secondary': '#8b4513',     # 深棕色
    'wood_light': '#deb887',       # 浅木色
    'wood_dark': '#8b7355',        # 深木色
    'gold': '#ffd700',             # 金色
    'red_chinese': '#dc143c',      # 中国红
    'black_ink': '#2f4f4f',        # 墨色
    'green_jade': '#00a86b',       # 翡翠绿
    'text_primary': '#2f4f4f',     # 主文字色
    'text_secondary': '#8b4513'    # 次文字色
}

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / "chess_assistant.log"

# 安全配置
ALLOWED_FILE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.json', '.log']
MAX_FILE_SIZE_MB = 50  # 最大文件大小限制
MAX_REGION_SIZE = (3840, 2160)  # 最大区域尺寸（4K分辨率）

def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否安全"""
    try:
        path = Path(file_path).resolve()
        
        # 检查是否在项目目录内
        if not str(path).startswith(str(PROJECT_ROOT)):
            return False
        
        # 检查文件扩展名
        if path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
            return False
        
        # 检查文件大小
        if path.exists() and path.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return False
        
        return True
    except (ValueError, OSError):
        return False

def load_user_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """加载用户配置文件"""
    if config_file is None:
        config_file = CONFIG_DIR / "user_config.json"
    
    try:
        config_path = Path(config_file)
        if not validate_file_path(str(config_path)):
            raise ValueError("配置文件路径不安全")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.warning(f"加载用户配置失败: {e}")
    
    return {}

def save_user_config(config: Dict[str, Any], config_file: Optional[str] = None):
    """保存用户配置文件"""
    if config_file is None:
        config_file = CONFIG_DIR / "user_config.json"
    
    try:
        config_path = Path(config_file)
        if not validate_file_path(str(config_path)):
            raise ValueError("配置文件路径不安全")
        
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"保存用户配置失败: {e}")
        raise

def setup_logging(level: str = LOG_LEVEL, debug: bool = False):
    """设置日志配置"""
    # 确保日志目录存在
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    if debug:
        log_level = logging.DEBUG
    
    # 配置日志格式
    formatter = logging.Formatter(LOG_FORMAT)
    
    # 文件处理器
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler]
    )

# 创建必要的目录
for directory in [ASSETS_DIR, TEMPLATES_DIR, CONFIG_DIR, LOGS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"警告: 无法创建目录 {directory}: {e}")