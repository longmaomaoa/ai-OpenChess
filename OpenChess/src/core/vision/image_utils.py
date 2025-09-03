#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理工具 - Image Processing Utilities
提供通用的图像处理和计算机视觉功能
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageEnhance
import pyautogui


class ImageUtils:
    """图像处理工具类"""
    
    @staticmethod
    def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """截取屏幕图像
        
        Args:
            region: 截取区域 (x, y, width, height)，None表示全屏
            
        Returns:
            np.ndarray: BGR格式的图像数组
        """
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        # 转换PIL图像到OpenCV格式
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray, 
                            brightness: float = 1.2,
                            contrast: float = 1.3,
                            sharpness: float = 1.5) -> np.ndarray:
        """增强图像质量
        
        Args:
            image: 输入图像
            brightness: 亮度增强因子
            contrast: 对比度增强因子
            sharpness: 锐度增强因子
            
        Returns:
            np.ndarray: 增强后的图像
        """
        # 转换为PIL图像进行增强
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # 亮度增强
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(brightness)
        
        # 对比度增强  
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(contrast)
        
        # 锐度增强
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(sharpness)
        
        # 转换回OpenCV格式
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def detect_chess_board(image: np.ndarray, 
                          min_area: int = 50000) -> Optional[Tuple[int, int, int, int]]:
        """检测象棋棋盘区域
        
        Args:
            image: 输入图像
            min_area: 最小棋盘面积阈值
            
        Returns:
            Optional[Tuple[int, int, int, int]]: 棋盘区域 (x, y, width, height)
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        
        # 形态学操作连接断开的线条
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 寻找最大的矩形轮廓
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
                
            # 轮廓近似
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 检查是否为四边形
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # 检查长宽比是否合理（象棋棋盘接近正方形）
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:
                    return (x, y, w, h)
        
        return None
    
    @staticmethod
    def extract_grid_cells(image: np.ndarray, 
                          board_region: Tuple[int, int, int, int],
                          rows: int = 10, 
                          cols: int = 9) -> List[List[np.ndarray]]:
        """从棋盘区域提取网格单元格
        
        Args:
            image: 输入图像
            board_region: 棋盘区域 (x, y, width, height)
            rows: 行数
            cols: 列数
            
        Returns:
            List[List[np.ndarray]]: 二维数组，包含每个网格单元格的图像
        """
        x, y, w, h = board_region
        board_image = image[y:y+h, x:x+w]
        
        cell_height = h // rows
        cell_width = w // cols
        
        cells = []
        for row in range(rows):
            cell_row = []
            for col in range(cols):
                cell_y = row * cell_height
                cell_x = col * cell_width
                cell = board_image[cell_y:cell_y+cell_height, cell_x:cell_x+cell_width]
                cell_row.append(cell)
            cells.append(cell_row)
        
        return cells
    
    @staticmethod
    def preprocess_piece_image(image: np.ndarray) -> np.ndarray:
        """预处理棋子图像用于识别
        
        Args:
            image: 棋子图像
            
        Returns:
            np.ndarray: 预处理后的图像
        """
        # 调整大小到标准尺寸
        resized = cv2.resize(image, (64, 64))
        
        # 高斯模糊减少噪声
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        
        # 增强对比度
        enhanced = ImageUtils.enhance_image_quality(blurred, contrast=1.5)
        
        return enhanced
    
    @staticmethod
    def template_match(image: np.ndarray, 
                      template: np.ndarray, 
                      threshold: float = 0.7) -> Tuple[bool, float, Tuple[int, int]]:
        """模板匹配
        
        Args:
            image: 输入图像
            template: 模板图像
            threshold: 匹配阈值
            
        Returns:
            Tuple[bool, float, Tuple[int, int]]: (是否匹配, 置信度, 匹配位置)
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image
            
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
        
        # 模板匹配
        result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        is_match = max_val >= threshold
        return is_match, max_val, max_loc
    
    @staticmethod
    def color_segment(image: np.ndarray, 
                     color_ranges: List[Dict]) -> np.ndarray:
        """基于HSV颜色范围进行图像分割
        
        Args:
            image: 输入图像 (BGR格式)
            color_ranges: 颜色范围列表，每个元素包含'lower'和'upper'键
            
        Returns:
            np.ndarray: 分割后的掩码图像
        """
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 创建合并掩码
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for color_range in color_ranges:
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        return combined_mask
    
    @staticmethod
    def draw_grid_overlay(image: np.ndarray, 
                         board_region: Tuple[int, int, int, int],
                         rows: int = 10, 
                         cols: int = 9) -> np.ndarray:
        """在图像上绘制网格覆盖层
        
        Args:
            image: 输入图像
            board_region: 棋盘区域
            rows: 行数
            cols: 列数
            
        Returns:
            np.ndarray: 带有网格的图像
        """
        result = image.copy()
        x, y, w, h = board_region
        
        # 计算网格线位置
        for i in range(rows + 1):
            line_y = y + (i * h // rows)
            cv2.line(result, (x, line_y), (x + w, line_y), (0, 255, 0), 1)
        
        for i in range(cols + 1):
            line_x = x + (i * w // cols)
            cv2.line(result, (line_x, y), (line_x, y + h), (0, 255, 0), 1)
        
        return result