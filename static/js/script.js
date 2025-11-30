document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const executePlanBtn = document.getElementById('execute-plan-btn');
    const cancelPlanBtn = document.getElementById('cancel-plan-btn');
    
    let currentPlan = null;

    // Auto-focus input
    userInput.focus();

    function addMessage(text, sender, isHtml = false) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        if (isHtml) {
            contentDiv.innerHTML = text;
        } else {
            contentDiv.textContent = text;
        }
        
        msgDiv.appendChild(contentDiv);
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = '';
        addMessage(text, 'user');

        // Show loading or waiting state?
        // For now just wait for response
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            if (data.error) {
                addMessage(`Error: ${data.error}`, 'bot');
                return;
            }

            currentPlan = data.plan;

            // Show the agent's response text
            if (currentPlan.user_response) {
                addMessage(currentPlan.user_response, 'bot');
            }

            // Check if there are actions
            if (!currentPlan.proposed_actions || currentPlan.proposed_actions.length === 0) {
                return;
            }
            
            // Check risk levels
            const hasHighRisk = currentPlan.proposed_actions.some(action => 
                ['MEDIUM', 'HIGH'].includes(action.risk_level.toUpperCase())
            );

            if (hasHighRisk) {
                showPlanModal(currentPlan);
            } else {
                displayPlanInChat(currentPlan);
                await executePlan();
            }

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong communicating with the server.', 'bot');
        }
    }

    function displayPlanInChat(plan) {
        let html = `<div class="plan-preview">`;
        html += `<div class="plan-actions-header">Executing Actions:</div>`;
        html += `<ul class="plan-actions-list">`;
        
        plan.proposed_actions.forEach(action => {
            const riskClass = `risk-${action.risk_level.toLowerCase()}`;
            html += `<li>
                <span class="command-code">${escapeHtml(action.command)}</span>
                <span class="risk-badge ${riskClass}">${action.risk_level}</span>
            </li>`;
        });
        html += `</ul></div>`;
        
        addMessage(html, 'bot', true);
    }

    function showPlanModal(plan) {
        const thoughtDiv = document.getElementById('thought-process');
        const actionsList = document.getElementById('actions-list');
        
        thoughtDiv.textContent = plan.thought_process;
        actionsList.innerHTML = '';

        plan.proposed_actions.forEach(action => {
            const item = document.createElement('div');
            item.classList.add('action-item');
            
            // Risk Level Styling
            const risk = action.risk_level.toUpperCase();
            if (risk === 'HIGH') item.classList.add('high-risk');
            if (risk === 'MEDIUM') item.classList.add('medium-risk');

            item.innerHTML = `
                <div class="action-header">
                    <span>${action.risk_level} RISK</span>
                </div>
                <div class="action-command">${escapeHtml(action.command)}</div>
                <div class="action-desc">${escapeHtml(action.description)}</div>
            `;
            
            actionsList.appendChild(item);
        });

        modalOverlay.classList.remove('hidden');
    }

    async function executePlan() {
        modalOverlay.classList.add('hidden');
        addMessage('Executing plan...', 'bot');

        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ plan: currentPlan })
            });

            const data = await response.json();
            
            if (data.results) {
                let resultHtml = '<div>Execution Complete:</div>';
                data.results.forEach(res => {
                    const statusColor = res.success ? '#87d447' : '#e74c3c';
                    const symbol = res.success ? '✔' : '✘';
                    resultHtml += `
                        <div style="margin-top: 0.5rem; border-left: 2px solid ${statusColor}; padding-left: 0.5rem;">
                            <div style="color: ${statusColor}; font-weight: bold;">${symbol} ${escapeHtml(res.command)}</div>
                            ${res.stdout ? `<pre>${escapeHtml(res.stdout)}</pre>` : ''}
                            ${res.stderr ? `<pre style="color: #e74c3c;">${escapeHtml(res.stderr)}</pre>` : ''}
                        </div>
                    `;
                });
                addMessage(resultHtml, 'bot', true);
            } else {
                addMessage('Execution finished with no details.', 'bot');
            }

        } catch (error) {
            console.error('Error:', error);
            addMessage('Error executing plan.', 'bot');
        }
    }

    function cancelPlan() {
        modalOverlay.classList.add('hidden');
        addMessage('Plan cancelled.', 'bot');
    }

    // Event Listeners
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    executePlanBtn.addEventListener('click', executePlan);
    cancelPlanBtn.addEventListener('click', cancelPlan);

    // Utilities
    function escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});

