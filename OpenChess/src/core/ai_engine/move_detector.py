#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
走法检测器模块
用于检测中国象棋棋局的变化和识别具体走法
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
import copy
import time

class Move(NamedTuple):
    """走法数据结构"""
    from_pos: Tuple[int, int]  # 起始位置 (row, col)
    to_pos: Tuple[int, int]    # 目标位置 (row, col)
    piece: str                 # 移动的棋子类型
    captured_piece: Optional[str] = None  # 被吃掉的棋子（如果有）
    move_type: str = 'normal'  # 走法类型：normal, capture, check
    
class MoveDetector:
    """走法检测器类
    
    负责检测棋盘状态变化，识别对手的具体走法
    """
    
    def __init__(self):
        """初始化走法检测器"""
        # 棋盘历史记录，用于检测变化
        self.board_history: List[List[List[Optional[str]]]] = []
        
        # 当前棋盘状态
        self.current_board: Optional[List[List[Optional[str]]]] = None
        
        # 上一次的棋盘状态
        self.previous_board: Optional[List[List[Optional[str]]]] = None
        
        # 走法历史
        self.move_history: List[Move] = []
        
        # 棋子类型定义（用于验证走法合法性）
        self.piece_types = {
            'red_king': '帅', 'red_advisor': '仕', 'red_elephant': '相',
            'red_horse': '马', 'red_chariot': '车', 'red_cannon': '炮', 'red_pawn': '兵',
            'black_king': '将', 'black_advisor': '士', 'black_elephant': '象',
            'black_horse': '马', 'black_chariot': '车', 'black_cannon': '炮', 'black_pawn': '卒'
        }
        
        # 棋盘尺寸
        self.board_size = (10, 9)  # 10行9列
        
    def update_board(self, new_board: List[List[Optional[str]]]) -> Optional[Move]:
        """更新棋盘状态并检测走法
        
        Args:
            new_board: 新的棋盘状态
            
        Returns:
            如果检测到走法则返回Move对象，否则返回None
        """
        # 验证棋盘格式
        if not self._is_valid_board(new_board):
            raise ValueError("无效的棋盘格式")
        
        # 保存上一次的棋盘状态
        self.previous_board = copy.deepcopy(self.current_board) if self.current_board else None
        
        # 更新当前棋盘
        self.current_board = copy.deepcopy(new_board)
        
        # 添加到历史记录
        self.board_history.append(copy.deepcopy(new_board))
        
        # 如果有上一次的棋盘状态，检测走法
        if self.previous_board is not None:
            detected_move = self._detect_move_from_boards(self.previous_board, self.current_board)
            if detected_move:
                self.move_history.append(detected_move)
                return detected_move
        
        return None
    
    def _is_valid_board(self, board: List[List[Optional[str]]]) -> bool:
        """验证棋盘格式是否正确
        
        Args:
            board: 待验证的棋盘
            
        Returns:
            是否为有效的棋盘格式
        """
        if not isinstance(board, list) or len(board) != 10:
            return False
        
        for row in board:
            if not isinstance(row, list) or len(row) != 9:
                return False
            
            for cell in row:
                if cell is not None and not isinstance(cell, str):
                    return False
                    
        return True
    
    def _detect_move_from_boards(self, prev_board: List[List[Optional[str]]], 
                                curr_board: List[List[Optional[str]]]) -> Optional[Move]:
        """从两个棋盘状态检测走法
        
        Args:
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            检测到的走法，如果无变化则返回None
        """
        # 查找所有变化的位置
        changes = self._find_board_changes(prev_board, curr_board)
        
        if not changes:
            return None
        
        # 分析变化模式识别走法
        move = self._analyze_changes_for_move(changes, prev_board, curr_board)
        
        return move
    
    def _find_board_changes(self, prev_board: List[List[Optional[str]]], 
                           curr_board: List[List[Optional[str]]]) -> List[Dict]:
        """找出两个棋盘之间的所有变化
        
        Args:
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            变化列表，每个变化包含位置和前后状态
        """
        changes = []
        
        for row in range(10):
            for col in range(9):
                prev_piece = prev_board[row][col]
                curr_piece = curr_board[row][col]
                
                if prev_piece != curr_piece:
                    changes.append({
                        'position': (row, col),
                        'before': prev_piece,
                        'after': curr_piece
                    })
        
        return changes
    
    def _analyze_changes_for_move(self, changes: List[Dict], 
                                 prev_board: List[List[Optional[str]]], 
                                 curr_board: List[List[Optional[str]]]) -> Optional[Move]:
        """分析变化模式以识别具体走法
        
        Args:
            changes: 棋盘变化列表
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            识别出的走法
        """
        if len(changes) == 0:
            return None
        
        # 情况1: 只有两个变化 - 正常移动或吃子
        if len(changes) == 2:
            return self._analyze_two_changes(changes, prev_board, curr_board)
        
        # 情况2: 只有一个变化 - 可能是棋子消失或出现
        elif len(changes) == 1:
            return self._analyze_single_change(changes[0], prev_board, curr_board)
        
        # 情况3: 多个变化 - 可能是复杂走法或识别错误
        else:
            return self._analyze_multiple_changes(changes, prev_board, curr_board)
    
    def _analyze_two_changes(self, changes: List[Dict], 
                            prev_board: List[List[Optional[str]]], 
                            curr_board: List[List[Optional[str]]]) -> Optional[Move]:
        """分析两个变化的情况（最常见的走法模式）
        
        Args:
            changes: 变化列表（应该包含2个变化）
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            识别出的走法
        """
        # 找出棋子消失的位置（起始位置）和出现的位置（目标位置）
        from_pos = None
        to_pos = None
        moving_piece = None
        captured_piece = None
        
        for change in changes:
            pos = change['position']
            before = change['before']
            after = change['after']
            
            # 棋子从这个位置消失
            if before is not None and after is None:
                from_pos = pos
                moving_piece = before
            
            # 棋子出现在这个位置
            elif before is None and after is not None:
                to_pos = pos
                # 验证移动的是同一个棋子
                if moving_piece and after != moving_piece:
                    return None  # 不匹配，可能是识别错误
            
            # 棋子被替换（吃子）
            elif before is not None and after is not None:
                to_pos = pos
                captured_piece = before
                # 验证移动的是同一个棋子
                if moving_piece and after != moving_piece:
                    return None  # 不匹配，可能是识别错误
        
        # 验证走法有效性
        if from_pos and to_pos and moving_piece:
            # 验证走法是否符合象棋规则
            if self._is_legal_move(from_pos, to_pos, moving_piece, prev_board):
                move_type = 'capture' if captured_piece else 'normal'
                
                # 检查是否构成将军
                if self._causes_check(to_pos, moving_piece, curr_board):
                    move_type = 'check'
                
                return Move(
                    from_pos=from_pos,
                    to_pos=to_pos,
                    piece=moving_piece,
                    captured_piece=captured_piece,
                    move_type=move_type
                )
        
        return None
    
    def _analyze_single_change(self, change: Dict, 
                              prev_board: List[List[Optional[str]]], 
                              curr_board: List[List[Optional[str]]]) -> Optional[Move]:
        """分析单个变化的情况
        
        Args:
            change: 单个变化
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            识别出的走法（通常返回None，因为单个变化很难构成有效走法）
        """
        # 单个变化通常不构成有效的走法，可能是识别错误
        # 但可以记录异常情况
        return None
    
    def _analyze_multiple_changes(self, changes: List[Dict], 
                                 prev_board: List[List[Optional[str]]], 
                                 curr_board: List[List[Optional[str]]]) -> Optional[Move]:
        """分析多个变化的情况
        
        Args:
            changes: 变化列表
            prev_board: 上一次的棋盘状态
            curr_board: 当前的棋盘状态
            
        Returns:
            识别出的走法
        """
        # 多个变化可能是：
        # 1. 识别错误导致的多余变化
        # 2. 特殊走法（如兵的升级等）
        
        # 尝试从多个变化中找出主要的走法模式
        # 寻找最可能的起始和目标位置
        
        piece_disappear = []  # 棋子消失的位置
        piece_appear = []     # 棋子出现的位置
        piece_change = []     # 棋子变化的位置
        
        for change in changes:
            before = change['before']
            after = change['after']
            
            if before is not None and after is None:
                piece_disappear.append(change)
            elif before is None and after is not None:
                piece_appear.append(change)
            else:
                piece_change.append(change)
        
        # 如果有一个消失和一个出现，可能是基本走法
        if len(piece_disappear) == 1 and len(piece_appear) == 1:
            # 构造两个变化并递归处理
            return self._analyze_two_changes([piece_disappear[0], piece_appear[0]], 
                                           prev_board, curr_board)
        
        return None
    
    def _is_legal_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                      piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证走法是否符合中国象棋规则
        
        Args:
            from_pos: 起始位置
            to_pos: 目标位置  
            piece: 移动的棋子
            board: 棋盘状态
            
        Returns:
            走法是否合法
        """
        # 基本验证
        if from_pos == to_pos:
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 位置是否在棋盘内
        if not (0 <= to_row < 10 and 0 <= to_col < 9):
            return False
        
        # 根据棋子类型验证走法
        if 'king' in piece:  # 帅/将
            return self._is_legal_king_move(from_pos, to_pos, piece, board)
        elif 'advisor' in piece:  # 仕/士
            return self._is_legal_advisor_move(from_pos, to_pos, piece, board)
        elif 'elephant' in piece:  # 相/象
            return self._is_legal_elephant_move(from_pos, to_pos, piece, board)
        elif 'horse' in piece:  # 马
            return self._is_legal_horse_move(from_pos, to_pos, piece, board)
        elif 'chariot' in piece:  # 车
            return self._is_legal_chariot_move(from_pos, to_pos, piece, board)
        elif 'cannon' in piece:  # 炮
            return self._is_legal_cannon_move(from_pos, to_pos, piece, board)
        elif 'pawn' in piece:  # 兵/卒
            return self._is_legal_pawn_move(from_pos, to_pos, piece, board)
        
        return False
    
    def _is_legal_king_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                           piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证帅/将的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 只能在九宫内移动
        if 'red' in piece:  # 红帅
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:  # 黑将
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # 只能走一格，且只能横走或竖走
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def _is_legal_advisor_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                              piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证仕/士的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 只能在九宫内移动
        if 'red' in piece:  # 红仕
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:  # 黑士
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # 只能斜走一格
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        return row_diff == 1 and col_diff == 1
    
    def _is_legal_elephant_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                               piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证相/象的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 不能过河
        if 'red' in piece:  # 红相
            if to_row < 5:
                return False
        else:  # 黑象
            if to_row > 4:
                return False
        
        # 必须走田字
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if row_diff != 2 or col_diff != 2:
            return False
        
        # 检查象眼是否被堵
        eye_row = from_row + (to_row - from_row) // 2
        eye_col = from_col + (to_col - from_col) // 2
        
        return board[eye_row][eye_col] is None
    
    def _is_legal_horse_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                            piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证马的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # 马走日字
        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            return False
        
        # 检查马腿是否被堵
        if row_diff == 2:  # 竖走
            leg_row = from_row + (to_row - from_row) // 2
            leg_col = from_col
        else:  # 横走
            leg_row = from_row
            leg_col = from_col + (to_col - from_col) // 2
        
        return board[leg_row][leg_col] is None
    
    def _is_legal_chariot_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                              piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证车的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 车只能直走
        if from_row != to_row and from_col != to_col:
            return False
        
        # 检查路径是否有障碍
        if from_row == to_row:  # 横走
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board[from_row][col] is not None:
                    return False
        else:  # 竖走
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board[row][from_col] is not None:
                    return False
        
        return True
    
    def _is_legal_cannon_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                             piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证炮的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 炮只能直走
        if from_row != to_row and from_col != to_col:
            return False
        
        # 计算路径上的棋子数量
        pieces_count = 0
        
        if from_row == to_row:  # 横走
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board[from_row][col] is not None:
                    pieces_count += 1
        else:  # 竖走
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board[row][from_col] is not None:
                    pieces_count += 1
        
        # 目标位置的情况
        target_piece = board[to_row][to_col]
        
        if target_piece is None:
            # 移动：路径上不能有棋子
            return pieces_count == 0
        else:
            # 吃子：路径上必须恰好有一个棋子作为炮架
            return pieces_count == 1
    
    def _is_legal_pawn_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                           piece: str, board: List[List[Optional[str]]]) -> bool:
        """验证兵/卒的走法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = to_row - from_row
        col_diff = abs(to_col - from_col)
        
        if 'red' in piece:  # 红兵
            # 未过河：只能向前
            if from_row > 4:
                return row_diff == -1 and col_diff == 0
            # 已过河：可以向前或左右
            else:
                return (row_diff == -1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
        else:  # 黑卒
            # 未过河：只能向前
            if from_row < 5:
                return row_diff == 1 and col_diff == 0
            # 已过河：可以向前或左右
            else:
                return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def _causes_check(self, to_pos: Tuple[int, int], piece: str, 
                     board: List[List[Optional[str]]]) -> bool:
        """检查走法是否构成将军
        
        Args:
            to_pos: 走法的目标位置
            piece: 移动的棋子
            board: 走法后的棋盘状态
            
        Returns:
            是否构成将军
        """
        # 找到对方的将/帅
        opponent_king = None
        opponent_king_pos = None
        
        if 'red' in piece:
            opponent_king = 'black_king'
        else:
            opponent_king = 'red_king'
        
        # 寻找对方王的位置
        for row in range(10):
            for col in range(9):
                if board[row][col] == opponent_king:
                    opponent_king_pos = (row, col)
                    break
            if opponent_king_pos:
                break
        
        if not opponent_king_pos:
            return False
        
        # 检查移动后的棋子是否能攻击到对方的王
        return self._can_attack(to_pos, opponent_king_pos, piece, board)
    
    def _can_attack(self, from_pos: Tuple[int, int], target_pos: Tuple[int, int], 
                   piece: str, board: List[List[Optional[str]]]) -> bool:
        """检查棋子是否能攻击到目标位置
        
        Args:
            from_pos: 棋子位置
            target_pos: 目标位置
            piece: 棋子类型
            board: 棋盘状态
            
        Returns:
            是否能攻击到目标
        """
        # 复制棋盘并清空目标位置来测试攻击
        test_board = copy.deepcopy(board)
        test_board[target_pos[0]][target_pos[1]] = None
        
        # 测试是否是合法的攻击走法
        return self._is_legal_move(from_pos, target_pos, piece, test_board)
    
    def get_last_move(self) -> Optional[Move]:
        """获取最后一次走法
        
        Returns:
            最后一次的走法，如果没有则返回None
        """
        return self.move_history[-1] if self.move_history else None
    
    def get_move_history(self) -> List[Move]:
        """获取所有走法历史
        
        Returns:
            走法历史列表
        """
        return copy.deepcopy(self.move_history)
    
    def clear_history(self):
        """清空历史记录"""
        self.board_history.clear()
        self.move_history.clear()
        self.current_board = None
        self.previous_board = None
    
    def format_move(self, move: Move) -> str:
        """格式化走法为易读的字符串
        
        Args:
            move: 走法对象
            
        Returns:
            格式化的走法字符串
        """
        piece_name = self.piece_types.get(move.piece, move.piece)
        
        # 转换坐标为中国象棋标准记法
        from_col_name = chr(ord('a') + move.from_pos[1])
        to_col_name = chr(ord('a') + move.to_pos[1])
        from_row_name = str(10 - move.from_pos[0])
        to_row_name = str(10 - move.to_pos[0])
        
        move_str = f"{piece_name} {from_col_name}{from_row_name}-{to_col_name}{to_row_name}"
        
        if move.captured_piece:
            captured_name = self.piece_types.get(move.captured_piece, move.captured_piece)
            move_str += f" 吃{captured_name}"
        
        if move.move_type == 'check':
            move_str += " 将军"
        
        return move_str