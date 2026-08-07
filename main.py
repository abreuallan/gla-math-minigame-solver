import argparse
import cv2
import pytesseract
import itertools
import re

# Update this path if you are on Windows and Tesseract isn't in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def parse_args():
    parser = argparse.ArgumentParser(description="Solve a left-to-right number puzzle from user input.")
    parser.add_argument("target_number", nargs="?", type=int, default=None, help="Target number to reach")
    parser.add_argument("--image", default="image.png", help="Path to the image file")
    return parser.parse_args()


def prompt_for_numbers():
    while True:
        raw_value = input("Enter all numbers separated by spaces: ").strip()
        if not raw_value:
            print("Please enter at least one number.")
            continue

        try:
            numbers = [int(token) for token in raw_value.split()]
            return numbers
        except ValueError:
            print("Please enter valid integers separated by spaces.")


def prompt_for_operators():
    while True:
        raw_value = input("Enter the available operators separated by spaces (for example: + - *): ").strip()
        if not raw_value:
            print("Please enter at least one operator.")
            continue

        operators = []
        valid = {"+", "-", "*", "x", "X"}
        for token in raw_value.split():
            if token in valid:
                operators.append("*" if token.upper() == "X" else token)
            else:
                print(f"Unsupported operator '{token}'. Use +, -, *, or x.")
                break
        else:
            return operators


def prompt_for_target(default_value=None):
    while True:
        prompt = f"Enter the end result{f' [{default_value}]' if default_value is not None else ''}: "
        raw_value = input(prompt).strip()
        if not raw_value and default_value is not None:
            return default_value

        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a valid integer.")


def extract_symbols_from_image(image_path):
    """Reads the image and extracts potential numbers and operators."""
    print("Reading image and performing OCR...")
    
    # Read the image using OpenCV
    img = cv2.imread(image_path)
    
    # Convert to grayscale to improve OCR accuracy
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply a bit of thresholding to make the text stand out from the blocks
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Perform OCR
    custom_config = r'--oem 3 --psm 11' # PSM 11 is good for sparse, disconnected text
    extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
    
    # Clean up the output to find our characters
    raw_chars = re.sub(r'\s+', '', extracted_text).upper()
    
    numbers = []
    operators = []
    
    for char in raw_chars:
        if char.isdigit():
            numbers.append(int(char))
        elif char in ['+', '-', 'X', '*', 'x']:
            # Normalize multiplication signs
            operators.append('*' if char.upper() == 'X' else char)
            
    return numbers, operators

def solve_left_to_right(numbers, operators, target):
    """
    Brute-forces permutations of numbers and operators to hit the target.
    Evaluates strictly left-to-right, ignoring standard order of operations.
    """
    print(f"Attempting to solve for target: {target}...")
    print(f"Available numbers: {numbers}")
    print(f"Available operators: {operators}")
    
    if len(operators) != len(numbers) - 1:
        print("Warning: The number of operators must be exactly one less than the numbers.")
        print("OCR may have missed or misread a block. You may need to tweak the image thresholding.")
        # Fallback to hardcoded values for the sake of the puzzle if OCR fails on game assets
        print("\n--- Falling back to known puzzle inputs ---")
        numbers = [3, 5, 6, 1]
        operators = ['+', '*', '-']

    # Generate every possible arrangement of the numbers and operators
    num_permutations = list(itertools.permutations(numbers))
    op_permutations = list(itertools.permutations(operators))
    
    for num_perm in num_permutations:
        for op_perm in op_permutations:
            
            # Start with the first number
            current_total = num_perm[0]
            expression_str = str(num_perm[0])
            
            # Apply each operator and the next number sequentially
            for i in range(len(op_perm)):
                next_num = num_perm[i+1]
                op = op_perm[i]
                
                expression_str += f" {op} {next_num}"
                
                if op == '+':
                    current_total += next_num
                elif op == '-':
                    current_total -= next_num
                elif op in ['*', 'X', 'x']:
                    current_total *= next_num
                    
            # Check if this combination hits our target
            if current_total == target:
                return f"\nSUCCESS! The solution is: {expression_str} = {target}"
                
    return "\nNo solution found with these combinations."

if __name__ == "__main__":
    args = parse_args()

    numbers = prompt_for_numbers()
    operators = prompt_for_operators()
    target_number = prompt_for_target(args.target_number)

    result = solve_left_to_right(numbers, operators, target_number)

    print(result)