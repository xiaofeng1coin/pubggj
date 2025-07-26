# app_secret.py
from flask import Blueprint, render_template, request, jsonify

secret_map_bp = Blueprint('secret_map', __name__, template_folder='../../frontend/templates')

# 查询容差（点击坐标与密室坐标的像素距离小于此值即视为命中）
PROXIMITY_THRESHOLD = 40

# 关键：所有密室坐标 (x, y) 均已更新为游戏内实际坐标系 (X: 420-1500, Y: 0-1080)
MAPS_DATA = {
    "Erangel": {
        "name": "艾伦格",
        "image_path": "/static/images/maps/Erangel.jpg",
        "secret_spots": [
            {"id": 1, "name": "密室1", "x": 1313, "y": 646,
             "image": "/static/images/secrets/Erangel_1313_646.png"},
            {"id": 2, "name": "密室2", "x": 1283, "y": 282,
             "image": "/static/images/secrets/Erangel_1283_282.png"},
            {"id": 3, "name": "密室3", "x": 1098, "y": 88,
             "image": "/static/images/secrets/Erangel_1098_88.png"},
            {"id": 4, "name": "密室4", "x": 965, "y": 260,
             "image": "/static/images/secrets/Erangel_965_260.png"},
            {"id": 5, "name": "密室5", "x": 762, "y": 290,
             "image": "/static/images/secrets/Erangel_762_290.png"},
            {"id": 6, "name": "密室6", "x": 1145, "y": 455,
             "image": "/static/images/secrets/Erangel_1145_455.png"},
            {"id": 7, "name": "密室7", "x": 1041, "y": 588,
             "image": "/static/images/secrets/Erangel_1041_588.png"},
            {"id": 8, "name": "密室8", "x": 820, "y": 494,
             "image": "/static/images/secrets/Erangel_820_494.png"},
            {"id": 9, "name": "密室9", "x": 617, "y": 465,
             "image": "/static/images/secrets/Erangel_617_465.png"},
            {"id": 10, "name": "密室10", "x": 605, "y": 239,
             "image": "/static/images/secrets/Erangel_605_239.png"},
            {"id": 11, "name": "密室11", "x": 586, "y": 732,
             "image": "/static/images/secrets/Erangel_586_732.png"},
            {"id": 12, "name": "密室12", "x": 1003, "y": 783,
             "image": "/static/images/secrets/Erangel_1003_783.png"},
            {"id": 13, "name": "密室13", "x": 860, "y": 889,
             "image": "/static/images/secrets/Erangel_860_889.png"},
            {"id": 14, "name": "密室14", "x": 1170, "y": 887,
             "image": "/static/images/secrets/Erangel_1170_887.png"},
            {"id": 15, "name": "密室15", "x": 783, "y": 683,
             "image": "/static/images/secrets/Erangel_783_683.png"}
        ]
    },
    "Taego": {
        "name": "泰戈",
        "image_path": "/static/images/maps/Taego.jpg",
        "secret_spots": [
            {"id": 1, "name": "密室1", "x": 1366, "y": 448, "image": "/static/images/secrets/Taego_1366_448.png"},
            {"id": 2, "name": "密室2", "x": 1225, "y": 514, "image": "/static/images/secrets/Taego_1225_514.png"},
            {"id": 3, "name": "密室3", "x": 1275, "y": 739, "image": "/static/images/secrets/Taego_1275_739.png"},
            {"id": 4, "name": "密室4", "x": 1267, "y": 952, "image": "/static/images/secrets/Taego_1267_952.png"},
            {"id": 5, "name": "密室5", "x": 1083, "y": 851, "image": "/static/images/secrets/Taego_1083_851.png"},
            {"id": 6, "name": "密室6", "x": 1009, "y": 660, "image": "/static/images/secrets/Taego_1009_660.png"},
            {"id": 7, "name": "密室7", "x": 744, "y": 859, "image": "/static/images/secrets/Taego_744_859.png"},
            {"id": 8, "name": "密室8", "x": 552, "y": 693, "image": "/static/images/secrets/Taego_552_693.png"},
            {"id": 9, "name": "密室9", "x": 558, "y": 451, "image": "/static/images/secrets/Taego_558_451.png"},
            {"id": 10, "name": "密室10", "x": 585, "y": 355, "image": "/static/images/secrets/Taego_585_355.png"},
            {"id": 11, "name": "密室11", "x": 609, "y": 159, "image": "/static/images/secrets/Taego_609_159.png"},
            {"id": 12, "name": "密室12", "x": 766, "y": 178, "image": "/static/images/secrets/Taego_766_178.png"},
            {"id": 13, "name": "密室13", "x": 898, "y": 262, "image": "/static/images/secrets/Taego_898_262.png"},
            {"id": 14, "name": "密室14", "x": 1065, "y": 230, "image": "/static/images/secrets/Taego_1065_230.png"},
            {"id": 15, "name": "密室15", "x": 1343, "y": 276, "image": "/static/images/secrets/Taego_1343_276.png"}
        ]
    },
    "Paramo": {
        "name": "帕拉莫",
        "image_path": "/static/images/maps/Paramo.jpg",
        "secret_spots": [
            {"id": 1, "name": "密室1", "x": 844, "y": 328, "image": "/static/images/secrets/Paramo_844_328.png"},
            {"id": 2, "name": "密室2", "x": 713, "y": 373, "image": "/static/images/secrets/Paramo_713_373.png"},
            {"id": 3, "name": "密室3", "x": 551, "y": 678, "image": "/static/images/secrets/Paramo_551_678.png"},
            {"id": 4, "name": "密室4", "x": 885, "y": 670, "image": "/static/images/secrets/Paramo_885_670.png"},
            {"id": 5, "name": "密室5", "x": 1092, "y": 514, "image": "/static/images/secrets/Paramo_1092_514.png"},
            {"id": 6, "name": "密室6", "x": 1070, "y": 636, "image": "/static/images/secrets/Paramo_1070_636.png"},
            {"id": 7, "name": "密室7", "x": 976, "y": 855, "image": "/static/images/secrets/Paramo_976_855.png"},
            {"id": 8, "name": "密室8", "x": 1303, "y": 602, "image": "/static/images/secrets/Paramo_1303_602.png"}
        ]
    },
    "Deston": {
        "name": "帝斯顿",
        "image_path": "/static/images/maps/Deston.jpg",
        "secret_spots": [
            {"id": 1, "name": "密室1", "x": 1396, "y": 420, "image": "/static/images/secrets/Deston_1396_420.png"},
            {"id": 2, "name": "密室2", "x": 1308, "y": 248, "image": "/static/images/secrets/Deston_1308_248.png"},
            {"id": 3, "name": "密室3", "x": 1107, "y": 123, "image": "/static/images/secrets/Deston_1107_123.png"},
            {"id": 4, "name": "密室4", "x": 1091, "y": 262, "image": "/static/images/secrets/Deston_1091_262.png"},
            {"id": 5, "name": "密室5", "x": 1020, "y": 359, "image": "/static/images/secrets/Deston_1020_359.png"},
            {"id": 6, "name": "密室6", "x": 916, "y": 758, "image": "/static/images/secrets/Deston_916_758.png"},
            {"id": 7, "name": "密室7", "x": 647, "y": 451, "image": "/static/images/secrets/Deston_647_451.png"},
            {"id": 8, "name": "密室8", "x": 635, "y": 607, "image": "/static/images/secrets/Deston_635_607.png"},
            {"id": 9, "name": "密室9", "x": 723, "y": 627, "image": "/static/images/secrets/Deston_723_627.png"},
            {"id": 10, "name": "密室10", "x": 568, "y": 840, "image": "/static/images/secrets/Deston_568_840.png"},
            {"id": 11, "name": "密室11", "x": 674, "y": 236, "image": "/static/images/secrets/Deston_674_236.png"},
            {"id": 12, "name": "密室12", "x": 1025, "y": 539, "image": "/static/images/secrets/Deston_1025_539.png"},
            {"id": 13, "name": "密室13", "x": 1173, "y": 851, "image": "/static/images/secrets/Deston_1173_851.png"},
            {"id": 14, "name": "密室14", "x": 786, "y": 68, "image": "/static/images/secrets/Deston_786_68.png"},
            {"id": 15, "name": "密室15", "x": 672, "y": 193, "image": "/static/images/secrets/Deston_672_193.png"},
            {"id": 16, "name": "密室16", "x": 833, "y": 352, "image": "/static/images/secrets/Deston_833_352.png"},
            {"id": 17, "name": "密室17", "x": 853, "y": 478, "image": "/static/images/secrets/Deston_853_478.png"}

        ]
    },
    "Vikendi": {
        "name": "维寒迪",
        "image_path": "/static/images/maps/Vikendi.jpg",
        "secret_spots": [
            {"id": 1, "name": "Ho San 监狱密室", "x": 1495, "y": 220,
             "image": "/static/images/secrets/Vikendi_1495_220.jpg"}
        ]
    }
}


# 提示: 请确保您的 /static/images/secrets/ 文件夹下有与上面 image 字段匹配的图片文件。

@secret_map_bp.route('/', methods=['GET'])
def index():
    # 将地图数据传递给模板，以便前端可以动态生成选项
    return render_template('secret_map.html', maps=MAPS_DATA)


@secret_map_bp.route('/get_map_details', methods=['POST'])
def get_map_details():
    """获取指定地图的详细信息，包括图片路径和所有密室的位置。"""
    data = request.get_json()
    map_name = data.get('map_name')

    if not map_name or map_name not in MAPS_DATA:
        return jsonify({"success": False, "error": "未知地图"}), 400

    map_info = MAPS_DATA[map_name]

    return jsonify({
        "success": True,
        "map_name": map_info["name"],
        "image_path": map_info["image_path"],
        "secret_spots": map_info["secret_spots"]  # 返回所有密室点位
    })


@secret_map_bp.route('/find_secret_by_coords', methods=['POST'])
def find_secret_by_coords():
    """根据坐标查找附近的密室。"""
    data = request.get_json()
    map_name = data.get('map_name')
    x = data.get('x')
    y = data.get('y')

    if not all([map_name, isinstance(x, (int, float)), isinstance(y, (int, float))]):
        return jsonify({"success": False, "error": "请求参数无效"}), 400

    if map_name not in MAPS_DATA:
        return jsonify({"success": False, "error": "未知地图"}), 400

    # 遍历该地图的所有密室，查找距离最近的一个
    for secret in MAPS_DATA[map_name]["secret_spots"]:
        # 使用简单的矩形范围判断是否接近
        if abs(secret["x"] - x) < PROXIMITY_THRESHOLD and abs(secret["y"] - y) < PROXIMITY_THRESHOLD:
            return jsonify({
                "success": True,
                "found": True,
                "secret_name": secret["name"],
                "secret_image": secret["image"]
            })

    # 如果没有找到
    return jsonify({"success": True, "found": False, "message": "指定坐标附近没有密室。"})

