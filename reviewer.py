import ollama

def get_ai_review(source_code: str, ast_issues: list) -> str:
    """
    Queries your local Ollama engine using the 1.5B model you verified.
    """
    issues_summary = "\n".join([
        f"- [Line {i['line']}] [{i['category']} - {i['severity']}]: {i['msg']}"
        for i in ast_issues
    ])

    prompt = f"""You are a senior code reviewer. Review this Python code.

AST Static Analysis findings:
{issues_summary if ast_issues else "No structural flaws found, look for deep logical bugs."}

Source Code:
```python
{source_code}
```
"""

    try:
        response = ollama.generate(
            model='qwen2.5-coder:1.5b',
            prompt=prompt,
            options={
                'temperature': 0.1,
                'num_ctx': 4096
            }
        )
        return str(response.response)
    except Exception as e:
        return f"[bold red]Local LLM Core Error:[/bold red] Ensure Ollama is running. ({str(e)})"