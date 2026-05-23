import ast

class LocalCodeScanner(ast.NodeVisitor):
    """
    traverses the Python Abstract Syntax Tree (AST) to look for structural flaws.
    """
    def __init__(self):
        self.issues = []
        self.secret_keywords = {"api_key", "password", "secret", "token", "cred"}

    def visit_Assign(self, node):
        """atches variable assignments to look for hardcoded secrets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(keyword in var_name for keyword in self.secret_keywords):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        self.issues.append({
                            "type": "🔴 SECURITY",
                            "line": node.lineno,
                            "msg": f"Potential hardcoded secret found in variable '{target.id}'."
                        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Analyzes functions for length, deep nesting, and dead code."""
        func_length = len(node.body)
        
        # Check for excessive length
        if func_length > 25:
            self.issues.append({
                "type": "微 COMPLEXITY",
                "line": node.lineno,
                "msg": f"Function '{node.name}' is quite long ({func_length} statements). Consider breaking it up."
            })

        # Check for dead code
        if func_length == 1 and isinstance(node.body[0], (ast.Pass, ast.Constant)):
            self.issues.append({
                "type": "🟡 DEAD CODE",
                "line": node.lineno,
                "msg": f"Function '{node.name}' appears to be empty or unfinished."
            })

        # Count loops to check for nesting risk
        loop_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loop_count += 1
        
        if loop_count >= 3:
            self.issues.append({
                "type": "🟡 COMPLEXITY",
                "line": node.lineno,
                "msg": f"Function '{node.name}' contains high nesting ({loop_count} loops). High risk of performance slowdowns."
            })

        self.generic_visit(node)

    def visit_Global(self, node):
        """Flags the use of 'global' keyword modifications."""
        for name in node.names:
            self.issues.append({
                "type": "🟡 ARCHITECTURE",
                "line": node.lineno,
                "msg": f"Use of 'global' keyword for '{name}' found. Modifying global state can lead to unexpected side-effects."
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        """Catches dangerous built-in execution functions like eval() or exec()."""
        if isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                self.issues.append({
                    "type": "🔴 SECURITY",
                    "line": node.lineno,
                    "msg": f"Dangerous built-in function call '{node.func.id}()' detected. This is a severe security vulnerability."
                })
        self.generic_visit(node)