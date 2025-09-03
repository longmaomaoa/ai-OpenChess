#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量定义 - Constants Module
定义项目中使用的各种常量
"""

# 棋子类型常量
PIECE_TYPES = {
    'KING': 'king',
    'ADVISOR': 'advisor',
    'ELEPHANT': 'elephant', 
    'HORSE': 'horse',
    'CHARIOT': 'chariot',
    'CANNON': 'cannon',
    'PAWN': 'pawn'
}

# 颜色常量
COLORS = {
    'RED': 'red',
    'BLACK': 'black'
}

# 棋子中文名称映射
PIECE_NAMES_CN = {
    'red': {
        'king': '帅',
        'advisor': '仕', 
        'elephant': '相',
        'horse': '马',
        'chariot': '车',
        'cannon': '炮',
        'pawn': '兵'
    },
    'black': {
        'king': '将',
        'advisor': '士',
        'elephant': '象', 
        'horse': '马',
        'chariot': '车',
        'cannon': '炮',
        'pawn': '卒'
    }
}

# 棋子英文名称映射
PIECE_NAMES_EN = {
    'red': {
        'king': 'Red King',
        'advisor': 'Red Advisor', 
        'elephant': 'Red Elephant',
        'horse': 'Red Horse',
        'chariot': 'Red Chariot',
        'cannon': 'Red Cannon',
        'pawn': 'Red Pawn'
    },
    'black': {
        'king': 'Black General',
        'advisor': 'Black Advisor',
        'elephant': 'Black Elephant', 
        'horse': 'Black Horse',
        'chariot': 'Black Chariot',
        'cannon': 'Black Cannon',
        'pawn': 'Black Soldier'
    }
}

# 棋子分值
PIECE_VALUES = {
    'king': 10000,     # 帅/将
    'advisor': 200,    # 仕/士
    'elephant': 250,   # 相/象
    'horse': 400,      # 马
    'chariot': 900,    # 车
    'cannon': 450,     # 炮
    'pawn': 100        # 兵/卒
}

# 游戏状态常量
GAME_STATES = {
    'ONGOING': 'ongoing',
    'RED_WIN': 'red_win',
    'BLACK_WIN': 'black_win',
    'DRAW': 'draw',
    'UNKNOWN': 'unknown'
}

# 位置评估权重
POSITION_WEIGHTS = {
    'material': 0.4,      # 物质分值权重
    'position': 0.3,      # 位置分值权重
    'mobility': 0.2,      # 机动性权重
    'king_safety': 0.1    # 王安全权重
}

# 界面消息类型
MESSAGE_TYPES = {
    'INFO': 'info',
    'WARNING': 'warning', 
    'ERROR': 'error',
    'SUCCESS': 'success'
}

# 文件扩展名
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
CONFIG_FILE_EXTENSION = '.json'
LOG_FILE_EXTENSION = '.log'