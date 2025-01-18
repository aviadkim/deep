import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend URL
BACKEND_URL = 'http://127.0.0.1:5000'

# Function to analyze code
def analyze_code(code):
    response = requests.post(f'{BACKEND_URL}/analyze-code', json={'code': code})
    if response.status_code == 200:
        return response.json()['analysis']
    else:
        return f"Error: {response.status_code}"

# Function to create a GitHub repository
def create_repo(repo_name, description=""):
    response = requests.post(f'{BACKEND_URL}/create-repo', json={'repo_name': repo_name, 'description': description})
    if response.status_code == 200:
        return response.json()['result']
    else:
        return f"Error: {response.status_code}"

# Function to create a GitHub issue
def create_issue(repo, title, body):
    response = requests.post(f'{BACKEND_URL}/create-issue', json={'repo': repo, 'title': title, 'body': body})
    if response.status_code == 200:
        return response.json()['result']
    else:
        return f"Error: {response.status_code}"

# Main chatbot loop
def main():
    print("Welcome to the GitHub Coding Chatbot!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        # Analyze code
        if user_input.startswith('analyze code:'):
            code = user_input[len('analyze code:'):].strip()
            analysis = analyze_code(code)
            print(f"Bot: {analysis}")

        # Create a GitHub repository
        elif user_input.startswith('create repo:'):
            repo_name = user_input[len('create repo:'):].strip()
            description = input("Enter repository description: ")
            result = create_repo(repo_name, description)
            print(f"Bot: {result}")

        # Create a GitHub issue
        elif user_input.startswith('create issue:'):
            repo = input("Enter repository (e.g., username/repo): ")
            title = input("Enter issue title: ")
            body = input("Enter issue description: ")
            result = create_issue(repo, title, body)
            print(f"Bot: {result}")

        # Unknown command
        else:
            print("Bot: I didn't understand that command. Try 'analyze code:', 'create repo:', or 'create issue:'.")

if __name__ == "__main__":
    main()