#!/bin/bash

# 检查是否已安装 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 使用 PyInstaller 打包脚本
echo "正在打包 wechat_backup.py..."
pyinstaller --onefile --name=wechat-backup \
    --paths /Users/markus/dev/code/workspace/lingma/swe-design/sync \
    wechat_backup.py

# 将打包后的可执行文件移动到 /usr/local/bin
if [ -f "dist/wechat-backup" ]; then
    sudo cp dist/wechat-backup /usr/local/bin/
    echo "安装完成，您现在可以使用 'wechat-backup' 命令运行程序。"
else
    echo "打包失败，请检查 PyInstaller 是否正确安装。"
fi