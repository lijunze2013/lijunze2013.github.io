

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置数据库
app.config.from_object('config.Config')
db = SQLAlchemy(app)


# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 项目模型
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 访问统计模型
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 登录装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "请先登录"}), 401
        return f(*args, **kwargs)

    return decorated_function


# 初始化数据库
@app.before_first_request
def create_tables():
    db.create_all()
    # 检查是否有管理员用户，如果没有则创建
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('li201338')  # 默认密码
        db.session.add(admin)
        db.session.commit()


# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({
            "status": "success",
            "message": "登录成功",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
    return jsonify({"status": "error", "message": "用户名或密码错误"}), 401


# 登出接口
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"status": "success", "message": "登出成功"})


# 检查登录状态
@app.route('/api/check-login', methods=['GET'])
def check_login():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            "logged_in": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
    return jsonify({"logged_in": False})


# 获取仪表盘数据
@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    # 模拟数据，实际应用中应该从数据库查询
    project_count = Project.query.count()
    visit_count = Visit.query.count()
    recent_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(5).all()

    return jsonify({
        "status": "success",
        "data": {
            "project_count": project_count,
            "visit_count": visit_count,
            "recent_visits": [
                {"page": visit.page, "time": visit.timestamp.strftime("%Y-%m-%d %H:%M")}
                for visit in recent_visits
            ]
        }
    })


# 获取个人资料
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    user = User.query.get(session['user_id'])
    if user:
        return jsonify({
            "status": "success",
            "data": {
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "avatar": user.avatar
            }
        })
    return jsonify({"status": "error", "message": "用户不存在"}), 404


# 更新个人资料
@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 404

    data = request.get_json()
    if 'email' in data:
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar' in data:
        user.avatar = data['avatar']

    db.session.commit()
    return jsonify({"status": "success", "message": "个人资料更新成功"})


# 修改密码
@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 404

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"status": "error", "message": "当前密码不正确"}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"status": "success", "message": "密码修改成功"})


# 获取所有项目
@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify({
        "status": "success",
        "data": [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "link": project.link,
                "image": project.image,
                "category": project.category,
                "created_at": project.created_at.strftime("%Y-%m-%d")
            } for project in projects
        ]
    })


# 获取单个项目
@app.route('/api/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get(id)
    if project:
        return jsonify({
            "status": "success",
            "data": {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "link": project.link,
                "image": project.image,
                "category": project.category,
                "created_at": project.created_at.strftime("%Y-%m-%d")
            }
        })
    return jsonify({"status": "error", "message": "项目不存在"}), 404


# 创建项目
@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()

    new_project = Project(
        title=data.get('title'),
        description=data.get('description'),
        link=data.get('link'),
        image=data.get('image'),
        category=data.get('category')
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "项目创建成功",
        "data": {
            "id": new_project.id,
            "title": new_project.title
        }
    }), 201


# 更新项目
@app.route('/api/projects/<int:id>', methods=['PUT'])
@login_required
def update_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({"status": "error", "message": "项目不存在"}), 404

    data = request.get_json()
    if 'title' in data:
        project.title = data['title']
    if 'description' in data:
        project.description = data['description']
    if 'link' in data:
        project.link = data['link']
    if 'image' in data:
        project.image = data['image']
    if 'category' in data:
        project.category = data['category']

    db.session.commit()
    return jsonify({"status": "success", "message": "项目更新成功"})


# 删除项目
@app.route('/api/projects/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({"status": "error", "message": "项目不存在"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"status": "success", "message": "项目删除成功"})


# 记录访问
@app.route('/api/log-visit', methods=['POST'])
def log_visit():
    data = request.get_json()
    page = data.get('page', 'unknown')

    new_visit = Visit(page=page)
    db.session.add(new_visit)
    db.session.commit()

    return jsonify({"status": "success", "message": "访问已记录"})


# 根路由
@app.route('/')
def index():
    return jsonify({"status": "success", "message": "欢迎访问我的个人博客API"})


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "接口不存在"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"status": "error", "message": "服务器内部错误"}), 500


# 启动应用
if __name__ == '__main__':
    # 确保在启动前创建数据库表
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
