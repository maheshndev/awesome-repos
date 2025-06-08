import requests
import os
from datetime import datetime

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
SEARCH_QUERY = "awesome in:name"
MAX_RESULTS = 100

def fetch_awesome_repositories():
    params = {
        "q": SEARCH_QUERY,
        "sort": "stars",
        "order": "desc",
        "per_page": MAX_RESULTS
    }
    response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

def generate_index_html(repos):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cards_html = "\n".join([
        f"""
        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <a href="{repo['html_url']}" target="_blank" class="text-lg font-bold text-blue-600 hover:underline">
                {repo['full_name']}
            </a>
            <p class="text-sm text-gray-700 mt-2">{repo.get('description', 'No description.')}</p>
            <div class="text-xs text-gray-500 mt-3">
                ⭐ {repo['stargazers_count']} stars • Updated: {repo['updated_at'][:10]}
            </div>
        </div>
        """ for repo in repos
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awesome Repositories</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-6">
    <div class="max-w-7xl mx-auto">
        <h1 class="text-4xl font-bold mb-4">🚀 Awesome Repositories</h1>
        <p class="text-sm text-gray-500 mb-6">Last updated: {timestamp}</p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards_html}
        </div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def generate_readme_md(repos):
    rows = "\n".join([
        f"| [{repo['full_name']}]({repo['html_url']}) | {repo.get('description', 'No description.')} | ⭐ {repo['stargazers_count']} |"
        for repo in repos
    ])
    markdown = f"""# 📚 Awesome Repositories

Last updated: **{datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}**

| Repository | Description | Stars |
|------------|-------------|-------|
{rows}
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    repos = fetch_awesome_repositories()
    generate_index_html(repos)
    generate_readme_md(repos)
