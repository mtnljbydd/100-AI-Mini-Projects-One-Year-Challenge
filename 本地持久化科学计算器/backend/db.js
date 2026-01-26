const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// 确保 database 目录存在
const dbDir = path.join(__dirname, '..', 'database');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const dbPath = path.join(dbDir, 'calculator.db');

// 创建数据库连接
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('数据库连接失败:', err.message);
  } else {
    console.log('已连接到 SQLite 数据库:', dbPath);
    initDatabase();
  }
});

// 初始化数据库表结构
function initDatabase() {
  const createTableSQL = `
    CREATE TABLE IF NOT EXISTS calculations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      expression TEXT NOT NULL,
      result TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `;

  db.run(createTableSQL, (err) => {
    if (err) {
      console.error('创建表失败:', err.message);
    } else {
      console.log('数据库表初始化完成');
    }
  });
}

// 查询所有历史记录（按时间倒序）
function getAllHistory(callback) {
  const sql = 'SELECT * FROM calculations ORDER BY timestamp DESC';
  db.all(sql, [], (err, rows) => {
    if (err) {
      callback(err, null);
    } else {
      callback(null, rows);
    }
  });
}

// 插入历史记录
function insertHistory(expression, result, callback) {
  const sql = 'INSERT INTO calculations (expression, result) VALUES (?, ?)';
  db.run(sql, [expression, result], function(err) {
    if (err) {
      callback(err, null);
    } else {
      callback(null, {
        id: this.lastID,
        expression,
        result,
        timestamp: new Date().toISOString()
      });
    }
  });
}

// 删除单条历史记录
function deleteHistory(id, callback) {
  const sql = 'DELETE FROM calculations WHERE id = ?';
  db.run(sql, [id], function(err) {
    if (err) {
      callback(err, false);
    } else {
      callback(null, this.changes > 0);
    }
  });
}

// 清空所有历史记录
function clearAllHistory(callback) {
  const sql = 'DELETE FROM calculations';
  db.run(sql, [], function(err) {
    if (err) {
      callback(err, false);
    } else {
      callback(null, true);
    }
  });
}

module.exports = {
  db,
  getAllHistory,
  insertHistory,
  deleteHistory,
  clearAllHistory
};