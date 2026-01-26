const express = require('express');
const cors = require('cors');
const path = require('path');
const historyRouter = require('./routes/history');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API 路由
app.use('/api/history', historyRouter);

// 生产环境：提供前端静态文件
if (process.env.NODE_ENV === 'production') {
  const publicPath = path.join(__dirname, 'public');
  app.use(express.static(publicPath));
  app.get('*', (req, res) => {
    res.sendFile(path.join(publicPath, 'index.html'));
  });
}

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: '计算器服务运行正常' });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  if (process.env.NODE_ENV !== 'production') {
    console.log(`API 端点: http://localhost:${PORT}/api`);
  }
});

module.exports = app;