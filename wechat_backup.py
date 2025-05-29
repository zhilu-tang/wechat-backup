import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sync.sync_logic import process_directory
from sync.config_store import get_config, set_config
import logging

def check_folder_permission(folder_path):
    """
    检查脚本是否具有访问指定文件夹的权限。
    :param folder_path: 需要检查权限的文件夹路径
    :return: 是否具有访问权限
    """
    try:
        os.listdir(folder_path)
        return True
    except PermissionError:
        return False

class WeChatBackupHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_dir, base_wechat_dir):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.base_wechat_dir = base_wechat_dir

    def on_created(self, event):
        if event.is_directory:
            return
        src_path = event.src_path
        process_directory(os.path.dirname(src_path), self.target_dir, self.base_wechat_dir)

def main():
    home_dir = os.path.expanduser("~")
    base_wechat_dir = os.getenv("WECHAT_DIR", os.path.join(home_dir, "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/"))
    backup_dir = os.path.join(home_dir, "WeChatBackup")
    
    if not os.path.exists(base_wechat_dir):
        print(f"未找到 WeChat 文件夹，请检查路径: {base_wechat_dir}")
        return
    
    os.makedirs(backup_dir, exist_ok=True)

    if not check_folder_permission(base_wechat_dir):
        print(f"权限错误：脚本无法访问 WeChat 文件夹 {base_wechat_dir}。")
        print("请按照以下步骤授予权限：")
        print("1. 打开 '系统偏好设置' -> '安全性与隐私' -> '隐私' -> '完全磁盘访问'。")
        print("2. 点击锁图标以解锁设置，然后输入您的密码。")
        print("3. 添加 Python 解释器（例如 /usr/bin/python3）到完全磁盘访问列表中。")
        print("4. 重新运行脚本。")
        return

    is_first_run = get_config("is_first_run", "True").lower() == "true"

    if is_first_run:
        print("首次启动，开始全量同步...")
        try:
            process_directory(base_wechat_dir, backup_dir, base_wechat_dir)
        except PermissionError as e:
            logging.error(f"权限错误：无法访问目录 {base_wechat_dir}，请检查权限设置。错误详情: {e}")
        except Exception as e:
            logging.error(f"全量同步过程中发生未知错误: {e}", exc_info=True)

        set_config("is_first_run", "False")
        print("全量同步完成。")

    event_handler = WeChatBackupHandler(base_wechat_dir, backup_dir, base_wechat_dir)
    observer = Observer()
    observer.schedule(event_handler, base_wechat_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()