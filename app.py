from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from github import Github
import requests
import logging

# Load environment variables from .env file
load_dotenv()

# Retrieve required environment variables
DEEPISEEK_API_KEY = os.getenv('DEEPISEEK_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
COMMITTER_NAME = os.getenv('COMMITTER_NAME', 'Default Name')
COMMITTER_EMAIL = os.getenv('COMMITTER_EMAIL', 'default@example.com')

# Check for required environment variables
required_env_vars = ['DEEPISEEK_API_KEY', 'GITHUB_TOKEN', 'COMMITTER_NAME', 'COMMITTER_EMAIL']
for var in required_env_vars:
    if not os.getenv(var):
        logging.error(f"Environment variable {var} is not set.")
        exit(1)

app = Flask(__name__)
CORS(app)

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)
logging.basicConfig(level=logging.DEBUG)

# Function to call DeepSeek API
def call_deepseek(prompt, action):
    headers = {
        'Authorization': f'Bearer {DEEPISEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'deepseek-chat',
        'prompt': prompt,
        'max_tokens': 500
    }
    try:
        response = requests.post('https://api.deepseek.com/beta/completions', headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['text'].strip()
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Endpoint to generate code
@app.route('/generate-code', methods=['POST'])
def generate_code():
    try:
        prompt = request.json['prompt']
        generated_code = call_deepseek(prompt, action='generate')
        return jsonify({'code': generated_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to fix code
@app.route('/fix-code', methods=['POST'])
def fix_code():
    try:
        code = request.json['code']
        fixed_code = call_deepseek(f"Fix the following code: {code}", action='fix')
        return jsonify({'fixed_code': fixed_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to analyze code
@app.route('/analyze-code', methods=['POST'])
def analyze_code():
    try:
        code = request.json['code']
        analysis = call_deepseek(f"Analyze the following code and provide suggestions for improvement:\n\n{code}", action='analyze')
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to create a new repository
@app.route('/create-repo', methods=['POST'])
def create_repo():
    try:
        repo_name = request.json['repo_name']
        description = request.json.get('description', '')
        repo = g.get_user().create_repo(name=repo_name, description=description)
        return jsonify({'repo_url': repo.html_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to push code to GitHub
@app.route('/push-code', methods=['POST'])
def push_code():
    try:
        repo_name = request.json['repo_name']
        branch_name = request.json['branch_name']
        file_name = request.json['file_name']
        file_content = request.json['file_content']
        
        repo = g.get_user().get_repo(repo_name)
        repo.create_file(
            path=file_name,
            message=f"Add {file_name}",
            content=file_content,
            branch=branch_name,
            committer={'name': COMMITTER_NAME, 'email': COMMITTER_EMAIL}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to create a new branch
@app.route('/create-branch', methods=['POST'])
def create_branch():
    try:
        repo_name = request.json['repo_name']
        branch_name = request.json['branch_name']
        base_branch = request.json['base_branch']
        
        repo = g.get_user().get_repo(repo_name)
        base_ref = repo.get_branch(base_branch)
        repo.create_git_ref(ref=f'refs/heads/{branch_name}', sha=base_ref.commit.sha)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to create an issue
@app.route('/create-issue', methods=['POST'])
def create_issue():
    try:
        repo_name = request.json['repo_name']
        title = request.json['title']
        body = request.json['body']
        
        repo = g.get_user().get_repo(repo_name)
        issue = repo.create_issue(title=title, body=body)
        return jsonify({'issue_url': issue.html_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to create a GitHub Actions workflow
@app.route('/create-github-action', methods=['POST'])
def create_github_action():
    try:
        repo_name = request.json['repo_name']
        workflow_name = request.json['workflow_name']
        workflow_content = request.json['workflow_content']
        
        repo = g.get_user().get_repo(repo_name)
        repo.create_file(
            path=f'.github/workflows/{workflow_name}.yml',
            message=f"Add {workflow_name} workflow",
            content=workflow_content,
            branch='main',
            committer={'name': COMMITTER_NAME, 'email': COMMITTER_EMAIL}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to trigger a GitHub Actions workflow
@app.route('/trigger-github-action', methods=['POST'])
def trigger_github_action():
    try:
        repo_name = request.json['repo_name']
        workflow_id = request.json['workflow_id']
        ref = request.json.get('ref', 'main')  # Default to 'main' if not provided
        
        repo = g.get_user().get_repo(repo_name)
        url = f'https://api.github.com/repos/{repo.full_name}/actions/workflows/{workflow_id}/dispatches'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'ref': ref
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            return jsonify({'success': True})
        else:
            return jsonify({'error': f'Failed to trigger workflow. Status code: {response.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Home endpoint to check if the server is running
@app.route('/')
def index():
    return "Hello, World! The bot is running."

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
