# AI功能配置说明

## 环境变量配置

在使用AI解读与建议功能之前，需要配置以下环境变量：

### 1. 设置API密钥

在系统环境变量中设置：
```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key_here"
```

或者在 `.env` 文件中添加：
```
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

### 2. 获取API密钥

1. 访问阿里云百炼平台：https://bailian.console.aliyun.com/
2. 注册并登录账号
3. 在控制台中获取API密钥
4. 将密钥配置到环境变量中

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 重启服务

配置完成后，重启Flask服务：
```bash
python app.py
```

## 功能说明

### AI解读与建议模块

1. **自动分析**：点击"获取AI解读与建议"按钮，AI会自动分析宝宝的：
   - 基本信息（姓名、性别、年龄等）
   - 生长记录（身高、体重历史数据）
   - 生长发育趋势

2. **专业建议**：AI会从以下方面提供建议：
   - 生长发育评估
   - 营养建议
   - 注意事项
   - 改进建议

3. **持续对话**：用户可以继续向AI提问，获得更详细的建议

### 注意事项

- 确保网络连接正常
- API密钥有效且余额充足
- 宝宝信息完整，生长记录准确
- AI建议仅供参考，重要医疗决策请咨询专业医生 