from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import llm_client
import executor
import safety
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# In-memory chat history
# Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
CHAT_HISTORY = []
MAX_HISTORY = 10  # Keep last 10 messages to prevent context window explosion

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        logger.info(f"Received user input: {user_input}")
        
        # Get plan from LLM with history
        response = llm_client.get_agent_response(user_input, CHAT_HISTORY)
        
        # Convert to dictionary for JSON response
        plan_dict = response.model_dump()
        
        # Update History
        # 1. Add User Input
        CHAT_HISTORY.append({"role": "user", "content": user_input})
        
        # 2. Add Agent Response (Summary) to history so the LLM knows what it proposed
        # We use the user_response field for conversational continuity
        CHAT_HISTORY.append({"role": "assistant", "content": plan_dict['user_response']})
        
        # Trim history if needed
        if len(CHAT_HISTORY) > MAX_HISTORY:
            CHAT_HISTORY.pop(0)
            CHAT_HISTORY.pop(0) # Pop pair to keep roles aligned

        return jsonify({'plan': plan_dict})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.json
        plan = data.get('plan')
        
        if not plan or 'proposed_actions' not in plan:
            return jsonify({'error': 'Invalid plan provided'}), 400

        results = []
        all_success = True
        
        logger.info("Executing plan...")

        for action in plan['proposed_actions']:
            command = action['command']
            risk = action['risk_level']
            
            # Double check safety (redundant but good practice)
            is_safe, reason = safety.check_safety(command, risk)
            if not is_safe:
                logger.warning(f"Executing UNSAFE/HIGH RISK command: {command} ({reason})")
            
            # Execute
            logger.info(f"Running: {command}")
            result = executor.execute_command(command)
            
            # Add command to result for frontend matching
            result['command'] = command
            results.append(result)
            
            if not result['success']:
                all_success = False
                logger.error(f"Command failed: {command}")
                # Stop execution on failure?
                # Previous logic stopped on failure.
                break
        
        # Optional: Add execution result to history for better context on failures/success?
        # For now, we stick to conversational context to keep it simple.
        
        return jsonify({'results': results, 'success': all_success})

    except Exception as e:
        logger.error(f"Error in execute endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global CHAT_HISTORY
    CHAT_HISTORY = []
    logger.info("Chat history cleared.")
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    print("Starting NLSA Web Server on port 6767...")
    app.run(host='0.0.0.0', port=6767)
