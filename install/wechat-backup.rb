class WechatBackup < Formula
  desc "Automatically backup WeChat images and videos to a specified directory"
  homepage "https://github.com/zhilu-tang/homebrew-wechat-backup"
  url "https://github.com/zhilu-tang/homebrew-wechat-backup.git"
  version "1.0.2"

  depends_on "python@3.9" => :build
  depends_on "pyinstaller" => :build
  depends_on "tcl-tk" => :build

  def install
    # 克隆仓库，指定 main 分支
    system "git", "clone", "--branch", "main", "https://github.com/zhilu-tang/wechat-backup.git", "wechat-backup"
    cd "wechat-backup" do
      # 使用 install.sh 脚本进行安装
#       system "bash" "./install/brew_install.sh"
      python = Formula["python@3.9"].opt_bin/"python3"
      system python, "-m", "pip", "install", "-r", "requirements.txt"

      # 打包主程序 wechat_backup.py
      system Formula["pyinstaller"].opt_bin/"pyinstaller", "--onefile",
             "--name=wechat-backup",
             "wechat_backup.py"

      # 打包 manage_rules.py，并指定 sync 目录到 PYTHONPATH
      system Formula["pyinstaller"].opt_bin/"pyinstaller", "--onefile",
         "--name=wechat-backup-manage",
         "--paths=#{Dir.pwd}/sync",
         "sync/manage_rules.py"      # 安装到 Homebrew 的 bin 目录
      bin.install "dist/wechat-backup"
      bin.install "dist/wechat-backup-manage"
    end

    # Install Python script
    libexec.install Dir["*"]
    bin.install_symlink libexec/"wechat-backup"

    # Install plist in user's LaunchAgents directory
    (prefix/"homebrew.mxcl.wechat-backup.plist").write plist
  end

  def plist
    <<~EOS
      <?xml version="1.0" encoding="UTF-8"?>
      <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
      <plist version="1.0">
        <dict>
          <key>Label</key>
          <string>homebrew.mxcl.wechat-backup</string>
          <key>ProgramArguments</key>
          <array>
            <string>#{opt_bin}/wechat-backup</string>
          </array>
          <key>RunAtLoad</key>
          <true/>
          <key>StandardOutPath</key>
          <string>#{var}/log/wechat-backup.log</string>
          <key>StandardErrorPath</key>
          <string>#{var}/log/wechat-backup.log</string>
        </dict>
      </plist>
    EOS
  end

  def post_install
    # Create the plist in the user's LaunchAgents directory
    user_plist = "#{Dir.home}/Library/LaunchAgents/homebrew.mxcl.wechat-backup.plist"
    system "cp", "#{prefix}/homebrew.mxcl.wechat-backup.plist", user_plist
    system "launchctl", "load", "-w", user_plist
  end

  def uninstall
    # Remove the plist from the user's LaunchAgents directory
    user_plist = "#{Dir.home}/Library/LaunchAgents/homebrew.mxcl.wechat-backup.plist"
    system "launchctl", "unload", "-w", user_plist
    system "rm", user_plist
  end

  def caveats
    <<~EOS
      To have launchd start wechat-backup now and restart at login:
        brew services start wechat-backup
      Or, if you don't want/need a background service you can just run:
        #{bin}/wechat-backup
    EOS
  end


  test do
    system "#{bin}/wechat-backup", "--version"
  end
end