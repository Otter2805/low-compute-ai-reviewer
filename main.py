import sys
import os
import ast
from scanner import LocalCodeScanner

def load_local_file(file_path):
    """Opens and reads a local file from the computer's hard drive safely."""
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is a directory, not a code file.")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        if not content.strip():
            print(f"Warning: The file '{file_path}' is empty.")
            return None
        return content
    except Exception as e:
        print(f"Critical Error reading file: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <name_of_code_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    source_code = load_local_file(target_file)
    
    if source_code:
        print(f"Loaded '{target_file}' into local memory.")
        print("\nRunning expanded local static analysis engine...")
        
        try:
            # Generate the AST map
            tree = ast.parse(source_code)
            scanner = LocalCodeScanner()
            scanner.visit(tree)
            
            if scanner.issues:
                print(f"\nLocal engine uncovered {len(scanner.issues)} issues:")
                for issue in scanner.issues:
                    print(f"  [{issue['type']}] Line {issue['line']}: {issue['msg']}")
            else:
                print("\nLocal engine found 0 structural or security code-smells!")
                
        except SyntaxError as e:
            print(f"Local Analysis Failed: The target file has a syntax error on line {e.lineno}.")
            sys.exit(1)