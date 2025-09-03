@echo off
chcp 65001 >nul
title 中国象棋智能助手

:: 切换到项目根目录
cd /d "%~dp0\.."

echo 🏯========================================🏯
echo           中国象棋智能助手 v3.2
echo     Chinese Chess Intelligent Assistant  
echo 🏯========================================🏯
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.7或更高版本
    echo 📥 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装，检查版本...
python --version

:start
echo.
echo 📋 请选择运行模式：
echo 1. 📦 安装依赖包
echo 2. 🖥️  运行GUI版本 (推荐)
echo 3. 💻 运行控制台版本
echo 4. 🔧 运行区域选择工具
echo 5. 🔍 调试模式
echo 6. ❌ 退出
echo.

set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto console
if "%choice%"=="4" goto region
if "%choice%"=="5" goto debug
if "%choice%"=="6" goto exit
goto invalid

:install
echo.
echo 📦 开始安装依赖包...
python scripts/install_requirements.py
echo.
echo ✅ 安装完成！
pause
goto start

:gui
echo.
echo 🚀 启动GUI版本...
python main.py --mode gui
goto start

:console
echo.
echo 🚀 启动控制台版本...
python main.py --mode console
goto start

:region
echo.
echo 🚀 启动区域选择工具...
python main.py --mode region-selector
goto start

:debug
echo.
echo 🔍 启动调试模式GUI版本...
python main.py --mode gui --debug
goto start

:invalid
echo.
echo ❌ 无效选择，请重新输入
goto start

:exit
echo.
echo 👋 再见！
timeout /t 2 >nul
exit /b 0