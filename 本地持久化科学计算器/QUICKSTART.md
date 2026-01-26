# 快速启动指南

## 🚀 快速开始（3 步完成）

### 1. 安装依赖

```bash
# 安装后端依赖
cd backend
npm install

# 安装前端依赖
cd ../frontend
npm install
```

### 2. 启动开发服务器

**终端 1 - 启动后端：**

**Bash/CMD：**
```bash
cd backend
npm run dev
```

**PowerShell：**
```powershell
cd backend
npm run dev
```

后端运行在 `http://localhost:3000`

**终端 2 - 启动前端：**

**Bash/CMD：**
```bash
cd frontend
npm run dev
```

**PowerShell：**
```powershell
cd frontend
npm run dev
```

前端运行在 `http://localhost:5173`

### 3. 打开浏览器

访问 `http://localhost:5173` 开始使用计算器！

## 📦 生产环境部署

### 构建前端

```bash
cd frontend
npm run build
```

### 启动生产服务器

**Bash/CMD：**
```bash
cd backend
NODE_ENV=production npm start
```

**PowerShell：**
```powershell
cd backend
$env:NODE_ENV="production"
npm start
```

访问 `http://localhost:3000`

## ✨ 功能说明

### 基本操作

- **数字输入**：点击数字按钮或使用键盘 `0-9`
- **运算符**：点击 `+`、`-`、`×`、`÷` 或使用键盘对应键
- **括号**：点击 `(` `)` 或使用键盘括号键
- **计算**：点击 `=` 或按 `Enter`
- **清除**：点击 `C` 或按 `Escape`/`Delete`
- **回删**：点击 `⌫` 或按 `Backspace`

### 高级功能

- **历史记录**：所有计算自动保存
- **点击填充**：点击历史记录项，表达式自动填充到计算器
- **删除记录**：点击历史记录项的 `×` 按钮删除
- **清空历史**：点击"清空"按钮批量删除所有记录
- **主题切换**：点击右上角 ☀️/🌙 切换浅色/深色模式

### 支持的计算

- ✅ 四则运算：`2 + 3 * 4` = 14
- ✅ 括号优先级：`(2 + 3) * 4` = 20
- ✅ 小数运算：`3.14 * 2` = 6.28
- ✅ 负数：`-5 + 3` = -2
- ✅ 复杂表达式：`(10 + 5) / (3 - 1)` = 7.5

## 🔧 常见问题

**Q: 数据库文件在哪里？**  
A: `database/calculator.db` - 首次运行自动创建

**Q: 如何迁移数据？**  
A: 复制 `database/calculator.db` 文件到新位置即可

**Q: 清除浏览器缓存后数据会丢失吗？**  
A: 不会。数据保存在 SQLite 数据库中，清除缓存后会从后端自动恢复

**Q: 如何修改端口？**  
A: 
- 后端：设置环境变量 `PORT=新端口` 
- 前端：修改 `frontend/vite.config.js` 中的 `server.port`

## 📝 技术栈

- **后端**：Node.js + Express + SQLite3
- **前端**：Vue 3 (Composition API) + Vite
- **样式**：纯 CSS（无 UI 库依赖）

---

**享受计算！** 🎉