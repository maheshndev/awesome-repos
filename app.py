# update_awesome.py

import requests
from datetime import datetime
import json

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
MAX_RESULTS = 1000  # GitHub Search API limit
PER_PAGE = 100

def fetch_awesome_repos():
    repos = []
    for page in range(1, MAX_RESULTS // PER_PAGE + 1):
        print(f"Fetching page {page}...")
        params = {
            "q": "awesome in:name",
            "sort": "stars",
            "order": "desc",
            "per_page": PER_PAGE,
            "page": page
        }
        response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()["items"]
        if not data:
            break
        repos.extend(data)
    return repos

def generate_html(repos):
    timestamp = datetime.utcnow().isoformat()

    with open("repos.json", "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awesome Repos</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <h1 class="text-3xl font-bold mb-6">🔥 Top Awesome Repositories</h1>
    <p class="mb-4 text-sm text-gray-500">Last updated: {timestamp} UTC</p>

    <div id="repo-list" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
    
    <div class="mt-6 flex justify-center space-x-2" id="pagination"></div>

    <script>
        let repos = {json.dumps(repos)};
        const perPage = 20;
        let currentPage = 1;

        function renderRepos(page) {{
            const start = (page - 1) * perPage;
            const end = start + perPage;
            const current = repos.slice(start, end);
            document.getElementById('repo-list').innerHTML = current.map(repo => `
                <div class="bg-white p-4 rounded shadow">
                    <a href="${{repo.html_url}}" class="text-xl font-semibold text-blue-600 hover:underline" target="_blank">${{repo.full_name}}</a>
                    <p class="text-sm text-gray-700 mt-1">${{repo.description || 'No description.'}}</p>
                    <p class="text-xs text-gray-500 mt-2">⭐ ${{repo.stargazers_count}} stars</p>
                </div>
            `).join('');
        }}

        function renderPagination() {{
            const totalPages = Math.ceil(repos.length / perPage);
            const container = document.getElementById('pagination');
            container.innerHTML = '';

            for (let i = 1; i <= totalPages; i++) {{
                const btn = document.createElement('button');
                btn.className = `px-3 py-1 border rounded ${i === currentPage ? 'bg-blue-500 text-white' : 'bg-white text-blue-600'}`;
                btn.textContent = i;
                btn.onclick = () => {{
                    currentPage = i;
                    renderRepos(currentPage);
                    renderPagination();
                }};
                container.appendChild(btn);
            }}
        }}

        renderRepos(currentPage);
        renderPagination();
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    repos = fetch_awesome_repos()
    generate_html(repos)
