import logging
from datetime import datetime
from typing import Literal

# Configure logging
logging.basicConfig(
    filename='agent_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_action(user_input: str, plan: dict, executed: bool, output: str = ""):
    """
    Log the full interaction context.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "plan": plan,
        "executed": executed,
        "output": output
    }
    logging.info(str(entry))

def check_safety(command: str, risk_level: str) -> tuple[bool, str]:
    """
    Checks if a command is safe to execute.
    Returns (is_safe, reason).
    """
    
    # Normalize risk level
    risk = risk_level.upper()
    
    # Automatic high risk keywords check
    destructive_keywords = ["rm ", "> /dev/null", "dd ", "mkfs", ":(){:|:&};:"]
    for kw in destructive_keywords:
        if kw in command:
            return False, f"Command contains destructive keyword: '{kw}'"

    if risk == "HIGH":
        return False, "Risk level is HIGH. User confirmation required."
    
    return True, "Safe to proceed."

