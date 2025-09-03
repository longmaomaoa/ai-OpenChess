#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区域选择工具 - 支持用户自定义扫描区域
提供类似截图软件的拖拽框选功能，用于多棋盘对弈场景
"""

import tkinter as tk
from tkinter import ttk
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Tuple, Optional, Callable
import threading
import json
import os

class RegionSelector:
    """区域选择工具类
    
    提供全屏覆盖的区域选择界面，用户可以拖拽选择棋盘区域
    支持区域预览、保存和加载功能
    """
    
    def __init__(self, callback: Optional[Callable] = None):
        """初始化区域选择器
        
        Args:
            callback: 选择完成后的回调函数，接收(x, y, width, height)参数
        """
        self.callback = callback
        self.selected_region = None
        self.selecting = False
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        
        # 配置文件路径
        self.config_file = "scan_regions.json"
        
        # GUI组件
        self.root = None
        self.canvas = None
        self.screenshot_image = None
        self.photo_image = None
        self.original_image = None
        self.clear_images = []  # 存储清晰区域图像的引用
        self.background_image = None
        self._image_refs = []  # 保持对图像对象的强引用，防止被垃圾回收
        
    def _cleanup_resources(self):
        """清理之前的资源，防止重复使用时的冲突"""
        try:
            # 清理图像引用
            self._image_refs.clear()
            self.clear_images.clear()
            
            # 重置图像对象
            self.photo_image = None
            self.original_image = None
            self.background_image = None
            
            # 清理Tkinter窗口（如果存在）
            if hasattr(self, 'root') and self.root:
                try:
                    self.root.destroy()
                except:
                    pass  # 忽略窗口已销毁的错误
                self.root = None
                self.canvas = None
            
            # 重置状态变量
            self.selecting = False
            self.start_x = 0
            self.start_y = 0
            self.end_x = 0
            self.end_y = 0
            
        except Exception as e:
            print(f"清理资源时出错: {e}")
        
    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """启动区域选择界面
        
        Returns:
            选择的区域坐标 (x, y, width, height)，如果取消则返回None
        """
        try:
            # 首先清理之前的资源
            self._cleanup_resources()
            
            self.selected_region = None
            
            # 截取整个屏幕
            try:
                screenshot = pyautogui.screenshot()
                if screenshot is None:
                    print("截图失败: 返回None")
                    return None
                    
                # 转换为OpenCV格式
                screenshot_array = np.array(screenshot)
                if screenshot_array.size == 0:
                    print("截图失败: 空数组")
                    return None
                    
                self.screenshot_image = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
                
            except Exception as e:
                print(f"截图失败: {e}")
                return None
            
            # 创建全屏选择界面
            try:
                self._create_selection_window()
            except Exception as e:
                print(f"创建选择窗口失败: {e}")
                self._cleanup_resources()
                return None
            
            return self.selected_region
            
        except Exception as e:
            print(f"区域选择过程失败: {e}")
            try:
                self._cleanup_resources()
            except:
                pass  # 清理失败也不抛出异常
            return None
    
    def _create_selection_window(self):
        """创建全屏选择窗口"""
        try:
            # 确保之前的窗口已清理
            if hasattr(self, 'root') and self.root:
                try:
                    self.root.destroy()
                except:
                    pass
            
            # 创建全新的窗口和组件
            self.root = tk.Tk()
            self.root.title("选择扫描区域")
            
            # 设置全屏并使用半透明效果
            try:
                self.root.attributes('-fullscreen', True)
                self.root.attributes('-topmost', True)
                self.root.attributes('-alpha', 0.8)  # 设置透明度
            except Exception as e:
                print(f"设置窗口属性失败: {e}")
                # 继续使用普通窗口
                
            self.root.configure(bg='gray20')  # 改为深灰色而不是纯黑
            
            # 获取屏幕尺寸
            try:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                if screen_width <= 0 or screen_height <= 0:
                    screen_width, screen_height = 1920, 1080  # 默认值
            except Exception as e:
                print(f"获取屏幕尺寸失败: {e}")
                screen_width, screen_height = 1920, 1080  # 默认值
            
            # 创建画布
            try:
                self.canvas = tk.Canvas(
                    self.root, 
                    width=screen_width, 
                    height=screen_height,
                    highlightthickness=0,
                    bg='gray30'  # 使用深灰色背景
                )
                self.canvas.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                print(f"创建画布失败: {e}")
                raise
            
            # 显示截图
            try:
                self._display_screenshot()
            except Exception as e:
                print(f"显示截图失败: {e}")
                # 继续，即使截图显示失败
            
            # 绑定事件
            try:
                # 绑定鼠标事件
                self.canvas.bind("<Button-1>", self._on_mouse_press)
                self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
                self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
                
                # 绑定键盘事件
                self.root.bind("<Escape>", self._on_escape)
                self.root.bind("<Return>", self._on_enter)
                
                # 添加说明文字
                self._add_instructions()
                
                # 聚焦到窗口
                self.root.focus_set()
                
            except Exception as e:
                print(f"绑定事件失败: {e}")
                # 继续执行
            
            # 设置异常处理器
            self.root.report_callback_exception = self._handle_tk_exception
            
            # 开始事件循环
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"主循环异常: {e}")
                self._cleanup_resources()
                
        except Exception as e:
            print(f"创建选择窗口失败: {e}")
            raise
    
    def _handle_tk_exception(self, exc, val, tb):
        """处理Tkinter异常，防止应用程序崩溃"""
        import traceback
        try:
            print(f"Tkinter异常: {exc.__name__}: {val}")
            if tb and hasattr(tb, 'tb_frame'):
                print("".join(traceback.format_tb(tb)))
            else:
                print(f"异常详情: {str(val)}")
        except Exception as e:
            print(f"处理异常时出错: {e}")
        # 不重新抛出异常，让程序继续运行
    
    def _display_screenshot(self):
        """在画布上显示带磨砂蒙版效果的截图"""
        try:
            # 验证必要的组件和数据
            if not self.canvas or not hasattr(self, 'screenshot_image') or self.screenshot_image is None:
                print("显示截图失败: 画布或截图数据无效")
                self._fallback_background()
                return
            
            # 清理旧的图像引用
            self._image_refs.clear()
            self.clear_images.clear()
            
            # 安全地获取屏幕尺寸
            try:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                if screen_width <= 0 or screen_height <= 0:
                    screen_width, screen_height = 1920, 1080
            except:
                screen_width, screen_height = 1920, 1080
            
            # 转换为PIL图像
            try:
                screenshot_rgb = cv2.cvtColor(self.screenshot_image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(screenshot_rgb)
            except Exception as e:
                print(f"图像格式转换失败: {e}")
                self._fallback_background()
                return
            
            # 调整图像尺寸以适应屏幕
            try:
                pil_image = pil_image.resize((screen_width, screen_height), Image.LANCZOS)
            except Exception as e:
                print(f"图像尺寸调整失败: {e}")
                self._fallback_background()
                return
            
            # 创建蒙版效果
            try:
                # 添加磨砂蒙版效果（模糊处理）
                from PIL import ImageFilter, ImageEnhance
                blurred_image = pil_image.filter(ImageFilter.GaussianBlur(radius=3))
                
                # 降低亮度和对比度创建蒙版效果
                enhancer = ImageEnhance.Brightness(blurred_image)
                dimmed_image = enhancer.enhance(0.4)  # 降低亮度到40%
                
                enhancer = ImageEnhance.Contrast(dimmed_image)
                final_image = enhancer.enhance(0.7)  # 降低对比度到70%
                
            except Exception as e:
                print(f"图像特效处理失败，使用原始图像: {e}")
                final_image = pil_image
            
            # 转换为Tkinter可用的格式
            try:
                self.photo_image = ImageTk.PhotoImage(final_image)
                self.original_image = ImageTk.PhotoImage(pil_image)  # 保存原始图像供清晰显示用
                
                # 保持对图像的强引用，防止垃圾回收
                self._image_refs.extend([self.photo_image, self.original_image])
                
                # 在画布上显示蒙版图像
                self.background_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
                
            except Exception as e:
                print(f"创建Tkinter图像失败: {e}")
                self._fallback_to_basic_image(pil_image, screen_width, screen_height)
                
        except Exception as e:
            print(f"显示截图过程失败: {e}")
            self._fallback_background()
    
    def _fallback_to_basic_image(self, pil_image, screen_width, screen_height):
        """尝试显示基本图像（无特效）"""
        try:
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self._image_refs.append(self.photo_image)
            self.background_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            print("已使用基本图像显示")
        except Exception as e2:
            print(f"创建基本图像失败: {e2}")
            self._fallback_background()
    
    def _fallback_background(self):
        """创建简单的背景色（最后的备用方案）"""
        try:
            if self.canvas:
                self.canvas.configure(bg='#333333')
                print("已使用纯色背景")
        except:
            print("设置背景色也失败")
    
    def _add_instructions(self):
        """添加美化的使用说明"""
        # 精美的半透明背景框
        self.canvas.create_rectangle(
            20, 20, 450, 120, 
            fill='#2a2a2a', 
            outline='#ffffff',
            width=2
        )
        
        # 内边框
        self.canvas.create_rectangle(
            25, 25, 445, 115, 
            fill='', 
            outline='#cccccc',
            width=1
        )
        
        # 标题
        self.canvas.create_text(
            235, 40,
            text="区域选择器",
            fill='#ffaa00',
            font=('Microsoft YaHei', 14, 'bold'),
            anchor=tk.CENTER
        )
        
        # 说明文字
        instructions = [
            "▶ 拖拽鼠标选择棋盘区域",
            "▶ 按 Enter 键确认选择",
            "▶ 按 Esc 键取消选择"
        ]
        
        for i, text in enumerate(instructions):
            self.canvas.create_text(
                35, 60 + i * 20,
                text=text,
                fill='#ffffff',
                font=('Microsoft YaHei', 11),
                anchor=tk.W
            )
    
    def _on_mouse_press(self, event):
        """鼠标按下事件"""
        self.selecting = True
        self.start_x = event.x
        self.start_y = event.y
        self.end_x = event.x
        self.end_y = event.y
        
        # 清除之前的选择框 - with validation
        if self._validate_canvas_state():
            self.canvas.delete("selection")
    
    def _on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if not self.selecting:
            return
        
        self.end_x = event.x
        self.end_y = event.y
        
        # 清除之前的选择框 - with validation
        if self._validate_canvas_state():
            self.canvas.delete("selection")
        
        # 绘制新的选择框
        self._draw_selection_rect()
    
    def _on_mouse_release(self, event):
        """鼠标释放事件"""
        if not self.selecting:
            return
        
        self.selecting = False
        self.end_x = event.x
        self.end_y = event.y
        
        # 绘制最终选择框
        self._draw_selection_rect()
    
    def _draw_selection_rect(self):
        """绘制选择矩形并显示清晰区域"""
        try:
            # 计算矩形坐标
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            # 验证坐标合理性
            if x2 - x1 < 10 or y2 - y1 < 10:
                return  # 选择区域太小，不处理
            
            # 首先清除之前的清晰区域
            if self._validate_canvas_state():
                self.canvas.delete("clear_area")
            
            # 安全地显示清晰区域
            self._safely_display_clear_area(x1, y1, x2, y2)
            
        except Exception as e:
            print(f"绘制选择矩形失败: {e}")
            # 即使失败也要绘制基本的选择框
            try:
                self._draw_basic_selection_rect()
            except:
                pass  # 如果连基本绘制都失败，就忽略
    

    def _validate_canvas_state(self):
        """CRITICAL FIX: 验证画布和窗口状态是否有效"""
        try:
            # Check if root window exists and is valid
            if not hasattr(self, 'root') or not self.root:
                return False
            
            # Check if canvas exists and is valid
            if not hasattr(self, 'canvas') or not self.canvas:
                return False
                
            # Try to access canvas properties to ensure it's still alive
            try:
                _ = self.canvas.winfo_exists()
                if not _:
                    return False
            except tk.TclError:
                # Canvas has been destroyed
                return False
                
            # Try to access root window to ensure it's still alive
            try:
                _ = self.root.winfo_exists()
                if not _:
                    return False
            except tk.TclError:
                # Root window has been destroyed
                return False
                
            return True
            
        except Exception:
            # Any exception means the state is invalid
            return False

    def _safely_display_clear_area(self, x1, y1, x2, y2):
        """安全地显示清晰区域"""
        try:
            # CRITICAL FIX: Add comprehensive validation before proceeding
            if not self._validate_canvas_state():
                return
                
            # 检查必要条件
            if not (hasattr(self, 'original_image') and self.original_image and 
                   hasattr(self, 'screenshot_image') and self.screenshot_image is not None):
                return
            
            # 验证截图图像的有效性
            if not hasattr(self.screenshot_image, 'shape') or len(self.screenshot_image.shape) != 3:
                return
                
            img_height, img_width = self.screenshot_image.shape[:2]
            
            # 边界检查和调整
            x1 = max(0, min(x1, img_width - 1))
            y1 = max(0, min(y1, img_height - 1))
            x2 = max(x1 + 1, min(x2, img_width))
            y2 = max(y1 + 1, min(y2, img_height))
            
            # 确保区域大小合理
            if (x2 - x1) < 5 or (y2 - y1) < 5:
                return
            
            # CRITICAL FIX: Double-check canvas validity before image operations
            if not self._validate_canvas_state():
                return
            
            # 安全地裁剪图像
            clear_region = self.screenshot_image[y1:y2, x1:x2].copy()
            
            if clear_region.size > 0 and clear_region.shape[0] > 0 and clear_region.shape[1] > 0:
                # 转换颜色空间
                clear_rgb = cv2.cvtColor(clear_region, cv2.COLOR_BGR2RGB)
                
                # 创建PIL图像
                clear_pil = Image.fromarray(clear_rgb)
                
                # CRITICAL FIX: Final validation before creating PhotoImage
                if not self._validate_canvas_state():
                    return
                
                # 创建Tkinter图像
                clear_photo = ImageTk.PhotoImage(clear_pil)
                
                # CRITICAL FIX: Validate one more time before canvas operation
                if self._validate_canvas_state():
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=clear_photo, tags="clear_area")
                    
                    # 保存图像引用防止垃圾回收
                    self.clear_images.append(clear_photo)
                    self._image_refs.append(clear_photo)
                    
        except Exception as e:
            # CRITICAL FIX: Don't print the error if it's a known image reference issue
            if "doesn't exist" not in str(e) and "pyimage" not in str(e).lower():
                print(f"显示清晰区域失败: {e}")
            # 不抛出异常，继续执行
            
        # 绘制选择框 - only if canvas is still valid
        if self._validate_canvas_state():
            self._draw_selection_borders(x1, y1, x2, y2)

    def _draw_basic_selection_rect(self):
        """绘制基本的选择矩形（出错时的备用方案）"""
        try:
            if not hasattr(self, 'start_x') or not hasattr(self, 'canvas') or not self.canvas:
                return
                
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)  
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            # 简单的红色边框
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='red',
                width=2,
                tags="selection"
            )
        except:
            pass  # 静默失败
    
    def _draw_selection_borders(self, x1, y1, x2, y2):
        """绘制精美的选择框边框"""
        try:
            # CRITICAL FIX: Validate canvas state before drawing
            if not self._validate_canvas_state():
                return
                
            # 外边框（深色）
            self.canvas.create_rectangle(
                x1-2, y1-2, x2+2, y2+2,
                outline='#ff4444',
                width=3,
                tags="selection"
            )
            
            # 内边框（亮色）
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='#ffaaaa',
                width=1,
                tags="selection"
            )
            
            # 绘制角落标记
            corner_size = 8
            for corner_x, corner_y in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
                self.canvas.create_rectangle(
                    corner_x - corner_size//2, corner_y - corner_size//2,
                    corner_x + corner_size//2, corner_y + corner_size//2,
                    fill='#ff4444', outline='white', width=1,
                    tags="selection"
                )
            
            # 绘制尺寸信息
            width = x2 - x1
            height = y2 - y1
            size_text = f"{width} x {height}"
            
            # 背景框
            self.canvas.create_rectangle(
                x1, y1 - 25, x1 + len(size_text) * 8 + 10, y1 - 5,
                fill='black', outline='white', width=1,
                tags="selection"
            )
            
            # 文字
            self.canvas.create_text(
                x1 + 5, y1 - 15,
                text=size_text,
                fill='white',
                font=('Arial', 11, 'bold'),
                anchor=tk.W,
                tags="selection"
            )
        except Exception as e:
            print(f"绘制选择框边框失败: {e}")
    
    def _on_escape(self, event):
        """Esc键取消选择"""
        self.selected_region = None
        self._close_window()
    
    def _on_enter(self, event):
        """Enter键确认选择"""
        if hasattr(self, 'start_x') and hasattr(self, 'end_x'):
            # 计算最终选择区域
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            width = x2 - x1
            height = y2 - y1
            
            # 验证选择区域大小
            if width < 50 or height < 50:
                print("选择区域太小，请重新选择")
                return
            
            self.selected_region = (x1, y1, width, height)
            
            # 调用回调函数
            if self.callback:
                self.callback(self.selected_region)
        
        self._close_window()
    
    def _close_window(self):
        """安全地关闭窗口并清理资源"""
        try:
            if hasattr(self, 'root') and self.root:
                self.root.destroy()
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
        finally:
            # 确保清理完成
            self.root = None
            self.canvas = None
    
    def save_region(self, name: str, region: Tuple[int, int, int, int]):
        """保存区域配置
        
        Args:
            name: 区域名称
            region: 区域坐标 (x, y, width, height)
        """
        try:
            # 加载现有配置
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 添加新区域
            config[name] = {
                'x': region[0],
                'y': region[1],
                'width': region[2],
                'height': region[3]
            }
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"区域 '{name}' 已保存")
            
        except Exception as e:
            print(f"保存区域配置失败: {e}")
    
    def load_region(self, name: str) -> Optional[Tuple[int, int, int, int]]:
        """加载区域配置
        
        Args:
            name: 区域名称
            
        Returns:
            区域坐标 (x, y, width, height)，如果不存在则返回None
        """
        try:
            if not os.path.exists(self.config_file):
                return None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if name not in config:
                return None
            
            region_config = config[name]
            return (
                region_config['x'],
                region_config['y'],
                region_config['width'],
                region_config['height']
            )
            
        except Exception as e:
            print(f"加载区域配置失败: {e}")
            return None
    
    def get_saved_regions(self) -> list:
        """获取所有已保存的区域名称
        
        Returns:
            区域名称列表
        """
        try:
            if not os.path.exists(self.config_file):
                return []
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return list(config.keys())
            
        except Exception as e:
            print(f"获取保存区域列表失败: {e}")
            return []
    
    def preview_region(self, region: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """预览选择的区域
        
        Args:
            region: 区域坐标 (x, y, width, height)
            
        Returns:
            区域截图的OpenCV图像
        """
        try:
            x, y, width, height = region
            region_screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return cv2.cvtColor(np.array(region_screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"预览区域失败: {e}")
            return None

def main():
    """测试区域选择工具"""
    def on_region_selected(region):
        print(f"选择的区域: {region}")
        
        # 预览选择的区域
        selector = RegionSelector()
        preview = selector.preview_region(region)
        if preview is not None:
            cv2.imshow("区域预览", preview)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
    
    print("区域选择工具测试")
    print("请拖拽选择一个区域...")
    
    selector = RegionSelector(callback=on_region_selected)
    result = selector.select_region()
    
    if result:
        print(f"最终选择: {result}")
        # 保存测试区域
        selector.save_region("测试区域", result)
    else:
        print("取消选择")

if __name__ == "__main__":
    main()