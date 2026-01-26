@echo off
chcp 65001 >nul
echo ========================================
echo   Kafka Explorer 打包脚本
echo ========================================
echo.

REM 检查 PyInstaller 是否安装
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo [INFO] 开始打包...
echo.

REM 使用 spec 文件打包
pyinstaller --clean build.spec

if errorlevel 1 (
    echo.
    echo [ERROR] 打包失败!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成!
echo   输出文件: dist\KafkaExplorer.exe
echo ========================================
echo.
pause

