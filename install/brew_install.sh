#!/bin/bash

# 检查是否已安装 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 使用 PyInstaller 打包脚本，显式指定模块路径
pyinstaller --onefile --name=wechat-backup \
    wechat_backup.py
pyinstaller --onefile --name=wechat-backup-manage \
    --paths $(pwd)/sync \
    sync/manage_rules.py

echo "安装完成！"