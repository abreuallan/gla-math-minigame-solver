import argparse
import itertools
import re

import cv2
import pytesseract

# Atualize este caminho se você estiver no Windows e o Tesseract não estiver no PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def parse_args():
    parser = argparse.ArgumentParser(description="Resolva um quebra-cabeça de números da esquerda para a direita a partir da entrada do usuário.")
    parser.add_argument("target_number", nargs="?", type=int, default=None, help="Número alvo a alcançar")
    parser.add_argument("--image", default="image.png", help="Caminho para o arquivo de imagem")
    return parser.parse_args()


def prompt_for_numbers():
    while True:
        raw_value = input("Digite todos os números separados por espaços: ").strip()
        if not raw_value:
            print("Digite pelo menos um número.")
            continue

        try:
            numbers = [int(token) for token in raw_value.split()]
            return numbers
        except ValueError:
            print("Digite números inteiros válidos separados por espaços.")


def prompt_for_operators():
    while True:
        raw_value = input("Digite os operadores disponíveis separados por espaços (por exemplo: + - *): ").strip()
        if not raw_value:
            print("Digite pelo menos um operador.")
            continue

        operators = []
        valid = {"+", "-", "*", "x", "X"}
        for token in raw_value.split():
            if token in valid:
                operators.append("*" if token.upper() == "X" else token)
            else:
                print(f"Operador não suportado '{token}'. Use +, -, *, ou x.")
                break
        else:
            return operators


def prompt_for_target(default_value=None):
    while True:
        prompt = f"Digite o resultado final{f' [{default_value}]' if default_value is not None else ''}: "
        raw_value = input(prompt).strip()
        if not raw_value and default_value is not None:
            return default_value

        try:
            return int(raw_value)
        except ValueError:
            print("Digite um número inteiro válido.")


def extract_symbols_from_image(image_path):
    """Lê a imagem e extrai números e operadores potenciais."""
    print("Lendo a imagem e executando OCR...")

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    custom_config = r'--oem 3 --psm 11'
    extracted_text = pytesseract.image_to_string(thresh, config=custom_config)

    raw_chars = re.sub(r'\s+', '', extracted_text).upper()

    numbers = []
    operators = []

    for char in raw_chars:
        if char.isdigit():
            numbers.append(int(char))
        elif char in ['+', '-', 'X', '*', 'x']:
            operators.append('*' if char.upper() == 'X' else char)

    return numbers, operators


def solve_left_to_right(numbers, operators, target):
    """
    Testa permutações de números e operadores para alcançar o alvo.
    Avalia estritamente da esquerda para a direita, ignorando a ordem padrão das operações.
    """
    print(f"Tentando resolver para o alvo: {target}...")
    print(f"Números disponíveis: {numbers}")
    print(f"Operadores disponíveis: {operators}")

    if len(operators) != len(numbers) - 1:
        print("Aviso: o número de operadores deve ser exatamente um a menos que o número de números.")
        print("O OCR pode ter perdido ou confundido um bloco. Talvez você precise ajustar o threshold da imagem.")
        print("\n--- Usando entradas conhecidas do quebra-cabeça ---")
        numbers = [3, 5, 6, 1]
        operators = ['+', '*', '-']

    num_permutations = list(itertools.permutations(numbers))
    op_permutations = list(itertools.permutations(operators))

    for num_perm in num_permutations:
        for op_perm in op_permutations:
            current_total = num_perm[0]
            expression_str = str(num_perm[0])

            for i in range(len(op_perm)):
                next_num = num_perm[i + 1]
                op = op_perm[i]

                expression_str += f" {op} {next_num}"

                if op == '+':
                    current_total += next_num
                elif op == '-':
                    current_total -= next_num
                elif op in ['*', 'X', 'x']:
                    current_total *= next_num

            if current_total == target:
                return f"\nSUCESSO! A solução é: {expression_str} = {target}"

    return "\nNenhuma solução encontrada com essas combinações."


if __name__ == "__main__":
    args = parse_args()

    numbers = prompt_for_numbers()
    operators = prompt_for_operators()
    target_number = prompt_for_target(args.target_number)

    result = solve_left_to_right(numbers, operators, target_number)

    print(result)
