# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # 修复Render PostgreSQL连接协议问题
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'  # 生产环境应使用强密钥
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
