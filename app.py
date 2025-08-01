import requests
import os
import json
from datetime import datetime, timedelta

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
CACHE_FILE = "repos_cache.json"
CACHE_DURATION_MINUTES = 30  # adjust if needed

def fetch_awesome_repositories(per_page=100, max_pages=10, use_cache=True):
    if use_cache and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
            if datetime.utcnow() - datetime.fromisoformat(cached["fetched_at"]) < timedelta(minutes=CACHE_DURATION_MINUTES):
                return cached["items"]

    all_repos = []
    for page in range(1, max_pages + 1):
        params = {
            "q": "awesome in:name",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        response = requests.get(GITHUB_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        repos = response.json().get("items", [])
        all_repos.extend(repos)
        if len(repos) < per_page:
            break

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.utcnow().isoformat(), "items": all_repos}, f, indent=2)

    return all_repos

def generate_index_html(repos):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cards_html = "\n".join([
        f"""
        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
            <div class="flex items-center space-x-4">
                <img src="{repo['owner']['avatar_url']}" alt="avatar" class="w-10 h-10 rounded-full">
                <div>
                    <a href="{repo['html_url']}" target="_blank" class="text-lg font-bold text-blue-600 hover:underline">
                        {repo['full_name']}
                    </a>
                    <p class="text-sm text-gray-500">{repo['language'] or "Unknown Language"}</p>
                </div>
            </div>
            <p class="text-sm text-gray-700 mt-3">{repo.get('description', 'No description.')}</p>
            <div class="flex flex-wrap mt-3 gap-2">
                {''.join(f'<span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded"><a href="https://github.com/topics/{topic}">{topic}</a></span>' for topic in repo.get('topics', []))}
            </div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A curated list of awesome repositories for developers, engineers, and tech enthusiasts. Updated regularly.">
    <meta name="keywords" content="GitHub, repositories, open source, developer tools, awesome list, projects, software, code">
    <meta name="author" content="Awesome Repositories - M">

    <!-- Open Graph / Facebook -->
    <meta property="og:title" content="Awesome Repositories">
    <meta property="og:description" content="A curated list of awesome repositories for developers and tech enthusiasts.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://maheshndev.github.io/awesome-repos/">
    <meta property="og:image" content="https://maheshndev.github.io/awesome-repos/assets/awesome-repo.png">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Awesome Repositories">
    <meta name="twitter:description" content="A curated list of awesome repositories for developers and tech enthusiasts.">
    <meta name="twitter:image" content="https://maheshndev.github.io/awesome-repos/assets/awesome-repo.png">

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
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    rows = "\n".join([
        f"| [{repo['full_name']}]({repo['html_url']}) | {repo.get('description', 'No description.')} | ⭐ {repo['stargazers_count']} | {repo['language'] or 'N/A'} |"
        for repo in repos
    ])
    markdown = f"""# 📚 Awesome Repositories

Check On 🫴 [https://maheshndev.github.io/awesome-repos/](https://maheshndev.github.io/awesome-repos/)

| Repository | Description | Stars | Language |
|------------|-------------|-------|----------|
{rows}
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    repos = fetch_awesome_repositories()
    generate_index_html(repos)
    generate_readme_md(repos)
