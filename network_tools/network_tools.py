import subprocess
import shlex

def execute(cmd: str):
    cmd = cmd.strip()  # 去掉首尾的空白字符
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()