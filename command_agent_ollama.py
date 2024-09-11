import os
import subprocess
import sys
import time
import typer
import ollama
from rich import print
import random

LLM_MODEL = "gemma2:2b-instruct-q4_0"

SYSTEM = """
You are an autonomous coding agent with the ability to read, write, and execute code.

Your capabilities include:
1. Reading files: Use cat filename to display file contents.
2. Writing files: Use echo "content" > filename to write content to a file.
3. Executing code: Use appropriate commands to run code (e.g., python script.py for Python).
4. Creating directories: Use mkdir directory_name to create new directories.
5. Listing directory contents: Use ls or dir to list files and directories.

Instructions:
1. Analyze the current task or problem.
2. Plan your approach step by step.
3. Execute one command at a time to progress towards your goal.
4. After each command, wait for the result before proceeding.
5. If you encounter an error, analyze it and attempt to correct it.
6. Continue until the task is completed.

Output format:
- Provide a brief explanation of your next action.
- Output the exact command to be executed, preceded by "COMMAND: ".
- Use '<|DONE|>' on a new line when the whole task is completed.

Remember to always prioritize efficient and secure coding practices.
"""

def ask_llm_ollama(system_prompt, user_prompt):
    response = ollama.chat(model=LLM_MODEL, messages=[
        {
            'role': 'system',
            'content': system_prompt,
        },
        {
            'role': 'user',
            'content': user_prompt,
        },
    ])
    
    return response['message']['content']

def chat(*, prompt: str, system: str | None = None) -> str:
    response = ask_llm_ollama(system or SYSTEM, prompt)
    print(f"[blue][PROMPT][/blue] {prompt}")
    print(f"[yellow][RESPONSE][/yellow] {response}")
    return response

def fake_execute_command(command: str) -> tuple[int, str]:
    # Simulate a slight delay
    time.sleep(random.uniform(0.1, 0.5))
    
    system_prompt = "You fake the CLI output based on the provided command."
    
    user_prompt = f"""
    Given the following CLI command: '{command}'
    Generate a realistic CLI output. Consider the following:
    1. The command might succeed or fail (rarely).
    2. The output should be concise but realistic.
    3. Include any relevant file names, directory structures, or data that makes sense.
    4. If the command is invalid, return an appropriate error message.

    Respond only with the simulated CLI output, nothing else.
    """
    
    output = ask_llm_ollama(system_prompt, user_prompt)
    
    # Simulate a return code (mostly 0, occasionally non-zero)
    return_code = 0 if random.random() < 0.9 else random.randint(1, 127)
    
    return return_code, output.strip()

def execute_command(command: str) -> tuple[int, str]:
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        return 0, output
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output

def main(prompt: str):
    context = f"GOAL: {prompt}\n\nCurrent working directory: {os.getcwd()}\n"
    
    while True:
        response = chat(prompt=f"{context}\nWhat is your next action? Explain briefly and provide the command.")
        
        if "<|DONE|>" in response.upper():
            print("[green]Task completed.[/green]")
            break

        command_parts = response.split("COMMAND:", 1)
        if len(command_parts) < 2:
            print("[red]Error: No command provided.[/red]")
            continue

        command = command_parts[1].strip()
        print(f"[green][EXECUTING][/green] {command}")
        
        return_code, output = fake_execute_command(command)
        
        context += f"\nExecuted command: {command}\nReturn code: {return_code}\nOutput:\n{output}\n"
        print(f"[cyan][OUTPUT][/cyan] (Return code: {return_code})\n{output}")

        time.sleep(1)

if __name__ == "__main__":
    typer.run(main)
