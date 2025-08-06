import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

class Config:
    # 优先使用 Railway 提供的 DATABASE_URL 环境变量
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../instance/site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
