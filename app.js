const form = document.getElementById('solver-form');
const resultBox = document.getElementById('result');

function parseNumbers(input) {
  const raw = input.trim();
  if (!raw) {
    throw new Error('Digite pelo menos um número.');
  }

  const values = raw.split(/\s+/).map((token) => Number(token));
  if (values.some((value) => Number.isNaN(value))) {
    throw new Error('Os números devem ser inteiros separados por espaços.');
  }

  return values;
}

function parseOperators(input) {
  const raw = input.trim();
  if (!raw) {
    throw new Error('Digite pelo menos um operador.');
  }

  const normalized = [];
  const validOperators = new Set(['+', '-', '*', 'x', 'X']);

  for (const token of raw.split(/\s+/)) {
    if (!validOperators.has(token)) {
      throw new Error(`Operador não suportado '${token}'. Use +, -, *, ou x.`);
    }
    normalized.push(token.toUpperCase() === 'X' ? '*' : token);
  }

  return normalized;
}

function getPermutations(items) {
  if (items.length <= 1) {
    return [items.slice()];
  }

  const permutations = [];
  for (let index = 0; index < items.length; index += 1) {
    const current = items[index];
    const remaining = items.filter((_, itemIndex) => itemIndex !== index);
    for (const permutation of getPermutations(remaining)) {
      permutations.push([current, ...permutation]);
    }
  }
  return permutations;
}

function solveLeftToRight(numbers, operators, target) {
  if (operators.length !== numbers.length - 1) {
    return {
      error: 'A quantidade de operadores deve ser exatamente uma a menos que a quantidade de valores.'
    };
  }

  const numberPermutations = getPermutations(numbers);
  const operatorPermutations = getPermutations(operators);

  for (const numberPermutation of numberPermutations) {
    for (const operatorPermutation of operatorPermutations) {
      let currentTotal = numberPermutation[0];
      let expression = String(numberPermutation[0]);

      for (let index = 0; index < operatorPermutation.length; index += 1) {
        const operator = operatorPermutation[index];
        const nextNumber = numberPermutation[index + 1];
        expression += ` ${operator} ${nextNumber}`;

        if (operator === '+') {
          currentTotal += nextNumber;
        } else if (operator === '-') {
          currentTotal -= nextNumber;
        } else if (operator === '*') {
          currentTotal *= nextNumber;
        }
      }

      if (currentTotal === target) {
        return { success: true, expression: `${expression} = ${target}` };
      }
    }
  }

  return { success: false, message: 'Nenhuma solução foi encontrada com essas combinações.' };
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  try {
    const numbers = parseNumbers(document.getElementById('numbers').value);
    const operators = parseOperators(document.getElementById('operators').value);
    const target = Number(document.getElementById('target').value);

    if (Number.isNaN(target)) {
      throw new Error('O alvo deve ser um número válido.');
    }

    const result = solveLeftToRight(numbers, operators, target);

    if (result.error) {
      resultBox.textContent = result.error;
      return;
    }

    if (result.success) {
      resultBox.textContent = `SUCESSO! A solução é: ${result.expression}`;
    } else {
      resultBox.textContent = result.message;
    }
  } catch (error) {
    resultBox.textContent = error.message;
  }
});
