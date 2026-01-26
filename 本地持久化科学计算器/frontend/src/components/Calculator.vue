<template>
  <div class="calculator-container">
    <div class="calculator-display">
      <div class="expression">{{ display || '0' }}</div>
      <div class="result" v-if="result">{{ result }}</div>
      <div class="error" v-if="error">{{ error }}</div>
    </div>

    <div class="calculator-buttons">
      <button class="btn btn-clear" @click="clear">C</button>
      <button class="btn btn-clear" @click="backspace">⌫</button>
      <button class="btn btn-operator" @click="append('(')">(</button>
      <button class="btn btn-operator" @click="append(')')">)</button>

      <button class="btn btn-number" @click="append('7')">7</button>
      <button class="btn btn-number" @click="append('8')">8</button>
      <button class="btn btn-number" @click="append('9')">9</button>
      <button class="btn btn-operator" @click="append('/')">÷</button>

      <button class="btn btn-number" @click="append('4')">4</button>
      <button class="btn btn-number" @click="append('5')">5</button>
      <button class="btn btn-number" @click="append('6')">6</button>
      <button class="btn btn-operator" @click="append('*')">×</button>

      <button class="btn btn-number" @click="append('1')">1</button>
      <button class="btn btn-number" @click="append('2')">2</button>
      <button class="btn btn-number" @click="append('3')">3</button>
      <button class="btn btn-operator" @click="append('-')">−</button>

      <button class="btn btn-number" @click="append('0')">0</button>
      <button class="btn btn-number" @click="append('.')">.</button>
      <button class="btn btn-equals" @click="calculate">=</button>
      <button class="btn btn-operator" @click="append('+')">+</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { calculateExpression } from '../utils/calculator';
import { useHistory } from '../composables/useHistory';

const display = ref('');
const result = ref('');
const error = ref('');

const { addHistory } = useHistory();

// 追加字符到显示
function append(char) {
  error.value = '';
  result.value = '';

  // 不允许连续的小数点
  if (char === '.' && display.value.endsWith('.')) {
    return;
  }

  // 不允许在数字中间插入小数点（已有小数点）
  if (char === '.') {
    const lastNumber = display.value.match(/[\d.]+$/)?.[0];
    if (lastNumber && lastNumber.includes('.')) {
      return;
    }
  }

  display.value += char;
}

// 清空
function clear() {
  display.value = '';
  result.value = '';
  error.value = '';
}

// 回删
function backspace() {
  error.value = '';
  result.value = '';
  if (display.value.length > 0) {
    display.value = display.value.slice(0, -1);
  }
}

// 计算
async function calculate() {
  error.value = '';
  result.value = '';

  if (!display.value.trim()) {
    return;
  }

  const calcResult = calculateExpression(display.value);

  if (calcResult.success) {
    result.value = calcResult.result;
    // 保存到历史记录
    await addHistory(display.value, calcResult.result);
  } else {
    error.value = calcResult.error;
  }
}

// 键盘事件处理
function handleKeyPress(event) {
  const key = event.key;

  // 数字
  if (/[\d.]/.test(key)) {
    event.preventDefault();
    append(key);
    return;
  }

  // 运算符
  if (['+', '-', '*', '/'].includes(key)) {
    event.preventDefault();
    append(key);
    return;
  }

  // 括号
  if (key === '(' || key === ')') {
    event.preventDefault();
    append(key);
    return;
  }

  // 等号或回车
  if (key === 'Enter' || key === '=') {
    event.preventDefault();
    calculate();
    return;
  }

  // 退格
  if (key === 'Backspace') {
    event.preventDefault();
    backspace();
    return;
  }

  // 清除（Escape 或 Delete）
  if (key === 'Escape' || key === 'Delete') {
    event.preventDefault();
    clear();
    return;
  }
}

// 填充表达式（从历史记录）
function fillExpression(expression) {
  display.value = expression;
  result.value = '';
  error.value = '';
}

// 暴露方法供父组件调用
defineExpose({
  fillExpression
});

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress);
});
</script>

<style scoped>
.calculator-container {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  min-width: 320px;
  max-width: 400px;
  width: 100%;
}

.calculator-display {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-end;
}

.expression {
  font-size: 1.2rem;
  color: var(--text-secondary);
  word-break: break-all;
  text-align: right;
  margin-bottom: 0.5rem;
}

.result {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-primary);
  word-break: break-all;
  text-align: right;
}

.error {
  font-size: 1rem;
  color: var(--error-color);
  word-break: break-all;
  text-align: right;
}

.calculator-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.btn {
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: 400;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--bg-number);
  color: var(--text-primary);
}

.btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-color);
}

.btn:active {
  background: var(--bg-active);
  transform: scale(0.98);
}

.btn-number {
  background: var(--bg-number);
}

.btn-operator {
  background: var(--bg-operator);
  color: var(--text-primary);
}

.btn-clear {
  background: var(--bg-clear);
  color: var(--text-primary);
}

.btn-equals {
  background: var(--bg-equals);
  color: var(--bg-secondary);
  font-weight: 500;
  grid-column: span 1;
}

.dark-theme .btn-equals {
  color: var(--bg-primary);
}

@media (max-width: 480px) {
  .calculator-container {
    padding: 1rem;
  }

  .btn {
    padding: 0.75rem;
    font-size: 1rem;
  }
}
</style>