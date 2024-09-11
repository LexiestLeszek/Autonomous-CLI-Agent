import os
import subprocess
import sys
import time
from rich import print
import typer
import ollama

# Set up Ollama model
ollama_model = "gemma2:2b-instruct-q4_0"

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
- Output the exact command to be executed.
- Use '<|DONE|>' on a new line when the task is completed.

Example output:
I will create a new Python file to solve the problem.
echo "print('Hello, World!')" > hello.py

Now I will execute the Python script.
python3 hello.py

<|DONE|>

End of example output.

Remember to always prioritize efficient and secure coding practices.
Remember to write only text related to your plans or executed actions. 
Do not write anything polite or somethig like 'Let me know if you want to explore other examples or have more coding tasks!'.
"""


# Function to interact with Ollama LLM
def ask_llm_ollama(system_prompt, user_prompt):
    response = ollama.chat(model=ollama_model, messages=[
        {
            'role': 'system',
            'content': system_prompt,
        },
        {
            'role': 'user',
            'content': user_prompt,
        },
    ])
    answer = response['message']['content']
    return answer

# Function to escape shell arguments
def quote(string: str) -> str:
    # Equivalent of PHP's escapeshellarg
    return "'{}'".format(string.replace("'", "'\\''"))

# Main function
def main(prompt: str):
    response = ask_llm_ollama(
        system_prompt=SYSTEM,
        user_prompt=f"GOAL: {prompt}\n\nWHAT IS YOUR OVERALL PLAN?"
    )

    print(f"[blue][PROMPT][/blue] GOAL: {prompt}")
    print(f"[yellow][RESPONSE][/yellow] {response}")

    while True:
        next_command = ask_llm_ollama(
            system_prompt=SYSTEM,
            user_prompt="SHELL COMMAND TO EXECUTE OR `<|DONE|>`. NO ADDITIONAL CONTEXT OR EXPLANATION:"
        ).strip()

        print(f"[blue][PROMPT][/blue] SHELL COMMAND TO EXECUTE OR `<|DONE|>`:")
        print(f"[yellow][RESPONSE][/yellow] {next_command}")

        if "<|DONE|>" in next_command:
            break

        time.sleep(3)

        try:
            output = subprocess.check_output(
                next_command, stderr=subprocess.STDOUT, shell=True
            ).decode()
            return_code = 0
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
            return_code = e.returncode

        observation = ask_llm_ollama(
            system_prompt=SYSTEM,
            user_prompt=f"COMMAND COMPLETED WITH RETURN CODE: {return_code}. OUTPUT:\n{output}\n\nWHAT ARE YOUR OBSERVATIONS?"
        )

        print(f"[blue][PROMPT][/blue] COMMAND COMPLETED WITH RETURN CODE: {return_code}. OUTPUT:")
        print(output)
        print(f"\n[blue][PROMPT][/blue] WHAT ARE YOUR OBSERVATIONS?")
        print(f"[yellow][RESPONSE][/yellow] {observation}")

# Set up Typer CLI
if __name__ == "__main__":
    typer.run(main)
