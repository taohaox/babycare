# 宝宝成长记录系统 API 文档

## 基础信息
- 基础URL: `http://localhost:5000`
- 内容类型: `application/json`
- 字符编码: `UTF-8`

## 认证方式
除了注册和登录接口外，所有API请求都需要在请求头中包含JWT token：
```
Authorization: Bearer <your_jwt_token>
```

## 用户认证系统

### 1. 用户注册
**POST** `/api/register`

**请求体：**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**响应：**
```json
{
    "message": "注册成功",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "created_at": "2024-01-01 12:00:00"
    }
}
```

### 2. 用户登录
**POST** `/api/login`

**请求体：**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**响应：**
```json
{
    "message": "登录成功",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "created_at": "2024-01-01 12:00:00"
    }
}
```

### 3. 获取当前用户信息
**GET** `/api/user`

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01 12:00:00"
}
```

### 4. 修改密码
**POST** `/api/user/change-password`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "current_password": "oldpassword123",
    "new_password": "newpassword123"
}
```

**响应：**
```json
{
    "message": "密码修改成功"
}
```

**错误响应：**
```json
{
    "message": "当前密码错误"
}
```

## 宝宝管理（需要登录）

### 5. 获取宝宝列表
**GET** `/api/babies`

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
[
    {
        "id": 1,
        "name": "小明",
        "photo": "http://localhost:5000/uploads/photo.jpg",
        "birth_date": "2023-01-01",
        "birth_time": "10:30:00",
        "gender": "男"
    }
]
```

### 6. 创建宝宝
**POST** `/api/babies`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "name": "小明",
    "birth_date": "2023-01-01",
    "birth_time": "10:30:00",
    "gender": "男",
    "photo": "/uploads/photo.jpg"
}
```

### 7. 获取宝宝详情
**GET** `/api/babies/<id>`

**请求头：**
```
Authorization: Bearer <token>
```

### 8. 更新宝宝信息
**PUT** `/api/babies/<id>`

**请求头：**
```
Authorization: Bearer <token>
```

### 9. 删除宝宝
**DELETE** `/api/babies/<id>`

**请求头：**
```
Authorization: Bearer <token>
```

## 生长记录管理（需要登录）

### 10. 获取宝宝生长记录
**GET** `/api/babies/<baby_id>/records`

**请求头：**
```
Authorization: Bearer <token>
```

### 11. 添加生长记录
**POST** `/api/babies/<baby_id>/records`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "date": "2024-01-01",
    "height": 75.5,
    "weight": 8.2
}
```

### 12. 删除生长记录
**DELETE** `/api/babies/<baby_id>/records/<record_id>`

**请求头：**
```
Authorization: Bearer <token>
```

## AI分析（需要登录）

### 13. AI解读与建议
**POST** `/api/babies/<baby_id>/ai-analysis`

**请求头：**
```
Authorization: Bearer <token>
```

**请求体：**
```json
{
    "message": "宝宝最近不爱吃饭怎么办？"
}
```

**响应：**
```json
{
    "success": true,
    "message": "AI分析结果...",
    "baby_info": "宝宝基本信息...",
    "growth_info": "生长记录..."
}
```

## 文件上传

### 13. 上传文件
**POST** `/api/upload`

**请求体：**
```
multipart/form-data
file: <file>
```

## 配置文件访问

### 14. 获取配置文件
**GET** `/config/<filename>`

例如：`/config/growth_curve_boy.json`

## 认证说明

1. **JWT Token**：登录成功后返回的token，有效期为24小时
2. **请求头格式**：`Authorization: Bearer <token>`
3. **权限控制**：用户只能操作自己的宝宝和记录
4. **错误响应**：
   - 401：未认证或token无效
   - 403：无权限访问
   - 404：资源不存在

## 环境变量配置

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=baby_growth
DB_USER=root
DB_PASSWORD=your_password

# 前端URL
FRONTEND_URL=http://localhost:8080

# 后端URL
BACKEND_URL=http://localhost:5000

# 上传文件夹
UPLOAD_FOLDER=uploads

# AI配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# JWT配置
JWT_SECRET_KEY=your-secret-key-change-in-production
``` 