import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
import prompts

load_dotenv()

class Action(BaseModel):
    command: str
    risk_level: str = Field(description="LOW, MEDIUM, or HIGH")
    description: str

class AgentResponse(BaseModel):
    thought_process: str
    proposed_actions: List[Action]
    user_response: str

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_agent_response(user_input: str) -> AgentResponse:
    """
    Sends user input to LLM and returns structured response.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": prompts.SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
            
        # Parse JSON into Pydantic model
        data = json.loads(content)
        return AgentResponse(**data)
        
    except Exception as e:
        # Fallback or error handling
        raise RuntimeError(f"LLM Error: {str(e)}")

