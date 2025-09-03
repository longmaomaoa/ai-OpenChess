#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证棋盘尺寸计算 - 确保10x9棋盘完整可见
"""

def validate_board_dimensions():
    """验证棋盘尺寸计算"""
    print("=== 中国象棋棋盘尺寸验证 ===")
    
    # 新的尺寸参数
    canvas_width = 720
    canvas_height = 800
    margin = 60
    cell_size = 65
    
    print(f"画布尺寸: {canvas_width} x {canvas_height}")
    print(f"边距: {margin}, 格子大小: {cell_size}")
    
    # 计算棋盘实际占用空间
    # 中国象棋: 9列 x 10行
    board_width = 8 * cell_size + 2 * margin  # 8个间隔 + 两侧边距
    board_height = 9 * cell_size + 2 * margin  # 9个间隔 + 上下边距
    
    print(f"棋盘实际尺寸: {board_width} x {board_height}")
    
    # 检查是否适合
    width_fit = canvas_width >= board_width
    height_fit = canvas_height >= board_height
    
    print(f"宽度适合: {'是' if width_fit else '否'} ({canvas_width} >= {board_width})")
    print(f"高度适合: {'是' if height_fit else '否'} ({canvas_height} >= {board_height})")
    
    if width_fit and height_fit:
        print("结论: 棋盘完全适合画布，10x9网格将完整可见")
        
        # 计算剩余空间
        width_margin = canvas_width - board_width
        height_margin = canvas_height - board_height
        print(f"剩余空间: 宽 {width_margin}px, 高 {height_margin}px")
        
        return True
    else:
        print("警告: 棋盘可能超出画布边界")
        return False

def calculate_piece_positions():
    """计算棋子位置范围"""
    print("\n=== 棋子位置计算 ===")
    
    margin = 60
    cell_size = 65
    start_x = margin
    start_y = margin
    
    # 棋子位置范围
    min_x = start_x + 0 * cell_size
    max_x = start_x + 8 * cell_size
    min_y = start_y + 0 * cell_size
    max_y = start_y + 9 * cell_size
    
    print(f"棋子X坐标范围: {min_x} - {max_x}")
    print(f"棋子Y坐标范围: {min_y} - {max_y}")
    
    # 棋子半径（最大）
    piece_radius = 22
    
    print(f"棋子半径: {piece_radius}px")
    print(f"棋子实际占用X范围: {min_x - piece_radius} - {max_x + piece_radius}")
    print(f"棋子实际占用Y范围: {min_y - piece_radius} - {max_y + piece_radius}")
    
    return (min_x - piece_radius, max_x + piece_radius, 
            min_y - piece_radius, max_y + piece_radius)

if __name__ == "__main__":
    print("中国象棋智能助手 - 棋盘尺寸验证")
    print("-" * 40)
    
    # 验证尺寸
    size_ok = validate_board_dimensions()
    
    # 计算位置
    x_min, x_max, y_min, y_max = calculate_piece_positions()
    
    print(f"\n=== 最终验证 ===")
    canvas_width = 720
    canvas_height = 800
    
    fits_width = x_min >= 0 and x_max <= canvas_width
    fits_height = y_min >= 0 and y_max <= canvas_height
    
    print(f"所有元素在画布X范围内: {'是' if fits_width else '否'}")
    print(f"所有元素在画布Y范围内: {'是' if fits_height else '否'}")
    
    if size_ok and fits_width and fits_height:
        print("\n结论: 配置正确，完整10x9中国象棋棋盘将完全可见")
    else:
        print("\n警告: 配置可能有问题，部分内容可能不可见")