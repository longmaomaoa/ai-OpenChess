#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋AI助手核心模块
整合走法检测、局面评估和AI决策功能
"""

import copy
from typing import Dict, List, Tuple, Optional, NamedTuple
import time
import random

from .move_detector import MoveDetector, Move
from .position_evaluator import PositionEvaluator

class Recommendation(NamedTuple):
    """推荐走法数据结构"""
    move: Move                    # 推荐的走法
    score: float                  # 评估分数
    win_probability: float        # 胜率
    confidence: float             # 推荐置信度
    reasoning: str                # 推荐理由
    
class GameAnalysis(NamedTuple):
    """游戏分析结果"""
    current_evaluation: Dict[str, float]  # 当前局面评估
    opponent_last_move: Optional[Move]    # 对手最后一步
    recommendations: List[Recommendation] # 推荐走法列表
    threats: List[str]                    # 威胁列表
    opportunities: List[str]              # 机会列表

class ChessAIAssistant:
    """中国象棋AI助手主类
    
    整合各个功能模块，为用户提供智能对弈建议
    """
    
    def __init__(self, player_color: str = 'red'):
        """初始化AI助手
        
        Args:
            player_color: 玩家颜色，'red'或'black'，默认为'red'（玩家在下方）
        """
        self.player_color = player_color
        self.opponent_color = 'black' if player_color == 'red' else 'red'
        
        # 初始化核心组件
        self.move_detector = MoveDetector()
        self.position_evaluator = PositionEvaluator()
        
        # 游戏状态
        self.current_board: Optional[List[List[Optional[str]]]] = None
        self.game_phase = 'opening'  # opening, middlegame, endgame
        self.move_count = 0
        
        # AI设置
        self.search_depth = 3  # 搜索深度
        self.max_recommendations = 5  # 最多推荐走法数
        
        # 分析历史
        self.analysis_history: List[GameAnalysis] = []
        
    def update_board_state(self, new_board: List[List[Optional[str]]]) -> GameAnalysis:
        """更新棋盘状态并进行AI分析
        
        Args:
            new_board: 新的棋盘状态
            
        Returns:
            游戏分析结果
        """
        # 检测走法变化
        detected_move = self.move_detector.update_board(new_board)
        
        # 更新当前棋盘
        self.current_board = copy.deepcopy(new_board)
        
        # 如果检测到对手走法，增加计数
        if detected_move and self.opponent_color in detected_move.piece:
            self.move_count += 1
            self._update_game_phase()
        
        # 进行局面分析
        analysis = self._analyze_position()
        
        # 添加到历史记录
        self.analysis_history.append(analysis)
        
        return analysis
    
    def _update_game_phase(self):
        """根据走法数更新游戏阶段"""
        if self.move_count <= 10:
            self.game_phase = 'opening'
        elif self.move_count <= 30:
            self.game_phase = 'middlegame'
        else:
            self.game_phase = 'endgame'
    
    def _analyze_position(self) -> GameAnalysis:
        """分析当前局面
        
        Returns:
            游戏分析结果
        """
        if not self.current_board:
            raise ValueError("棋盘状态未初始化")
        
        # 评估当前局面
        current_evaluation = self.position_evaluator.evaluate_position(
            self.current_board, self.player_color
        )
        
        # 获取对手最后一步
        opponent_last_move = self.move_detector.get_last_move()
        
        # 生成推荐走法
        recommendations = self._generate_recommendations()
        
        # 分析威胁和机会
        threats = self._analyze_threats()
        opportunities = self._analyze_opportunities()
        
        return GameAnalysis(
            current_evaluation=current_evaluation,
            opponent_last_move=opponent_last_move,
            recommendations=recommendations,
            threats=threats,
            opportunities=opportunities
        )
    
    def _generate_recommendations(self) -> List[Recommendation]:
        """生成走法推荐
        
        Returns:
            推荐走法列表，按评分排序
        """
        if not self.current_board:
            return []
        
        # 生成所有可能的走法
        possible_moves = self._generate_all_legal_moves(self.current_board, self.player_color)
        
        # 评估每个走法
        move_evaluations = []
        for move in possible_moves:
            evaluation = self._evaluate_move(move)
            if evaluation:
                move_evaluations.append(evaluation)
        
        # 按评分排序
        move_evaluations.sort(key=lambda x: x.score, reverse=True)
        
        # 返回前N个推荐
        return move_evaluations[:self.max_recommendations]
    
    def _generate_all_legal_moves(self, board: List[List[Optional[str]]], 
                                 color: str) -> List[Move]:
        """生成指定颜色的所有合法走法
        
        Args:
            board: 棋盘状态
            color: 要生成走法的颜色
            
        Returns:
            合法走法列表
        """
        legal_moves = []
        
        # 遍历棋盘找到己方棋子
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece and color in piece:
                    # 为每个棋子生成可能的走法
                    piece_moves = self._generate_piece_moves(board, (row, col), piece)
                    legal_moves.extend(piece_moves)
        
        return legal_moves
    
    def _generate_piece_moves(self, board: List[List[Optional[str]]], 
                             from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """为特定棋子生成所有可能的走法
        
        Args:
            board: 棋盘状态
            from_pos: 棋子位置
            piece: 棋子类型
            
        Returns:
            该棋子的可能走法列表
        """
        moves = []
        from_row, from_col = from_pos
        
        # 根据棋子类型生成走法
        if 'king' in piece:
            moves.extend(self._generate_king_moves(board, from_pos, piece))
        elif 'advisor' in piece:
            moves.extend(self._generate_advisor_moves(board, from_pos, piece))
        elif 'elephant' in piece:
            moves.extend(self._generate_elephant_moves(board, from_pos, piece))
        elif 'horse' in piece:
            moves.extend(self._generate_horse_moves(board, from_pos, piece))
        elif 'chariot' in piece:
            moves.extend(self._generate_chariot_moves(board, from_pos, piece))
        elif 'cannon' in piece:
            moves.extend(self._generate_cannon_moves(board, from_pos, piece))
        elif 'pawn' in piece:
            moves.extend(self._generate_pawn_moves(board, from_pos, piece))
        
        return moves
    
    def _generate_king_moves(self, board: List[List[Optional[str]]], 
                            from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成帅/将的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 帅/将只能在九宫内移动
        if 'red' in piece:
            palace_rows = range(7, 10)
            palace_cols = range(3, 6)
        else:
            palace_rows = range(0, 3)
            palace_cols = range(3, 6)
        
        # 四个方向移动一格
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            to_row, to_col = from_row + dr, from_col + dc
            
            # 检查是否在九宫内
            if to_row in palace_rows and to_col in palace_cols:
                target_piece = board[to_row][to_col]
                
                # 空位或对方棋子
                if target_piece is None or self.player_color not in target_piece:
                    move_type = 'capture' if target_piece else 'normal'
                    move = Move(
                        from_pos=from_pos,
                        to_pos=(to_row, to_col),
                        piece=piece,
                        captured_piece=target_piece,
                        move_type=move_type
                    )
                    moves.append(move)
        
        return moves
    
    def _generate_advisor_moves(self, board: List[List[Optional[str]]], 
                               from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成仕/士的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 仕/士只能在九宫内斜走
        if 'red' in piece:
            palace_rows = range(7, 10)
            palace_cols = range(3, 6)
        else:
            palace_rows = range(0, 3)
            palace_cols = range(3, 6)
        
        # 四个对角方向
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            to_row, to_col = from_row + dr, from_col + dc
            
            if to_row in palace_rows and to_col in palace_cols:
                target_piece = board[to_row][to_col]
                
                if target_piece is None or self.player_color not in target_piece:
                    move_type = 'capture' if target_piece else 'normal'
                    move = Move(
                        from_pos=from_pos,
                        to_pos=(to_row, to_col),
                        piece=piece,
                        captured_piece=target_piece,
                        move_type=move_type
                    )
                    moves.append(move)
        
        return moves
    
    def _generate_elephant_moves(self, board: List[List[Optional[str]]], 
                                from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成相/象的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 相/象走田字，不能过河
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        for dr, dc in directions:
            to_row, to_col = from_row + dr, from_col + dc
            
            # 检查是否在棋盘内且不过河
            if 0 <= to_row < 10 and 0 <= to_col < 9:
                if 'red' in piece and to_row >= 5:  # 红相不过河
                    # 检查象眼是否被堵
                    eye_row, eye_col = from_row + dr//2, from_col + dc//2
                    if board[eye_row][eye_col] is None:
                        target_piece = board[to_row][to_col]
                        if target_piece is None or self.player_color not in target_piece:
                            move_type = 'capture' if target_piece else 'normal'
                            move = Move(
                                from_pos=from_pos,
                                to_pos=(to_row, to_col),
                                piece=piece,
                                captured_piece=target_piece,
                                move_type=move_type
                            )
                            moves.append(move)
                elif 'black' in piece and to_row <= 4:  # 黑象不过河
                    eye_row, eye_col = from_row + dr//2, from_col + dc//2
                    if board[eye_row][eye_col] is None:
                        target_piece = board[to_row][to_col]
                        if target_piece is None or self.player_color not in target_piece:
                            move_type = 'capture' if target_piece else 'normal'
                            move = Move(
                                from_pos=from_pos,
                                to_pos=(to_row, to_col),
                                piece=piece,
                                captured_piece=target_piece,
                                move_type=move_type
                            )
                            moves.append(move)
        
        return moves
    
    def _generate_horse_moves(self, board: List[List[Optional[str]]], 
                             from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成马的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 马走日字的8个方向
        directions = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        # 对应的马腿位置
        leg_positions = [
            (-1, 0), (-1, 0), (0, -1), (0, 1),
            (0, -1), (0, 1), (1, 0), (1, 0)
        ]
        
        for i, (dr, dc) in enumerate(directions):
            to_row, to_col = from_row + dr, from_col + dc
            
            if 0 <= to_row < 10 and 0 <= to_col < 9:
                # 检查马腿是否被堵
                leg_dr, leg_dc = leg_positions[i]
                leg_row, leg_col = from_row + leg_dr, from_col + leg_dc
                
                if board[leg_row][leg_col] is None:
                    target_piece = board[to_row][to_col]
                    if target_piece is None or self.player_color not in target_piece:
                        move_type = 'capture' if target_piece else 'normal'
                        move = Move(
                            from_pos=from_pos,
                            to_pos=(to_row, to_col),
                            piece=piece,
                            captured_piece=target_piece,
                            move_type=move_type
                        )
                        moves.append(move)
        
        return moves
    
    def _generate_chariot_moves(self, board: List[List[Optional[str]]], 
                               from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成车的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 车可以横走和竖走
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for distance in range(1, 10):  # 最大距离
                to_row, to_col = from_row + dr * distance, from_col + dc * distance
                
                if not (0 <= to_row < 10 and 0 <= to_col < 9):
                    break
                
                target_piece = board[to_row][to_col]
                
                if target_piece is None:
                    # 空位，可以移动
                    move = Move(
                        from_pos=from_pos,
                        to_pos=(to_row, to_col),
                        piece=piece,
                        move_type='normal'
                    )
                    moves.append(move)
                elif self.player_color not in target_piece:
                    # 对方棋子，可以吃掉，然后停止
                    move = Move(
                        from_pos=from_pos,
                        to_pos=(to_row, to_col),
                        piece=piece,
                        captured_piece=target_piece,
                        move_type='capture'
                    )
                    moves.append(move)
                    break
                else:
                    # 己方棋子，不能走，停止
                    break
        
        return moves
    
    def _generate_cannon_moves(self, board: List[List[Optional[str]]], 
                              from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成炮的走法"""
        moves = []
        from_row, from_col = from_pos
        
        # 炮可以横走和竖走
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            # 第一阶段：找到炮架或边界
            cannon_mount_found = False
            
            for distance in range(1, 10):
                to_row, to_col = from_row + dr * distance, from_col + dc * distance
                
                if not (0 <= to_row < 10 and 0 <= to_col < 9):
                    break
                
                target_piece = board[to_row][to_col]
                
                if not cannon_mount_found:
                    if target_piece is None:
                        # 空位，正常移动
                        move = Move(
                            from_pos=from_pos,
                            to_pos=(to_row, to_col),
                            piece=piece,
                            move_type='normal'
                        )
                        moves.append(move)
                    else:
                        # 找到炮架
                        cannon_mount_found = True
                else:
                    # 已经有炮架，寻找目标
                    if target_piece is not None and self.player_color not in target_piece:
                        # 找到对方棋子，可以吃掉
                        move = Move(
                            from_pos=from_pos,
                            to_pos=(to_row, to_col),
                            piece=piece,
                            captured_piece=target_piece,
                            move_type='capture'
                        )
                        moves.append(move)
                        break
                    elif target_piece is not None:
                        # 己方棋子，不能吃，停止
                        break
        
        return moves
    
    def _generate_pawn_moves(self, board: List[List[Optional[str]]], 
                            from_pos: Tuple[int, int], piece: str) -> List[Move]:
        """生成兵/卒的走法"""
        moves = []
        from_row, from_col = from_pos
        
        if 'red' in piece:  # 红兵
            # 未过河：只能向前
            if from_row > 4:
                to_row, to_col = from_row - 1, from_col
                if 0 <= to_row < 10:
                    target_piece = board[to_row][to_col]
                    if target_piece is None or self.player_color not in target_piece:
                        move_type = 'capture' if target_piece else 'normal'
                        move = Move(
                            from_pos=from_pos,
                            to_pos=(to_row, to_col),
                            piece=piece,
                            captured_piece=target_piece,
                            move_type=move_type
                        )
                        moves.append(move)
            # 已过河：可以向前或左右
            else:
                directions = [(-1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    to_row, to_col = from_row + dr, from_col + dc
                    if 0 <= to_row < 10 and 0 <= to_col < 9:
                        target_piece = board[to_row][to_col]
                        if target_piece is None or self.player_color not in target_piece:
                            move_type = 'capture' if target_piece else 'normal'
                            move = Move(
                                from_pos=from_pos,
                                to_pos=(to_row, to_col),
                                piece=piece,
                                captured_piece=target_piece,
                                move_type=move_type
                            )
                            moves.append(move)
        
        else:  # 黑卒
            # 未过河：只能向前
            if from_row < 5:
                to_row, to_col = from_row + 1, from_col
                if 0 <= to_row < 10:
                    target_piece = board[to_row][to_col]
                    if target_piece is None or self.player_color not in target_piece:
                        move_type = 'capture' if target_piece else 'normal'
                        move = Move(
                            from_pos=from_pos,
                            to_pos=(to_row, to_col),
                            piece=piece,
                            captured_piece=target_piece,
                            move_type=move_type
                        )
                        moves.append(move)
            # 已过河：可以向前或左右
            else:
                directions = [(1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    to_row, to_col = from_row + dr, from_col + dc
                    if 0 <= to_row < 10 and 0 <= to_col < 9:
                        target_piece = board[to_row][to_col]
                        if target_piece is None or self.player_color not in target_piece:
                            move_type = 'capture' if target_piece else 'normal'
                            move = Move(
                                from_pos=from_pos,
                                to_pos=(to_row, to_col),
                                piece=piece,
                                captured_piece=target_piece,
                                move_type=move_type
                            )
                            moves.append(move)
        
        return moves
    
    def _evaluate_move(self, move: Move) -> Optional[Recommendation]:
        """评估单个走法
        
        Args:
            move: 要评估的走法
            
        Returns:
            走法推荐，如果走法无效则返回None
        """
        if not self.current_board:
            return None
        
        # 模拟走法后的棋盘
        board_after_move = self._simulate_move(self.current_board, move)
        
        # 评估走法后的局面
        evaluation = self.position_evaluator.evaluate_position(
            board_after_move, self.player_color
        )
        
        # 计算相对于当前局面的改进
        current_evaluation = self.position_evaluator.evaluate_position(
            self.current_board, self.player_color
        )
        
        score_improvement = evaluation['total_score'] - current_evaluation['total_score']
        
        # 生成推荐理由
        reasoning = self._generate_move_reasoning(move, score_improvement, evaluation)
        
        # 计算置信度（基于分数改进和走法类型）
        confidence = self._calculate_move_confidence(move, score_improvement)
        
        return Recommendation(
            move=move,
            score=evaluation['total_score'],
            win_probability=evaluation['win_probability'],
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _simulate_move(self, board: List[List[Optional[str]]], move: Move) -> List[List[Optional[str]]]:
        """模拟执行走法后的棋盘状态
        
        Args:
            board: 当前棋盘
            move: 要执行的走法
            
        Returns:
            走法后的棋盘状态
        """
        new_board = copy.deepcopy(board)
        
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        # 移动棋子
        new_board[to_row][to_col] = new_board[from_row][from_col]
        new_board[from_row][from_col] = None
        
        return new_board
    
    def _generate_move_reasoning(self, move: Move, score_improvement: float, 
                                evaluation: Dict[str, float]) -> str:
        """生成走法推荐理由
        
        Args:
            move: 走法
            score_improvement: 分数改进
            evaluation: 局面评估
            
        Returns:
            推荐理由文本
        """
        reasoning_parts = []
        
        # 基于走法类型的理由
        if move.move_type == 'capture':
            piece_name = self.position_evaluator.piece_values.get(move.captured_piece, 0)
            reasoning_parts.append(f"吃掉对方{move.captured_piece}，获得子力优势")
        elif move.move_type == 'check':
            reasoning_parts.append("将军，迫使对方应对")
        
        # 基于分数改进的理由
        if score_improvement > 100:
            reasoning_parts.append("大幅改善局面")
        elif score_improvement > 50:
            reasoning_parts.append("明显改善局面")
        elif score_improvement > 0:
            reasoning_parts.append("略微改善局面")
        
        # 基于胜率的理由
        win_prob = evaluation['win_probability']
        if win_prob > 0.8:
            reasoning_parts.append("确立优势地位")
        elif win_prob > 0.6:
            reasoning_parts.append("获得优势")
        
        # 基于游戏阶段的理由
        if self.game_phase == 'opening':
            reasoning_parts.append("有利于开局发展")
        elif self.game_phase == 'endgame':
            reasoning_parts.append("适合残局走法")
        
        return "，".join(reasoning_parts) if reasoning_parts else "常规走法"
    
    def _calculate_move_confidence(self, move: Move, score_improvement: float) -> float:
        """计算走法推荐的置信度
        
        Args:
            move: 走法
            score_improvement: 分数改进
            
        Returns:
            置信度（0-1之间）
        """
        base_confidence = 0.5
        
        # 基于分数改进调整置信度
        if score_improvement > 100:
            base_confidence += 0.3
        elif score_improvement > 50:
            base_confidence += 0.2
        elif score_improvement > 0:
            base_confidence += 0.1
        
        # 基于走法类型调整置信度
        if move.move_type == 'capture':
            base_confidence += 0.1
        elif move.move_type == 'check':
            base_confidence += 0.15
        
        # 确保置信度在合理范围内
        return max(0.1, min(0.95, base_confidence))
    
    def _analyze_threats(self) -> List[str]:
        """分析当前局面的威胁
        
        Returns:
            威胁描述列表
        """
        threats = []
        
        if not self.current_board:
            return threats
        
        # 检查王是否受到威胁
        my_king_pos = self._find_king_position(self.current_board, self.player_color)
        if my_king_pos and self._is_king_under_attack(my_king_pos):
            threats.append("王受到威胁！")
        
        # 检查重要棋子是否受到威胁
        important_pieces = ['chariot', 'cannon', 'horse']
        for piece_type in important_pieces:
            threatened_pieces = self._find_threatened_pieces(piece_type)
            if threatened_pieces:
                threats.append(f"{piece_type}受到威胁")
        
        return threats
    
    def _analyze_opportunities(self) -> List[str]:
        """分析当前局面的机会
        
        Returns:
            机会描述列表
        """
        opportunities = []
        
        if not self.current_board:
            return opportunities
        
        # 检查是否可以攻击对方王
        opponent_king_pos = self._find_king_position(self.current_board, self.opponent_color)
        if opponent_king_pos and self._can_attack_king(opponent_king_pos):
            opportunities.append("可以攻击对方王！")
        
        # 检查是否有吃子机会
        capture_opportunities = self._find_capture_opportunities()
        if capture_opportunities:
            opportunities.extend(capture_opportunities)
        
        return opportunities
    
    def _find_king_position(self, board: List[List[Optional[str]]], color: str) -> Optional[Tuple[int, int]]:
        """找到指定颜色的王的位置
        
        Args:
            board: 棋盘状态
            color: 王的颜色
            
        Returns:
            王的位置，如果未找到则返回None
        """
        king_piece = f"{color}_king"
        
        for row in range(10):
            for col in range(9):
                if board[row][col] == king_piece:
                    return (row, col)
        
        return None
    
    def _is_king_under_attack(self, king_pos: Tuple[int, int]) -> bool:
        """检查王是否受到攻击
        
        Args:
            king_pos: 王的位置
            
        Returns:
            是否受到攻击
        """
        if not self.current_board:
            return False
        
        # 检查对方所有棋子是否能攻击到王
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece and self.opponent_color in piece:
                    if self._can_piece_attack_position((row, col), king_pos, piece):
                        return True
        
        return False
    
    def _can_piece_attack_position(self, piece_pos: Tuple[int, int], 
                                  target_pos: Tuple[int, int], piece: str) -> bool:
        """检查棋子是否能攻击目标位置
        
        Args:
            piece_pos: 棋子位置
            target_pos: 目标位置
            piece: 棋子类型
            
        Returns:
            是否能攻击到目标
        """
        # 简化的攻击检查，可以根据需要完善
        return self.move_detector._is_legal_move(piece_pos, target_pos, piece, self.current_board)
    
    def _can_attack_king(self, king_pos: Tuple[int, int]) -> bool:
        """检查是否可以攻击对方王
        
        Args:
            king_pos: 对方王的位置
            
        Returns:
            是否可以攻击
        """
        if not self.current_board:
            return False
        
        # 检查己方棋子是否能攻击到对方王
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece and self.player_color in piece:
                    if self._can_piece_attack_position((row, col), king_pos, piece):
                        return True
        
        return False
    
    def _find_threatened_pieces(self, piece_type: str) -> List[Tuple[int, int]]:
        """找到受威胁的指定类型棋子
        
        Args:
            piece_type: 棋子类型
            
        Returns:
            受威胁棋子的位置列表
        """
        threatened = []
        
        if not self.current_board:
            return threatened
        
        # 找到己方的该类型棋子
        my_piece_type = f"{self.player_color}_{piece_type}"
        
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece == my_piece_type:
                    # 检查是否受到威胁
                    if self._is_position_under_attack((row, col)):
                        threatened.append((row, col))
        
        return threatened
    
    def _is_position_under_attack(self, position: Tuple[int, int]) -> bool:
        """检查位置是否受到攻击
        
        Args:
            position: 要检查的位置
            
        Returns:
            是否受到攻击
        """
        if not self.current_board:
            return False
        
        # 检查对方棋子是否能攻击到该位置
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece and self.opponent_color in piece:
                    if self._can_piece_attack_position((row, col), position, piece):
                        return True
        
        return False
    
    def _find_capture_opportunities(self) -> List[str]:
        """寻找吃子机会
        
        Returns:
            吃子机会描述列表
        """
        opportunities = []
        
        if not self.current_board:
            return opportunities
        
        # 简化的吃子机会检测
        valuable_pieces = ['chariot', 'cannon', 'horse']
        
        for piece_type in valuable_pieces:
            opponent_piece_type = f"{self.opponent_color}_{piece_type}"
            
            # 寻找对方的该类型棋子
            for row in range(10):
                for col in range(9):
                    piece = self.current_board[row][col]
                    if piece == opponent_piece_type:
                        # 检查是否可以吃掉
                        if self._can_capture_piece((row, col)):
                            opportunities.append(f"可以吃掉对方{piece_type}")
        
        return opportunities
    
    def _can_capture_piece(self, target_pos: Tuple[int, int]) -> bool:
        """检查是否可以吃掉目标位置的棋子
        
        Args:
            target_pos: 目标位置
            
        Returns:
            是否可以吃掉
        """
        if not self.current_board:
            return False
        
        # 检查己方棋子是否能攻击到目标位置
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece and self.player_color in piece:
                    if self._can_piece_attack_position((row, col), target_pos, piece):
                        return True
        
        return False
    
    def get_game_summary(self) -> str:
        """获取游戏状态摘要
        
        Returns:
            游戏状态摘要文本
        """
        if not self.analysis_history:
            return "暂无分析数据"
        
        latest_analysis = self.analysis_history[-1]
        evaluation = latest_analysis.current_evaluation
        
        summary = f"游戏阶段: {self.game_phase}\n"
        summary += f"走法数: {self.move_count}\n"
        summary += self.position_evaluator.get_evaluation_summary(evaluation)
        
        if latest_analysis.threats:
            summary += f"\n威胁: {', '.join(latest_analysis.threats)}"
        
        if latest_analysis.opportunities:
            summary += f"\n机会: {', '.join(latest_analysis.opportunities)}"
        
        return summary
    
    def reset_game(self):
        """重置游戏状态"""
        self.move_detector.clear_history()
        self.current_board = None
        self.game_phase = 'opening'
        self.move_count = 0
        self.analysis_history.clear()