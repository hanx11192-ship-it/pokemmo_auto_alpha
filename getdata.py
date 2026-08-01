import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== 调试配置 ==========
DEBUG_MODE = False
DEBUG_IDS = [94, 4, 7, 25, 150]

# ========== 蛋组映射表 ==========
EGG_GROUP_MAP = {
    "monster": "怪兽",
    "water1": "水中1",
    "bug": "虫",
    "flying": "飞行",
    "field": "陆上",
    "ground": "陆上",
    "fairy": "妖精",
    "plant": "植物",
    "humanshape": "人形",
    "human-like": "人形",
    "water3": "水中3",
    "mineral": "矿物",
    "indeterminate": "不定形",
    "water2": "水中2",
    "ditto": "百变怪",
    "dragon": "龙",
    "no‑eggs": "未发现"
}

# ----- 创建带重试的 Session -----
def create_retry_session(retries=3, backoff_factor=1.0):
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # 若持续 SSL 错误可取消下面注释（临时绕过证书验证）
    # session.verify = False
    return session

session = create_retry_session(retries=3, backoff_factor=1.5)

def safe_request(url, timeout=15):
    """发送 GET 请求，自动重试，若最终失败则返回 None"""
    try:
        resp = session.get(url, timeout=timeout)
        return resp
    except Exception as e:
        print(f"  请求失败（已重试）: {e}")
        return None

def get_ability_chinese_name(ability_url):
    """
    根据特性详情 URL 获取其中文名（zh-hans）
    若请求失败或找不到中文名，返回 None
    """
    time.sleep(0.5)  # 每次 API 调用前延迟 0.5s
    resp = safe_request(ability_url)
    if resp and resp.status_code == 200:
        data = resp.json()
        for name_obj in data.get("names", []):
            if name_obj.get("language", {}).get("name") == "zh-hans":
                return name_obj.get("name")
    return None

def get_pokemon_data(pokemon_id):
    """
    返回字典，包含：
        status: "success" | "not_found" | "error"
        以及 data 字段（成功时）
    """
    # ---------- 1. 请求 species ----------
    time.sleep(0.5)
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
    resp_s = safe_request(species_url)
    if resp_s is None:
        return {"status": "error", "id": pokemon_id, "message": "species request failed"}
    if resp_s.status_code == 404:
        return {"status": "not_found", "id": pokemon_id}
    if resp_s.status_code != 200:
        print(f"  species 状态码 {resp_s.status_code}，视为错误")
        return {"status": "error", "id": pokemon_id, "message": f"species status {resp_s.status_code}"}

    species_data = resp_s.json()

    # ---- 中文名 ----
    chinese_name = None
    for name_entry in species_data.get("names", []):
        lang = name_entry.get("language", {}).get("name", "")
        if lang.lower() == "zh-hans":
            chinese_name = name_entry.get("name")
            break
    if not chinese_name:
        chinese_name = species_data.get("name", f"未知_{pokemon_id}")

    # ---- 蛋组 ----
    groups = []
    for eg in species_data.get("egg_groups", []):
        en_name = eg.get("name")
        groups.append(EGG_GROUP_MAP.get(en_name, en_name))

    # ---- 性别率 ----
    gender_rate = species_data.get("gender_rate")
    if gender_rate == -1:
        rate = None
    else:
        rate = round((8 - gender_rate) * 100 / 8, 1)

    # ---------- 2. 请求 pokemon（特性） ----------
    time.sleep(0.5)
    pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    resp_p = safe_request(pokemon_url)
    hidden_ability = None

    if resp_p and resp_p.status_code == 200:
        pokemon_data = resp_p.json()
        abilities = pokemon_data.get("abilities", [])

        # 分离隐藏特性和普通特性
        hidden_entries = [a for a in abilities if a.get("is_hidden", False)]
        non_hidden_entries = [a for a in abilities if not a.get("is_hidden", False)]

        target_ability_url = None

        if hidden_entries:
            # 有隐藏特性，使用第一个隐藏特性
            target_ability_url = hidden_entries[0].get("ability", {}).get("url")
        else:
            # 没有隐藏特性，检查普通特性个数
            if len(non_hidden_entries) == 1:
                target_ability_url = non_hidden_entries[0].get("ability", {}).get("url")
            # 否则 target_ability_url 保持 None，最终 hidden_ability 为 None

        if target_ability_url:
            hidden_ability = get_ability_chinese_name(target_ability_url)

    elif resp_p and resp_p.status_code != 200:
        print(f"  pokemon 请求状态码 {resp_p.status_code}，隐藏特性将置空")
    else:
        print("  pokemon 请求失败，隐藏特性将置空")

    # 组装成功数据
    data = {
        "id": pokemon_id,
        "name": chinese_name,
        "rate": rate,
        "group": groups,
        "hidden_ability": hidden_ability
    }
    return {"status": "success", "data": data}

def main():
    all_data = {}
    if DEBUG_MODE:
        ids_to_fetch = DEBUG_IDS
        print(f"【调试模式】仅抓取 {ids_to_fetch}")
    else:
        ids_to_fetch = None
        print("【正常模式】从 ID=1 连续抓取，连续 5 次 404 停止")

    pokemon_id = 1
    consecutive_404 = 0
    max_404 = 5

    while True:
        if ids_to_fetch is not None:
            if pokemon_id - 1 >= len(ids_to_fetch):
                break
            current_id = ids_to_fetch[pokemon_id - 1]
        else:
            current_id = pokemon_id

        print(f"\n正在抓取 ID={current_id} ...")
        result = get_pokemon_data(current_id)

        if result["status"] == "not_found":
            consecutive_404 += 1
            if ids_to_fetch is not None:
                pokemon_id += 1
                continue
            else:
                if consecutive_404 >= max_404:
                    print(f"连续 {max_404} 次 404，停止抓取。")
                    break
                pokemon_id += 1
                continue
        elif result["status"] == "error":
            print(f"  ID={current_id} 请求错误，跳过。")
            if ids_to_fetch is not None:
                pokemon_id += 1
            else:
                pokemon_id += 1
            continue
        else:  # success
            consecutive_404 = 0
            all_data[str(current_id)] = result["data"]
            print(f"  ID={current_id} 抓取成功。")

        # 准备下一个 ID
        if ids_to_fetch is not None:
            pokemon_id += 1
        else:
            pokemon_id += 1

        # 每只精灵处理完后延迟 1 秒
        time.sleep(1.0)

    out_file = "pokemon_data.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n完成！共成功抓取 {len(all_data)} 只宝可梦，数据保存至 {out_file}")

if __name__ == "__main__":
    main()