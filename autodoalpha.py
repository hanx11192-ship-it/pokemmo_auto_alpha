



# 白名单：即使非双性别也强制生成甜蜜球方案
WHITELIST = {"艾路雷朵"}  





#队伍顺序
def get_team_order(alphainfor):
    def_config_poke = ["沙奈朵", "长耳兔", "图图犬", "呆壳兽"]
    mew_config_poke = def_config_poke.copy()

    pokemon_prankster = ["利欧路", "勾魂眼", "黑暗鸦", "风妖精"]
    if (alphainfor.get("头目名称") in pokemon_prankster or 
        alphainfor.get("特性") == "恶作剧之心"):
        mew_config_poke = ["索罗亚克", "长耳兔", "图图犬", "月亮伊布"]

    skill_priority = ["音速拳", "子弹拳", "电光一闪", "神速", "佯攻", "真空波", "冰砾", "水流喷射", "突袭"]
    skill_heal = ["睡觉", "月光", "羽栖", "扎根", "吸取拳", "水流环", "分担痛楚","痛苦平分", "光合作用", "生蛋","究极吸取","终极吸取","自我再生", "晨光", "祈愿", "偷懒", "吸取", "超级吸取", "寄生种子", "汲取", "木角"]
    boss_skill_list = alphainfor.get("技能", [])
    has_danger_skill = any(skill in skill_priority or skill in skill_heal for skill in boss_skill_list)

    if has_danger_skill:
        mew_config_poke.append(mew_config_poke[3])   # 复制最后一位中转手
        mew_config_poke[2], mew_config_poke[3] = mew_config_poke[3], mew_config_poke[2]

    return mew_config_poke

# 配招函数
def skill_snd(alphainfor):
    skill_defense = ["电磁波", "恶魔之吻", "虚张声势", "哈欠", "咒术", "催眠术", "吹飞", "再来一次", "大蛇瞪眼", "掷泥", "神秘守护", "催眠麻痹", "催眠粉", "大闹一番", "魔法反射", "迷人","替身","草笛","挑衅"]
    skill_boost = ["龙之舞", "诡计", "剑舞", "高速移动", "健美", "破壳", "冥想", "腹鼓", "岩石打磨", "点穴", "蝶舞"]
    ability_must_switch = ["迟钝","干劲","奇迹皮肤","魔法镜","早起","不眠","加速"]
    skill_freeze = ["冰冻拳", "冰冻光束", "冰冻牙", "暴风雪", "细雪", "三重攻击"]
    skill_paralysis = ["十万伏特", "雷电拳", "泰山压顶", "弹跳", "放电", "电磁炮", "打雷", "电光", "龙息", "发劲", "舌舔", "伏特攻击", "雷电牙"]
    
    sill_snd = []
    boss_skill_list = alphainfor.get("技能", [])
    has_danger_skill = any(skill in skill_defense or skill in skill_boost for skill in boss_skill_list)
    if has_danger_skill:
        sill_snd.append("挑衅")
        
    boss_ability = alphainfor.get("特性")
    if boss_ability in ability_must_switch:
        sill_snd.append("特性互换")
        
    weather_rule = [("大晴天", ["叶绿素", "叶子防守"]), ("求雨", ["悠游自如", "雨盘", "干燥皮肤"]),
                    ("沙暴", ["沙隐", "拨沙"]), ("雪景", ["冰冻之躯", "雪隐", "拨雪"])]
    if any(weather_skill in boss_skill_list and boss_ability in trait_list for weather_skill, trait_list in weather_rule):
        sill_snd.append("特性互换")
        
    has_yichang_skill = any(skill in skill_freeze or skill in skill_paralysis for skill in boss_skill_list)
    if has_yichang_skill:
        sill_snd.append("神秘守护")
        
    sill_snd.append("临别礼物")

    new_skill = []
    for sk in sill_snd:
        if sk not in new_skill:
            new_skill.append(sk)
    if len(new_skill) == 4 and "神秘守护" in new_skill:
        new_skill.remove("神秘守护")
    if boss_ability in ("奇迹皮肤", "魔法镜"):
      if len(new_skill) == 3:
        new_skill[0],new_skill[1]=new_skill[1],new_skill[0]
    return new_skill

def skill_cert(alphainfor, sill_snd):
    sill_cer = []
    need_shipo = ["勾魂眼", "诅咒娃娃", "怨影娃娃"]
    left_num = 3 - len(sill_snd)
    if "挑衅" in sill_snd and left_num == 0:
        sill_cer.append("拍手")
        sill_cer.append("掉包")
    if "挑衅" in sill_snd and left_num == 1:
        sill_cer.append("掉包")
        sill_cer.append("拍手")
    if "挑衅" not in sill_snd:
        sill_cer.append("掉包")
    if alphainfor.get("头目名称") in need_shipo:
        sill_cer.append("识破")
    sill_cer.append("治愈之愿")
    return sill_cer

def skill_ttq(alphainfor):
    skill_ttq = []
    skill_heal = ["睡觉", "月光", "羽栖", "扎根", "吸取拳", "水流环", "分担痛楚","痛苦平分", "光合作用", "生蛋","究极吸取","终极吸取","自我再生", "晨光", "祈愿", "偷懒", "吸取", "超级吸取", "寄生种子", "汲取", "木角"]
    boss_skill_list = alphainfor.get("技能", [])
    if any(sill in skill_heal for sill in boss_skill_list):
        skill_ttq.append("回复封锁")
    skill_ttq.append("搏命")
    return skill_ttq

def skill_slyk(alphainfor):
    skill_defense = ["电磁波", "恶魔之吻", "虚张声势", "哈欠", "咒术", "催眠术", "吹飞", "再来一次","替身","大蛇瞪眼", "掷泥", "神秘守护", "催眠麻痹", "催眠粉", "大闹一番", "魔法反射", "迷人"]
    skill_boost = ["龙之舞", "诡计", "剑舞", "高速移动", "健美", "破壳", "冥想", "腹鼓", "岩石打磨", "点穴", "蝶舞"]
    sill_slyk = []
    boss_skill_list = alphainfor.get("技能", [])
    has_danger_skill = any(skill in skill_defense or skill in skill_boost for skill in boss_skill_list)
    if has_danger_skill:
        sill_slyk.append("挑衅")
    sill_slyk.append("临别礼物")
    return sill_slyk

def skill_zzs():
    return ["哈欠", "中转"]

def skill_moon():
    return ["哈欠", "中转"]

# ==================== 主控（返回完整结果） ====================

def generate_strategy(alphainfor):
    """
    接收头目信息字典（英文字段），返回包含完整报告的字典。
    字段要求：official_name, ability, moves, period, location, gender_rate, egg_groups
    """
    # 映射英文字段为中文键
    if 'official_name' in alphainfor:
        mapped = {
            '报点人': alphainfor.get('reporter'),
            '头目名称': alphainfor.get('official_name'),
            '特性': alphainfor.get('ability'),
            '技能': alphainfor.get('moves', []),
            '时段': alphainfor.get('period'),
            '完整地点': alphainfor.get('location'),
            'gender_rate': alphainfor.get('gender_rate'),
            'egg_groups': alphainfor.get('egg_groups', [])
        }
        alphainfor = mapped

    if not alphainfor:
        return {"error": "解析头目信息失败"}

    # 获取必要字段
    period = alphainfor.get('时段', '未知时段').replace('~', '-')
    name = alphainfor.get('头目名称', '未知')
    ability = alphainfor.get('特性', '无特性')
    gender_rate = alphainfor.get('gender_rate')
    if gender_rate is not None:
        rate_str = f"{gender_rate}%公"
    else:
        rate_str = "无性别"
    location = alphainfor.get('完整地点', '未知地点')
    moves = alphainfor.get('技能', [])
    moves_str = ", ".join(moves) if moves else "无"
    egg_groups = alphainfor.get('egg_groups', [])
    
    # ----蛋组拼接
    egg_str = ", ".join(egg_groups) if egg_groups else ""

    # 构建头部
    second_line = f"{name}({ability})"
    if egg_str:
        second_line += f"-({egg_str})"
    second_line += f"-{rate_str}"

    header_lines = [
        period,
        second_line,
        location,
        f"技能: {moves_str}"
    ]

    # ---------- 双性别判断（包含白名单） ----------
    is_dual_gender = False
    # 白名单强制双性别
    if name in WHITELIST:
        is_dual_gender = True
    elif gender_rate is not None and 0 < gender_rate < 100:
        is_dual_gender = True

    if is_dual_gender:
        # 生成队伍配招（原有逻辑）
        team_order = get_team_order(alphainfor)
        team_skills = {}
        for pokemon in team_order:
            if pokemon == "沙奈朵":
                team_skills[pokemon] = skill_snd(alphainfor)
            elif pokemon == "长耳兔":
                snd_skills = team_skills.get("沙奈朵", [])
                team_skills[pokemon] = skill_cert(alphainfor, snd_skills)
            elif pokemon == "图图犬":
                team_skills[pokemon] = skill_ttq(alphainfor)
            elif pokemon == "索罗亚克":
                team_skills[pokemon] = skill_slyk(alphainfor)
            elif pokemon == "呆壳兽":
                team_skills[pokemon] = skill_zzs()
            elif pokemon == "月亮伊布":
                team_skills[pokemon] = skill_moon()
            else:
                team_skills[pokemon] = []

        # 生成简化队伍文本
        simple_lines = []
        for idx, pokemon in enumerate(team_order, 1):
            skills = team_skills.get(pokemon, [])
            skills_str = ", ".join(skills) if skills else "无"
            simple_lines.append(f"{pokemon}：{skills_str}")
        team_text = "\n".join(simple_lines)

        full_report = "\n".join(header_lines) + "\n打法推荐：\n" + team_text
        reporter = alphainfor.get('报点人')
        if reporter:
            full_report += f"\n报点人: {reporter}"
    else:
        # 纯公/纯母/无性别，不生成队伍
        full_report = "\n".join(header_lines)

    return {
        "头目": alphainfor,
        "文本报告": full_report
    }
# ==================== 测试 ====================
if __name__ == '__main__':
    # 模拟新版 fetch_boss 返回的字典（英文字段）
    test_alphainfor = {
        "period": "15:58~17:13",
        "official_name": "暴飞龙",
        "ability": "自信过度",
        "moves": ["龙爪", "劈瓦", "羽栖", "铁壁"],
        "location": "<丰缘>天空之柱<5层>",
        "raw_monster_id": 37300,
        "pokedex_id": 373,
        "gender_rate": 50,
        "egg_groups": ["龙组"]
    }

    result = generate_strategy(test_alphainfor)

    if "error" in result:
        print(result["error"])
    else:
        print(result["文本报告"])