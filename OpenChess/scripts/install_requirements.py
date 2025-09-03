#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋智能对弈助手安装脚本
自动安装所需的依赖包和配置环境
支持扫描识别、AI分析和智能推荐功能
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ 安装 {package} 失败")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ 需要Python 3.7或更高版本")
        return False
    print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_opencv():
    """安装OpenCV"""
    print("正在安装OpenCV...")
    return install_package("opencv-python")

def install_pyautogui():
    """安装PyAutoGUI"""
    print("正在安装PyAutoGUI...")
    return install_package("pyautogui")

def install_pytesseract():
    """安装Pytesseract"""
    print("正在安装Pytesseract...")
    return install_package("pytesseract")

def install_pillow():
    """安装Pillow"""
    print("正在安装Pillow...")
    return install_package("pillow")

def install_numpy():
    """安装NumPy"""
    print("正在安装NumPy...")
    return install_package("numpy")

def check_tesseract():
    """检查Tesseract是否安装"""
    try:
        import pytesseract
        # 尝试获取版本信息
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract已安装，版本: {version}")
        return True
    except Exception as e:
        print("✗ Tesseract未安装或配置不正确")
        print("请按照以下步骤安装Tesseract:")
        
        system = platform.system().lower()
        if system == "windows":
            print("Windows安装步骤:")
            print("1. 下载Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            print("2. 安装到默认路径: C:\\Program Files\\Tesseract-OCR")
            print("3. 将安装路径添加到系统PATH环境变量")
            print("4. 重启命令行窗口")
        elif system == "darwin":  # macOS
            print("macOS安装步骤:")
            print("1. 安装Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. 安装Tesseract: brew install tesseract")
        else:  # Linux
            print("Linux安装步骤:")
            print("Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
            print("CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi-sim")
        
        return False

def create_config_file():
    """创建配置文件"""
    config_content = """# 中国象棋智能对弈助手配置文件

# Tesseract路径配置（Windows用户需要设置）
# TESSERACT_PATH = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# 扫描配置
SCAN_INTERVAL = 2.0  # 扫描间隔（秒）
CONFIDENCE_THRESHOLD = 0.7  # 模板匹配置信度阈值

# 棋盘配置
BOARD_WIDTH = 9  # 棋盘宽度（列数）
BOARD_HEIGHT = 10  # 棋盘高度（行数）

# AI助手配置
PLAYER_COLOR = 'red'  # 玩家颜色（red=红方/下方，black=黑方/上方）
AI_SEARCH_DEPTH = 3   # AI搜索深度
MAX_RECOMMENDATIONS = 5  # 最大推荐走法数

# 颜色配置（HSV格式）
RED_COLOR_RANGE = {
    'lower': [0, 100, 100],
    'upper': [10, 255, 255]
}

BLACK_COLOR_RANGE = {
    'lower': [0, 0, 0],
    'upper': [180, 255, 30]
}
"""
    
    try:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✓ 配置文件已创建: config.py")
        return True
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
        return False

def create_readme():
    """创建README文件"""
    readme_content = """# 中国象棋智能对弈助手

这是一个基于计算机视觉和AI技术的中国象棋智能对弈助手，能够实时分析棋局并提供走法建议。

## 核心功能

### 🎯 智能分析
- 实时监控对手行动（屏幕上方为对手）
- AI分析局面并提供最佳走法推荐
- 动态计算胜率和局势变化
- 威胁检测和机会识别

### 🔍 视觉识别
- 自动检测棋盘位置和边界
- 精确识别棋子类型和颜色
- 支持模板匹配和OCR双重识别
- 自适应多种界面风格

### 💡 AI助手
- 多维度局面评估算法
- 智能走法生成和排序
- 实时胜率计算和趋势分析
- 个性化推荐理由说明

## 安装要求

- Python 3.7+
- OpenCV (计算机视觉)
- PyAutoGUI (屏幕截图)
- Pytesseract (OCR识别)
- Tesseract OCR引擎
- NumPy (数值计算)

## 快速开始

1. 运行安装脚本：
   ```bash
   python install_requirements.py
   ```

2. 启动GUI版本（推荐）：
   ```bash
   python gui_chess_scanner.py
   ```

3. 或使用命令行版本：
   ```bash
   python advanced_chess_scanner.py
   ```

## 使用流程

1. **校准棋盘** - 点击棋盘左上角和右下角进行定位
2. **启动AI助手** - 开始智能分析和监控
3. **获取建议** - 查看推荐走法和胜率分析
4. **实时监控** - AI持续分析对手走法并更新建议

## 界面说明

- **上方区域**：识别为对手（敌方）
- **下方区域**：识别为玩家（我方）
- **胜率显示**：实时计算当前胜率百分比
- **推荐走法**：AI建议的最佳走法及理由
- **局面分析**：威胁、机会和游戏状态

## 技术特色

- 🧠 **多模态AI分析**：结合子力价值、位置优势、王安全性等多个维度
- 🎯 **智能推荐系统**：提供走法建议、胜率预测和推荐理由
- 🔄 **实时响应**：2秒内完成扫描、分析和推荐的完整流程
- 🛡️ **鲁棒性强**：支持多种棋盘样式和光线条件

## 故障排除

### 识别问题
- 重新校准棋盘位置
- 调整屏幕亮度和对比度
- 创建自定义棋子模板

### 性能问题  
- 关闭不必要的后台程序
- 调整扫描间隔时间
- 检查内存使用情况

### AI功能问题
- 确保棋盘状态正确识别
- 检查是否正确检测到走法变化
- 重启AI助手功能

## 注意事项

⚠️ **重要提醒**：
- 本程序仅供学习和辅助分析使用
- 请遵守在线象棋平台的使用条款
- 建议在练习和学习场景中使用
"""
    
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✓ README文件已创建: README.md")
        return True
    except Exception as e:
        print(f"✗ 创建README文件失败: {e}")
        return False

def main():
    """主安装函数"""
    print("中国象棋智能对弈助手安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    print("\n开始安装依赖包...")
    
    # 安装Python包
    packages = [
        ("NumPy", install_numpy),
        ("OpenCV", install_opencv),
        ("PyAutoGUI", install_pyautogui),
        ("Pytesseract", install_pytesseract),
        ("Pillow", install_pillow)
    ]
    
    success_count = 0
    for name, installer in packages:
        if installer():
            success_count += 1
    
    print(f"\n依赖包安装完成: {success_count}/{len(packages)} 成功")
    
    # 检查Tesseract
    print("\n检查Tesseract...")
    tesseract_ok = check_tesseract()
    
    # 创建配置文件
    print("\n创建配置文件...")
    config_ok = create_config_file()
    
    # 创建README
    print("\n创建说明文档...")
    readme_ok = create_readme()
    
    # 总结
    print("\n" + "=" * 50)
    print("安装总结:")
    print(f"依赖包: {success_count}/{len(packages)} 成功")
    print(f"Tesseract: {'✓' if tesseract_ok else '✗'}")
    print(f"配置文件: {'✓' if config_ok else '✗'}")
    print(f"说明文档: {'✓' if readme_ok else '✗'}")
    
    if success_count == len(packages) and tesseract_ok:
        print("\n🎉 安装完成！可以运行程序了。")
        print("推荐使用GUI版本: python gui_chess_scanner.py")
        print("或命令行版本: python advanced_chess_scanner.py")
    else:
        print("\n⚠️  安装未完全成功，请检查上述问题。")
        if not tesseract_ok:
            print("请先安装Tesseract OCR引擎")

if __name__ == "__main__":
    main()
