# backend/stats_tracker/app_stats.py

from flask import Blueprint, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

stats_tracker_bp = Blueprint(
    'stats_tracker',
    __name__,
    template_folder='../../frontend/templates'
)

# --- API 配置 ---
API_BASE_URL = "https://api.pubg.com/shards"
API_KEY = os.getenv("PUBG_API_KEY")  # 从环境变量安全地获取API密钥

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json"
}

# --- (1) 修改点：将DUO，SOLO，SQUAD以中文形式展示 ---
# 创建一个从API模式名到中文显示的映射
MODE_MAPPING = {
    "solo": "单人",
    "duo": "双人",
    "squad": "四人",
    "solo-fpp": "单人(FPP)",
    "duo-fpp": "双人(FPP)",
    "squad-fpp": "四人(FPP)"
}

# 【新增】创建地图名称到中文的映射
MAP_NAME_MAPPING = {
    "Baltic_Main": "艾伦格",
    "Chimera_Main": "帕拉莫",
    "Desert_Main": "米拉玛",
    "DihorOtok_Main": "维寒迪",
    "Erangel_Main": "艾伦格",
    "Heaven_Main": "褐湾",
    "Kiki_Main": "帝斯顿",
    "Range_Main": "训练场",
    "Savage_Main": "萨诺",
    "Summerland_Main": "卡拉金",
    "Tiger_Main": "泰戈",
    "Neon_Main": "荣都",  # Rondo
    # 可能会有其他变体，可以根据需要添加
    "Erangel (Remastered)": "艾伦格",
    "Vikendi": "维寒迪"
}


# --- 辅助函数 ---

# --- (2) 修改点：增加详细比赛列表查询 ---
def fetch_recent_matches(match_ids, platform, player_name):
    """
    根据比赛ID列表，通过官方API获取最近的比赛详情。
    """
    recent_matches_data = []
    # 为避免请求超时和API滥用，只查询最近的5场比赛
    matches_to_fetch = match_ids[:20]

    for match_ref in matches_to_fetch:
        match_id = match_ref['id']
        match_url = f"{API_BASE_URL}/{platform}/matches/{match_id}"
        try:
            match_response = requests.get(match_url, headers=HEADERS)
            if match_response.status_code != 200:
                print(f"Failed to fetch match details for {match_id}, status: {match_response.status_code}")
                continue

            match_data = match_response.json()
            all_included = match_data.get('included', [])

            total_teams = sum(1 for item in all_included if item['type'] == 'roster')
            game_mode_api = match_data['data']['attributes']['gameMode']
            game_mode_chinese = MODE_MAPPING.get(game_mode_api, game_mode_api.upper())

            # 【修改】获取地图名并进行中文转换
            map_name_api = match_data['data']['attributes']['mapName']
            map_name_chinese = MAP_NAME_MAPPING.get(map_name_api, map_name_api)  # 使用 get 方法，如果找不到则返回原名

            player_participant = None
            for p in all_included:
                if p['type'] == 'participant' and p['attributes']['stats']['name'] == player_name:
                    player_participant = p
                    break

            if player_participant:
                stats = player_participant['attributes']['stats']

                recent_matches_data.append({
                    "map": map_name_chinese,  # 使用转换后的中文名
                    "mode": game_mode_chinese,
                    "rank": stats.get('winPlace', 0),
                    "totalTeams": total_teams,
                    "kills": stats.get('kills', 0),
                    "damage": stats.get('damageDealt', 0.0)
                })

        except requests.exceptions.RequestException as e:
            print(f"Request error for match {match_id}: {e}")
        except KeyError as e:
            print(f"Key error while parsing match {match_id}: {e}")

    return recent_matches_data


def transform_api_data(api_response_data, player_name, platform, recent_matches):
    """
    将从PUBG API获取的赛季统计数据和比赛数据转换为前端渲染所需的格式。
    """
    try:
        stats = api_response_data['data']['attributes']['gameModeStats']
        modes_to_extract = ["solo", "duo", "squad"]
        transformed_stats = {}
        for mode in modes_to_extract:
            if mode in stats and stats[mode].get('roundsPlayed', 0) > 0:
                mode_data = stats[mode]
                original_mode_mapping = {"solo": "单人模式", "duo": "双人模式", "squad": "四人模式"}
                chinese_mode = original_mode_mapping.get(mode, mode.upper())
                transformed_stats[chinese_mode] = {
                    "kills": mode_data.get('kills', 0),
                    "assists": mode_data.get('assists', 0),
                    "wins": mode_data.get('wins', 0),
                    "top10s": mode_data.get('top10s', 0),
                    "roundsPlayed": mode_data.get('roundsPlayed', 0),
                    "damageDealt": mode_data.get('damageDealt', 0.0),
                    "longestKill": mode_data.get('longestKill', 0.0)
                }

        return {
            "playerName": player_name,
            "platform": platform.upper(),
            "stats": transformed_stats,
            "recentMatches": recent_matches
        }

    except KeyError as e:
        print(f"Data transformation error due to missing key: {e}")
        return None


@stats_tracker_bp.route('/')
def index():
    """渲染战绩查询页面"""
    return render_template('stats_tracker.html')


@stats_tracker_bp.route('/query', methods=['POST'])
def query_stats():
    """处理战绩查询请求，调用官方API"""
    if not API_KEY:
        return jsonify({"success": False, "error": "服务器API密钥未配置"}), 500
    try:
        data = request.get_json()
        username = data.get('username')
        platform = data.get('platform')
        if not username or not platform:
            return jsonify({"success": False, "error": "用户名和平台不能为空"}), 400

        player_url = f"{API_BASE_URL}/{platform}/players?filter[playerNames]={username}"
        player_response = requests.get(player_url, headers=HEADERS)
        if player_response.status_code == 404:
            return jsonify({"success": False, "error": f"在平台 {platform} 上未找到玩家 {username}"}), 404
        if player_response.status_code != 200:
            error_detail = player_response.json().get('errors', '未知错误')
            return jsonify(
                {"success": False, "error": f"API错误 (玩家查询): {error_detail}"}), player_response.status_code

        player_data = player_response.json()['data'][0]
        player_id = player_data['id']
        match_ids = player_data.get('relationships', {}).get('matches', {}).get('data', [])

        seasons_url = f"{API_BASE_URL}/{platform}/seasons"
        seasons_response = requests.get(seasons_url, headers=HEADERS)
        if seasons_response.status_code != 200:
            error_detail = seasons_response.json().get('errors', '未知错误')
            return jsonify(
                {"success": False, "error": f"API错误 (赛季查询): {error_detail}"}), seasons_response.status_code

        current_season = next(
            (s for s in seasons_response.json()['data'] if s['attributes']['isCurrentSeason']), None)
        if not current_season:
            return jsonify({"success": False, "error": "无法确定当前赛季"}), 500
        current_season_id = current_season['id']

        stats_url = f"{API_BASE_URL}/{platform}/players/{player_id}/seasons/{current_season_id}"
        stats_response = requests.get(stats_url, headers=HEADERS)
        if stats_response.status_code != 200:
            error_detail = stats_response.json().get('errors', '该玩家可能没有本赛季的战绩')
            return jsonify(
                {"success": False, "error": f"API错误 (战绩查询): {error_detail}"}), stats_response.status_code

        recent_matches_list = fetch_recent_matches(match_ids, platform, username)
        api_data = stats_response.json()
        transformed_data = transform_api_data(api_data, username, platform, recent_matches_list)

        if not transformed_data:
            return jsonify({"success": False, "error": "无法解析玩家战绩数据，可能数据格式已更新"}), 500

        return jsonify({
            "success": True,
            "data": transformed_data
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"网络请求失败: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"success": False, "error": "服务器内部错误"}), 500
