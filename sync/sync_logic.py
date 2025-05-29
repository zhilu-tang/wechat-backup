import json
import os
import hashlib
import shutil

from .config_store import get_config, set_config, get_file_hash, set_file_hash

def save_hash(file_path, file_hash):
    """保存文件的 MD5 哈希值"""
    set_file_hash(file_path, file_hash)

def get_file_md5(file_path):
    """获取文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_duplicate(file_path):
    """检查文件是否重复"""
    file_hash = get_file_hash(file_path)
    if file_hash:
        return True
    save_hash(file_path, get_file_md5(file_path))
    return False

def match_directory_rule(file_path, include_dirs, exclude_dirs):
    """
    判断文件路径是否符合目录规则。
    :param file_path: 文件路径
    :param include_dirs: 包含规则列表
    :param exclude_dirs: 排除规则列表
    :return: 是否匹配规则
    """
    if not include_dirs:
        return True
    
    file_dirs = os.path.abspath(file_path).split(os.sep)
    
    for include_dir in include_dirs:
        if include_dir in file_dirs:
            for exclude_dir in exclude_dirs:
                if exclude_dir in file_dirs:
                    return False
            return True
    
    return False

def should_backup(file_path):
    """判断文件是否需要备份"""
    file_types = json.loads(get_config("file_types", '[".jpg", ".png", ".mp4", ".mov"]'))

    if not any(file_path.endswith(ext.strip()) for ext in file_types):
        print(f"跳过非备份文件类型: {file_path}")
        return False
    
    return True

def backup_file(src_path, target_dir, base_wechat_dir):
    """
    统一处理文件备份逻辑，包括去重和日志输出。
    :param src_path: 源文件路径
    :param target_dir: 备份目标目录
    :param base_wechat_dir: WeChat 文件夹的根目录
    """
    filename = os.path.basename(src_path)
    relative_path = os.path.relpath(os.path.dirname(src_path), base_wechat_dir)
    target_subdir = os.path.join(target_dir, relative_path)
    
    if not should_backup(src_path):
        print(f"跳过不符合备份条件的文件: {filename}")
        return
    
    if is_duplicate(src_path):
        print(f"跳过重复文件: {filename}")
        return
    
    # 确保只有在需要备份文件时才创建目录
    os.makedirs(target_subdir, exist_ok=True)
    target_path = os.path.join(target_subdir, filename)
    
    try:
        shutil.copy2(src_path, target_path)
        print(f"已备份文件: {filename} -> {target_path}")
    except Exception as e:
        print(f"备份文件 {filename} 时出错: {e}")

def process_directory_matched(source_dir, target_dir, base_wechat_dir):
    """
    递归处理符合条件的子文件夹。
    :param source_dir: 当前处理的源目录
    :param target_dir: 备份目标目录
    :param base_wechat_dir: WeChat 文件夹的根目录
    """
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)

        if os.path.isdir(item_path):
            process_directory_matched(item_path, target_dir, base_wechat_dir)
        else:
            backup_file(item_path, target_dir, base_wechat_dir)

def process_directory(root, target_dir, base_wechat_dir):
    """
    递归处理符合条件的子文件夹。
    :param root: 当前处理的根目录
    :param target_dir: 备份目标目录
    :param config: 配置信息
    :param base_wechat_dir: WeChat 文件夹的根目录
    """
    include_dirs = json.loads(get_config("include_dirs", "[]"))
    exclude_dirs = json.loads(get_config("exclude_dirs", "[]"))

    for item in os.listdir(root):
        item_path = os.path.join(root, item)
        
        if os.path.isdir(item_path):
            if match_directory_rule(item_path, include_dirs, exclude_dirs):
                process_directory_matched(item_path, target_dir, base_wechat_dir)
            else:
                process_directory(item_path, target_dir, base_wechat_dir)
                print(f"跳过不符合目录规则的子文件夹: {item_path}")