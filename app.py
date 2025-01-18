from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# DeepSeek API Key
DEEPISEEK_API_KEY = os.getenv('DEEPISEEK_API_KEY')
# GitHub Token
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Function to call DeepSeek API
def call_deepseek(prompt):
    headers = {
        'Authorization': f'Bearer {DEEPISEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'deepseek-chat',
        'prompt': prompt,
        'max_tokens': 500
    }
    response = requests.post('https://api.deepseek.com/beta/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['text'].strip()
    else:
        return f"Error: {response.status_code}"

# Function to create a GitHub repository
def create_github_repo(repo_name, description=""):
    url = 'https://api.github.com/user/repos'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'name': repo_name,
        'description': description,
        'private': False  # Set to True for private repos
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return f"Repository created: {response.json()['html_url']}"
    else:
        return f"Failed to create repository: {response.status_code}"

# Function to create a GitHub issue
def create_github_issue(repo, title, body):
    url = f'https://api.github.com/repos/{repo}/issues'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {'title': title, 'body': body}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return f"Issue created: {response.json()['html_url']}"
    else:
        return f"Failed to create issue: {response.status_code}"

# API endpoint to handle code analysis
@app.route('/analyze-code', methods=['POST'])
def analyze_code():
    code = request.json['code']
    prompt = f"Analyze the following code and provide suggestions for improvement:\n\n{code}"
    analysis = call_deepseek(prompt)
    return jsonify({'analysis': analysis})

# API endpoint to handle GitHub repository creation
@app.route('/create-repo', methods=['POST'])
def create_repo():
    repo_name = request.json['repo_name']
    description = request.json.get('description', '')
    result = create_github_repo(repo_name, description)
    return jsonify({'result': result})

# API endpoint to handle GitHub issue creation
@app.route('/create-issue', methods=['POST'])
def create_issue():
    repo = request.json['repo']
    title = request.json['title']
    body = request.json['body']
    result = create_github_issue(repo, title, body)
    return jsonify({'result': result})

if __name__ == "__main__":
    app.run(debug=True)