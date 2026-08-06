import requests
import json
import re
import os
import time
import importlib.util
import sys
from datetime import datetime
from send import send

API_URL = "https://pokemmo.lanbizi.com/api/alpha/spawn/current"
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 15; PKG110 Build/UKQ1.231108.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.200 Mobile Safari/537.36",
    'Content-Type': "application/json",
    'Content-Encoding': "gzip",
    'Origin': "https://pokemmo.lanbizi.com",
    'Sec-Fetch-Site': "same-origin",
    'Sec-Fetch-Mode': "cors",
    'Sec-Fetch-Dest': "empty",
    'Referer': "https://pokemmo.lanbizi.com/",
    'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
}
TIME_FILE = "time.txt"
DATA_FILE = "data.json"
DEBUG_FILE = "alphadebug.json"

# ---------- 动态加载策略脚本 ----------
def load_strategy_function():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    strategy_path = os.path.join(script_dir, "autodoalpha.py")
    if not os.path.exists(strategy_path):
        print("[警告] 策略脚本 autodoalpha.py 不存在，将无法生成策略报告。")
        return None
    spec = importlib.util.spec_from_file_location("strategy_module", strategy_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["strategy_module"] = module
    try:
        spec.loader.exec_module(module)
        return getattr(module, "generate_strategy")
    except Exception as e:
        print(f"[警告] 加载策略脚本失败: {e}")
        return None

generate_strategy = load_strategy_function()

# ---------- 加载图鉴数据 ----------
def load_pokemon_data():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, DATA_FILE)
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 data.json 失败: {e}")
        return {}

POKEMON_DATA = load_pokemon_data()

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

def extract_ability(text):
    match = re.search(r'\[[^<]+<([^>]+)>', text)
    if match:
        return match.group(1).strip()
    return None

def extract_reporter(text):
    match = re.search(r'报点人[:：](@?[\w]+)', text)
    if match:
        return match.group(1).strip()
    return None

def parse_boss_data(boss_info):
    start = boss_info.get('start_time_str', '')
    end = boss_info.get('end_time_str', '')
    period = f"{start}~{end}" if start and end else None

    text = boss_info.get('text', '')
    
    moves = []
    for i in range(1, 5):
        move = boss_info.get(f'move{i}')
        if move:
            moves.append(move)

    location_full = boss_info.get('location_full_name', '')
    description = boss_info.get('description')
    if description is None:
        description = ''
    else:
        description = description.strip()
    if description:
        location = f"{location_full} - {description}"
    else:
        location = location_full

    monster_id = boss_info.get('monster_id')
    pokedex_id = None
    if monster_id is not None:
        pokedex_id = int(monster_id / 100)

    # 初始化 pokedex_data（必须在使用前）
    pokedex_data = {
        'official_name': None,
        'gender_rate': None,
        'egg_groups': [],
        'hidden_ability': None
    }
    if pokedex_id is not None and str(pokedex_id) in POKEMON_DATA:
        pkm = POKEMON_DATA[str(pokedex_id)]
        pokedex_data['official_name'] = pkm.get('name')
        pokedex_data['gender_rate'] = pkm.get('rate')
        pokedex_data['egg_groups'] = pkm.get('group', [])
        pokedex_data['hidden_ability'] = pkm.get('hidden_ability')

    # 现在从 pokedex_data 获取特性（不再使用正则）
    ability = pokedex_data.get('hidden_ability')
    
    reporter = extract_reporter(text)
    return {
        'reporter': reporter,
        'period': period,
        'official_name': pokedex_data['official_name'],
        'ability': ability,
        'moves': moves,
        'location': location,
        'raw_monster_id': monster_id,
        'pokedex_id': pokedex_id,
        'gender_rate': pokedex_data['gender_rate'],
        'egg_groups': pokedex_data['egg_groups']
    }
def fetch_boss():
    debug = int(os.environ.get('alpha_debug', '0'))

    if debug == 1:
        print("=== 调试模式 ===")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            debug_path = os.path.join(script_dir, DEBUG_FILE)
            with open(debug_path, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
            print("已加载调试数据文件 alphadebug.json")
        except Exception as e:
            print(f"读取调试数据文件失败: {e}")
            return False

        boss_list = mock_data.get('data', [])
        if not boss_list:
            print("调试数据中没有头目信息（data 为空）")
            return False

        boss_info = boss_list[0]
        if 'text' not in boss_info:
            print("调试数据中没有 'text' 字段")
            return False

        parsed = parse_boss_data(boss_info)
        print("调试模式 - 头目信息解析成功：")
        for key, value in parsed.items():
            print(f"  {key}: {value}")

        # 直接调用策略生成报告
        if generate_strategy is not None:
            try:
                result = generate_strategy(parsed)
                if "error" in result:
                    print(f"策略生成错误: {result['error']}")
                    # 回退：使用基本头部（但策略已内置处理，一般不会出错）
                    report = "策略生成失败"
                else:
                    report = result["文本报告"]
            except Exception as e:
                print(f"策略生成异常: {e}")
                report = "策略生成异常"
        else:
            report = "策略脚本未加载"

        print("\n【生成的报告】")
        print(report)
        send(report, summary="debug")
        print("调试模式不写入 time.txt，仅测试解析并已发送。")
        return True

    else:
        print("=== 正常模式 ===")
        try:
            def request_and_parse():
                resp = requests.post(API_URL, data=json.dumps({}), headers=HEADERS, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if data.get('code') != 0:
                    print(f"API 返回错误: {data.get('msg')}")
                    return None
                boss_list = data.get('data', [])
                if not boss_list:
                    print("当前时段没有头目（data 为空）")
                    return None
                return parse_boss_data(boss_list[0])

            parsed = request_and_parse()
            if parsed is None:
                return False

            # 技能解析失败（moves 为空）时重新请求 API，最多重试 3 次：立即、0.5s、1s
            retry_delays = [0, 0.5, 1]
            if not parsed.get('moves'):
                print("头目技能解析失败（moves 为空），重新请求 API 重试...")
                for i, delay in enumerate(retry_delays, 1):
                    if delay > 0:
                        time.sleep(delay)
                    retry_parsed = request_and_parse()
                    if retry_parsed is None:
                        print(f"第 {i} 次重试请求失败")
                        continue
                    if retry_parsed.get('moves'):
                        print(f"第 {i} 次重试后技能解析成功")
                        parsed = retry_parsed
                        break
                    print(f"第 {i} 次重试后技能仍为空")
                else:
                    print("3 次重试均未解析到技能，继续按兜底流程处理。")

            print("头目信息解析成功：")
            for key, value in parsed.items():
                print(f"  {key}: {value}")

            # 直接调用策略生成报告
            if generate_strategy is not None:
                try:
                    result = generate_strategy(parsed)
                    if "error" in result:
                        print(f"策略生成错误: {result['error']}")
                        report = "策略生成失败"
                    else:
                        report = result["文本报告"]
                except Exception as e:
                    print(f"策略生成异常: {e}")
                    report = "策略生成异常"
            else:
                report = "策略脚本未加载"

            print("\n【生成的报告】")
            print(report)

            send(report)  # 正常模式摘要自动生成

            with open(TIME_FILE, 'w', encoding='utf-8') as f:
                f.write(get_current_period_str())
            print("已标记当前时段已处理。")
            return True

        except Exception as e:
            print(f"请求或解析失败: {e}")
            return False

if __name__ == "__main__":
    fetch_boss()