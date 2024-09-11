import os
import subprocess
import time
import typer
import re
from typing import List, Tuple
from rich.console import Console
from rich.panel import Panel
import ollama
from ollama import Options

DESTRUCTIVE_COMMANDS = [
    "rm", "rmdir", "dd", "mkfs", "fdisk", "format", 
    "del", "rd", "erase", "chown", "chmod",
    "truncate", "shred", "sudo", "mv", "cp", "rf", "sudo"
    ]

LLM_MODEL = "gemma2:2b-instruct-q8_0"

SYSTEM_PROMPT = """
You are an autonomous CLI agent with the ability to read, write, and execute code using proper CLI commands.

Capabilities:
1. Reading files: Use 'cat filename' to display file contents.
2. Writing files: Use 'echo "content" > filename' to write content to a file.
3. Executing code: Use appropriate commands to run code (e.g., 'python3 script.py' for Python).
4. Creating directories: Use 'mkdir directory_name' to create new directories.
5. Listing directory contents: Use 'ls' or 'dir' to list files and directories.
6. Navigating directories: Use 'cd directory_name' to change directories.

Follow the provided step-by-step process and consider previous actions. Every action must be a CLI command.

Output format:
EXPLANATION: Brief explanation of your next action.
COMMAND: The exact command to be executed.

Prioritize efficient and secure coding practices. Only provide explanations and commands, no unnecessary text.
"""

console = Console()

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """Interact with the language model."""
    response = ollama.chat(
        model=LLM_MODEL,
        options=Options(temperature=0.0),
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
    )
    return response['message']['content']

def execute_command(command: str, simulate: bool = True) -> Tuple[int, str]:
    """Execute or simulate a command."""
    if simulate:
        time.sleep(0.5)  # Simulate execution time
        output = ask_llm(
            "You are simulating CLI output.",
            f"Simulate realistic output for this command: {command}"
        )
        return 0, output.strip()
    else:
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
            return 0, output.strip()
        except subprocess.CalledProcessError as e:
            return e.returncode, e.output.strip()

def generate_plan(goal: str) -> List[str]:
    """Generate a plan to achieve the goal with steps enclosed in tags."""
    plan_prompt = f"""
    Create a step-by-step plan to achieve this goal: {goal}
    Enclose each step in <step></step> tags.
    Example:
    <step>First action to take</step>
    <step>Second action to take</step>
    """
    plan_response = ask_llm(SYSTEM_PROMPT, plan_prompt)
    return parse_steps(plan_response)

def parse_steps(plan_response: str) -> List[str]:
    """Parse steps from the response, extracting content from <step> tags."""
    step_pattern = r'<step>(.*?)</step>'
    steps = re.findall(step_pattern, plan_response, re.DOTALL)
    return [step.strip() for step in steps]

def execute_step(goal: str, step: str, context: str) -> Tuple[str, str]:
    """Execute a single step of the plan."""
    step_prompt = f"""
    Goal: {goal}
    Current Step: {step}
    Context: {context}

    Determine the next CLI command to execute for this step.
    """
    response = ask_llm(SYSTEM_PROMPT, step_prompt)
    explanation, command = response.split('COMMAND:', 1)
    explanation = explanation.replace('EXPLANATION:', '').strip()
    command = command.strip()
    return explanation, command

def main(query: str):
    console.print(Panel(f"[bold blue]Query:[/bold blue] {query}"))

    # Generate goal
    goal = ask_llm("You expertly understand problems and rewrite them as clear goals.", 
                   f"Generate a clear, one-sentence goal to solve this problem: {query}")
    console.print(Panel(f"[bold green]Goal:[/bold green] {goal}"))

    # Generate plan
    plan = generate_plan(goal)
    console.print(Panel("[bold yellow]Plan:[/bold yellow]\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))))

    # Execute plan
    context = f"Current working directory: {os.getcwd()}\n"
    for i, step in enumerate(plan, 1):
        console.print(f"\n[bold cyan]Step {i}:[/bold cyan] {step}")
        explanation, command = execute_step(goal, step, context)
        
        console.print(f"[italic]{explanation}[/italic]")
        console.print(f"[bold]Executing:[/bold] {command}")
        
        if command in DESTRUCTIVE_COMMANDS:
            console.print(f"[bold red]DESTRUCTIVE COMMAND FOUND![/bold red] {command}")
            break
        
        return_code, output = execute_command(command, simulate=False)
        
        console.print(Panel(f"[bold]Output:[/bold]\n{output}", border_style="yellow"))
        context += f"Executed: {command}\nOutput: {output}\n"

        if return_code != 0:
            console.print(f"[bold red]Command failed with return code {return_code}[/bold red]")
            break

    console.print("\n[bold green]Task completed.[/bold green]")

if __name__ == "__main__":
    typer.run(main)
