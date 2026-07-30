#1分钟运行一次
import os
import subprocess
from datetime import datetime
TIME_FILE = "time.txt"
def get_current_period_str():
    hour = datetime.now().hour
    if 8 <= hour < 14:
        return "8-14"
    elif 14 <= hour < 20:
        return "14-20"
    elif hour >= 20 or hour < 2:
        return "20-2"
    else:
        return "2-8"
def main():
    current_period = get_current_period_str()
    
    # 读取 time.txt 中保存的时段
    if os.path.exists(TIME_FILE):
        with open(TIME_FILE, 'r', encoding='utf-8') as f:
            saved_period = f.read().strip()
    else:
        saved_period = ""
    
    # 如果 time.txt 为空或保存的时段不是当前时段，则调用获取脚本
    if not saved_period:
        print("time.txt 为空，需要检查头目。")
        need_fetch = True
    elif saved_period != current_period:
        print(f"时段变化：{saved_period} -> {current_period}，重新检查头目。")
        need_fetch = True
    else:
        print(f"当前时段 {current_period} 已记录，跳过检查。")
        need_fetch = False
    
    if need_fetch:
        # 调用同目录下的 fetch.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fetch_script = os.path.join(script_dir, "fetch.py")
        result = subprocess.run(["python", fetch_script], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
if __name__ == "__main__":
    main()