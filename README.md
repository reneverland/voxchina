# VoxChina AI Platform

VoxChina 智能内容生成与知识管理平台

---

## 🚀 服务架构

- **后端**: FastAPI (端口 8300)
- **前端**: Vue 3 + Vite (端口 8400)
- **管理**: Supervisor 守护进程

---

## 📦 Supervisor 配置

### 后端配置

```ini
[program:voxchina_backend]
command=/www/wwwroot/voxchina/backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1
directory=/www/wwwroot/voxchina/backend
user=www
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=60
stdout_logfile=/www/wwwroot/voxchina/backend/logs/supervisor_out.log
stderr_logfile=/www/wwwroot/voxchina/backend/logs/supervisor_err.log
```

### 前端配置

```ini
[program:voxchina_frontend]
command=/usr/bin/node node_modules/vite/bin/vite.js --host 0.0.0.0 --port 8400
directory=/www/wwwroot/voxchina/frontend
user=www
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=60
environment=NODE_ENV="development"
stdout_logfile=/www/wwwroot/voxchina/frontend/logs/supervisor_out.log
stderr_logfile=/www/wwwroot/voxchina/frontend/logs/supervisor_err.log
```

---

## 🔧 管理命令

### 后端

```bash
# 手动测试
cd /www/wwwroot/voxchina/backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8300

# Supervisor 管理
supervisorctl status voxchina_backend
supervisorctl start voxchina_backend
supervisorctl stop voxchina_backend
supervisorctl restart voxchina_backend
```

### 前端

```bash
# 手动测试
cd /www/wwwroot/voxchina/frontend
npm run dev

# Supervisor 管理
supervisorctl status voxchina_frontend
supervisorctl start voxchina_frontend
supervisorctl stop voxchina_frontend
supervisorctl restart voxchina_frontend
```

---

## 🧪 验证服务

### 后端
```bash
curl http://localhost:8300/health
# 浏览器: http://你的IP:8300/docs
```

### 前端
```bash
curl http://localhost:8400/
# 浏览器: http://你的IP:8400/
```

---

## 📁 项目结构

```
voxchina/
├── backend/                # 后端服务
│   ├── app/               # 应用代码
│   ├── venv/              # Python 虚拟环境
│   ├── requirements.txt   # 依赖列表
│   ├── main.py           # 入口文件
│   └── supervisor_voxchina.conf  # Supervisor配置
│
├── frontend/              # 前端服务
│   ├── src/              # 源代码
│   ├── package.json      # 依赖配置
│   └── supervisor_frontend.conf  # Supervisor配置
│
└── README.md             # 本文件
```

---

## 🔐 防火墙

确保开放以下端口：
- **8300**: 后端 API
- **8400**: 前端界面

```bash
# firewalld
firewall-cmd --zone=public --add-port=8300/tcp --permanent
firewall-cmd --zone=public --add-port=8400/tcp --permanent
firewall-cmd --reload

# ufw
ufw allow 8300/tcp
ufw allow 8400/tcp
```

---

## 📝 日志位置

- 后端: `/www/wwwroot/voxchina/backend/logs/`
- 前端: `/www/wwwroot/voxchina/frontend/logs/`

---

## 👤 作者

**Ren CBIT**  
GitHub: https://github.com/reneverland/

---

## 📄 许可

Copyright © 2026 VoxChina
