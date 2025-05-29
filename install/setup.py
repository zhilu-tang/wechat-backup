from setuptools import setup

setup(
    name="wechat-backup",
    version="1.0.0",
    description="Automatically backup WeChat images and videos to a specified directory",
    author="zhilu.tang",
    author_email="zhilu.tang@gmail.com",
    url="https://github.com/zhilu-tang/wechat-backup",
    packages=["sync"],
    entry_points={
        "console_scripts": [
            "wechat-backup=wechat_backup:main",
        ],
    },
    install_requires=[
        "watchdog",
    ],
)