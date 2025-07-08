# 服务器配置
class Config:
    # 后端服务器配置
    BACKEND_HOST = 'localhost'
    BACKEND_PORT = 5000
    BACKEND_URL = f'http://{BACKEND_HOST}:{BACKEND_PORT}'
    
    # 前端服务器配置
    FRONTEND_HOST = 'localhost'
    FRONTEND_PORT = 8080
    FRONTEND_URL = f'http://{FRONTEND_HOST}:{FRONTEND_PORT}'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://baby_growth:TpK7JeW3ZJC45BNE@192.168.187.128/baby_growth'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 