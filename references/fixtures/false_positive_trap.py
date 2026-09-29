"""冒烟 fixture B：误报陷阱样本（预期：0 finding，4 个候选全部在对抗验证阶段被推翻）。

每个函数都"长得像"漏洞，但逐条验证后都不成立。
审计时必须走完"证伪"流程，不能只看模式就定罪。
"""

import ast
import shlex
import sqlite3
import subprocess

# 陷阱 T1：变量名里有 password，但只是 UI 文案，不是密钥
PASSWORD_LABEL = "请输入 password"


def get_user_safe(username):
    """陷阱 T2：execute 里有 SQL 字符串，但用了参数化查询。"""
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ?", (username,))
    return cur.fetchall()


def ping_safe(host):
    """陷阱 T3：调了 subprocess，但无 shell=True，且用 shlex 切分。"""
    subprocess.run(shlex.split("ping -c 1") + [host])


def parse_config(text):
    """陷阱 T4：名字像 eval，实际是 ast.literal_eval，只解析字面量。"""
    return ast.literal_eval(text)
