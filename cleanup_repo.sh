#!/bin/bash

# 安装 git-filter-repo（如果尚未安装）
pip install git-filter-repo

# 运行 git-filter-repo 来删除涉及二进制文件的提交
git filter-repo --strip-blobs-bigger-than 10M

# 强制推送修改后的历史记录到远程仓库
git push --force