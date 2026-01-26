<template>
  <div class="history-panel">
    <div class="history-header">
      <h2>历史记录</h2>
      <div class="history-actions">
        <button 
          class="btn-refresh" 
          @click="refreshHistory"
          :disabled="loading"
          title="刷新"
        >
          🔄
        </button>
        <button 
          class="btn-clear-all" 
          @click="handleClearAll"
          :disabled="history.length === 0"
          title="清空所有"
        >
          清空
        </button>
      </div>
    </div>

    <div class="history-content">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="history.length === 0" class="empty">暂无历史记录</div>
      <div v-else class="history-list">
        <div 
          v-for="item in history" 
          :key="item.id" 
          class="history-item"
          @click="handleItemClick(item.expression)"
          :title="`点击填充表达式: ${item.expression}`"
        >
          <div class="history-expression">{{ item.expression }}</div>
          <div class="history-result">= {{ item.result }}</div>
          <div class="history-time">{{ formatTime(item.timestamp) }}</div>
          <button 
            class="btn-delete" 
            @click.stop="handleDelete(item.id)"
            title="删除"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useHistory } from '../composables/useHistory';

const emit = defineEmits(['fill-expression']);

const { history, loading, error, fetchHistory, deleteHistory, clearHistory } = useHistory();

// 格式化时间
function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  // 小于 1 分钟：刚刚
  if (diff < 60000) {
    return '刚刚';
  }
  
  // 小于 1 小时：X 分钟前
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`;
  }
  
  // 今天：HH:mm
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  
  // 昨天：昨天 HH:mm
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
  }
  
  // 其他：MM-DD HH:mm
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

// 刷新历史记录
async function refreshHistory() {
  await fetchHistory();
}

// 删除单条记录
async function handleDelete(id) {
  if (confirm('确定要删除这条记录吗？')) {
    await deleteHistory(id);
  }
}

// 清空所有记录
async function handleClearAll() {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
    await clearHistory();
  }
}

// 点击历史项，填充表达式到计算器
function handleItemClick(expression) {
  emit('fill-expression', expression);
}

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
.history-panel {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  min-width: 300px;
  max-width: 500px;
  width: 100%;
  height: fit-content;
  max-height: 80vh;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.history-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-refresh,
.btn-clear-all {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled),
.btn-clear-all:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-refresh:disabled,
.btn-clear-all:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.history-content {
  flex: 1;
  overflow-y: auto;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.error {
  color: var(--error-color);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  position: relative;
  transition: all 0.2s;
  cursor: pointer;
}

.history-item:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
}

.history-expression {
  font-size: 1rem;
  color: var(--text-secondary);
  word-break: break-all;
  margin-bottom: 0.25rem;
}

.history-result {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--text-primary);
  word-break: break-all;
  margin-bottom: 0.5rem;
}

.history-time {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.btn-delete {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  border-radius: 50%;
  background: var(--bg-hover);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: var(--error-color);
  color: white;
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .history-panel {
    max-height: 60vh;
  }
}
</style>