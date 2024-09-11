# Autonomous-CLI-Agent README

## Overview

This project implements an autonomous CLI agent that can read, write, and execute code using proper CLI commands. It utilizes a language model to generate plans and execute steps based on user input.

## Key Features

- File reading and writing capabilities
- Code execution support
- Directory management functions
- Interactive planning and execution process
- Rich console output formatting

## Dependencies

- `typer`: For building the command-line interface
- `rich`: For enhanced console output formatting
- `ollama`: For interacting with the language model
- `subprocess`: For executing shell commands

## Usage

To run the agent, execute the following command:

```bash
python autonomous_cli_agent.py
```

The agent will prompt you for a query, generate a goal, create a plan, and then execute the steps one by one.

## Configuration

- `DESTRUCTIVE_COMMANDS`: A list of commands that could potentially cause harm if executed
- `LLM_MODEL`: The default language model used for generating plans and explanations
- `SYSTEM_PROMPT`: The initial prompt given to the language model

## Functionality Breakdown

1. `ask_llm`: Interacts with the language model to get responses
2. `execute_command`: Executes or simulates CLI commands
3. `generate_plan`: Creates a step-by-step plan to achieve a goal
4. `parse_steps`: Extracts individual steps from the generated plan
5. `execute_step`: Determines the next CLI command to execute for a given step
6. `main`: Orchestrates the entire process, including querying, planning, and execution

## Safety Features

- Destructive command detection: The agent will stop execution if a destructive command is encountered
- Simulated execution: Allows for testing without actually running potentially harmful commands

## Development

To contribute to this project:

1. Fork the repository
2. Clone your forked copy
3. Set up a virtual environment and install dependencies
4. Write tests and make changes
5. Commit your changes and push to your branch
6. Open a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This project was inspired by the concept of autonomous agents and utilizes open-source libraries for natural language processing and console output formatting.
