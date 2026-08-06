@echo off
chcp 65001 >nul
echo ========================================
echo   UviLUX (Wails) 构建脚本
echo ========================================
echo.

REM 检查 Go 是否安装
where go >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Go，请先安装 Go 1.21+
    echo 下载地址: https://go.dev/dl/
    pause
    exit /b 1
)

REM 检查 wails 是否安装
where wails >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [提示] 安装 Wails CLI...
    go install github.com/wailsapp/wails/v2/cmd/wails@latest
)

echo [1/2] 更新 Go 依赖...
go mod tidy
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 依赖更新失败
    pause
    exit /b 1
)

echo [2/2] 编译 uvilux.exe...
wails build -ldflags="-s -w" -platform windows/amd64
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 编译失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   构建完成！
echo.
echo   可执行文件: build\bin\uvilux.exe
echo.
echo   直接将 build\bin\uvilux.exe 复制到任意
echo   Windows 10/11 电脑即可运行（无需安装
echo   Python 或任何运行时）。
echo ========================================
pause
