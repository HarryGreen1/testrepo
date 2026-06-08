import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_USERNAME = "HarryGreen1"
REPO_NAME = "testrepo"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 

url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/commits"

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28" 
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    commits = response.json()
    print(f"Successfully fetched {len(commits)} recent commits!\n")
    
    for commit in commits[:5]: 
        author = commit['commit']['author']['name']
        message = commit['commit']['message']
        print(f"[{author}]: {message}")
        
    with open("github_data.json", "w", encoding="utf-8") as file:
        json.dump(commits, file, indent=4)
    print("\nData saved successfully to github_data.json!")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print(response.text)