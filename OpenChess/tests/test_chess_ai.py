#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋AI助手测试模块
测试走法检测、局面评估和AI助手的各种功能
"""

import unittest
import copy
from typing import List, Optional

from move_detector import MoveDetector, Move
from position_evaluator import PositionEvaluator
from chess_ai_assistant import ChessAIAssistant

class TestChessAI(unittest.TestCase):
    """中国象棋AI功能测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.move_detector = MoveDetector()
        self.position_evaluator = PositionEvaluator()
        self.ai_assistant = ChessAIAssistant()
        
        # 创建一个标准的初始棋盘
        self.initial_board = self._create_initial_board()
        
        # 创建一个中局棋盘用于测试
        self.middle_game_board = self._create_middle_game_board()
        
    def _create_initial_board(self) -> List[List[Optional[str]]]:
        """创建标准的象棋初始棋盘
        
        Returns:
            初始棋盘状态
        """
        board = [[None for _ in range(9)] for _ in range(10)]
        
        # 黑方棋子（上方，第0-2行）
        board[0] = ['black_chariot', 'black_horse', 'black_elephant', 'black_advisor', 
                   'black_king', 'black_advisor', 'black_elephant', 'black_horse', 'black_chariot']
        board[2][1] = 'black_cannon'
        board[2][7] = 'black_cannon'
        board[3] = ['black_pawn', None, 'black_pawn', None, 'black_pawn', 
                   None, 'black_pawn', None, 'black_pawn']
        
        # 红方棋子（下方，第6-9行）
        board[6] = ['red_pawn', None, 'red_pawn', None, 'red_pawn', 
                   None, 'red_pawn', None, 'red_pawn']
        board[7][1] = 'red_cannon'
        board[7][7] = 'red_cannon'
        board[9] = ['red_chariot', 'red_horse', 'red_elephant', 'red_advisor', 
                   'red_king', 'red_advisor', 'red_elephant', 'red_horse', 'red_chariot']
        
        return board
    
    def _create_middle_game_board(self) -> List[List[Optional[str]]]:
        """创建一个中局棋盘状态用于测试
        
        Returns:
            中局棋盘状态
        """
        board = [[None for _ in range(9)] for _ in range(10)]
        
        # 简化的中局棋盘，只放置关键棋子
        board[0][4] = 'black_king'        # 黑将
        board[0][3] = 'black_advisor'     # 黑士
        board[2][1] = 'black_cannon'      # 黑炮
        board[4][5] = 'black_horse'       # 黑马
        board[5][2] = 'black_pawn'        # 过河黑卒
        
        board[9][4] = 'red_king'          # 红帅
        board[9][5] = 'red_advisor'       # 红仕
        board[7][7] = 'red_cannon'        # 红炮
        board[5][3] = 'red_horse'         # 红马
        board[4][6] = 'red_pawn'          # 过河红兵
        board[8][0] = 'red_chariot'       # 红车
        
        return board

class TestMoveDetector(TestChessAI):
    """走法检测器测试类"""
    
    def test_board_validation(self):
        """测试棋盘格式验证"""
        # 测试有效棋盘
        valid_board = self.initial_board
        result = self.move_detector._is_valid_board(valid_board)
        self.assertTrue(result, "有效棋盘应该通过验证")
        
        # 测试无效棋盘 - 错误的行数
        invalid_board_rows = [[None for _ in range(9)] for _ in range(8)]
        result = self.move_detector._is_valid_board(invalid_board_rows)
        self.assertFalse(result, "行数错误的棋盘应该验证失败")
        
        # 测试无效棋盘 - 错误的列数
        invalid_board_cols = [[None for _ in range(7)] for _ in range(10)]
        result = self.move_detector._is_valid_board(invalid_board_cols)
        self.assertFalse(result, "列数错误的棋盘应该验证失败")
    
    def test_simple_move_detection(self):
        """测试简单走法检测"""
        # 创建走法前后的棋盘状态
        board_before = copy.deepcopy(self.initial_board)
        board_after = copy.deepcopy(self.initial_board)
        
        # 模拟红兵从(6,0)移动到(5,0)
        board_after[5][0] = 'red_pawn'
        board_after[6][0] = None
        
        # 更新棋盘状态
        self.move_detector.update_board(board_before)
        detected_move = self.move_detector.update_board(board_after)
        
        # 验证检测到的走法
        self.assertIsNotNone(detected_move, "应该检测到走法")
        self.assertEqual(detected_move.from_pos, (6, 0), "起始位置应该正确")
        self.assertEqual(detected_move.to_pos, (5, 0), "目标位置应该正确")
        self.assertEqual(detected_move.piece, 'red_pawn', "移动的棋子应该正确")
        self.assertEqual(detected_move.move_type, 'normal', "走法类型应该是normal")
    
    def test_capture_move_detection(self):
        """测试吃子走法检测"""
        # 创建吃子场景
        board_before = copy.deepcopy(self.middle_game_board)
        board_after = copy.deepcopy(self.middle_game_board)
        
        # 模拟红车吃掉黑卒：红车从(8,0)到(5,2)
        board_after[5][2] = 'red_chariot'  # 红车移动到黑卒位置
        board_after[8][0] = None           # 红车原位置空出
        
        # 更新棋盘状态
        self.move_detector.update_board(board_before)
        detected_move = self.move_detector.update_board(board_after)
        
        # 验证检测到的吃子走法
        self.assertIsNotNone(detected_move, "应该检测到吃子走法")
        self.assertEqual(detected_move.from_pos, (8, 0), "起始位置应该正确")
        self.assertEqual(detected_move.to_pos, (5, 2), "目标位置应该正确")
        self.assertEqual(detected_move.piece, 'red_chariot', "移动的棋子应该正确")
        self.assertEqual(detected_move.captured_piece, 'black_pawn', "被吃的棋子应该正确")
        self.assertEqual(detected_move.move_type, 'capture', "走法类型应该是capture")
    
    def test_move_legality(self):
        """测试走法合法性验证"""
        # 测试合法的兵走法
        legal_pawn_move = self.move_detector._is_legal_move(
            (6, 0), (5, 0), 'red_pawn', self.initial_board
        )
        self.assertTrue(legal_pawn_move, "兵向前一格应该是合法走法")
        
        # 测试非法的兵走法（横走）
        illegal_pawn_move = self.move_detector._is_legal_move(
            (6, 0), (6, 1), 'red_pawn', self.initial_board
        )
        self.assertFalse(illegal_pawn_move, "兵横走应该是非法走法")
        
        # 测试车的走法
        test_board = copy.deepcopy(self.initial_board)
        test_board[8][0] = None  # 清空车前面的位置
        
        legal_chariot_move = self.move_detector._is_legal_move(
            (9, 0), (8, 0), 'red_chariot', test_board
        )
        self.assertTrue(legal_chariot_move, "车向前一格应该是合法走法")
    
    def test_king_move_validation(self):
        """测试帅/将走法验证"""
        # 测试帅在九宫内的合法走法
        legal_king_move = self.move_detector._is_legal_king_move(
            (9, 4), (8, 4), 'red_king', self.initial_board
        )
        self.assertTrue(legal_king_move, "帅在九宫内向前一格应该合法")
        
        # 测试帅出九宫的非法走法
        illegal_king_move = self.move_detector._is_legal_king_move(
            (9, 4), (9, 2), 'red_king', self.initial_board
        )
        self.assertFalse(illegal_king_move, "帅出九宫应该非法")
    
    def test_horse_move_validation(self):
        """测试马走法验证"""
        # 创建马可以自由移动的棋盘
        test_board = copy.deepcopy(self.initial_board)
        test_board[7][1] = None  # 清空马前面的兵
        
        # 测试合法的马走法
        legal_horse_move = self.move_detector._is_legal_horse_move(
            (9, 1), (7, 2), 'red_horse', test_board
        )
        self.assertTrue(legal_horse_move, "马走日字应该合法")
        
        # 测试马腿被蹩的情况
        blocked_horse_move = self.move_detector._is_legal_horse_move(
            (9, 1), (7, 0), 'red_horse', self.initial_board
        )
        self.assertFalse(blocked_horse_move, "马腿被蹩应该非法")

class TestPositionEvaluator(TestChessAI):
    """局面评估器测试类"""
    
    def test_material_evaluation(self):
        """测试子力价值评估"""
        # 测试初始局面的子力评估
        evaluation = self.position_evaluator.evaluate_position(self.initial_board, 'red')
        
        # 初始局面双方子力应该相等
        self.assertAlmostEqual(
            evaluation['material_score'], 0, delta=50,
            "初始局面双方子力价值应该基本相等"
        )
    
    def test_position_value_evaluation(self):
        """测试位置价值评估"""
        # 创建兵过河的情况
        test_board = copy.deepcopy(self.initial_board)
        test_board[4][0] = 'red_pawn'  # 红兵过河
        test_board[6][0] = None
        
        evaluation_before = self.position_evaluator.evaluate_position(self.initial_board, 'red')
        evaluation_after = self.position_evaluator.evaluate_position(test_board, 'red')
        
        # 兵过河后位置价值应该提高
        self.assertGreater(
            evaluation_after['position_score'], 
            evaluation_before['position_score'],
            "兵过河后位置价值应该提高"
        )
    
    def test_win_probability_calculation(self):
        """测试胜率计算"""
        # 测试均势局面
        evaluation = self.position_evaluator.evaluate_position(self.initial_board, 'red')
        win_prob = evaluation['win_probability']
        
        # 初始局面胜率应该接近50%
        self.assertGreater(win_prob, 0.4, "初始局面胜率不应该太低")
        self.assertLess(win_prob, 0.6, "初始局面胜率不应该太高")
        
        # 测试优势局面
        advantage_board = copy.deepcopy(self.middle_game_board)
        advantage_board[0][4] = None  # 移除黑将，模拟红方大优
        
        advantage_evaluation = self.position_evaluator.evaluate_position(advantage_board, 'red')
        advantage_prob = advantage_evaluation['win_probability']
        
        # 优势局面胜率应该很高
        self.assertGreater(advantage_prob, 0.8, "优势局面胜率应该很高")
    
    def test_king_safety_evaluation(self):
        """测试王安全性评估"""
        # 测试王周围有保护的情况
        safe_board = copy.deepcopy(self.initial_board)
        evaluation_safe = self.position_evaluator.evaluate_position(safe_board, 'red')
        
        # 测试王周围没有保护的情况
        unsafe_board = copy.deepcopy(self.initial_board)
        unsafe_board[9][3] = None  # 移除仕
        unsafe_board[9][5] = None  # 移除仕
        evaluation_unsafe = self.position_evaluator.evaluate_position(unsafe_board, 'red')
        
        # 有保护的王安全性应该更高
        self.assertGreater(
            evaluation_safe['king_safety_score'],
            evaluation_unsafe['king_safety_score'],
            "有保护的王安全性应该更高"
        )
    
    def test_position_comparison(self):
        """测试局面比较"""
        # 比较初始局面和中局局面
        comparison = self.position_evaluator.compare_positions(
            self.initial_board, self.middle_game_board, 'red'
        )
        
        # 验证比较结果包含必要信息
        self.assertIn('board1_evaluation', comparison)
        self.assertIn('board2_evaluation', comparison)
        self.assertIn('score_difference', comparison)
        self.assertIn('probability_difference', comparison)
        self.assertIn('is_improvement', comparison)
    
    def test_evaluation_summary(self):
        """测试评估结果摘要"""
        evaluation = self.position_evaluator.evaluate_position(self.initial_board, 'red')
        summary = self.position_evaluator.get_evaluation_summary(evaluation)
        
        # 验证摘要包含关键信息
        self.assertIn('局面评估', summary)
        self.assertIn('胜率', summary)
        self.assertIn('%', summary)

class TestChessAIAssistant(TestChessAI):
    """AI助手测试类"""
    
    def test_board_update_and_analysis(self):
        """测试棋盘更新和分析"""
        # 更新初始棋盘
        analysis = self.ai_assistant.update_board_state(self.initial_board)
        
        # 验证分析结果
        self.assertIsNotNone(analysis, "应该返回分析结果")
        self.assertIn('current_evaluation', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('threats', analysis)
        self.assertIn('opportunities', analysis)
    
    def test_move_generation(self):
        """测试走法生成"""
        # 设置棋盘状态
        self.ai_assistant.current_board = copy.deepcopy(self.initial_board)
        
        # 生成红方的所有合法走法
        moves = self.ai_assistant._generate_all_legal_moves(self.initial_board, 'red')
        
        # 验证生成了走法
        self.assertGreater(len(moves), 0, "应该生成至少一个走法")
        
        # 验证走法的格式
        for move in moves[:5]:  # 检查前5个走法
            self.assertIsInstance(move, Move, "应该是Move类型")
            self.assertEqual(len(move.from_pos), 2, "起始位置应该是二元组")
            self.assertEqual(len(move.to_pos), 2, "目标位置应该是二元组")
    
    def test_move_recommendation(self):
        """测试走法推荐"""
        # 更新棋盘并获取推荐
        analysis = self.ai_assistant.update_board_state(self.middle_game_board)
        recommendations = analysis.recommendations
        
        # 验证推荐结果
        if recommendations:  # 如果有推荐走法
            best_recommendation = recommendations[0]
            self.assertIsInstance(best_recommendation.move, Move)
            self.assertIsInstance(best_recommendation.score, (int, float))
            self.assertIsInstance(best_recommendation.win_probability, (int, float))
            self.assertIsInstance(best_recommendation.confidence, (int, float))
            self.assertIsInstance(best_recommendation.reasoning, str)
    
    def test_threat_analysis(self):
        """测试威胁分析"""
        # 创建有威胁的局面
        threat_board = copy.deepcopy(self.middle_game_board)
        threat_board[1][4] = 'black_chariot'  # 黑车威胁红帅
        
        self.ai_assistant.current_board = threat_board
        threats = self.ai_assistant._analyze_threats()
        
        # 验证威胁分析结果
        self.assertIsInstance(threats, list)
    
    def test_opportunity_analysis(self):
        """测试机会分析"""
        # 创建有机会的局面
        opportunity_board = copy.deepcopy(self.middle_game_board)
        opportunity_board[1][4] = 'black_horse'  # 黑马可以被吃
        
        self.ai_assistant.current_board = opportunity_board
        opportunities = self.ai_assistant._analyze_opportunities()
        
        # 验证机会分析结果
        self.assertIsInstance(opportunities, list)
    
    def test_game_phase_detection(self):
        """测试游戏阶段识别"""
        # 初始应该是开局
        self.assertEqual(self.ai_assistant.game_phase, 'opening')
        
        # 模拟多步走法后进入中局
        for i in range(12):
            self.ai_assistant.move_count = i
            self.ai_assistant._update_game_phase()
        
        self.assertEqual(self.ai_assistant.game_phase, 'middlegame')
    
    def test_game_summary(self):
        """测试游戏状态摘要"""
        # 更新棋盘状态
        self.ai_assistant.update_board_state(self.initial_board)
        
        # 获取游戏摘要
        summary = self.ai_assistant.get_game_summary()
        
        # 验证摘要内容
        self.assertIsInstance(summary, str)
        self.assertIn('游戏阶段', summary)
    
    def test_reset_functionality(self):
        """测试重置功能"""
        # 先进行一些操作
        self.ai_assistant.update_board_state(self.initial_board)
        self.ai_assistant.move_count = 10
        
        # 重置
        self.ai_assistant.reset_game()
        
        # 验证重置结果
        self.assertEqual(self.ai_assistant.move_count, 0)
        self.assertEqual(self.ai_assistant.game_phase, 'opening')
        self.assertIsNone(self.ai_assistant.current_board)

class TestIntegration(TestChessAI):
    """集成测试类"""
    
    def test_complete_game_scenario(self):
        """测试完整的游戏场景"""
        # 1. 初始化游戏
        ai_assistant = ChessAIAssistant(player_color='red')
        
        # 2. 设置初始棋盘
        analysis1 = ai_assistant.update_board_state(self.initial_board)
        self.assertIsNotNone(analysis1)
        
        # 3. 模拟对手走法
        board_after_opponent_move = copy.deepcopy(self.initial_board)
        board_after_opponent_move[3][0] = None      # 黑卒消失
        board_after_opponent_move[4][0] = 'black_pawn'  # 黑卒前进
        
        # 4. 更新棋盘并获取建议
        analysis2 = ai_assistant.update_board_state(board_after_opponent_move)
        
        # 5. 验证AI检测到了对手的走法
        self.assertIsNotNone(analysis2.opponent_last_move)
        self.assertEqual(analysis2.opponent_last_move.piece, 'black_pawn')
        
        # 6. 验证AI提供了推荐走法
        self.assertGreater(len(analysis2.recommendations), 0)
    
    def test_performance_benchmark(self):
        """测试性能基准"""
        import time
        
        # 测试局面评估性能
        start_time = time.time()
        for _ in range(10):
            self.position_evaluator.evaluate_position(self.middle_game_board, 'red')
        evaluation_time = time.time() - start_time
        
        # 评估应该在合理时间内完成
        self.assertLess(evaluation_time, 1.0, "10次局面评估应该在1秒内完成")
        
        # 测试走法生成性能
        start_time = time.time()
        for _ in range(5):
            self.ai_assistant._generate_all_legal_moves(self.middle_game_board, 'red')
        move_generation_time = time.time() - start_time
        
        # 走法生成应该在合理时间内完成
        self.assertLess(move_generation_time, 2.0, "5次走法生成应该在2秒内完成")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效棋盘输入
        invalid_board = [[None for _ in range(8)] for _ in range(8)]  # 错误尺寸
        
        with self.assertRaises(ValueError):
            self.move_detector.update_board(invalid_board)
        
        # 测试空棋盘
        empty_board = [[None for _ in range(9)] for _ in range(10)]
        
        # 空棋盘应该能正常处理但不会有推荐
        analysis = self.ai_assistant.update_board_state(empty_board)
        self.assertEqual(len(analysis.recommendations), 0)

def run_comprehensive_tests():
    """运行全面的测试套件"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestMoveDetector,
        TestPositionEvaluator, 
        TestChessAIAssistant,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()

def run_specific_test_demo():
    """运行特定的测试演示"""
    print("中国象棋AI助手功能演示")
    print("="*50)
    
    # 创建AI助手
    ai_assistant = ChessAIAssistant(player_color='red')
    
    # 创建测试棋盘
    test_board = TestChessAI()._create_middle_game_board()
    
    print("\\n1. 初始棋盘分析:")
    analysis = ai_assistant.update_board_state(test_board)
    
    print(f"当前胜率: {analysis.current_evaluation['win_probability']*100:.1f}%")
    print(f"局面评分: {analysis.current_evaluation['total_score']:.1f}")
    
    if analysis.recommendations:
        print(f"\\n2. 推荐走法 (共{len(analysis.recommendations)}个):")
        for i, rec in enumerate(analysis.recommendations[:3], 1):
            move_str = ai_assistant.move_detector.format_move(rec.move)
            print(f"  {i}. {move_str}")
            print(f"     胜率: {rec.win_probability*100:.1f}%, 置信度: {rec.confidence*100:.1f}%")
            print(f"     理由: {rec.reasoning}")
    
    if analysis.threats:
        print(f"\\n3. 威胁分析:")
        for threat in analysis.threats:
            print(f"  - {threat}")
    
    if analysis.opportunities:
        print(f"\\n4. 机会分析:")
        for opportunity in analysis.opportunities:
            print(f"  - {opportunity}")
    
    print(f"\\n5. 游戏摘要:")
    print(ai_assistant.get_game_summary())

if __name__ == '__main__':
    print("中国象棋AI助手测试程序")
    print("="*50)
    print("1. 运行全面测试")
    print("2. 运行功能演示") 
    print("3. 退出")
    
    while True:
        choice = input("\\n请选择 (1-3): ").strip()
        
        if choice == '1':
            print("\\n开始运行全面测试...")
            success = run_comprehensive_tests()
            if success:
                print("\\n✅ 所有测试通过！")
            else:
                print("\\n❌ 部分测试失败，请检查上述错误信息")
        
        elif choice == '2':
            print("\\n开始运行功能演示...")
            try:
                run_specific_test_demo()
                print("\\n✅ 功能演示完成！")
            except Exception as e:
                print(f"\\n❌ 演示过程中出现错误: {e}")
        
        elif choice == '3':
            print("\\n再见！")
            break
        
        else:
            print("\\n无效选择，请重新输入")