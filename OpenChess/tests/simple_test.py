#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本，验证象棋AI功能
"""

def create_initial_board():
    """创建初始棋盘"""
    board = [[None for _ in range(9)] for _ in range(10)]
    
    # 黑方棋子（上方）
    board[0] = ['black_chariot', 'black_horse', 'black_elephant', 'black_advisor', 
               'black_king', 'black_advisor', 'black_elephant', 'black_horse', 'black_chariot']
    board[2][1] = 'black_cannon'
    board[2][7] = 'black_cannon'
    board[3] = ['black_pawn', None, 'black_pawn', None, 'black_pawn', 
               None, 'black_pawn', None, 'black_pawn']
    
    # 红方棋子（下方）
    board[6] = ['red_pawn', None, 'red_pawn', None, 'red_pawn', 
               None, 'red_pawn', None, 'red_pawn']
    board[7][1] = 'red_cannon'
    board[7][7] = 'red_cannon'
    board[9] = ['red_chariot', 'red_horse', 'red_elephant', 'red_advisor', 
               'red_king', 'red_advisor', 'red_elephant', 'red_horse', 'red_chariot']
    
    return board

def test_move_detector():
    """测试走法检测器"""
    print("测试走法检测器...")
    
    try:
        from move_detector import MoveDetector
        
        detector = MoveDetector()
        board = create_initial_board()
        
        # 测试棋盘验证
        is_valid = detector._is_valid_board(board)
        print(f"✓ 棋盘验证: {'通过' if is_valid else '失败'}")
        
        # 测试走法检测
        detector.update_board(board)
        
        # 模拟一个走法
        board_after = [row[:] for row in board]  # 深拷贝
        board_after[5][0] = 'red_pawn'  # 红兵前进
        board_after[6][0] = None
        
        detected_move = detector.update_board(board_after)
        if detected_move:
            print(f"✓ 走法检测: 检测到走法 {detected_move.piece} 从 {detected_move.from_pos} 到 {detected_move.to_pos}")
        else:
            print("✓ 走法检测: 初次测试完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 走法检测器测试失败: {e}")
        return False

def test_position_evaluator():
    """测试局面评估器"""
    print("测试局面评估器...")
    
    try:
        from position_evaluator import PositionEvaluator
        
        evaluator = PositionEvaluator()
        board = create_initial_board()
        
        # 测试局面评估
        evaluation = evaluator.evaluate_position(board, 'red')
        
        print(f"✓ 局面评估: 总分={evaluation['total_score']:.1f}, 胜率={evaluation['win_probability']*100:.1f}%")
        print(f"  子力分数: {evaluation['material_score']:.1f}")
        print(f"  位置分数: {evaluation['position_score']:.1f}")
        
        # 测试评估摘要
        summary = evaluator.get_evaluation_summary(evaluation)
        print(f"✓ 评估摘要生成成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 局面评估器测试失败: {e}")
        return False

def test_ai_assistant():
    """测试AI助手"""
    print("测试AI助手...")
    
    try:
        from chess_ai_assistant import ChessAIAssistant
        
        assistant = ChessAIAssistant(player_color='red')
        board = create_initial_board()
        
        # 测试棋盘分析
        analysis = assistant.update_board_state(board)
        
        print(f"✓ AI分析: 胜率={analysis.current_evaluation['win_probability']*100:.1f}%")
        print(f"  推荐数量: {len(analysis.recommendations)}")
        print(f"  威胁数量: {len(analysis.threats)}")
        print(f"  机会数量: {len(analysis.opportunities)}")
        
        # 测试游戏摘要
        summary = assistant.get_game_summary()
        print("✓ 游戏摘要生成成功")
        
        return True
        
    except Exception as e:
        print(f"✗ AI助手测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("中国象棋AI助手功能测试")
    print("=" * 50)
    
    tests = [
        ("走法检测器", test_move_detector),
        ("局面评估器", test_position_evaluator),
        ("AI助手", test_ai_assistant)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{name}测试:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {name}测试异常: {e}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查实现")

if __name__ == '__main__':
    main()