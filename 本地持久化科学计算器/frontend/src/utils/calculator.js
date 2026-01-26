/**
 * 表达式验证器
 */
export function validateExpression(expression) {
  if (!expression || typeof expression !== 'string') {
    return { valid: false, error: '表达式不能为空' };
  }

  const trimmed = expression.trim();
  if (trimmed.length === 0) {
    return { valid: false, error: '表达式不能为空' };
  }

  // 检查括号匹配
  let parenthesesCount = 0;
  for (let char of trimmed) {
    if (char === '(') parenthesesCount++;
    if (char === ')') parenthesesCount--;
    if (parenthesesCount < 0) {
      return { valid: false, error: '括号不匹配' };
    }
  }
  if (parenthesesCount !== 0) {
    return { valid: false, error: '括号不匹配' };
  }

  // 检查连续运算符（允许 - 作为负数符号）
  const operators = ['+', '*', '/'];
  for (let i = 0; i < trimmed.length - 1; i++) {
    if (operators.includes(trimmed[i]) && operators.includes(trimmed[i + 1])) {
      return { valid: false, error: '不能有连续运算符' };
    }
    if (operators.includes(trimmed[i]) && trimmed[i + 1] === '-') {
      return { valid: false, error: '不能有连续运算符' };
    }
  }

  // 检查是否以运算符结尾（- 除外，因为它可能是负数的一部分）
  const lastChar = trimmed[trimmed.length - 1];
  if (['+', '*', '/'].includes(lastChar)) {
    return { valid: false, error: '表达式不能以运算符结尾' };
  }

  return { valid: true };
}

/**
 * 将中缀表达式转换为后缀表达式（逆波兰表达式）
 */
function infixToPostfix(expression) {
  const output = [];
  const operators = [];
  const precedence = { '+': 1, '-': 1, '*': 2, '/': 2 };

  // 移除空格
  const tokens = expression.replace(/\s+/g, '');
  let i = 0;

  while (i < tokens.length) {
    const char = tokens[i];

    // 数字（包括小数）
    if (/[\d.]/.test(char)) {
      let num = '';
      while (i < tokens.length && /[\d.]/.test(tokens[i])) {
        num += tokens[i];
        i++;
      }
      output.push(parseFloat(num));
      continue;
    }

    // 左括号
    if (char === '(') {
      operators.push(char);
      i++;
      continue;
    }

    // 右括号
    if (char === ')') {
      while (operators.length > 0 && operators[operators.length - 1] !== '(') {
        output.push(operators.pop());
      }
      operators.pop(); // 移除左括号
      i++;
      continue;
    }

    // 运算符
    if (['+', '-', '*', '/'].includes(char)) {
      // 处理负数（如果 - 是第一个字符或在 ( 或运算符之后）
      if (char === '-' && (i === 0 || ['(', '+', '-', '*', '/'].includes(tokens[i - 1]))) {
        i++;
        // 如果是括号后的负数，如 -(5+3)，处理为 0-(5+3)
        if (i < tokens.length && tokens[i] === '(') {
          output.push(0); // 推入 0
          operators.push('-'); // 将 - 作为运算符
          i--; // 回退，让下一个循环处理 (
          i++;
          continue;
        }
        // 读取数字，如 -5
        let num = '';
        while (i < tokens.length && /[\d.]/.test(tokens[i])) {
          num += tokens[i];
          i++;
        }
        if (num) {
          output.push(parseFloat('-' + num));
          continue;
        }
        // 如果没有数字，回退并作为普通运算符处理
        i--;
      }

      while (
        operators.length > 0 &&
        operators[operators.length - 1] !== '(' &&
        precedence[operators[operators.length - 1]] >= precedence[char]
      ) {
        output.push(operators.pop());
      }
      operators.push(char);
      i++;
      continue;
    }

    i++;
  }

  // 将剩余运算符弹出
  while (operators.length > 0) {
    output.push(operators.pop());
  }

  return output;
}

/**
 * 计算后缀表达式
 */
function evaluatePostfix(postfix) {
  const stack = [];

  for (let token of postfix) {
    if (typeof token === 'number') {
      stack.push(token);
    } else {
      const b = stack.pop();
      const a = stack.pop();

      if (a === undefined || b === undefined) {
        throw new Error('表达式格式错误');
      }

      switch (token) {
        case '+':
          stack.push(a + b);
          break;
        case '-':
          stack.push(a - b);
          break;
        case '*':
          stack.push(a * b);
          break;
        case '/':
          if (b === 0) {
            throw new Error('除数不能为零');
          }
          stack.push(a / b);
          break;
        default:
          throw new Error('未知运算符: ' + token);
      }
    }
  }

  if (stack.length !== 1) {
    throw new Error('表达式计算错误');
  }

  return stack[0];
}

/**
 * 计算表达式
 */
export function calculateExpression(expression) {
  try {
    // 验证表达式
    const validation = validateExpression(expression);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    // 转换为后缀表达式
    const postfix = infixToPostfix(expression);

    // 计算后缀表达式
    const result = evaluatePostfix(postfix);

    // 格式化结果
    const formatted = formatResult(result);

    return { success: true, result: formatted };
  } catch (error) {
    return { success: false, error: error.message || '计算错误' };
  }
}

/**
 * 格式化计算结果
 */
export function formatResult(num) {
  if (typeof num !== 'number' || isNaN(num) || !isFinite(num)) {
    return 'Error';
  }

  // 处理极大或极小的数字（使用科学计数法）
  if (Math.abs(num) > 1e10 || (Math.abs(num) < 1e-6 && num !== 0)) {
    return num.toExponential(6);
  }

  // 转换为字符串，保留最多 10 位有效数字
  let str = num.toString();

  // 如果是科学计数法，直接返回
  if (str.includes('e')) {
    return str;
  }

  // 处理小数
  if (str.includes('.')) {
    // 移除末尾的零
    str = str.replace(/\.?0+$/, '');
    
    // 限制小数位数（最多 10 位）
    const parts = str.split('.');
    if (parts[1] && parts[1].length > 10) {
      // 四舍五入到 10 位小数
      num = Math.round(num * 1e10) / 1e10;
      str = num.toString().replace(/\.?0+$/, '');
    }
  }

  return str;
}