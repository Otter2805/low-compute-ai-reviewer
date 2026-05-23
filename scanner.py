import ast

class LocalCodeScanner(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.secret_keywords = {"api_key", "password", "secret", "token", "cred"}
        
        # Track counts for local engineering metrics
        self.total_functions = 0
        self.documented_functions = 0

    def visit_Assign(self, node):
        """Catches variable assignments to look for hardcoded secrets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(keyword in var_name for keyword in self.secret_keywords):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        self.issues.append({
                            "category": "Security",
                            "severity": "CRITICAL",
                            "line": node.lineno,
                            "msg": f"Potential hardcoded secret found in variable '{target.id}'."
                        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Analyzes functions for metrics, length, deep nesting, and dead code."""
        self.total_functions += 1
        
        # Check if function has a docstring
        if ast.get_docstring(node):
            self.documented_functions += 1

        func_length = len(node.body)
        if func_length > 25:
            self.issues.append({
                "category": "Complexity",
                "severity": "WARNING",
                "line": node.lineno,
                "msg": f"Function '{node.name}' is quite long ({func_length} statements)."
            })

        if func_length == 1 and isinstance(node.body[0], (ast.Pass, ast.Constant)):
            self.issues.append({
                "category": "Dead Code",
                "severity": "LOW",
                "line": node.lineno,
                "msg": f"Function '{node.name}' appears to be empty or unfinished."
            })

        loop_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loop_count += 1
        
        if loop_count >= 3:
            self.issues.append({
                "category": "Complexity",
                "severity": "WARNING",
                "line": node.lineno,
                "msg": f"Function '{node.name}' contains deep nesting ({loop_count} loops)."
            })

        self.generic_visit(node)

    def visit_Global(self, node):
        """Flags dangerous global definitions."""
        for name in node.names:
            self.issues.append({
                "category": "Architecture",
                "severity": "LOW",
                "line": node.lineno,
                "msg": f"Use of 'global' keyword for '{name}' found."
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        """Catches dangerous execution calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                self.issues.append({
                    "category": "Security",
                    "severity": "CRITICAL",
                    "line": node.lineno,
                    "msg": f"Dangerous dynamic execution call '{node.func.id}()' detected."
                })
        self.generic_visit(node)

    def calculate_health_score(self):
        """Calculates a deterministic quality code grade out of 100."""
        score = 100
        for issue in self.issues:
            if issue["severity"] == "CRITICAL":
                score -= 25
            elif issue["severity"] == "WARNING":
                score -= 15
            else:
                score -= 5
        return max(0, score)