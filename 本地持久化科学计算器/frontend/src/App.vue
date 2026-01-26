<template>
  <div class="app-container">
    <div class="app-header">
      <h1>科学计算器</h1>
      <button 
        class="theme-toggle" 
        @click="toggleTheme"
        :title="isDarkMode ? '切换到浅色模式' : '切换到深色模式'"
      >
        {{ isDarkMode ? '☀️' : '🌙' }}
      </button>
    </div>
    <div class="main-content">
      <div class="calculator-wrapper">
        <Calculator ref="calculatorRef" />
      </div>
      <div class="history-wrapper">
        <HistoryPanel @fill-expression="handleFillExpression" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Calculator from './components/Calculator.vue';
import HistoryPanel from './components/HistoryPanel.vue';

const isDarkMode = ref(false);
const calculatorRef = ref(null);

// 填充表达式到计算器
function handleFillExpression(expression) {
  if (calculatorRef.value) {
    calculatorRef.value.fillExpression(expression);
  }
}

// 初始化主题（从系统偏好或 localStorage 读取）
onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark';
  } else {
    // 检测系统主题
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    isDarkMode.value = prefersDark;
  }
  updateTheme();
});

// 切换主题
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  updateTheme();
};

// 更新主题
const updateTheme = () => {
  const root = document.documentElement;
  if (isDarkMode.value) {
    root.classList.add('dark-theme');
    localStorage.setItem('theme', 'dark');
  } else {
    root.classList.remove('dark-theme');
    localStorage.setItem('theme', 'light');
  }
};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-primary);
}

.theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  transform: scale(1.05);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 2rem;
  width: 100%;
}

.calculator-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 500px;
}

.history-wrapper {
  width: 100%;
  max-width: 500px;
  display: flex;
  justify-content: center;
}

@media (min-width: 1024px) {
  .main-content {
    flex-direction: row;
    align-items: flex-start;
    justify-content: center;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .calculator-wrapper {
    max-width: 400px;
  }
  
  .history-wrapper {
    max-width: 400px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
    gap: 1.5rem;
  }
  
  .app-header {
    padding: 1rem;
  }
}
</style>