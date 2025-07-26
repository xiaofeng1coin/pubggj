from flask import Flask, render_template  # 导入render_template
from backend.mortar_calculator.app_mortar import mortar_calculator_bp
from backend.secret_map.app_secret import secret_map_bp
from backend.stats_tracker.app_stats import stats_tracker_bp # <-- 1. 导入新蓝图

# 这是修改后的代码
app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')


# 注册蓝图
app.register_blueprint(mortar_calculator_bp, url_prefix='/mortar_calculator')
app.register_blueprint(secret_map_bp, url_prefix='/secret_map')
app.register_blueprint(stats_tracker_bp, url_prefix='/stats_tracker') # <-- 2. 注册新蓝图

# 主路由
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)