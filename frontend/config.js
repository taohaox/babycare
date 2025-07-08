// 服务器配置
const config = {
    // 后端服务器配置
    BACKEND_HOST: 'localhost',
    BACKEND_PORT: 5000,
    get BACKEND_URL() {
        return `http://${this.BACKEND_HOST}:${this.BACKEND_PORT}`;
    },
    
    // 前端服务器配置
    FRONTEND_HOST: 'localhost',
    FRONTEND_PORT: 8080,
    get FRONTEND_URL() {
        return `http://${this.FRONTEND_HOST}:${this.FRONTEND_PORT}`;
    }
};

// 导出配置
window.config = config; 