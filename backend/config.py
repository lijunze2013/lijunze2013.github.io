import os

class Config:
    # 数据库配置（SQLite，文件存储在instance文件夹）
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全密钥（用于会话管理）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    
    # 应用配置
    DEBUG = False  # 生产环境关闭调试模式
