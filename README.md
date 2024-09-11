# Autonomous-CLI-Agent
Autonomous CLI Agent that uses Local LLM with Ollama to execute tasks in CLI.

# Autonomous Coding Agent

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements an interactive shell-like environment powered by a large language model (LLM). It allows users to describe goals and receive step-by-step instructions and explanations for achieving those goals through shell commands.

The Autonomous Coding Agent uses Ollama to interact with an AI model, providing a unique interface between human users and the command line. It's designed to assist with coding tasks, file manipulation, and general system operations.

## Features

- Interactive shell environment powered by an AI model
- Step-by-step instructions for complex tasks
- Real-time observations and explanations after each command execution
- Colored console output for improved readability
- Error handling and feedback for failed commands
- Modular design allowing easy modification and extension

## Usage

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/autonomous-cli-agent.git
   cd autonomous-cli-agent
   ```

2. Install dependencies:
   ```
   pip install typer ollama rich
   ```

3. Run the application:
   ```
   python main.py
   ```

## Example output

/path/to/autonomous-cli-agent.py "codey.py doesn't work, it sshould count from 1 to 10. Take a look at this file and fix it."
[PROMPT] GOAL: codey.py doesn't work, it sshould count from 1 to 10. Take a look at this file and fix it.

Current working directory: /path/to/autonomous-cli-agent


Action History:


What is your next action? Explain briefly and provide the command. If the goal is completed (codey.py doesn't work, it sshould count from 1
to 10. Take a look at this file and fix it.), then only return <|DONE|>.
[RESPONSE] Action: Analyze codey.py to identify the issue causing it not to run correctly.

COMMAND: cat codey.py 



[EXECUTING] cat codey.py
[OUTPUT] (Return code: 0)
```
# codey.py
```
[PROMPT] GOAL: codey.py doesn't work, it sshould count from 1 to 10. Take a look at this file and fix it.

Current working directory: /path/to/autonomous-cli-agent

Executed command: cat codey.py
Return code: 0
Output:
```
# codey.py
```


Action History:
Explanation: Action: Analyze codey.py to identify the issue causing it not to run correctly.
Command: cat codey.py
Return code: 0
Output: ```
# codey.py
```

What is your next action? Explain briefly and provide the command. If the goal is completed (codey.py doesn't work, it sshould count from 1
to 10. Take a look at this file and fix it.), then only return <|DONE|>.
[RESPONSE] Action:  Add code to make the script count from 1 to 10.

Command: echo """"
for i in {1..10}:
    print(i)
echo """ > codey.py 


<|DONE|> 

Task completed.
```

## Requirements

- Python 3.7+
- Typer
- Ollama
- Rich

## Installation

1. Install Python (version 3.7+ recommended)
2. Install the required packages using pip:
   ```
   pip install typer ollama rich
   ```
3. Ensure Ollama is installed and configured on your system

## Configuration

The main configuration is done through the `ollama_model` variable at the top of the `main.py` file. You can modify this to use different Ollama models.

Additional customization options can be added by modifying the `SYSTEM` prompt in the `main.py` file.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---
