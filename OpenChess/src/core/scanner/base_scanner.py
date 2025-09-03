#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础扫描器抽象类 - Base Scanner Abstract Class
为所有象棋扫描器提供统一接口和共同功能
"""

import abc
from typing import Dict, List, Tuple, Optional
import numpy as np


class BaseChessScanner(abc.ABC):
    """象棋扫描器抽象基类
    
    定义所有扫描器必须实现的接口和共同的属性
    """
    
    def __init__(self):
        """初始化基础扫描器"""
        self.board_size = (9, 10)  # 中国象棋棋盘标准尺寸
        self.custom_scan_region = None
        self.board_state = {}
        self.previous_state = {}
        
        # 标准棋子定义
        self.pieces = {
            'red': {
                '帅': 'red_king',
                '仕': 'red_advisor', 
                '相': 'red_elephant',
                '马': 'red_horse',
                '车': 'red_chariot',
                '炮': 'red_cannon',
                '兵': 'red_pawn'
            },
            'black': {
                '将': 'black_king',
                '士': 'black_advisor',
                '象': 'black_elephant', 
                '马': 'black_horse',
                '车': 'black_chariot',
                '炮': 'black_cannon',
                '卒': 'black_pawn'
            }
        }
    
    @abc.abstractmethod
    def scan_board(self) -> Dict:
        """扫描棋盘并返回当前状态
        
        Returns:
            Dict: 棋盘状态字典
        """
        pass
    
    @abc.abstractmethod
    def detect_board_area(self) -> Optional[Tuple[int, int, int, int]]:
        """检测棋盘区域
        
        Returns:
            Optional[Tuple[int, int, int, int]]: (x, y, width, height) 或 None
        """
        pass
    
    @abc.abstractmethod
    def identify_piece(self, piece_image: np.ndarray) -> Tuple[str, float]:
        """识别棋子
        
        Args:
            piece_image: 棋子图像
            
        Returns:
            Tuple[str, float]: (棋子类型, 置信度)
        """
        pass
    
    def set_scan_region(self, region: Tuple[int, int, int, int]):
        """设置自定义扫描区域"""
        self.custom_scan_region = region
    
    def get_board_state(self) -> Dict:
        """获取当前棋盘状态"""
        return self.board_state.copy()
    
    def has_state_changed(self) -> bool:
        """检查棋盘状态是否发生变化"""
        return self.board_state != self.previous_state
    
    def update_previous_state(self):
        """更新前一状态为当前状态"""
        self.previous_state = self.board_state.copy()