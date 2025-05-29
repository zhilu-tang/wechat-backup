import os

def export_directory_tree(base_dir, output_file="directory_tree.txt"):
    """
    导出指定目录的完整目录树结构到 txt 文件，末级目录下输出文件类型计数数据。
    
    :param base_dir: 需要导出目录树的根目录
    :param output_file: 输出的 txt 文件路径
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(base_dir):
            level = root.replace(base_dir, "").count(os.sep)
            indent = " " * 4 * (level)
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            # 统计文件类型计数
            file_type_counts = {}
            for file in files:
                _, ext = os.path.splitext(file)
                file_type_counts[ext] = file_type_counts.get(ext, 0) + 1
            
            # 输出文件类型计数
            subindent = " " * 4 * (level + 1)
            for ext, count in file_type_counts.items():
                f.write(f"{subindent}{ext}: {count}\n")

if __name__ == "__main__":
    home_dir = os.path.expanduser("~")
    # 指定需要导出目录树的根目录
    base_dir = os.getenv("WECHAT_DIR", os.path.join(home_dir, "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/"))

    # 导出目录树到 txt 文件
    export_directory_tree(base_dir)
    print(f"目录树已成功导出到 {os.path.abspath('directory_tree.txt')}")