# update_awesome.py

import requests
import os
from datetime import datetime

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}

def fetch_awesome_repos():
    params = {
        "q": "awesome in:name",
        "sort": "stars",
        "order": "desc",
        "per_page": 1000
    }
    response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()["items"]

def generate_html(repos):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awesome Repos</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <h1 class="text-3xl font-bold mb-6">🔥 Top Awesome Repositories</h1>
    <p class="mb-4 text-sm text-gray-500">Last updated: {datetime.utcnow().isoformat()} UTC</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
"""
    for repo in repos:
        html += f"""
        <div class="bg-white p-4 rounded shadow">
            <a href="{repo['html_url']}" class="text-xl font-semibold text-blue-600 hover:underline" target="_blank">{repo['full_name']}</a>
            <p class="text-sm text-gray-700 mt-1">{repo['description'] or 'No description.'}</p>
            <p class="text-xs text-gray-500 mt-2">⭐ {repo['stargazers_count']} stars</p>
        </div>
"""
    html += """
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    repos = fetch_awesome_repos()
    generate_html(repos)
