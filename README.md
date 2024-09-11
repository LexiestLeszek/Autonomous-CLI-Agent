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

4. Follow the prompts to set up your goal and start interacting with the agent.

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
