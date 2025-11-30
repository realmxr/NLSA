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

## Running the Agent

Start the Flask Web Server:
```bash
python main.py
```
Access the interface at: `http://<your-dietpi-ip>:6767` (or `http://localhost:6767`)

## Architecture

- **main.py**: The Flask Web Server entry point.
- **llm_client.py**: Handles communication with the OpenAI API using structured JSON outputs.
- **executor.py**: Safely executes shell commands.
- **safety.py**: Validates commands and manages risk levels.
- **prompts.py**: Contains the system prompt.
- **agent_audit.log**: Logs all actions taken by the agent.
- **templates/ & static/**: Frontend assets (HTML/CSS/JS).

## Features

- **Natural Language Input**: "Check disk space", "Restart nginx", "Update the system".
- **Safety First**: High-risk commands (like `rm` or service restarts) require explicit confirmation.
- **DietPi Aware**: Preferentially uses DietPi specific tools (`dietpi-services`, etc.) where applicable.
- **Modern UI**: Dark-themed web interface with DietPi branding colors.
- **Audit Logging**: Keeps a record of all operations.
