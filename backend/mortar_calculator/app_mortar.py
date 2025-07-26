from flask import Blueprint, render_template, request, jsonify
import math

mortar_calculator_bp = Blueprint('mortar_calculator', __name__, template_folder='../../frontend/templates')

# <<<< 关键修改：使用新的数据结构，区分物理网格和测量基准 >>>>
MAP_SPECS = {
    # 'grid_size_m': 地图的物理网格大小，用于显示，恒为100
    # 'ref_pixels':  截图上用于测量的参考像素值
    # 'ref_meters':  参考像素值对应的游戏内实际距离（米）
    "Erangel": {"display_name": "艾伦格", "dimensions": "8x8", "grid_size_m": 100, "ref_pixels": 220,
                "ref_meters": 100},
    "Miramar": {"display_name": "米拉玛", "dimensions": "8x8", "grid_size_m": 100, "ref_pixels": 220,
                "ref_meters": 100},
    "Sanhok": {"display_name": "萨诺", "dimensions": "4x4", "grid_size_m": 100, "ref_pixels": 110, "ref_meters": 100},
    "Deston": {"display_name": "帝斯顿", "dimensions": "8x8", "grid_size_m": 100, "ref_pixels": 220, "ref_meters": 100},
    "Taego": {"display_name": "泰戈", "dimensions": "8x8", "grid_size_m": 100, "ref_pixels": 220, "ref_meters": 100},
    "Paramo": {"display_name": "帕拉莫", "dimensions": "3x3", "grid_size_m": 100, "ref_pixels": 140, "ref_meters": 100}
}


@mortar_calculator_bp.route('/', methods=['GET'])
def index():
    # 传递 MAP_SPECS 给模板，下拉框的显示将自动恢复正常
    return render_template('mortar_calculator.html', maps=MAP_SPECS)


@mortar_calculator_bp.route('/calculate', methods=['POST'])
def calculate_distance():
    try:
        data = request.get_json()

        player_x_px = float(data['player_x_px'])
        player_y_px = float(data['player_y_px'])
        target_x_px = float(data['target_x_px'])
        target_y_px = float(data['target_y_px'])
        map_name = data['map_name']

        if map_name not in MAP_SPECS:
            return jsonify({"success": False, "error": "未知地图"}), 400

        map_spec = MAP_SPECS[map_name]

        # <<<< 关键修改：使用新的、更通用的计算公式 >>>>
        # 核心公式: 游戏距离 = 像素距离 * (参考米数 / 参考像素)
        # 这个公式现在对所有地图都适用

        pixel_distance_x = target_x_px - player_x_px
        pixel_distance_y = target_y_px - player_y_px

        # 计算每一像素代表多少米
        meters_per_pixel = map_spec["ref_meters"] / map_spec["ref_pixels"]

        game_distance_x = pixel_distance_x * meters_per_pixel
        game_distance_y = pixel_distance_y * meters_per_pixel

        total_game_distance = math.sqrt(game_distance_x ** 2 + game_distance_y ** 2)

        return jsonify({
            "success": True,
            "distance": round(total_game_distance, 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"服务器计算错误: {str(e)}"}), 400
