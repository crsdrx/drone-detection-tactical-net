from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not in .env")

client = Anthropic(api_key=api_key)

tasks = []
conversation_history = []
memory = {}

OBSIDIAN_VAULT = os.path.expanduser('~/obsidian-vault')

def load_memory():
    global memory
    try:
        with open('memory.json', 'r') as f:
            memory = json.load(f)
    except:
        memory = {
            "user_profile": {"name": "crsdrx", "role": "CEO, ML Lead", "company": "Elear Sonics", "projects": ["DDTN", "Second Brain"], "interests": ["ML", "drone detection"], "timezone": "UTC+1"},
            "conversation_memory": [],
            "learned_facts": [],
            "preferences": {"communication_style": "direct", "detail_level": "technical", "language": "Polish/English"}
        }
    return memory

def save_memory():
    with open('memory.json', 'w') as f:
        json.dump(memory, f, indent=2)

def save_to_obsidian(title, content, folder="Second Brain"):
    try:
        vault_path = os.path.join(OBSIDIAN_VAULT, folder)
        os.makedirs(vault_path, exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '' for c in title)
        file_path = os.path.join(vault_path, f"{safe_title}.md")
        backlinks = f"\n\n## Links\n- [[Second Brain]]\n- [[{datetime.now().strftime('%Y-%m-%d')}]]"
        full_content = f"# {title}\n\n{content}{backlinks}\n\n_Created: {datetime.now().isoformat()}_"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_daily_log(entry):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        log_path = os.path.join(OBSIDIAN_VAULT, 'Daily Logs', f'{today}.md')
        if not os.path.exists(log_path):
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            header = f"# {today}\n\n## Activity\n\n"
        else:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            header = content
        timestamp = datetime.now().strftime('%H:%M')
        new_entry = f"- [{timestamp}] {entry}\n"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(header + new_entry)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/api/chat', methods=['POST'])
def chat():
    global memory, conversation_history
    message = request.json.get('message')
    memory = load_memory()
    
    system_prompt = f"""You are Second Brain - AI assistant for crsdrx working on DDTN.
User: {memory['user_profile']['name']} ({memory['user_profile']['role']})
Projects: {', '.join(memory['user_profile']['projects'])}
Style: Direct, technical."""
    
    conversation_history.append({"role": "user", "content": message})
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=conversation_history
        )
        assistant_message = response.content[0].text
        conversation_history.append({"role": "assistant", "content": assistant_message})
        
        save_to_obsidian(f"Chat - {message[:30]}", assistant_message)
        update_daily_log(f"Chat: {message[:50]}")
        
        return jsonify({'response': assistant_message})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    return jsonify(load_memory())

@app.route('/api/memory', methods=['POST'])
def update_memory():
    global memory
    updates = request.json
    memory = load_memory()
    for key, value in updates.items():
        if key in memory:
            if isinstance(memory[key], dict):
                memory[key].update(value)
            elif isinstance(memory[key], list):
                memory[key] = value
    save_memory()
    return jsonify({'success': True, 'memory': memory})

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

if __name__ == '__main__':
    load_memory()
    app.run(port=5000, debug=True)
