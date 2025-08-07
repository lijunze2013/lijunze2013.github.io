import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_cors import CORS
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 配置CORS
CORS(app, supports_credentials=True, origins=[
    "https://lijunze2013.github.io",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email or '',
            'bio': self.bio or ''
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))
    image = db.Column(db.String(200))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image or 'https://picsum.photos/seed/default/300/200',
            'link': self.link or '#',
            'category': self.category or '未分类',
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 初始化默认管理员用户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('li201338')  # 默认密码
        db.session.add(admin)
        db.session.commit()
    
    # 初始化默认项目
    if not Project.query.first():
        default_projects = [
            Project(
                title='个人博客系统', 
                description='基于Flask和JavaScript构建的个人展示平台', 
                image='https://picsum.photos/seed/blog/300/200', 
                link='https://lijunze2013.github.io',
                category='Web开发'
            ),
            Project(
                title='任务管理应用', 
                description='简洁高效的任务管理工具，支持拖拽排序', 
                image='https://picsum.photos/seed/task/300/200', 
                link='#',
                category='应用程序'
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

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# 管理后台路由
@app.route('/admin/')
@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/projects')
def admin_projects():
    return render_template('admin/projects.html')

@app.route('/admin/profile')
def admin_profile():
    return render_template('admin/profile.html')

@app.route('/admin/settings')
def admin_settings():
    return render_template('admin/settings.html')

# API - 登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        session['username'] = user.username
        user.last_login = datetime.now()
        db.session.commit()
        return jsonify({'status': 'success', 'message': '登录成功'})
    
    return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

# API - 登出
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': '已退出登录'})

# API - 检查登录状态
@app.route('/api/check-login', methods=['GET'])
def check_login():
    logged_in = 'username' in session
    user_data = None
    if logged_in:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_data = user.to_dict()
            
    return jsonify({
        'status': 'success',
        'logged_in': logged_in,
        'user': user_data
    })

# API - 获取仪表盘数据
@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    user = User.query.filter_by(username=session['username']).first()
    project_count = Project.query.count()
    
    return jsonify({
        'status': 'success',
        'dashboard': {
            'stats': {
                'total_visits': 128,  # 模拟数据
                'project_count': project_count,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未登录'
            }
        }
    })

# API - 获取项目列表
@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify({
        'status': 'success',
        'projects': [p.to_dict() for p in projects]
    })

# API - 获取单个项目
@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'status': 'success',
        'project': project.to_dict()
    })

# API - 创建项目
@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    new_project = Project(
        title=data.get('title'),
        description=data.get('description'),
        image=data.get('image'),
        link=data.get('link'),
        category=data.get('category')
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': '项目创建成功',
        'project': new_project.to_dict()
    })

# API - 更新项目
@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.image = data.get('image', project.image)
    project.link = data.get('link', project.link)
    project.category = data.get('category', project.category)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': '项目更新成功',
        'project': project.to_dict()
    })

# API - 删除项目
@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '项目已删除'})

# API - 更新个人资料
@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    user = User.query.filter_by(username=session['username']).first()
    data = request.get_json()
    
    user.email = data.get('email', user.email)
    user.bio = data.get('bio', user.bio)
    
    # 如果提供了新密码则更新密码
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '个人资料更新成功',
        'user': user.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)
    