"""冒烟 fixture A：已知漏洞样本（预期：5 个 finding，2 高 3 中，0 漏报）。

业务背景（供审计第 1 步建上下文用）：
- 一个内部运维小工具的后端模块，直接处理来自 Web 表单的用户输入。
- 信任边界：get_user / ping_host / read_file 的参数均来自不可信的远程用户输入；
  check_password 的 stored 来自数据库，pw 来自用户登录表单。
"""

import hashlib
import os
import sqlite3
import subprocess

DB = "app.db"

# 候选 V1：硬编码生产密钥（维度③）
ADMIN_TOKEN = "sk-live-9f2c4a7d1e5b"


def get_user(username):
    """按用户名查用户。username 来自 Web 表单（不可信输入）。"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # 候选 V2：SQL 注入——字符串拼接构造 SQL（维度①，也会被维度⑨命中，考验去重）
    cur.execute("SELECT * FROM users WHERE name = '%s'" % username)
    return cur.fetchall()


def ping_host(host):
    """ping 一台主机。host 来自 Web 表单（不可信输入）。"""
    # 候选 V3：命令注入——shell=True + 输入拼接（维度①）
    subprocess.run("ping -c 1 " + host, shell=True)


def check_password(pw, stored):
    """校验登录口令。pw 来自登录表单，stored 来自数据库。"""
    # 候选 V4：弱密码学——MD5 做口令比对（维度⑥）
    return hashlib.md5(pw.encode()).hexdigest() == stored


def read_file(name):
    """读取 /var/data 下的文件。name 来自 Web 表单（不可信输入）。"""
    # 候选 V5：路径穿越——未校验拼接路径（维度①）
    with open("/var/data/" + name) as f:
        return f.read()


def data_dir():
    # 安全：环境变量读取，无漏洞
    return os.environ.get("DATA_DIR", "/var/data")
