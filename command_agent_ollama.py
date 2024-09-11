import os
import subprocess
import sys
import time
import typer
import ollama
from ollama import Options
from rich import print
import random
import re

LLM_MODEL = "gemma2:2b-instruct-q4_0"

SYSTEM = """
You are an autonomous CLI agent with the ability to read, write, and execute code by using CLI commands.

Your capabilities include:
1. Reading files: Use cat filename to display file contents.
2. Writing files: Use echo "content" > filename to write content to a file.
3. Executing code: Use appropriate commands to run code (e.g., python script.py for Python).
4. Creating directories: Use mkdir directory_name to create new directories.
5. Listing directory contents: Use ls or dir to list files and directories.
6. You act accordingly to the provided step-by-step process and previous performed actions.

Output format:
- Use Goal and current Step to generate output.
- Provide a brief explanation of your next action.
- Output the exact command to be executed, starting with "COMMAND".

Example output 1:
EXPLANATION: I will create a new Python file to solve the problem.
COMMAND: echo "print('Hello, World!')" > hello.py

Example output 2:
EXPLANATION: Now I will execute the Python script.
COMMAND: python3 hello.py

End of example outputs.

Remember to always prioritize efficient and secure coding practices.
Remember to write only text related to your plans or executed actions. 
Do not write anything polite or somethig like 'Let me know if you want to explore other examples or have more coding tasks!'.
"""

def get_list_elements(input_string,steps):
    # Regex pattern to match <li>...</li> tags
    pattern = r'<li>(.*?)</li>'
    
    # Find all matches
    matches = re.findall(pattern, input_string)
    
    # Print each match
    for match in matches:
        steps.append(match.strip())

def ask_llm_ollama(system_prompt, user_prompt):
    response = ollama.chat(model=LLM_MODEL,
                           options=Options(
                                temperature=0.0
                            ),
                           messages=[
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
    return_code = 0
    
    return return_code, output.strip()

def execute_command(command: str) -> tuple[int, str]:
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        return 0, output
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output

def main(query: str):
    # Goal and plan setting
    dir_path = f"Current working directory: {os.getcwd()}"
    goal = chat(system='You masterfully understand problems and rewrite them into clear goals.',prompt=f"Generate a clear goal in one sentence to solve this problem: {query}")
    goal_context = f"""{dir_path}
    Goal: {goal}
    Generate a step-by-step plan to achieve the Goal. Return only the numbered list of the steps to achieve the plan and nothing else. Each step should be inside a <li></li> tag"""
    plan = chat(system='you are a master of creating step-by-step plans based on the Goal in the format of numbered list.',prompt=goal_context)
    print('>>>>>PLAN: ',plan)
    steps = []
    action_history = []
    action_history.append(f'Prepare to achieve the goal: {goal}')
    get_list_elements(plan, steps)
    steps.append('Final step, only return "<|DONE|>"')
    
    for step in steps:
        full_context = f"""{dir_path}
        Goal is {goal}
        Action Plan is {steps}
        Action History (already performed actions) is {action_history}
        Current step is {step}
        Based on the current step, return the CLI command needed to to finish this step and a brief explanation of it.
        """
        
        response = chat(prompt=full_context)
        
        if "<|DONE|>" in response:
            print("[green]Task completed.[/green]")
            break

        command_parts = response.split("COMMAND:", 1)
        if len(command_parts) < 2:
            command = command_parts[0].strip()
            continue
        
        command = command_parts[1].strip()
        
        print(f"[green][EXECUTING][/green] {command}")
        
        return_code, output = execute_command(command)
        
        action_history.append(response)
        print(f"[cyan][OUTPUT][/cyan] (Return code: {return_code})\n{output}")

        time.sleep(3)

if __name__ == "__main__":
    query = "codey.py doesn't work, it sshould count from 1 to 10. fix it."
    main(query)
    
# Query - user's problem that needs to be solved.    
# Goal - based on the user's problem (Query), restate it to be a goal that can be achieved
# Plan - based on the Goal, develop step-by-step actionable plan to achieve the goal
# Step - based on the Plan and history of previous actions (if any), perform next step.
