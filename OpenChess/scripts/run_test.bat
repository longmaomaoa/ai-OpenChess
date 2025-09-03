@echo off
chcp 65001 >nul
title 中国象棋AI测试

echo ========================================
echo           中国象棋AI功能测试
echo ========================================
echo.

python --version
echo.

echo 开始测试...
python simple_test.py

echo.
echo 测试完成！
pause