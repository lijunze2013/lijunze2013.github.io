from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from functools import wraps
from models import db, User, Project
from config import config

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(config['default'])

# 初始化数据库
db.init_app(app)

# 配置CORS，允许前端跨域访问
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5500",  # 本地开发常见端口
    "http://127.0.0.1:5500",
    "https://yourusername.github.io"  # GitHub Pages地址
])

# 创建数据存储目录和初始数据
with app.app_context():
    # 创建数据库目录
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    # 创建所有数据表
    db.create_all()
    
    # 检查是否有管理员用户，如果没有则创建默认管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('li201338')  # 默认密码
        db.session.add(admin)
        db.session.commit()
    
    # 添加默认项目（如果没有）
    if not Project.query.first():
        default_projects = [
            Project(
                name='个人博客系统',
                description='基于Flask和原生前端技术构建的个人博客系统，支持项目展示和个人信息管理。',
                image='static/images/placeholder.jpg',
                link='#'
            ),
            Project(
                name='任务管理应用',
                description='一款简洁高效的任务管理工具，支持任务创建、分类和进度跟踪。',
                image='static/images/placeholder.jpg',
                link='#'
            ),
            Project(
                name='数据可视化平台',
                description='基于Python的数据可视化工具，能够生成各种交互式图表和数据报表。',
                image='static/images/placeholder.jpg',
                link='#'
            )
        ]
        db.session.add_all(default_projects)
        db.session.commit()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 认证接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        # 登录成功，设置会话
        session['username'] = username
        # 记录最后登录时间
        user.last_login = datetime.now()
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '登录成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    # 清除会话
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': '已退出登录'})

@app.route('/api/check-login', methods=['GET'])
def check_login():
    # 检查用户是否登录
    if 'username' in session:
        return jsonify({'status': 'success', 'logged_in': True})
    else:
        return jsonify({'status': 'success', 'logged_in': False})

# 控制面板数据接口
@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 获取统计数据
    user = User.query.filter_by(username=session['username']).first()
    
    # 模拟访问量数据
    total_visits = 128
    
    # 格式化最后登录时间
    last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未登录'
    
    return jsonify({
        'status': 'success',
        'dashboard': {
            'stats': {
                'total_visits': total_visits,
                'last_login': last_login
            }
        }
    })

# 项目管理接口
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取所有项目列表"""
    projects = Project.query.all()
    return jsonify({
        'status': 'success',
        'projects': [project.to_dict() for project in projects]
    })

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取单个项目详情"""
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'status': 'success',
        'project': project.to_dict()
    })

@app.route('/api/projects', methods