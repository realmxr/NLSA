import streamlit as st
import pandas as pd
import llm_client
import safety
import executor
import json

# Page Config
st.set_page_config(
    page_title="NLSA - DietPi Agent",
    page_icon="🐧",
    layout="wide"
)

st.title("🐧 DietPi System Administrator")
st.markdown("Control your server using natural language.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_plan" not in st.session_state:
    st.session_state.pending_plan = None
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

# Sidebar for basic info/logs
with st.sidebar:
    st.header("System Info")
    st.info("Running on DietPi")
    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.pending_plan = None
        st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What would you like to do? (e.g., 'Check disk space', 'Restart nginx')"):
    # Store input
    st.session_state.last_user_input = prompt
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call LLM
    with st.chat_message("assistant"):
        with st.spinner("Analyzing request..."):
            try:
                response = llm_client.get_agent_response(prompt)
                st.session_state.pending_plan = response
                # Don't append to messages yet, wait for execution result or just show plan
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")

# Display Pending Plan (if any)
if st.session_state.pending_plan:
    plan = st.session_state.pending_plan
    
    with st.container():
        st.divider()
        st.subheader("📋 Proposed Action Plan")
        
        # Thought Process
        st.markdown(f"**Thinking:** {plan.thought_process}")
        st.markdown(f"**Agent says:** {plan.user_response}")
        
        # Prepare Data for Table
        actions_data = []
        high_risk_flag = False
        
        for action in plan.proposed_actions:
            is_safe, reason = safety.check_safety(action.command, action.risk_level)
            status_icon = "🟢"
            if not is_safe:
                high_risk_flag = True
                status_icon = "🔴"
            elif action.risk_level.upper() == "MEDIUM":
                status_icon = "jq" # Orange/Yellow emoji not universally consistent, using plain text or coloring
                status_icon = "Mz"
                status_icon = "🟠"
            
            actions_data.append({
                "Status": status_icon,
                "Risk": action.risk_level,
                "Command": action.command,
                "Description": action.description,
                "Safety Check": reason
            })
            
        # Display Table
        df = pd.DataFrame(actions_data)
        st.table(df)
        
        # Safety Warning
        if high_risk_flag:
            st.error("⚠️ WARNING: This plan contains HIGH RISK or DESTRUCTIVE actions. Review the commands carefully before proceeding.")
        
        # Action Buttons
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("✅ Execute Plan", type="primary", use_container_width=True):
                
                # Execution Logic
                output_container = st.container()
                with output_container:
                    with st.status("Executing...", expanded=True) as status:
                        all_success = True
                        
                        for action in plan.proposed_actions:
                            st.write(f"Running: `{action.command}`")
                            result = executor.execute_command(action.command)
                            
                            if result['success']:
                                st.success("Success")
                                if result['stdout']:
                                    st.code(result['stdout'])
                            else:
                                st.error("Failed")
                                st.error(result['stderr'])
                                all_success = False
                                st.warning("Stopping execution sequence due to failure.")
                                break
                        
                        status.update(label="Execution Finished", state="complete" if all_success else "error")
                
                # Logging
                safety.log_action(
                    st.session_state.last_user_input,
                    plan.model_dump(),
                    all_success
                )
                
                # Finalize
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Plan executed. Status: {'Success' if all_success else 'Failed'}."
                })
                st.session_state.pending_plan = None
                if st.button("Continue"): # Optional, forces a rerun to clear the view
                    st.rerun()

        with col2:
            if st.button("❌ Cancel", use_container_width=False):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Plan cancelled by user."
                })
                st.session_state.pending_plan = None
                st.rerun()

