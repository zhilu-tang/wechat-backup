class WechatBackup < Formula
  desc "Automatically backup WeChat images and videos to a specified directory"
  homepage "https://github.com/zhilu-tang/homebrew-wechat-backup"
  url "https://github.com/zhilu-tang/homebrew-wechat-backup.git"
  version "1.0.2"

  depends_on "python@3.9" => :build
  depends_on "pyinstaller" => :build

  def install
    # 克隆仓库，指定 main 分支
    system "git", "clone", "--branch", "main", "https://github.com/zhilu-tang/wechat-backup.git", "wechat-backup"
    cd "wechat-backup" do
      # 使用 install.sh 脚本进行安装
      system "./install/brew_install.sh"
      # 安装到 Homebrew 的 bin 目录
      bin.install "dist/wechat-backup"
      bin.install "dist/wechat-backup-manage"
    end

    # 创建 launchd 配置文件
    (bin/"homebrew.mxcl.wechat-backup.plist").write plist
  end

  def caveats
    <<~EOS
      To have launchd start wechat-backup now and restart at login:
        brew services start wechat-backup
      Or, if you don't want/need a background service you can just run:
        #{bin}/wechat-backup
    EOS
  end

  def plist
    <<~EOS
      <?xml version="1.0" encoding="UTF-8"?>
      <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
      <plist version="1.0">
      <dict>
        <key>Label</key>
        <string>#{plist_name}</string>
        <key>ProgramArguments</key>
        <array>
          <string>#{opt_bin}/wechat-backup</string>
          <string>--service</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>StandardOutPath</key>
        <string>/tmp/wechat-backup.log</string>
        <key>StandardErrorPath</key>
        <string>/tmp/wechat-backup.log</string>
      </dict>
      </plist>
    EOS
  end

  test do
    system "#{bin}/wechat-backup", "--version"
  end
end