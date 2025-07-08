# 宝宝成长记录系统部署指南

## 系统概述

宝宝成长记录系统是一个基于Flask的Web应用，提供儿童生长发育记录、生长曲线分析和AI智能解读功能。系统支持多用户管理，每个用户可以管理自己的宝宝信息。

### 主要功能

- 用户注册和登录
- 用户密码修改
- 宝宝信息管理（添加、编辑、删除）
- 生长记录管理（添加、删除）
- 生长曲线图表展示
- AI智能解读与建议
- 用户数据隔离

## 技术栈

- **后端**: Flask + SQLite + JWT认证
- **前端**: Vue.js + Bootstrap + Chart.js
- **AI**: 集成大语言模型API
- **数据库**: SQLite

## 部署步骤

### 1. 环境准备

确保系统已安装：
- Python 3.7+
- pip包管理器

### 2. 下载代码

```bash
git clone <repository_url>
cd 宝宝成长记录
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库初始化

执行数据库迁移脚本：

```bash
# 方法1：使用SQLite命令行
sqlite3 baby_growth.db < database_migration.sql

# 方法2：使用Python脚本
python -c "
import sqlite3
with open('database_migration.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
conn = sqlite3.connect('baby_growth.db')
conn.executescript(sql)
conn.close()
print('数据库初始化完成')
"
```

### 5. 配置环境变量

创建 `.env` 文件：

```env
# Flask配置
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# AI API配置（可选）
AI_API_KEY=your-ai-api-key
AI_API_URL=https://api.openai.com/v1/chat/completions

# 数据库配置
DATABASE_URL=sqlite:///baby_growth.db

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### 6. 创建上传目录

```bash
mkdir uploads
```

### 7. 启动应用

#### 开发环境
```bash
python app.py
```

#### 生产环境
```bash
# 使用gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 或使用uwsgi
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --module app:app --processes 4
```

### 8. 配置Web服务器（可选）

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/app/static/;
    }

    location /uploads/ {
        alias /path/to/your/app/uploads/;
    }
}
```

## 系统配置

### 1. 前端配置

修改 `frontend/config.js`：

```javascript
window.config = {
    BACKEND_URL: 'http://your-domain.com'  // 生产环境URL
};
```

### 2. CORS配置

在生产环境中，修改 `app.py` 中的CORS配置：

```python
CORS(app, origins=[
    'http://your-domain.com',
    'https://your-domain.com'
])
```

### 3. 安全配置

- 修改 `SECRET_KEY` 为强密码
- 启用HTTPS
- 配置防火墙
- 定期备份数据库

## 数据备份

### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_FILE="baby_growth.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_FILE $BACKUP_DIR/baby_growth_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# 删除7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

设置定时任务：

```bash
# 编辑crontab
crontab -e

# 添加每日备份任务
0 2 * * * /path/to/backup.sh
```

## 监控和维护

### 1. 日志监控

配置日志轮转：

```bash
# 创建logrotate配置
sudo nano /etc/logrotate.d/baby-growth

/path/to/your/app/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 2. 性能监控

使用工具监控系统性能：
- htop - 系统资源监控
- iotop - 磁盘I/O监控
- netstat - 网络连接监控

### 3. 数据库维护

定期优化数据库：

```sql
-- 清理过期数据
DELETE FROM baby_records WHERE date < date('now', '-5 years');

-- 优化数据库
VACUUM;
ANALYZE;
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件权限
   - 确认数据库路径正确

2. **文件上传失败**
   - 检查uploads目录权限
   - 确认磁盘空间充足

3. **AI功能异常**
   - 检查AI API配置
   - 确认网络连接正常

4. **CORS错误**
   - 检查前端配置
   - 确认后端CORS设置

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看系统日志
sudo journalctl -u baby-growth -f
```

## 更新部署

### 1. 备份当前版本

```bash
# 备份代码
cp -r /path/to/app /path/to/backup/app_$(date +%Y%m%d)

# 备份数据库
cp baby_growth.db baby_growth_backup_$(date +%Y%m%d).db
```

### 2. 更新代码

```bash
git pull origin main
```

### 3. 更新依赖

```bash
pip install -r requirements.txt
```

### 4. 执行数据库迁移

```bash
sqlite3 baby_growth.db < database_migration.sql
```

### 5. 重启服务

```bash
sudo systemctl restart baby-growth
```



## 联系支持

如有问题，请联系技术支持团队。 