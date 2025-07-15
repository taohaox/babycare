from flask import Flask, request, jsonify, send_from_directory, current_app, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import logging
from config import Config
import pymysql
import functools
import base64
import time
from functools import wraps
from openai import OpenAI
import json
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# 配置 PyMySQL
pymysql.install_as_MySQLdb()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# JWT配置
jwt_secret = os.getenv('JWT_SECRET_KEY')
if not jwt_secret:
    raise RuntimeError('JWT_SECRET_KEY 环境变量未设置，服务无法启动！')
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 初始化OpenAI客户端
try:
    logger.info('DASHSCOPE_API_KEY:'+os.getenv("DASHSCOPE_API_KEY"))
    ai_client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    logger.info("AI客户端初始化成功")
except Exception as e:
    logger.error(f"AI客户端初始化失败: {str(e)}")
    ai_client = None

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": [Config.FRONTEND_URL,"*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    
})

# 配置数据库
db = SQLAlchemy(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# JWT工具函数
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': '无效或过期的认证令牌'}), 401
        
        # 将用户ID添加到请求上下文
        request.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# 创建日志装饰器
def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app.logger.info(f"请求路径: {request.path}")
        app.logger.info(f"请求方法: {request.method}")
        app.logger.info(f"请求参数: {request.get_json()}")
        
        response = f(*args, **kwargs)
        
        # 检查响应是否是元组（状态码和响应体）
        if isinstance(response, tuple):
            status_code = response[1]
            app.logger.info(f"响应状态码: {status_code}")
        else:
            app.logger.info(f"响应状态码: {response.status_code}")
        
        return response
    return decorated_function

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    babies = db.relationship('Baby', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

# 宝宝模型
class Baby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_time = db.Column(db.Time, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'birth_time': self.birth_time.strftime('%H:%M:%S') if self.birth_time else None,
            'gender': self.gender,
            'photo': self.photo,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'user_id': self.user_id
        }

# 身高体重记录模型
class GrowthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('baby.id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    height = db.Column(db.Float, nullable=False)  # 身高(cm)
    weight = db.Column(db.Float, nullable=False)  # 体重(kg)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 用户注册接口
@app.route('/api/register', methods=['POST'])
@log_request
def register():
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': '邮箱和密码是必填项'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # 验证邮箱格式
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'message': '邮箱格式不正确'}), 400
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'message': '密码长度至少6位'}), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'message': '该邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 生成JWT令牌
        token = generate_token(user.id)
        
        return jsonify({
            'message': '注册成功',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"用户注册失败: {str(e)}")
        return jsonify({'message': '注册失败，请重试'}), 500

# 用户登录接口
@app.route('/api/login', methods=['POST'])
@log_request
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': '邮箱和密码是必填项'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # 查找用户
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': '邮箱或密码错误'}), 401
        
        # 生成JWT令牌
        token = generate_token(user.id)
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return jsonify({'message': '登录失败，请重试'}), 500

# 获取当前用户信息
@app.route('/api/user', methods=['GET'])
@login_required
def get_current_user():
    try:
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'message': '获取用户信息失败'}), 500

# 修改密码接口
@app.route('/api/user/change-password', methods=['POST'])
@login_required
@log_request
def change_password():
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': '当前密码和新密码是必填项'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # 验证新密码长度
        if len(new_password) < 6:
            return jsonify({'message': '新密码长度至少6位'}), 400
        
        # 获取当前用户
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 验证当前密码
        if not user.check_password(current_password):
            return jsonify({'message': '当前密码错误'}), 400
        
        # 检查新密码是否与当前密码相同
        if user.check_password(new_password):
            return jsonify({'message': '新密码不能与当前密码相同'}), 400
        
        # 更新密码
        user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"用户 {user.email} 修改密码成功")
        return jsonify({'message': '密码修改成功'})
        
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '修改密码失败，请重试'}), 500

# 修改宝宝列表接口，只返回当前用户的宝宝
@app.route('/api/babies', methods=['GET'])
@login_required
@log_request
def get_babies():
    try:
        logger.info("开始获取宝宝列表")
        babies = Baby.query.filter_by(user_id=request.current_user_id).all()
        result = [{
            'id': baby.id,
            'name': baby.name,
            'photo': baby.photo,
            'birth_date': baby.birth_date.strftime('%Y-%m-%d'),
            'birth_time': baby.birth_time.strftime('%H:%M:%S') if baby.birth_time else None,
            'gender': baby.gender
        } for baby in babies]
        logger.info(f"成功获取宝宝列表，共 {len(result)} 条记录")
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取宝宝列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 修改创建宝宝接口，自动关联当前用户
@app.route('/api/babies', methods=['POST'])
@login_required
@log_request
def create_baby():
    try:
        data = request.get_json()
        app.logger.info(f"请求参数: {data}")
        
        # 验证必填字段
        required_fields = ['name', 'birth_date', 'gender']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 是必填项'}), 400
        
        # 处理日期和时间
        birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        birth_time = None
        if data.get('birth_time'):
            birth_time = datetime.strptime(data['birth_time'], '%H:%M:%S').time()
        
        # 创建新宝宝记录，自动关联当前用户
        baby = Baby(
            name=data['name'],
            birth_date=birth_date,
            birth_time=birth_time,
            gender=data['gender'],
            photo=data.get('photo'),
            user_id=request.current_user_id
        )
        
        db.session.add(baby)
        db.session.commit()
        
        return jsonify(baby.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建宝宝信息失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

# 修改获取宝宝详情接口，验证用户权限
@app.route('/api/babies/<int:id>', methods=['GET'])
@login_required
def get_baby(id):
    try:
        baby = Baby.query.filter_by(id=id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限访问'}), 404
        
        return jsonify(baby.to_dict())
    except Exception as e:
        logger.error(f"获取宝宝信息失败: {str(e)}")
        return jsonify({'message': '获取宝宝信息失败'}), 500

# 修改更新宝宝接口，验证用户权限
@app.route('/api/babies/<int:id>', methods=['PUT'])
@login_required
@log_request
def update_baby(id):
    try:
        baby = Baby.query.filter_by(id=id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限修改'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            baby.name = data['name']
        if 'birth_date' in data:
            baby.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        if 'birth_time' in data:
            if data['birth_time']:
                baby.birth_time = datetime.strptime(data['birth_time'], '%H:%M:%S').time()
            else:
                baby.birth_time = None
        if 'gender' in data:
            baby.gender = data['gender']
        if 'photo' in data:
            baby.photo = data['photo']
        
        baby.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(baby.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新宝宝信息失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

# 修改删除宝宝接口，验证用户权限
@app.route('/api/babies/<int:id>', methods=['DELETE'])
@login_required
@log_request
def delete_baby(id):
    try:
        baby = Baby.query.filter_by(id=id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限删除'}), 404
        
        # 删除相关的生长记录
        GrowthRecord.query.filter_by(baby_id=id).delete()
        
        # 删除宝宝
        db.session.delete(baby)
        db.session.commit()
        
        return jsonify({'message': '宝宝删除成功'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除宝宝失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

# 修改获取宝宝记录接口，验证用户权限
@app.route('/api/babies/<int:baby_id>/records', methods=['GET'])
@login_required
def get_baby_records(baby_id):
    try:
        # 验证宝宝是否属于当前用户
        baby = Baby.query.filter_by(id=baby_id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限访问'}), 404
        
        records = GrowthRecord.query.filter_by(baby_id=baby_id).order_by(GrowthRecord.record_date.desc()).all()
        return jsonify([{
            'id': record.id,
            'date': record.record_date.strftime('%Y-%m-%d'),
            'height': record.height,
            'weight': record.weight
        } for record in records])
    except Exception as e:
        logger.error(f"获取宝宝记录失败: {str(e)}")
        return jsonify({'message': '获取宝宝记录失败'}), 500

# 修改添加宝宝记录接口，验证用户权限
@app.route('/api/babies/<int:baby_id>/records', methods=['POST'])
@login_required
@log_request
def add_baby_record(baby_id):
    try:
        # 验证宝宝是否属于当前用户
        baby = Baby.query.filter_by(id=baby_id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限操作'}), 404
        
        data = request.get_json()
        
        if not data.get('date') or not data.get('height') or not data.get('weight'):
            return jsonify({'message': '日期、身高、体重都是必填项'}), 400
        
        record = GrowthRecord(
            baby_id=baby_id,
            record_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            height=float(data['height']),
            weight=float(data['weight'])
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'id': record.id,
            'date': record.record_date.strftime('%Y-%m-%d'),
            'height': record.height,
            'weight': record.weight
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加宝宝记录失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

# 修改删除宝宝记录接口，验证用户权限
@app.route('/api/babies/<int:baby_id>/records/<int:record_id>', methods=['DELETE'])
@login_required
@log_request
def delete_baby_record(baby_id, record_id):
    try:
        # 验证宝宝是否属于当前用户
        baby = Baby.query.filter_by(id=baby_id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限操作'}), 404
        
        record = GrowthRecord.query.filter_by(id=record_id, baby_id=baby_id).first()
        if not record:
            return jsonify({'message': '记录不存在'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': '记录删除成功'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除宝宝记录失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

# 修改AI分析接口，验证用户权限
@app.route('/api/babies/<int:baby_id>/ai-analysis', methods=['POST'])
@login_required
@log_request
def get_ai_analysis(baby_id):
    try:
        # 验证宝宝是否属于当前用户
        baby = Baby.query.filter_by(id=baby_id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'message': '宝宝不存在或无权限访问'}), 404
        if ai_client is None:
            return jsonify({'success': False, 'message': 'AI服务未正确配置，请检查API密钥'}), 500
        records = GrowthRecord.query.filter_by(baby_id=baby_id).order_by(GrowthRecord.record_date).all()
        from datetime import date
        today = date.today()
        age_days = (today - baby.birth_date).days
        age_months = age_days / 30.44
        age_years = age_days / 365.25
        gender = baby.gender
        if gender == '男':
            std_file = os.path.join('config', 'growth_curve_boy.json')
        else:
            std_file = os.path.join('config', 'growth_curve_gril.json')
        try:
            with open(std_file, 'r', encoding='utf-8') as f:
                std_data = json.load(f)
            std_summary = json.dumps({
                'units': std_data['growth_curve'].get('units'),
                'percentile_data': std_data['growth_curve'].get('percentile_data'),
                'notes': std_data['growth_curve'].get('notes')
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            std_summary = '（未能加载生长标准资料）'
        baby_info = f"""
宝宝基本信息：
- 姓名：{baby.name}
- 性别：{baby.gender}
- 出生日期：{baby.birth_date}
- 当前年龄：{age_years:.1f}岁（{age_months:.1f}个月）
"""
        if records:
            growth_info = "\n生长记录：\n"
            for record in records:
                record_age_days = (record.record_date - baby.birth_date).days
                record_age_months = record_age_days / 30.44
                growth_info += f"- {record.record_date}（{record_age_months:.1f}个月）：身高{record.height}cm，体重{record.weight}kg\n"
        else:
            growth_info = "\n暂无生长记录"
        data = request.get_json() or {}
        user_message = data.get('message', '')
        std_prompt = f"以下是儿童生长标准资料（请结合分析）：\n{std_summary}\n"
        if not user_message:
            system_prompt = """你是一位专业的儿科医生和儿童生长发育专家。请根据提供的宝宝信息、生长记录和生长标准资料，给出专业的生长发育解读和建议。\n\n请从以下几个方面进行分析：\n1. 生长发育评估：根据年龄、身高、体重数据评估宝宝的生长发育情况\n2. 百分位分析：结合生长标准资料，分析宝宝在同龄儿童中的位置\n3. 营养建议：根据生长发育情况给出营养建议\n4. 注意事项：提醒家长需要注意的事项\n5. 建议：给出具体的改进建议或继续保持的建议\n\n请用通俗易懂的语言回答，避免过于专业的医学术语。"""
            user_prompt = f"{std_prompt}{baby_info}{growth_info}\n\n请对这位宝宝的生长发育情况进行专业解读和建议。"
        else:
            system_prompt = """你是一位专业的儿科医生和儿童生长发育专家。请根据之前的对话、宝宝信息和生长标准资料，继续为用户提供专业的建议和解答。\n\n请保持专业、耐心、友好的态度，用通俗易懂的语言回答用户的问题。"""
            user_prompt = f"{std_prompt}{baby_info}{growth_info}\n\n用户问题：{user_message}"
        logger.info(f"发送AI请求，用户消息长度: {len(user_message)}")
        def generate():
            try:
                completion = ai_client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True
                )
                for chunk in completion:
                    delta = getattr(chunk.choices[0], 'delta', None)
                    if delta and getattr(delta, 'content', None):
                        # SSE格式，前端可直接用fetch+EventSource接收
                        yield f"data: {delta.content}\n\n"
            except Exception as e:
                yield f"data: [AI分析失败] {str(e)}\n\n"
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"AI分析失败: {str(e)}")
        return jsonify({'success': False, 'message': f'AI分析失败: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
@log_request
def upload_file():
    try:
        app.logger.info("开始处理文件上传")
        if 'file' not in request.files:
            app.logger.error("没有文件")
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            app.logger.error("没有选择文件")
            return jsonify({'error': '没有选择文件'}), 400
            
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            filename = f"{int(time.time())}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(file_path)
            app.logger.info(f"文件保存成功: {file_path}")
            
            # 返回文件URL
            file_url = f'/api/uploads/{filename}'
            return jsonify({
                'message': '文件上传成功',
                'url': file_url
            })
        else:
            app.logger.error("不支持的文件类型")
            return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 提供上传文件的访问
@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/config/<filename>')
def config_file(filename):
    return send_from_directory('config', filename)

@app.route('/api/babies/<int:baby_id>/photo', methods=['POST'])
@login_required
@log_request
def update_baby_photo(baby_id):
    try:
        baby = Baby.query.filter_by(id=baby_id, user_id=request.current_user_id).first()
        if not baby:
            return jsonify({'error': '宝宝不存在'}), 404

        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        # 保存新图片
        filename = secure_filename(f"{baby_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 可选：删除旧图片文件
        if baby.photo:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(baby.photo))
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        # 更新数据库
        baby.photo = f'/api/uploads/{filename}'
        db.session.commit()

        return jsonify({'success': True, 'photo': baby.photo})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {str(e)}")
    app.run(host=Config.BACKEND_HOST, port=Config.BACKEND_PORT, debug=True) 