import sys
import os
import ast
from scanner import LocalCodeScanner
from reviewer import get_ai_review

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def load_local_file(file_path):
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] The file '{file_path}' does not exist.")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        console.print(f"[bold red]Critical System Error reading file:[/bold red] {e}")
        return None

def cli_entrypoint():
    """Main execution path triggered when the user types 'review <file>' in VS Code terminal."""
    if len(sys.argv) < 2:
        console.print("[bold yellow]Usage:[/bold yellow] review <name_of_code_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    source_code = load_local_file(target_file)
    
    if not source_code:
        sys.exit(1)
        
    console.print(Panel(f"Context targeted: '{target_file}'", title="Offline AI Reviewer Engine", border_style="cyan"))
    
    try:
        # AST Analysis Stage
        tree = ast.parse(source_code)
        scanner = LocalCodeScanner()
        scanner.visit(tree)
        
        doc_ratio = 0
        if scanner.total_functions > 0:
            doc_ratio = (scanner.documented_functions / scanner.total_functions) * 100
            
        health = scanner.calculate_health_score()
        health_color = "green" if health >= 80 else "yellow" if health >= 50 else "red"
        
        console.print(f"\n[bold underline]Local Static Analysis Structural Telemetry[/bold underline]")
        console.print(f" * Total Functions Found: {scanner.total_functions}")
        console.print(f" * Documentation Density: {doc_ratio:.1f}%")
        console.print(f" * Algorithmic Health Score: [{health_color}]{health}/100[/{health_color}]\n")

        # Render AST Issues Table
        if scanner.issues:
            table = Table(title="Local Syntax and Security Infractions Detected", title_style="bold red", border_style="red")
            table.add_column("Line", style="dim", width=6, justify="center")
            table.add_column("Category", style="bold")
            table.add_column("Severity", style="bold")
            table.add_column("Detailed Explanation")

            for issue in scanner.issues:
                sev_style = "bold red" if issue["severity"] == "CRITICAL" else "yellow" if issue["severity"] == "WARNING" else "blue"
                table.add_row(
                    str(issue["line"]),
                    issue["category"],
                    f"[{sev_style}]{issue['severity']}[/{sev_style}]",
                    issue["msg"]
                )
            console.print(table)
        else:
            console.print(Panel("AST Scan Clear: No structural smell or hardcoded credentials found.", border_style="green"))
            
        # Local LLM Reasoning Stage - Forced to execute to review logical flaws
        console.print("\n[bold yellow]Triggering Local LLM Reasoning Loop...[/bold yellow]")
        console.print("Contacting local Ollama engine socket for deep architectural feedback...")
        
        with console.status("[bold cyan]Generating review analysis...", spinner="dots"):
            ai_feedback = get_ai_review(source_code, scanner.issues)
        
        console.print(Panel("Local AI Cognitive Insights and Suggested Code Refactor", border_style="purple"))
        console.print(Markdown(ai_feedback))
        console.print("─" * 60 + "\n")
            
    except SyntaxError as e:
        console.print(f"[bold red]Local Compilation Failure:[/bold red] Target code has invalid syntax on line [bold]{e.lineno}[/bold].")
        sys.exit(1)

if __name__ == "__main__":
    cli_entrypoint()