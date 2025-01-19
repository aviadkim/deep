from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from github import Github
import requests
import logging
import json
import time
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GitHubAssistant:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.deepseek_key = os.getenv('DEEPISEEK_API_KEY')
        self.g = Github(self.github_token)
        self.user = self.g.get_user()
        logger.info(f"Initialized GitHub Assistant for user: {self.user.login}")

    def analyze_repository(self, repo_name):
        """Comprehensive repository analysis"""
        try:
            repo = self.g.get_repo(repo_name)
            analysis = {
                "name": repo.name,
                "description": repo.description,
                "stats": {
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "issues": repo.open_issues_count,
                    "created": repo.created_at.strftime("%Y-%m-%d"),
                    "last_update": repo.updated_at.strftime("%Y-%m-%d")
                },
                "files": []
            }

            # Analyze contents
            contents = repo.get_contents("")
            for content in contents:
                if content.type == "file":
                    file_analysis = self.analyze_file(repo, content)
                    analysis["files"].append(file_analysis)

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_name}: {str(e)}")
            raise

    def analyze_file(self, repo, content):
        """Analyze a single file"""
        try:
            file_content = content.decoded_content.decode('utf-8')
            file_type = content.path.split('.')[-1] if '.' in content.path else 'unknown'
            
            analysis = self.get_code_analysis(file_content, file_type)
            
            return {
                "name": content.path,
                "type": file_type,
                "size": len(file_content),
                "content": file_content[:500] + "..." if len(file_content) > 500 else file_content,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing file {content.path}: {str(e)}")
            return {
                "name": content.path,
                "error": str(e)
            }

    def get_code_analysis(self, code, language):
        """Get AI analysis of code"""
        try:
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.deepseek_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {"role": "system", "content": f"You are a code analysis expert. Analyze this {language} code."},
                        {"role": "user", "content": code}
                    ]
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error getting code analysis: {str(e)}")
            return None

    def create_pull_request(self, repo_name, title, body, base="main"):
        """Create a pull request with improvements"""
        try:
            repo = self.g.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head="improvements",
                base=base
            )
            return pr.html_url
        except Exception as e:
            logger.error(f"Error creating PR: {str(e)}")
            raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize GitHub Assistant
assistant = GitHubAssistant()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message', '').lower()
        logger.info(f"Received message: {message}")

        if "analyze" in message and "repository" in message:
            # Extract repository name
            parts = message.split()
            repo_name = next((p for p in parts if '/' in p), None)
            
            if not repo_name:
                return jsonify({
                    'response': "Please provide repository name in format owner/repo. Example: analyze repository aviadkim/deep"
                })

            analysis = assistant.analyze_repository(repo_name)
            
            # Format response
            response = f"Analysis of {analysis['name']}:\n\n"
            response += f"📊 Statistics:\n"
            response += f"• Stars: {analysis['stats']['stars']}\n"
            response += f"• Forks: {analysis['stats']['forks']}\n"
            response += f"• Open Issues: {analysis['stats']['issues']}\n"
            response += f"• Created: {analysis['stats']['created']}\n"
            response += f"• Last Update: {analysis['stats']['last_update']}\n\n"
            
            response += "📁 Files Analysis:\n"
            for file in analysis['files']:
                response += f"\n### {file['name']} ###\n"
                if 'error' in file:
                    response += f"Error: {file['error']}\n"
                else:
                    response += f"Type: {file['type']}\n"
                    if file['analysis']:
                        response += f"Analysis:\n{file['analysis']}\n"
                    response += f"\nPreview:\n```\n{file['content']}\n```\n"

            return jsonify({'response': response})

        elif "improve" in message:
            # Handle code improvement request
            code = message.split("improve:", 1)[1].strip() if ":" in message else ""
            if not code:
                return jsonify({
                    'response': "Please provide code to improve. Example: improve: def hello(): print('Hello')"
                })
                
            analysis = assistant.get_code_analysis(code, "python")
            return jsonify({'response': f"Code Analysis:\n{analysis}"})

        else:
            return jsonify({
                'response': """I can help you with:
1. Repository Analysis: "analyze repository owner/repo"
2. Code Improvement: "improve: [your code here]"
3. File Analysis: "analyze file owner/repo/path"

Example: analyze repository aviadkim/deep"""
            })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    # Try different ports if 5001 is busy
    ports = [5001, 5002, 5003, 5004, 5005]
    
    for port in ports:
        try:
            app.run(debug=True, host='0.0.0.0', port=port)
            break
        except OSError:
            logger.warning(f"Port {port} is in use, trying next port...")
            continue