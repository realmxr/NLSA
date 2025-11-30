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

### Option 1: Terminal Interface (CLI)
Best for direct SSH access or local usage.
```bash
python main.py
```

### Option 2: Web Interface (Streamlit)
Best for remote access via browser.
```bash
streamlit run app.py --server.port 6767
```
Access at: `http://<your-dietpi-ip>:6767`

## Architecture

- **main.py**: The TUI (Terminal User Interface).
- **app.py**: The Streamlit Web Interface.
- **llm_client.py**: Handles communication with the OpenAI API using structured JSON outputs.
- **executor.py**: Safely executes shell commands.
- **safety.py**: Validates commands and manages risk levels.
- **prompts.py**: Contains the system prompt.
- **agent_audit.log**: Logs all actions taken by the agent.

## Features

- **Natural Language Input**: "Check disk space", "Restart nginx", "Update the system".
- **Safety First**: High-risk commands (like `rm` or service restarts) require explicit confirmation.
- **DietPi Aware**: Preferentially uses DietPi specific tools (`dietpi-services`, etc.) where applicable.
- **Audit Logging**: Keeps a record of all operations.
