# 宝宝成长记录系统

这是一个用于记录宝宝成长信息的Web应用系统，包括宝宝基本信息和身高体重记录功能。

## 功能特点

1. 宝宝管理
   - 添加宝宝基本信息（姓名、照片、出生日期、出生时间、性别）
   - 查看宝宝列表
   - 上传宝宝照片

2. 成长记录
   - 记录宝宝身高体重数据
   - 按日期查看成长记录

## 技术栈

- 前端：Vue.js + Element UI
- 后端：Python Flask
- 数据库：MySQL
- ORM：SQLAlchemy

## 安装步骤

1. 安装Python依赖（使用清华源加速）
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. 配置环境变量（推荐，安全性更高）
- 数据库连接字符串：
  - 设置环境变量 `SQLALCHEMY_DATABASE_URI`，如：
    ```bash
    export SQLALCHEMY_DATABASE_URI='mysql+pymysql://用户名:密码@localhost/baby_growth'
    ```
- JWT密钥：
  - 设置环境变量 `JWT_SECRET_KEY`，如：
    ```bash
    export JWT_SECRET_KEY='your-very-secret-key'
    ```

3. 运行后端服务
```bash
python app.py
```

4. 运行前端
- 使用任意Web服务器托管frontend目录
- 或使用Python的简单HTTP服务器：
```bash
cd frontend
python -m http.server 8080
```

5. 访问应用
- 打开浏览器访问：http://localhost:8080

## 使用说明

1. 添加宝宝
   - 点击"添加宝宝"按钮
   - 填写宝宝信息
   - 上传宝宝照片
   - 点击确定保存

2. 添加成长记录
   - 在宝宝卡片中点击"添加成长记录"按钮
   - 选择记录日期
   - 输入身高和体重数据
   - 点击确定保存

## 注意事项

1. 必须设置环境变量 `JWT_SECRET_KEY`，否则后端无法启动
2. 如需自定义数据库连接，建议通过 `SQLALCHEMY_DATABASE_URI` 环境变量配置
3. 确保MySQL服务已启动
4. 确保uploads目录具有写入权限
5. 照片上传大小限制为5MB
6. 建议定期备份数据库 