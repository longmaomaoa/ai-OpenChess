#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局面评估器模块
用于评估中国象棋局面的优劣和计算胜率
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import math
from .move_detector import Move

class PositionEvaluator:
    """局面评估器类
    
    负责评估棋盘局面的价值，计算胜率和提供走法建议
    """
    
    def __init__(self):
        """初始化局面评估器"""
        
        # 棋子基础分值（厘子为单位）
        self.piece_values = {
            'red_king': 10000,      # 帅：无价
            'red_advisor': 200,     # 仕：2子
            'red_elephant': 200,    # 相：2子  
            'red_horse': 450,       # 马：4.5子
            'red_chariot': 900,     # 车：9子
            'red_cannon': 450,      # 炮：4.5子
            'red_pawn': 100,        # 兵：1子
            'black_king': 10000,    # 将：无价
            'black_advisor': 200,   # 士：2子
            'black_elephant': 200,  # 象：2子
            'black_horse': 450,     # 马：4.5子
            'black_chariot': 900,   # 车：9子
            'black_cannon': 450,    # 炮：4.5子
            'black_pawn': 100       # 卒：1子
        }
        
        # 棋子位置价值表（中心控制、灵活性等因素）
        self.position_values = self._init_position_values()
        
        # 评估权重
        self.weights = {
            'material': 1.0,        # 子力价值权重
            'position': 0.3,        # 位置价值权重
            'mobility': 0.2,        # 机动性权重
            'king_safety': 0.4,     # 王的安全性权重
            'center_control': 0.15, # 中心控制权重
            'development': 0.1,     # 子力发展权重
            'attack': 0.25,         # 攻击性权重
            'defense': 0.2          # 防守性权重
        }
        
    def _init_position_values(self) -> Dict[str, np.ndarray]:
        """初始化位置价值表
        
        Returns:
            各种棋子的位置价值表
        """
        position_values = {}
        
        # 兵/卒的位置价值（过河后价值增加）
        pawn_red = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],  # 第10行（对方底线）
            [70, 70, 70, 70, 70, 70, 70, 70, 70],  # 第9行
            [50, 50, 50, 50, 50, 50, 50, 50, 50],  # 第8行
            [40, 40, 40, 40, 40, 40, 40, 40, 40],  # 第7行
            [30, 30, 30, 30, 30, 30, 30, 30, 30],  # 第6行
            [20, 20, 20, 20, 20, 20, 20, 20, 20],  # 第5行（河界）
            [10, 10, 10, 10, 10, 10, 10, 10, 10],  # 第4行
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],  # 第3行
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],  # 第2行
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0]   # 第1行（己方底线）
        ])
        
        # 黑卒位置价值（翻转红兵表）
        pawn_black = np.flip(pawn_red, axis=0)
        
        # 马的位置价值（中心较高）
        horse_value = np.array([
            [-20, -10, -10, -10, -10, -10, -10, -10, -20],
            [-10,   0,   0,   0,   0,   0,   0,   0, -10],
            [-10,   0,   5,  10,  10,  10,   5,   0, -10],
            [-10,   0,  10,  20,  20,  20,  10,   0, -10],
            [-10,   0,  10,  20,  30,  20,  10,   0, -10],
            [-10,   0,  10,  20,  30,  20,  10,   0, -10],
            [-10,   0,  10,  20,  20,  20,  10,   0, -10],
            [-10,   0,   5,  10,  10,  10,   5,   0, -10],
            [-10,   0,   0,   0,   0,   0,   0,   0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -10, -20]
        ])
        
        # 车的位置价值（开放线路较高）
        chariot_value = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [ 5, 10, 10, 10, 10, 10, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0]
        ])
        
        # 炮的位置价值（中心和对面较高）
        cannon_value = np.array([
            [20, 20, 20, 20, 20, 20, 20, 20, 20],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  5,  5,  5,  0,  0, -5],
            [-5,  0,  0,  5, 10,  5,  0,  0, -5],
            [-5,  0,  0,  5, 10,  5,  0,  0, -5],
            [-5,  0,  0,  5,  5,  5,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0,  0, -5],
            [20, 20, 20, 20, 20, 20, 20, 20, 20]
        ])
        
        # 帅/将的位置价值（九宫内安全位置较高）
        king_value = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 5, 1, 0, 0, 0],
            [0, 0, 0, 2, 3, 2, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0]
        ])
        
        # 仕/士的位置价值
        advisor_value = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 20, 0, 20, 0, 0, 0],
            [0, 0, 0, 0, 23, 0, 0, 0, 0],
            [0, 0, 0, 20, 0, 20, 0, 0, 0]
        ])
        
        # 相/象的位置价值
        elephant_value = np.array([
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0, 20,  0,  0,  0, 20,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [18, 0,  0,  0, 23,  0,  0,  0, 18],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0, 20,  0,  0,  0, 20,  0,  0]
        ])
        
        # 为红方和黑方分别设置位置价值表
        position_values['red_pawn'] = pawn_red
        position_values['black_pawn'] = pawn_black
        position_values['red_horse'] = horse_value
        position_values['black_horse'] = np.flip(horse_value, axis=0)
        position_values['red_chariot'] = chariot_value
        position_values['black_chariot'] = np.flip(chariot_value, axis=0)
        position_values['red_cannon'] = cannon_value
        position_values['black_cannon'] = np.flip(cannon_value, axis=0)
        position_values['red_king'] = king_value
        position_values['black_king'] = np.flip(king_value, axis=0)
        position_values['red_advisor'] = advisor_value
        position_values['black_advisor'] = np.flip(advisor_value, axis=0)
        position_values['red_elephant'] = elephant_value
        position_values['black_elephant'] = np.flip(elephant_value, axis=0)
        
        return position_values
    
    def evaluate_position(self, board: List[List[Optional[str]]], 
                         perspective: str = 'red') -> Dict[str, float]:
        """评估局面价值
        
        Args:
            board: 棋盘状态
            perspective: 评估视角，'red'或'black'
            
        Returns:
            包含各项评估指标的字典
        """
        evaluation = {
            'material_score': 0,      # 子力分数
            'position_score': 0,      # 位置分数
            'mobility_score': 0,      # 机动性分数
            'king_safety_score': 0,   # 王安全分数
            'center_control_score': 0, # 中心控制分数
            'development_score': 0,   # 发展分数
            'attack_score': 0,        # 攻击分数
            'defense_score': 0,       # 防守分数
            'total_score': 0,         # 总分
            'win_probability': 0.5    # 胜率
        }
        
        # 计算各项分数
        evaluation['material_score'] = self._calculate_material_score(board, perspective)
        evaluation['position_score'] = self._calculate_position_score(board, perspective)
        evaluation['mobility_score'] = self._calculate_mobility_score(board, perspective)
        evaluation['king_safety_score'] = self._calculate_king_safety_score(board, perspective)
        evaluation['center_control_score'] = self._calculate_center_control_score(board, perspective)
        evaluation['development_score'] = self._calculate_development_score(board, perspective)
        evaluation['attack_score'] = self._calculate_attack_score(board, perspective)
        evaluation['defense_score'] = self._calculate_defense_score(board, perspective)
        
        # 计算总分（加权求和）
        evaluation['total_score'] = (
            evaluation['material_score'] * self.weights['material'] +
            evaluation['position_score'] * self.weights['position'] +
            evaluation['mobility_score'] * self.weights['mobility'] +
            evaluation['king_safety_score'] * self.weights['king_safety'] +
            evaluation['center_control_score'] * self.weights['center_control'] +
            evaluation['development_score'] * self.weights['development'] +
            evaluation['attack_score'] * self.weights['attack'] +
            evaluation['defense_score'] * self.weights['defense']
        )
        
        # 计算胜率
        evaluation['win_probability'] = self._score_to_win_probability(evaluation['total_score'])
        
        return evaluation
    
    def _calculate_material_score(self, board: List[List[Optional[str]]], 
                                 perspective: str) -> float:
        """计算子力分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            子力分数差值
        """
        my_material = 0
        opponent_material = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue
                
                piece_value = self.piece_values.get(piece, 0)
                
                if perspective in piece:  # 我方棋子
                    my_material += piece_value
                else:  # 对方棋子
                    opponent_material += piece_value
        
        return my_material - opponent_material
    
    def _calculate_position_score(self, board: List[List[Optional[str]]], 
                                 perspective: str) -> float:
        """计算位置分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            位置分数差值
        """
        my_position = 0
        opponent_position = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue
                
                # 获取该棋子类型的位置价值表
                if piece in self.position_values:
                    position_value = self.position_values[piece][row][col]
                    
                    if perspective in piece:  # 我方棋子
                        my_position += position_value
                    else:  # 对方棋子
                        opponent_position += position_value
        
        return my_position - opponent_position
    
    def _calculate_mobility_score(self, board: List[List[Optional[str]]], 
                                 perspective: str) -> float:
        """计算机动性分数（棋子的可走位置数量）
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            机动性分数差值
        """
        # 这里简化计算，实际应该计算每个棋子的合法走法数量
        my_mobility = 0
        opponent_mobility = 0
        
        # 基于棋子类型给予基础机动性分数
        mobility_base = {
            'king': 4, 'advisor': 4, 'elephant': 4,
            'horse': 8, 'chariot': 14, 'cannon': 14, 'pawn': 3
        }
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue
                
                # 简化的机动性计算
                for piece_type, base_mobility in mobility_base.items():
                    if piece_type in piece:
                        if perspective in piece:
                            my_mobility += base_mobility
                        else:
                            opponent_mobility += base_mobility
                        break
        
        return (my_mobility - opponent_mobility) * 2
    
    def _calculate_king_safety_score(self, board: List[List[Optional[str]]], 
                                    perspective: str) -> float:
        """计算王的安全性分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            王安全性分数差值
        """
        my_safety = 0
        opponent_safety = 0
        
        # 寻找双方的王
        my_king_pos = None
        opponent_king_pos = None
        
        my_king = f"{perspective}_king"
        opponent_king = "black_king" if perspective == "red" else "red_king"
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece == my_king:
                    my_king_pos = (row, col)
                elif piece == opponent_king:
                    opponent_king_pos = (row, col)
        
        # 计算王周围的保护情况
        if my_king_pos:
            my_safety = self._evaluate_king_safety(board, my_king_pos, perspective)
        
        if opponent_king_pos:
            opponent_perspective = "black" if perspective == "red" else "red"
            opponent_safety = self._evaluate_king_safety(board, opponent_king_pos, opponent_perspective)
        
        return (my_safety - opponent_safety) * 50
    
    def _evaluate_king_safety(self, board: List[List[Optional[str]]], 
                             king_pos: Tuple[int, int], color: str) -> float:
        """评估特定王的安全性
        
        Args:
            board: 棋盘状态
            king_pos: 王的位置
            color: 王的颜色
            
        Returns:
            安全性分数
        """
        safety_score = 0
        row, col = king_pos
        
        # 检查九宫内的保护情况
        if color == "red":
            palace_rows = range(7, 10)
            palace_cols = range(3, 6)
        else:
            palace_rows = range(0, 3)
            palace_cols = range(3, 6)
        
        # 计算九宫内己方棋子数量（保护力量）
        protectors = 0
        for r in palace_rows:
            for c in palace_cols:
                piece = board[r][c]
                if piece and color in piece and 'king' not in piece:
                    protectors += 1
        
        safety_score += protectors * 20
        
        # 检查是否有对方攻击性棋子威胁王
        threats = 0
        opponent_color = "black" if color == "red" else "red"
        
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece and opponent_color in piece:
                    if self._can_threaten_king(board, (r, c), king_pos, piece):
                        threats += 1
        
        safety_score -= threats * 30
        
        return safety_score
    
    def _can_threaten_king(self, board: List[List[Optional[str]]], 
                          piece_pos: Tuple[int, int], king_pos: Tuple[int, int], 
                          piece: str) -> bool:
        """检查棋子是否能威胁到王
        
        Args:
            board: 棋盘状态
            piece_pos: 棋子位置
            king_pos: 王的位置
            piece: 棋子类型
            
        Returns:
            是否能威胁到王
        """
        # 简化的威胁检测，这里只检查直接攻击
        from_row, from_col = piece_pos
        to_row, to_col = king_pos
        
        # 车和炮的直线威胁
        if 'chariot' in piece or 'cannon' in piece:
            if from_row == to_row or from_col == to_col:
                return True
        
        # 马的威胁
        elif 'horse' in piece:
            row_diff = abs(to_row - from_row)
            col_diff = abs(to_col - from_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True
        
        # 兵/卒的威胁
        elif 'pawn' in piece:
            if 'red' in piece:
                if to_row == from_row - 1 and to_col == from_col:
                    return True
                elif from_row <= 4 and to_row == from_row and abs(to_col - from_col) == 1:
                    return True
            else:
                if to_row == from_row + 1 and to_col == from_col:
                    return True
                elif from_row >= 5 and to_row == from_row and abs(to_col - from_col) == 1:
                    return True
        
        return False
    
    def _calculate_center_control_score(self, board: List[List[Optional[str]]], 
                                       perspective: str) -> float:
        """计算中心控制分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            中心控制分数差值
        """
        # 定义中心区域（河界附近的重要位置）
        center_positions = [
            (4, 3), (4, 4), (4, 5),  # 河界上方
            (5, 3), (5, 4), (5, 5)   # 河界下方
        ]
        
        my_control = 0
        opponent_control = 0
        
        for pos in center_positions:
            row, col = pos
            piece = board[row][col]
            
            if piece:
                if perspective in piece:
                    my_control += 15  # 占据中心位置的奖励
                else:
                    opponent_control += 15
        
        return my_control - opponent_control
    
    def _calculate_development_score(self, board: List[List[Optional[str]]], 
                                    perspective: str) -> float:
        """计算子力发展分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            发展分数差值
        """
        my_development = 0
        opponent_development = 0
        
        # 检查子力是否离开了初始位置
        initial_positions = self._get_initial_positions()
        
        for piece_type, positions in initial_positions.items():
            if perspective in piece_type:
                for pos in positions:
                    row, col = pos
                    if board[row][col] != piece_type:
                        my_development += 10  # 子力发展奖励
            else:
                opposite_piece = piece_type.replace(perspective, "black" if perspective == "red" else "red")
                if opposite_piece in initial_positions:
                    for pos in initial_positions[opposite_piece]:
                        row, col = pos
                        if board[row][col] != opposite_piece:
                            opponent_development += 10
        
        return my_development - opponent_development
    
    def _get_initial_positions(self) -> Dict[str, List[Tuple[int, int]]]:
        """获取棋子的初始位置
        
        Returns:
            棋子初始位置字典
        """
        return {
            'red_chariot': [(9, 0), (9, 8)],
            'red_horse': [(9, 1), (9, 7)],
            'red_elephant': [(9, 2), (9, 6)],
            'red_advisor': [(9, 3), (9, 5)],
            'red_king': [(9, 4)],
            'red_cannon': [(7, 1), (7, 7)],
            'red_pawn': [(6, 0), (6, 2), (6, 4), (6, 6), (6, 8)],
            'black_chariot': [(0, 0), (0, 8)],
            'black_horse': [(0, 1), (0, 7)],
            'black_elephant': [(0, 2), (0, 6)],
            'black_advisor': [(0, 3), (0, 5)],
            'black_king': [(0, 4)],
            'black_cannon': [(2, 1), (2, 7)],
            'black_pawn': [(3, 0), (3, 2), (3, 4), (3, 6), (3, 8)]
        }
    
    def _calculate_attack_score(self, board: List[List[Optional[str]]], 
                               perspective: str) -> float:
        """计算攻击分数
        
        Args:
            board: 棋盘状态
            perspective: 评估视角
            
        Returns:
            攻击分数差值
        """
        # 简化的攻击分数计算
        # 主要考虑子力向对方半场的渗透程度
        
        my_attack = 0
        opponent_attack = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue
                
                if perspective in piece:
                    # 我方棋子深入对方半场的奖励
                    if perspective == "red" and row <= 4:
                        my_attack += self.piece_values[piece] * 0.1
                    elif perspective == "black" and row >= 5:
                        my_attack += self.piece_values[piece] * 0.1
                else:
                    # 对方棋子深入我方半场的威胁
                    if perspective == "red" and row >= 5:
                        opponent_attack += self.piece_values[piece] * 0.1
                    elif perspective == "black" and row <= 4:
                        opponent_attack += self.piece_values[piece] * 0.1
        
        return my_attack - opponent_attack
    
    def _calculate_defense_score(self, board: List[List[Optional[str]]], 
                                perspective: str) -> float:
        """计算防守分数
        
        Args:
            board: 棋盘状态  
            perspective: 评估视角
            
        Returns:
            防守分数差值
        """
        # 简化的防守分数计算
        # 主要考虑己方半场的子力密度
        
        my_defense = 0
        opponent_defense = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue
                
                piece_value = self.piece_values.get(piece, 0)
                
                if perspective in piece:
                    # 我方子力在己方半场的防守价值
                    if perspective == "red" and row >= 5:
                        my_defense += piece_value * 0.05
                    elif perspective == "black" and row <= 4:
                        my_defense += piece_value * 0.05
                else:
                    # 对方子力在其半场的防守价值
                    if perspective == "red" and row <= 4:
                        opponent_defense += piece_value * 0.05
                    elif perspective == "black" and row >= 5:
                        opponent_defense += piece_value * 0.05
        
        return my_defense - opponent_defense
    
    def _score_to_win_probability(self, score: float) -> float:
        """将评估分数转换为胜率百分比
        
        Args:
            score: 评估分数
            
        Returns:
            胜率（0-1之间）
        """
        # 使用Sigmoid函数将分数映射到胜率
        # 分数越高胜率越高，使用合适的缩放因子
        
        # 缩放因子，可以调整以获得合适的胜率范围
        scale_factor = 0.002
        
        # Sigmoid函数: 1 / (1 + e^(-x))
        probability = 1.0 / (1.0 + math.exp(-score * scale_factor))
        
        # 确保胜率在合理范围内
        probability = max(0.01, min(0.99, probability))
        
        return probability
    
    def compare_positions(self, board1: List[List[Optional[str]]], 
                         board2: List[List[Optional[str]]], 
                         perspective: str = 'red') -> Dict[str, any]:
        """比较两个局面的优劣
        
        Args:
            board1: 第一个棋盘状态
            board2: 第二个棋盘状态
            perspective: 评估视角
            
        Returns:
            比较结果
        """
        eval1 = self.evaluate_position(board1, perspective)
        eval2 = self.evaluate_position(board2, perspective)
        
        score_diff = eval2['total_score'] - eval1['total_score']
        prob_diff = eval2['win_probability'] - eval1['win_probability']
        
        return {
            'board1_evaluation': eval1,
            'board2_evaluation': eval2,
            'score_difference': score_diff,
            'probability_difference': prob_diff,
            'is_improvement': score_diff > 0,
            'improvement_magnitude': abs(score_diff)
        }
    
    def get_evaluation_summary(self, evaluation: Dict[str, float]) -> str:
        """获取评估结果的文字描述
        
        Args:
            evaluation: 评估结果字典
            
        Returns:
            评估结果的文字描述
        """
        total_score = evaluation['total_score']
        win_prob = evaluation['win_probability'] * 100
        
        # 根据胜率给出形势判断
        if win_prob >= 80:
            situation = "大优"
        elif win_prob >= 65:
            situation = "优势"
        elif win_prob >= 55:
            situation = "小优"
        elif win_prob >= 45:
            situation = "均势"
        elif win_prob >= 35:
            situation = "小劣"
        elif win_prob >= 20:
            situation = "劣势"
        else:
            situation = "大劣"
        
        summary = f"局面评估: {situation} (胜率: {win_prob:.1f}%)\n"
        summary += f"总分: {total_score:.1f}\n"
        summary += f"子力优势: {evaluation['material_score']:.1f}\n"
        summary += f"位置价值: {evaluation['position_score']:.1f}\n"
        summary += f"王安全性: {evaluation['king_safety_score']:.1f}"
        
        return summary