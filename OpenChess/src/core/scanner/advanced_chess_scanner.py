#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能对弈助手 - 高级扫描模块
使用模板匹配和颜色识别技术，提高棋子识别准确性
支持AI助手模块进行智能分析和走法推荐
"""

import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import os
import json
from PIL import Image, ImageDraw, ImageFont
import threading
from typing import Dict, List, Tuple, Optional
import colorsys

class AdvancedChessScanner:
    """中国象棋智能对弈助手 - 高级扫描器类
    
    提供更精确的棋子识别功能，支持模板匹配和颜色识别
    上方棋子识别为对手，下方棋子识别为玩家
    """
    
    def __init__(self):
        """初始化高级扫描器"""
        self.board_size = (9, 10)  # 中国象棋棋盘大小：9列10行
        
        # 自定义扫描区域 (x, y, width, height)
        self.custom_scan_region = None
        
        # 配置Tesseract OCR
        self._configure_tesseract()
        
        # 棋子定义
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
        
        # 颜色范围定义（HSV格式）
        self.color_ranges = {
            'red': {
                'lower': np.array([0, 100, 100]),
                'upper': np.array([10, 255, 255])
            },
            'black': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 255, 30])
            }
        }
        
        # 棋盘位置映射
        self.board_positions = {}
        
        # 当前棋盘状态
        self.current_board = [[None for _ in range(9)] for _ in range(10)]
        
        # 游戏状态
        self.game_state = {
            'red_king_alive': True,
            'black_king_alive': True,
            'current_turn': 'red',
            'last_move': None
        }
        
        # 模板图片路径
        self.template_dir = "chess_templates"
        self.templates = {}
        self._ensure_template_dir()
        self._load_templates()
        
        # 配置
        self.confidence_threshold = 0.7
        self.min_piece_size = 20
        
        # OCR相关配置
        self.ocr_available = False
        self.chinese_ocr_available = False
    
    def set_scan_region(self, region: Optional[Tuple[int, int, int, int]]):
        """设置扫描区域
        
        Args:
            region: 扫描区域 (x, y, width, height)，None表示全屏扫描
        """
        # 只在区域实际改变时显示消息
        if region != self.custom_scan_region:
            self.custom_scan_region = region
            if region:
                x, y, w, h = region
                print(f"扫描区域已设置: {x}, {y}, {w}x{h}")
            else:
                print("扫描区域已重置为全屏")
        else:
            self.custom_scan_region = region
    
    def _configure_tesseract(self):
        """配置Tesseract OCR"""
        try:
            # 尝试设置Tesseract路径
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe", 
                r"C:\Tesseract-OCR\tesseract.exe"
            ]
            
            tesseract_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    tesseract_path = path
                    break
            
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print(f"Tesseract路径设置为: {tesseract_path}")
                
                # 测试基本OCR功能
                try:
                    # 创建一个小测试图像
                    import numpy as np
                    from PIL import Image
                    test_img = Image.fromarray(np.ones((50, 50), dtype=np.uint8) * 255)
                    pytesseract.image_to_string(test_img, lang='eng')
                    self.ocr_available = True
                    print("英文OCR功能正常")
                except Exception as e:
                    print(f"英文OCR测试失败: {e}")
                
                # 测试中文OCR功能
                try:
                    pytesseract.image_to_string(test_img, lang='chi_sim')
                    self.chinese_ocr_available = True
                    print("中文OCR功能正常")
                except Exception as e:
                    print(f"中文OCR不可用: {e}")
                    print("提示: 请安装中文语言包或使用模板匹配功能")
            else:
                print("未找到Tesseract安装，OCR功能将不可用")
                print("请从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装Tesseract")
                
        except Exception as e:
            print(f"配置Tesseract时出错: {e}")
        
    def _ensure_template_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            print(f"创建模板目录: {self.template_dir}")
            print("请将棋子模板图片放入此目录")
    
    def _load_templates(self):
        """加载模板图片"""
        if not os.path.exists(self.template_dir):
            return
        
        for filename in os.listdir(self.template_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_path = os.path.join(self.template_dir, filename)
                template_name = os.path.splitext(filename)[0]
                
                try:
                    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                    if template is not None:
                        self.templates[template_name] = template
                        print(f"加载模板: {template_name}")
                except Exception as e:
                    print(f"加载模板失败 {filename}: {e}")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """截取屏幕"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot_cv
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def detect_chess_board(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """检测棋盘位置"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用多种方法检测棋盘
        
        # 方法1: 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 方法2: 霍夫线变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # 分析直线分布，找到棋盘区域
            horizontal_lines = []
            vertical_lines = []
            
            for rho, theta in lines:
                if theta < np.pi/4 or theta > 3*np.pi/4:
                    vertical_lines.append(rho)
                else:
                    horizontal_lines.append(rho)
            
            if len(horizontal_lines) >= 8 and len(vertical_lines) >= 8:
                # 找到棋盘边界
                h_min, h_max = min(horizontal_lines), max(horizontal_lines)
                v_min, v_max = min(vertical_lines), max(vertical_lines)
                
                return (int(v_min), int(h_min), int(v_max-v_min), int(h_max-h_min))
        
        # 方法3: 轮廓检测
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        max_area = 0
        board_contour = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:
                    if area > max_area:
                        max_area = area
                        board_contour = approx
        
        if board_contour is not None:
            x, y, w, h = cv2.boundingRect(board_contour)
            return (x, y, w, h)
        
        return None
    
    def detect_piece_color(self, piece_image: np.ndarray) -> Optional[str]:
        """检测棋子颜色"""
        try:
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(piece_image, cv2.COLOR_BGR2HSV)
            
            # 检测红色
            red_mask = cv2.inRange(hsv, self.color_ranges['red']['lower'], self.color_ranges['red']['upper'])
            red_pixels = cv2.countNonZero(red_mask)
            
            # 检测黑色
            black_mask = cv2.inRange(hsv, self.color_ranges['black']['lower'], self.color_ranges['black']['upper'])
            black_pixels = cv2.countNonZero(black_mask)
            
            total_pixels = piece_image.shape[0] * piece_image.shape[1]
            
            # 计算颜色比例
            red_ratio = red_pixels / total_pixels
            black_ratio = black_pixels / total_pixels
            
            if red_ratio > 0.1:
                return 'red'
            elif black_ratio > 0.1:
                return 'black'
            
            return None
        except Exception as e:
            print(f"颜色检测失败: {e}")
            return None
    
    def template_match_piece(self, piece_image: np.ndarray) -> Optional[str]:
        """使用模板匹配识别棋子"""
        best_match = None
        best_confidence = 0
        
        for template_name, template in self.templates.items():
            try:
                # 调整模板大小
                resized_template = cv2.resize(template, (piece_image.shape[1], piece_image.shape[0]))
                
                # 模板匹配
                result = cv2.matchTemplate(piece_image, resized_template, cv2.TM_CCOEFF_NORMED)
                confidence = np.max(result)
                
                if confidence > best_confidence and confidence > self.confidence_threshold:
                    best_confidence = confidence
                    best_match = template_name
                    
            except Exception as e:
                continue
        
        return best_match
    
    def ocr_recognize_piece(self, piece_image: np.ndarray) -> Optional[str]:
        """使用OCR识别棋子"""
        if not self.ocr_available:
            return None
            
        try:
            # 图像预处理
            gray = cv2.cvtColor(piece_image, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 转换为PIL图像
            pil_image = Image.fromarray(binary)
            
            # OCR识别 - 根据可用语言包选择
            text = ""
            if self.chinese_ocr_available:
                # 首选中文OCR
                text = pytesseract.image_to_string(pil_image, lang='chi_sim', config='--psm 7')
            elif self.ocr_available:
                # 备用英文OCR（可能识别出拼音或形似字符）
                text = pytesseract.image_to_string(pil_image, lang='eng', config='--psm 7')
            
            text = text.strip()
            
            if text:
                # 匹配棋子类型
                result = self._match_piece_text(text)
                if result:
                    return result
            
            return None
            
        except Exception as e:
            if "chi_sim" in str(e):
                print(f"中文OCR识别失败: {e}")
                print("提示: 请安装中文语言包或使用模板匹配功能")
                # 标记中文OCR不可用，避免重复错误
                self.chinese_ocr_available = False
            else:
                print(f"OCR识别失败: {e}")
            return None
    
    def _match_piece_text(self, text: str) -> Optional[str]:
        """匹配识别文本到棋子类型"""
        # 直接匹配中文字符
        for color, pieces in self.pieces.items():
            for piece_name, piece_id in pieces.items():
                if piece_name in text:
                    return piece_id
        
        # 模糊匹配（处理识别错误）
        text_lower = text.lower()
        fuzzy_matches = {
            # 英文或拼音匹配
            'king': ['red_king', 'black_king'],
            'shuai': 'red_king',
            'jiang': 'black_king',
            'shi': ['red_advisor', 'black_advisor'],
            'xiang': ['red_elephant', 'black_elephant'],
            'ma': ['red_horse', 'black_horse'], 
            'che': ['red_chariot', 'black_chariot'],
            'pao': ['red_cannon', 'black_cannon'],
            'bing': 'red_pawn',
            'zu': 'black_pawn',
            # 形似字符匹配
            'H': ['red_king', 'black_king'],  # 帅/将 可能识别为H
            'E': ['red_advisor', 'black_advisor'],  # 仕/士 可能识别为E
            'X': ['red_elephant', 'black_elephant'],  # 相/象 可能识别为X
        }
        
        for pattern, matches in fuzzy_matches.items():
            if pattern in text_lower:
                if isinstance(matches, list):
                    # 返回第一个匹配，实际应用中可能需要更智能的选择
                    return matches[0]
                else:
                    return matches
        
        return None
    
    def recognize_piece(self, piece_image: np.ndarray) -> Optional[str]:
        """综合识别棋子"""
        # 方法1: 模板匹配
        template_result = self.template_match_piece(piece_image)
        if template_result:
            return template_result
        
        # 方法2: OCR识别
        ocr_result = self.ocr_recognize_piece(piece_image)
        if ocr_result:
            return ocr_result
        
        # 方法3: 颜色检测（作为辅助）
        color = self.detect_piece_color(piece_image)
        if color:
            # 如果只检测到颜色，返回通用标识
            return f"{color}_piece"
        
        return None
    
    def scan_board(self) -> List[List[Optional[str]]]:
        """扫描整个棋盘"""
        # 确定扫描区域
        if self.custom_scan_region:
            # 使用自定义区域
            board_region = self.custom_scan_region
            screenshot = self.capture_screen(board_region)
        else:
            # 全屏截图并检测棋盘
            screenshot = self.capture_screen()
            if screenshot is None:
                return self.current_board
            
            # 检测棋盘位置
            board_region = self.detect_chess_board(screenshot)
            if board_region is None:
                print("未检测到棋盘，使用默认区域")
                board_region = (100, 100, 540, 600)
        
        if screenshot is None:
            return self.current_board
        
        # 获取棋盘图像
        if self.custom_scan_region:
            # 自定义区域时，screenshot已经是棋盘区域
            board_image = screenshot
            x, y, w, h = board_region
        else:
            # 全屏扫描时，需要从截图中提取棋盘区域
            x, y, w, h = board_region
            board_image = screenshot[y:y+h, x:x+w]
        
        # 更新棋盘位置映射
        cell_width = w // 9
        cell_height = h // 10
        
        for row in range(10):
            for col in range(9):
                cell_x = x + col * cell_width
                cell_y = y + row * cell_height
                self.board_positions[(row, col)] = (cell_x, cell_y)
        
        # 扫描每个位置
        new_board = [[None for _ in range(9)] for _ in range(10)]
        
        for row in range(10):
            for col in range(9):
                cell_x, cell_y = self.board_positions[(row, col)]
                
                # 提取棋子图像
                piece_region = (
                    cell_x - cell_width//4,
                    cell_y - cell_height//4,
                    cell_width//2,
                    cell_height//2
                )
                
                piece_image = self.capture_screen(piece_region)
                if piece_image is not None and piece_image.size > 0:
                    piece_type = self.recognize_piece(piece_image)
                    new_board[row][col] = piece_type
        
        self.current_board = new_board
        return new_board
    
    def get_board_state(self) -> List[List[Optional[str]]]:
        """获取当前棋盘状态，供AI助手分析使用
        
        Returns:
            当前棋盘状态的二维列表
        """
        return self.current_board
    
    def check_win_condition(self) -> Optional[str]:
        """检查胜利条件（保留兼容性）
        
        注意：建议使用AI助手的智能分析功能获得更准确的局面判断
        """
        red_king_found = False
        black_king_found = False
        
        for row in range(10):
            for col in range(9):
                piece = self.current_board[row][col]
                if piece == 'red_king':
                    red_king_found = True
                elif piece == 'black_king':
                    black_king_found = True
        
        # 更新游戏状态
        self.game_state['red_king_alive'] = red_king_found
        self.game_state['black_king_alive'] = black_king_found
        
        # 判断胜负
        if not red_king_found:
            return 'black'  # 对手(上方)胜利
        elif not black_king_found:
            return 'red'    # 玩家(下方)胜利
        
        return None
    
    def display_board(self):
        """显示当前棋盘状态"""
        print("\n当前棋盘状态:")
        print("  " + " ".join([str(i) for i in range(9)]))
        print("-" * 20)
        
        for row in range(10):
            row_str = f"{row} "
            for col in range(9):
                piece = self.current_board[row][col]
                if piece is None:
                    row_str += "· "
                else:
                    if 'red' in piece:
                        row_str += "R "
                    elif 'black' in piece:
                        row_str += "B "
                    else:
                        row_str += "? "
            print(row_str)
    
    def show_winner(self, winner: str):
        """显示胜利者"""
        winner_text = "红方胜利！" if winner == 'red' else "黑方胜利！"
        
        try:
            pyautogui.alert(
                text=f"恭喜！{winner_text}",
                title="中国象棋胜负判定",
                button="确定"
            )
        except:
            print(f"\n🎉 {winner_text} 🎉")
    
    def create_template_from_screenshot(self, piece_name: str):
        """从截图创建模板（GUI版本）"""
        try:
            # 确保模板目录存在
            self._ensure_template_dir()
            
            # 获取当前鼠标位置
            pos = pyautogui.position()
            
            # 截取棋子区域（以鼠标位置为中心）
            piece_region = (pos[0]-30, pos[1]-30, 60, 60)
            piece_image = self.capture_screen(piece_region)
            
            if piece_image is not None:
                # 保存模板
                template_path = os.path.join(self.template_dir, f"{piece_name}.png")
                success = cv2.imwrite(template_path, piece_image)
                
                if success:
                    print(f"模板已保存: {template_path}")
                    # 重新加载模板
                    self._load_templates()
                    return True
                else:
                    raise Exception("保存模板图片失败")
            else:
                raise Exception("屏幕截图失败")
                
        except Exception as e:
            print(f"创建模板失败: {e}")
            raise e
    
    def calibrate_board(self):
        """校准棋盘位置"""
        print("棋盘校准模式")
        print("请将鼠标移动到棋盘左上角，然后按回车...")
        input()
        
        left_top = pyautogui.position()
        print(f"左上角坐标: {left_top}")
        
        print("请将鼠标移动到棋盘右下角，然后按回车...")
        input()
        
        right_bottom = pyautogui.position()
        print(f"右下角坐标: {right_bottom}")
        
        # 计算棋盘尺寸
        board_width = right_bottom[0] - left_top[0]
        board_height = right_bottom[1] - left_top[1]
        
        # 更新棋盘位置映射
        cell_width = board_width // 9
        cell_height = board_height // 10
        
        for row in range(10):
            for col in range(9):
                x = left_top[0] + col * cell_width
                y = left_top[1] + row * cell_height
                self.board_positions[(row, col)] = (x, y)
        
        print("棋盘校准完成！")
    
    def run_continuous_scan(self, interval: float = 2.0):
        """持续扫描棋盘"""
        print("开始持续扫描中国象棋棋盘...")
        print("按 Ctrl+C 停止扫描")
        
        try:
            while True:
                self.scan_board()
                self.display_board()
                
                winner = self.check_win_condition()
                if winner:
                    self.show_winner(winner)
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n扫描已停止")

def main():
    """主函数 - 高级扫描器演示
    
    注意：建议使用GUI版本或集成AI助手获得完整的智能对弈功能
    """
    print("中国象棋智能对弈助手 - 高级扫描器 v2.0")
    print("=" * 50)
    print("提示：此为高级扫描模块，完整功能请使用gui_chess_scanner.py")
    print("=" * 50)
    
    scanner = AdvancedChessScanner()
    
    while True:
        print("\n请选择操作:")
        print("1. 校准棋盘位置")
        print("2. 创建棋子模板")
        print("3. 单次扫描")
        print("4. 持续扫描（高级版）")
        print("5. 退出")
        
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            scanner.calibrate_board()
        elif choice == '2':
            piece_name = input("请输入棋子名称（如：red_king）: ").strip()
            if piece_name:
                scanner.create_template_from_screenshot(piece_name)
        elif choice == '3':
            scanner.scan_board()
            scanner.display_board()
            winner = scanner.check_win_condition()
            if winner:
                scanner.show_winner(winner)
        elif choice == '4':
            interval = input("请输入扫描间隔（秒，默认2秒）: ").strip()
            try:
                interval = float(interval) if interval else 2.0
            except ValueError:
                interval = 2.0
            scanner.run_continuous_scan(interval)
        elif choice == '5':
            print("再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
