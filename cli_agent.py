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
    "del", "rd", "erase", "chown",
    "truncate", "shred", "sudo", "mv", "rf"
    ]

LLM_MODEL = "llama3.1:8b-instruct-q8_0"
#LLM_MODEL = "gemma2:2b-instruct-q8_0"

SYSTEM_PROMPT = f"""
You are an autonomous CLI agent designed to interpret user queries and execute appropriate commands on a Unix-like system. Your primary goal is to understand the task, create a plan, and execute it using CLI commands.

Role and Responsibilities:
1. Interpret user queries and translate them into actionable CLI tasks.
2. Generate a step-by-step plan to accomplish the given task.
3. Execute each step using appropriate CLI commands.
4. Provide clear explanations for each action taken.

Core Capabilities:
1. File Operations:
   - Read: 'cat filename'
   - Write: 'echo "content" > filename' (overwrites existing content)
   - Append: 'echo "content" >> filename'
   - List: 'ls -l' (detailed), 'ls -a' (include hidden files)

2. Directory Operations:
   - Create: 'mkdir -p directory_name'
   - Navigate: 'cd directory_name', 'cd ..' (parent directory)
   - Current Path: 'pwd'

3. Code Execution:
   - Python: '/usr/bin/python3 script.py'
   - Shell: 'bash script.sh'
   - Make Executable: 'chmod +x filename'

4. Text Processing:
   - Search: 'grep pattern filename'
   - Edit: 'sed -i 's/old/new/g' filename'

5. System Information:
   - System: 'uname -a'
   - Disk Space: 'df -h'
   - Memory: 'free -h'

Safety Protocol:
- NEVER use these potentially destructive commands: {DESTRUCTIVE_COMMANDS}
- NEVER use text editors like nano, vim, emacs in commands.
- Use relative paths unless absolute paths are necessary.

Execution Process:
1. Analyze the user query and formulate a clear goal.
2. Create a step-by-step plan to achieve the goal.
3. For each step consider the context and results of previous commands and:
   a. Provide a brief explanation of the action.
   b. Generate the exact CLI command to execute.
4. If a command fails, suggest an alternative or troubleshooting step.

Output Format for Each Step:
EXPLANATION: [Brief explanation of the action]
COMMAND: [Exact CLI command to be executed]

Remember:
- Prioritize efficiency, security, and clarity in your commands.
- Provide only explanations and commands, no unnecessary text.
- Always consider the context of previous actions when planning next steps.
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
    """Generate a simple plan to achieve the goal with steps enclosed in tags."""
    plan_prompt = f"""
    Create a step-by-step plan to achieve this goal using CLI commands: {goal}
    Enclose each step in <step></step> tags.
    Example:
    <step>First action to take</step>
    <step>Second action to take</step>
    The plan must have the smallest amount of steps as possible to achieve the goal.
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
    Task Goal: {goal}
    Current Step: {step}
    Context and Previous Actions: {context}

    Based on the above information, determine the next CLI command to execute for this step. Follow these guidelines:

    1. Analyze the current step in the context of the overall goal and previous actions.
    2. Choose the most appropriate CLI command to accomplish this step.
    3. Ensure the command is safe and non-destructive.
    4. If the step requires multiple commands, choose only the next logical command.
    5. If the step is unclear, interpret it in the most reasonable way to progress towards the goal.

    Provide your response in this exact format:
    EXPLANATION: A brief, clear explanation of what this command will do and why it's necessary.
    COMMAND: The exact CLI command to be executed, with no additional text or formatting.

    Remember:
    - Use only standard Unix/Linux CLI commands.
    - Avoid any potentially destructive commands.
    - Consider the current working directory and the results of previous commands.
    - NEVER use text editors like nano, vim, emacs in commands.
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
                   f"Generate a clear, one-sentence goal to solve this problem: {query}. Do not return anything else other than one-sentence Goal.")
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
        
        if any(cmd in command.lower().split() for cmd in DESTRUCTIVE_COMMANDS):
            console.print(f"[bold red]DESTRUCTIVE COMMAND FOUND![/bold red] {command}")
            break
        
        return_code, output = execute_command(command, simulate=False)
        
        console.print(Panel(f"[bold]Output:[/bold]\n{output}", border_style="yellow"))
        
        # Update context with the current step's execution details
        context += f"\nExecuted: {command}\nOutput: {output}\nReturn Code {return_code}"
        
        #if return_code != 0:
        #    console.print(f"[bold red]Command might have failed with return code {return_code}[/bold red]")
    
    console.print("\n[bold green]Task completed.[/bold green]")

if __name__ == "__main__":
    typer.run(main)
    
# tested successfully:
# python3 cli_agent.py "codey.py doesn't work on my macbook, it should count from 1 to 10. fix the file."
# python3 cli_agent.py "textfile.txt has some grammatic errors. Fix the file."
