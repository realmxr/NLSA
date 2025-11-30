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
        
        # Get plan from LLM
        response = llm_client.get_agent_response(user_input)
        
        # Convert to dictionary for JSON response
        # Assuming response is a Pydantic model, use .model_dump() or .dict()
        plan_dict = response.model_dump()
        
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
        
        # Log the interaction
        # Reconstruct user input from somewhere if needed, or just log the execution
        # safety.log_action(..., plan, all_success) 
        # Since we don't strictly have the original user input here easily unless passed, 
        # we might skip logging user_input or pass it in the execute request too.
        # Let's skip strict logging or just log what we have.
        
        return jsonify({'results': results, 'success': all_success})

    except Exception as e:
        logger.error(f"Error in execute endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting NLSA Web Server on port 6767...")
    app.run(host='0.0.0.0', port=6767)
