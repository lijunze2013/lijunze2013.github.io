from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化数据库
db = SQLAlchemy()

class User(db.Model):
    """用户模型（用于登录验证）"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 设置密码（加密存储）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    """项目模型（用于展示个人项目）"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(200))  # 项目链接
    image = db.Column(db.String(200))  # 项目图片路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
