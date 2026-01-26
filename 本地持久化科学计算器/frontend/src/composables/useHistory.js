import { ref } from 'vue';
import {
  loadFromLocalStorage,
  saveToLocalStorage,
  updateLocalStorage,
  deleteFromLocalStorage,
  clearLocalStorage
} from '../utils/storage';

const API_BASE = '/api/history';

/**
 * 历史记录管理组合式函数
 */
export function useHistory() {
  const history = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // 从后端获取历史记录
  async function fetchFromAPI() {
    try {
      loading.value = true;
      error.value = null;
      const response = await fetch(API_BASE);
      
      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`);
      }
      
      // 检查响应内容类型
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('响应不是有效的 JSON 格式');
      }
      
      // 检查响应是否有内容
      const text = await response.text();
      if (!text || text.trim().length === 0) {
        throw new Error('响应为空');
      }
      
      const data = JSON.parse(text);

      if (data.success) {
        history.value = data.data || [];
        // 同步到 localStorage
        updateLocalStorage(history.value);
        return history.value;
      } else {
        throw new Error(data.error || '获取历史记录失败');
      }
    } catch (err) {
      error.value = err.message;
      console.error('获取历史记录失败:', err);
      // 如果后端请求失败，至少保留 localStorage 中的数据
      const localHistory = loadFromLocalStorage();
      if (localHistory.length > 0) {
        history.value = localHistory;
      }
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 获取历史记录（优先从 localStorage 读取）
  async function fetchHistory() {
    // 先从 localStorage 读取（快速响应）
    const localHistory = loadFromLocalStorage();
    if (localHistory.length > 0) {
      history.value = localHistory;
    }

    // 然后从后端同步（确保数据一致）
    await fetchFromAPI();
  }

  // 添加历史记录
  async function addHistory(expression, result) {
    const item = {
      expression,
      result: String(result),
      timestamp: new Date().toISOString()
    };

    // 先保存到 localStorage（快速反馈）
    saveToLocalStorage(item);

    // 添加到本地状态（临时 ID）
    item.id = Date.now(); // 临时 ID
    history.value.unshift(item);

    // 异步保存到后端
    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          expression: item.expression,
          result: item.result
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const text = await response.text();
        if (text && text.trim().length > 0) {
          const data = JSON.parse(text);
          if (data.success && data.data) {
            // 更新本地记录的真实 ID
            const index = history.value.findIndex(h => h.id === item.id);
            if (index !== -1) {
              history.value[index] = data.data;
              // 更新 localStorage
              updateLocalStorage(history.value);
            }
          }
        }
      }
    } catch (err) {
      console.error('保存到后端失败:', err);
      // 即使后端失败，localStorage 已保存，数据不会丢失
    }
  }

  // 删除历史记录
  async function deleteHistory(id) {
    // 先从本地删除（快速反馈）
    history.value = history.value.filter(item => item.id !== id);
    deleteFromLocalStorage(id);

    // 然后从后端删除
    try {
      const response = await fetch(`${API_BASE}/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const text = await response.text();
        if (text && text.trim().length > 0) {
          const data = JSON.parse(text);
          if (!data.success) {
            throw new Error(data.error || '删除失败');
          }
        }
      }
    } catch (err) {
      console.error('从后端删除失败:', err);
      // 重新同步数据
      await fetchFromAPI();
    }
  }

  // 清空所有历史记录
  async function clearHistory() {
    // 先清空本地
    history.value = [];
    clearLocalStorage();

    // 然后清空后端
    try {
      const response = await fetch(API_BASE, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const text = await response.text();
        if (text && text.trim().length > 0) {
          const data = JSON.parse(text);
          if (!data.success) {
            throw new Error(data.error || '清空失败');
          }
        }
      }
    } catch (err) {
      console.error('清空后端失败:', err);
      // 如果后端清空失败，保持本地已清空状态
      // 不重新同步，避免恢复已删除的数据
    }
  }

  return {
    history,
    loading,
    error,
    fetchHistory,
    addHistory,
    deleteHistory,
    clearHistory
  };
}