@echo off
chcp 65001 >nul 2>&1
:: 强制切换到批处理文件所在目录（关键！）
cd /d "%~dp0"
echo ========================多区域地图编辑器========================
echo 📁 当前目录：%~dp0
echo 🔍 正在以管理员权限启动...
echo 🌐 启动后自动打开浏览器，请勿关闭此窗口！
echo ⚠️  关闭服务：按 Ctrl+C → 输入 Y → 回车
echo ===============================================================
echo.
:: 以管理员权限运行Python脚本（跳过360云盘锁）
powershell -Command "Start-Process python -ArgumentList '地图编辑.py' -WorkingDirectory '%~dp0' -Verb RunAs"