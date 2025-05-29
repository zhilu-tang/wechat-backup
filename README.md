# WeChat Backup 安装说明

WeChat Backup 是一个用于自动备份 WeChat 图片和视频的工具。本项目提供了一种简单的方式来将 WeChat 的媒体文件同步到本地指定目录。

## 系统要求

- macOS 10.12 或更高版本
- Python 3.6 或更高版本
- Homebrew（可选，用于安装和管理依赖）

## 安装步骤

### 方法 1：使用 Homebrew 安装

1. 打开终端。
2. 运行以下命令添加 Homebrew Tap：
   ```bash
   brew tap zhilu-tang/wechat-backup
   ```
   
3. 安装 WeChat Backup：
   ```bash
   brew install wechat-backup
   ```

### 方法 2：手动安装

1. 克隆项目仓库：
   ```bash
   git clone https://github.com/zhilu-tang/wechat-backup.git
   cd wechat-backup
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行安装脚本：
   ```bash
   ./brew_install.sh
   ```


## 配置与使用

1. 首次运行时，脚本会自动检测 WeChat 文件夹并开始全量同步。
2. 要启动后台服务，请运行：
   ```bash
   brew services start wechat-backup
   ```

3. 要停止服务，请运行：
   ```bash
   brew services stop wechat-backup
   ```


## 卸载

如果您使用 Homebrew 安装，可以通过以下命令卸载：
```bash
brew uninstall wechat-backup
brew untap zhilu-tang/wechat-backup
```
curl -OL https://github.com/zhilu-tang/wechat-backup/archive/v1.0.0.tar.gz
shasum -a 256 v1.0.0.tar.gz


对于手动安装的用户，您可以删除安装的可执行文件和配置文件。

## 常见问题

1. **权限问题**：如果遇到权限错误，请确保脚本具有访问 WeChat 文件夹的权限。请参考[权限设置指南](https://github.com/zhilu-tang/wechat-backup/blob/main/docs/permissions.md)。
2. **依赖问题**：如果缺少某些依赖，请运行 `pip install -r requirements.txt` 来安装所有必要的包。

## 贡献

我们欢迎任何形式的贡献，包括但不限于 bug 报告、功能建议和代码贡献。请参阅[贡献指南](https://github.com/zhilu-tang/wechat-backup/blob/main/CONTRIBUTING.md)了解更多信息。

## 许可证

本项目采用 MIT 许可证。有关详细信息，请参阅 [LICENSE](https://github.com/zhilu-tang/wechat-backup/blob/main/LICENSE) 文件。

如果您在安装或使用过程中遇到任何问题，请随时在 [GitHub Issues](https://github.com/zhilu-tang/wechat-backup/issues) 页面提交问题。谢谢！

