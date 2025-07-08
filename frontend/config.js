// 服务器配置
const config = {
    // 前端服务器配置
    FRONTEND_HOST: 'localhost',
    FRONTEND_PORT: 8080,
    // 后端主机
    // BACKEND_HOST: 'babyapi.gonyb.com',
    // // 后端端口（如有需要可填写，如 8080；如 80/443 可留空）
    // BACKEND_PORT: '',

    BACKEND_HOST: 'localhost:5000',
    // 后端端口（如有需要可填写，如 8080；如 80/443 可留空）
};

// 自动拼接 API 基础地址，支持 http/https
window.API_BASE = `${window.location.protocol}//${config.BACKEND_HOST}/api`;

// 其他配置依然可通过 window.config 访问
window.config = config; 