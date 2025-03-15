@echo off
echo 正在启动Python注册表组件清理工具...
echo 请注意，此操作需要管理员权限

:: 运行Python脚本
python "%~dp0注册表清理工具.py"

echo.
echo 如果没有看到脚本输出，可能是因为需要管理员权限
echo 请右键点击此批处理文件，选择"以管理员身份运行"
echo.
pause
