import requests
import os
import json
from datetime import datetime, timedelta
import shutil

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
CACHE_FILE = "repos_cache.json"
CACHE_DURATION_MINUTES = 30  # adjust if needed
OLD_DIR = "old"
HTML_FILE = "index.html"

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

def backup_old_html():
    if os.path.exists(HTML_FILE):
        if not os.path.exists(OLD_DIR):
            os.makedirs(OLD_DIR)
        timestamp = datetime.utcnow().strftime("%d-%m-%Y")
        backup_filename = f"awesome-repos-{timestamp}.html"
        backup_path = os.path.join(OLD_DIR, backup_filename)
        shutil.move(HTML_FILE, backup_path)
        print(f"Backed up old index.html → {backup_path}")

def generate_old_files_section():
    """Generate HTML list of hyperlinks to old HTML backups in /old directory."""
    if not os.path.exists(OLD_DIR):
        return ""

    files = sorted(os.listdir(OLD_DIR), reverse=True)  # newest first
    if not files:
        return ""

    links_html = "\n".join([
        f'<li class="p-1 hover:bg-slate-100"><a href="{OLD_DIR}/{fname}" target="_blank" class="text-blue-600 hover:underline">{fname}</a></li>'
        for fname in files if fname.endswith(".html")
    ])

    return f"""
    <div class="mt-10 bg-white p-4 rounded-lg shadow">
        <h2 class="text-xl font-bold mb-3">📂 Old Snapshots</h2>
        <div>
              <ul class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 list-none">
                {links_html}
              </ul>
        </div>
    </div>
    """

def generate_index_html(repos):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cards_html = "\n".join([
        f"""
        <div class="bg-white p-4 rounded-lg shadow hover:shadow-lg transition">
            <div class="flex items-center space-x-3">
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

    old_files_section = generate_old_files_section()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awesome Repositories</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A curated list of awesome repositories for developers, engineers, and tech enthusiasts. Updated regularly.">
    <meta name="keywords" content="GitHub, repositories, open source, developer tools, awesome list, projects, software, code">
    <meta name="author" content="Awesome Repositories - M">
    <link rel="icon" type="image/png" sizes="32x32" href="assets/awesome-repo.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/awesome-repo.png">
    <link rel="icon" type="image/png" sizes="16x16" href="assets/awesome-repo.png">
    <link rel="shortcut icon" href="assets/awesome-repo.png">
    <meta property="og:title" content="Awesome Repositories">
    <meta property="og:description" content="A curated list of awesome repositories for developers and tech enthusiasts.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://maheshndev.github.io/awesome-repos/">
    <meta property="og:image" content="assets/awesome-repo.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Awesome Repositories">
    <meta name="twitter:description" content="A curated list of awesome repositories for developers and tech enthusiasts.">
    <meta name="twitter:image" content="assets/awesome-repo.png">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-6">
    <div class="max-w-7xl mx-auto">
        <img src="assets/awesome-repos.png" width="50px" height="50px"> <h1 class="text-4xl font-bold mb-4">🚀 Awesome Repositories</h1>
        <p class="text-sm text-gray-500 mb-6">Last updated: {timestamp}</p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cards_html}
        </div>
        {old_files_section}
    </div>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ New index.html generated.")

def generate_readme_md(repos):
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
    print(f"✅ README.md updated.")

if __name__ == "__main__":
    repos = fetch_awesome_repositories()
    backup_old_html()
    generate_index_html(repos)
    generate_readme_md(repos)
