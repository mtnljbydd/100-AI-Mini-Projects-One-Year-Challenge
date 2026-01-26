const STORAGE_KEY = 'calculator_history';

/**
 * 从 localStorage 加载历史记录
 */
export function loadFromLocalStorage() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('加载 localStorage 失败:', error);
  }
  return [];
}

/**
 * 保存到 localStorage
 */
export function saveToLocalStorage(item) {
  try {
    const history = loadFromLocalStorage();
    history.unshift(item); // 添加到开头
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    return true;
  } catch (error) {
    console.error('保存到 localStorage 失败:', error);
    return false;
  }
}

/**
 * 更新 localStorage（同步后端数据）
 */
export function updateLocalStorage(history) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    return true;
  } catch (error) {
    console.error('更新 localStorage 失败:', error);
    return false;
  }
}

/**
 * 从 localStorage 删除指定记录
 */
export function deleteFromLocalStorage(id) {
  try {
    const history = loadFromLocalStorage();
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('从 localStorage 删除失败:', error);
    return false;
  }
}

/**
 * 清空 localStorage
 */
export function clearLocalStorage() {
  try {
    localStorage.removeItem(STORAGE_KEY);
    return true;
  } catch (error) {
    console.error('清空 localStorage 失败:', error);
    return false;
  }
}