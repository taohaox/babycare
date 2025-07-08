import os
import requests

# 创建目录
os.makedirs('frontend/js', exist_ok=True)
os.makedirs('frontend/css', exist_ok=True)
os.makedirs('frontend/css/fonts', exist_ok=True)

# 需要下载的文件列表
files = {
    'frontend/js/vue.min.js': 'https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.min.js',
    'frontend/js/axios.min.js': 'https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js',
    'frontend/js/moment.min.js': 'https://cdn.jsdelivr.net/npm/moment@2.29.1/moment.min.js',
    'frontend/js/moment-zh-cn.js': 'https://cdn.jsdelivr.net/npm/moment@2.29.1/locale/zh-cn.js',
    'frontend/js/sweetalert2.all.min.js': 'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.all.min.js',
    'frontend/css/bootstrap-icons.css': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css',
    'frontend/css/fonts/bootstrap-icons.woff': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/fonts/bootstrap-icons.woff',
    'frontend/css/fonts/bootstrap-icons.woff2': 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/fonts/bootstrap-icons.woff2'
}

# 下载文件
for file_path, url in files.items():
    print(f'下载 {url} 到 {file_path}')
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查是否下载成功
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f'成功下载 {file_path}')
    except Exception as e:
        print(f'下载 {file_path} 失败: {str(e)}')

print('所有文件下载完成') 