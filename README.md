# Natural Language System Administrator (NLSA)

This is an AI-powered system administrator agent for DietPi/Debian systems. It translates natural language requests into executable system commands, with a safety layer for high-risk actions.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

3. **Run the Agent**
   ```bash
   python main.py
   ```

## Architecture

- **main.py**: The entry point and TUI (Terminal User Interface).
- **llm_client.py**: Handles communication with the OpenAI API using structured JSON outputs.
- **executor.py**: Safely executes shell commands.
- **safety.py**: Validates commands and manages risk levels (requires user confirmation for HIGH risk).
- **prompts.py**: Contains the system prompt and behavioral instructions for the LLM.
- **agent_audit.log**: Logs all actions taken by the agent.

## Features

- **Natural Language Input**: "Check disk space", "Restart nginx", "Update the system".
- **Safety First**: High-risk commands (like `rm` or service restarts) require explicit Y/N confirmation.
- **DietPi Aware**: Preferentially uses DietPi specific tools (`dietpi-services`, etc.) where applicable.
- **Audit Logging**: Keeps a record of all operations.

