# WeChat 图片和视频自动备份到系统盘扩展方案

## 目标
在 macOS 系统上，通过扩展 WeChat 的功能，实现用户发送和接收的图片和视频文件自动备份到系统指定的目录。

## 可行性分析
WeChat 是一个封闭的应用程序，没有公开的 API 或插件系统来直接扩展其功能。然而，我们可以通过以下方式实现自动备份：

1. **监控 WeChat 文件夹**：WeChat 在 macOS 上会将图片和视频存储在特定的文件夹中。我们可以通过监控这些文件夹的变化来实现自动备份。
2. **使用文件系统事件监听**：macOS 提供了文件系统事件监听机制（如 `FSEvents`），可以用来监控文件夹的变化。
3. **编写脚本或应用程序**：使用 Python 或其他脚本语言编写一个程序，监听 WeChat 文件夹的变化，并将新文件复制到目标备份目录。

## 实现步骤

### 1. 确定 WeChat 文件存储位置
WeChat 在 macOS 上的图片和视频文件通常存储在以下路径：

```
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/Media/
```
其中 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` 是用户的唯一标识符。

### 2. 创建备份目录
在系统盘上创建一个备份目录，例如：
```

/Users/用户名/WeChatBackup/
```
### 3. 编写监听脚本
使用 Python 编写一个脚本，监听 WeChat 文件夹的变化，并将新文件复制到备份目录。

```

python::/Users/markus/dev/code/workspace/lingma/swe-design/wechat_backup.py::d5dcff0d-d133-4e4a-8cfb-fdd74ffb70ca
```
### 4. 安装依赖
运行脚本前需要安装 `watchdog` 库，可以通过以下命令安装：
```

bash
pip install watchdog
```
### 5. 设置脚本为开机启动
为了确保脚本在系统启动时自动运行，可以将其添加到 macOS 的登录项中：
1. 打开“系统偏好设置” -> “用户与群组”。
2. 选择当前用户，点击“登录项”。
3. 点击“+”按钮，添加 Python 脚本的路径。

### 6. 测试和验证
运行脚本后，发送或接收图片和视频，检查备份目录是否正确生成了备份文件。

## 业务逻辑细节描述
以下是脚本的核心业务逻辑细节：

1. **文件类型过滤**：
   - 脚本通过配置文件 `config.json` 定义需要备份的文件类型（如 `.jpg`, `.png`, `.mp4`, `.mov`）。
   - 使用 `should_backup` 函数校验文件是否符合备份条件。

2. **目录规则匹配**：
   - 配置文件中支持定义包含规则（`include_dirs`）和排除规则（`exclude_dirs`）。
   - 使用 `match_directory_rule` 函数判断文件路径是否符合目录规则。

3. **重复文件检测**：
   - 使用文件的 MD5 哈希值检测文件是否重复。
   - 哈希值存储在 `config.json` 的 `hashes` 字段中，避免重复备份。

4. **动态目录结构匹配**：
   - 监听 WeChat 文件夹的变化时，动态匹配源目录结构并创建对应的备份目录。

5. **配置管理**：
   - 使用 `load_config` 和 `save_config` 函数加载和保存配置文件，统一管理文件类型、目录规则和哈希值。

6. **文件备份逻辑**：
   - 使用 `shutil.copy2` 将文件从源目录复制到目标备份目录。
   - 在复制前调用 `should_backup` 和 `is_duplicate` 函数确保文件符合备份条件且不重复。

## 技术功能清单描述
以下是脚本支持的技术功能清单：

1. **文件类型过滤**：
   - 支持通过配置文件定义需要备份的文件类型。
   - 动态加载和保存配置文件，确保灵活性。

2. **目录规则匹配**：
   - 支持包含规则和排除规则，灵活控制备份范围。
   - 动态匹配目录结构，确保备份目录与源目录一致。

3. **重复文件检测**：
   - 使用文件的 MD5 哈希值检测文件是否重复。
   - 避免重复备份，节省存储空间。

4. **动态目录结构匹配**：
   - 监听 WeChat 文件夹的变化时，动态匹配源目录结构并创建对应的备份目录。

5. **配置管理**：
   - 使用 JSON 格式的配置文件统一管理文件类型、目录规则和哈希值。
   - 提供加载和保存配置的接口，便于扩展和维护。

6. **文件备份逻辑**：
   - 使用 `shutil.copy2` 实现文件复制，保留文件元数据。
   - 在复制前调用 `should_backup` 和 `is_duplicate` 函数确保文件符合备份条件且不重复。

## 注意事项
1. **权限问题**：确保脚本有权限访问 WeChat 文件夹和备份目录。
2. **性能影响**：频繁的文件复制可能会影响系统性能，建议定期清理备份目录。
3. **数据安全**：备份的文件应妥善保管，避免泄露敏感信息。

通过以上步骤，您可以实现 WeChat 图片和视频的自动备份功能，提升数据的安全性和便利性。
