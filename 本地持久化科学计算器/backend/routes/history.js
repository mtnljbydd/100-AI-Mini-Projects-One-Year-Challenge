const express = require('express');
const router = express.Router();
const {
  getAllHistory,
  insertHistory,
  deleteHistory,
  clearAllHistory
} = require('../db');

// GET /api/history - 获取所有历史记录
router.get('/', (req, res) => {
  getAllHistory((err, rows) => {
    if (err) {
      return res.status(500).json({ error: '查询历史记录失败', message: err.message });
    }
    res.json({ success: true, data: rows });
  });
});

// POST /api/history - 创建历史记录
router.post('/', (req, res) => {
  const { expression, result } = req.body;

  if (!expression || result === undefined || result === null) {
    return res.status(400).json({ error: '缺少必要参数: expression, result' });
  }

  insertHistory(expression, String(result), (err, record) => {
    if (err) {
      return res.status(500).json({ error: '保存历史记录失败', message: err.message });
    }
    res.json({ success: true, data: record });
  });
});

// DELETE /api/history - 清空所有历史记录（必须在 /:id 之前）
router.delete('/', (req, res) => {
  clearAllHistory((err, success) => {
    if (err) {
      return res.status(500).json({ error: '清空历史记录失败', message: err.message });
    }
    res.json({ success: true, message: '清空成功' });
  });
});

// DELETE /api/history/:id - 删除单条历史记录（必须在 / 之后）
router.delete('/:id', (req, res) => {
  const id = parseInt(req.params.id);

  if (isNaN(id)) {
    return res.status(400).json({ error: '无效的记录 ID' });
  }

  deleteHistory(id, (err, success) => {
    if (err) {
      return res.status(500).json({ error: '删除历史记录失败', message: err.message });
    }
    if (!success) {
      return res.status(404).json({ error: '记录不存在' });
    }
    res.json({ success: true, message: '删除成功' });
  });
});

module.exports = router;