from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Use API key directly
client = Anthropic(api_key="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")

tasks = []
conversation_history = []

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        task = request.json
        task['id'] = len(tasks) + 1
        task['created'] = datetime.now().isoformat()
        tasks.append(task)
        return jsonify(task)
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({'success': True})

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    
    conversation_history.append({
        "role": "user",
        "content": message
    })
    
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system="You are Second Brain - an AI assistant helping manage knowledge, research, and tasks. Be concise and helpful.",
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return jsonify({'response': assistant_message})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
