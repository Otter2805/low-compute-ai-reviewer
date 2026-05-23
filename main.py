import sys
import os
import ast

class LocalCodeScanner(ast.NodeVisitor):
    """
    traverses the Python Abstract Syntax Tree (AST) to look for structural flaws.
    """
    def __init__(self):
        self.issues = []
        self.secret_keywords = {"api_key", "password", "secret", "token", "cred"}

    def visit_Assign(self, node):
        """Catches variable assignments to look for hardcoded secrets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                # Check if the variable name matches a secret keyword
                if any(keyword in var_name for keyword in self.secret_keywords):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        self.issues.append({
                            "type": "🔴 SECURITY",
                            "line": node.lineno,
                            "msg": f"Potential hardcoded secret found in variable '{target.id}'."
                        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Analyzes functions to check for excessive length or complexity."""
        # Check function length (basic metric)
        func_length = len(node.body)
        if func_length > 25:
            self.issues.append({
                "type": "🟡 COMPLEXITY",
                "line": node.lineno,
                "msg": f"Function '{node.name}' is quite long ({func_length} statements). Consider breaking it up."
            })

        # Count how many loops are nested inside this function
        loop_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loop_count += 1
        
        if loop_count >= 3:
            self.issues.append({
                "type": "🟡 COMPLEXITY",
                "line": node.lineno,
                "msg": f"Function '{node.name}' contains high nesting ({loop_count} loops). High risk of slowdowns."
            })

        self.generic_visit(node)

def load_local_file(file_path):
    """
    opens and reads a local file from the computer's hard drive.
    """
    # Check if the file actually exists on the computer
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None

    # Check if it's actually a file and not a folder
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
        print("\nRunning local static analysis engine...")
        try:
            # Parse the code text into a mathematical structure tree
            tree = ast.parse(source_code)
            scanner = LocalCodeScanner()
            scanner.visit(tree)
            
            if scanner.issues:
                print(f"Local engine found {len(scanner.issues)} issues:")
                for issue in scanner.issues:
                    print(f"  [{issue['type']}] Line {issue['line']}: {issue['msg']}")
            else:
                print("Local engine found 0 structural or security code-smells!")
                
        except SyntaxError as e:
            print(f"Local Analysis Failed: The target file has a syntax error on line {e.lineno}.")
            sys.exit(1)