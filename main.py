from github_scraper import retrieve_gh_repos_from_topic, retrieve_multiple_repos_graphql
from tabulate import tabulate

def process_widgets(data):
    widgets = []
    repos = data.get('data', {})
    for repo_key, repo_data in repos.items():
        description = repo_data.get('description', '')
        topics_nodes = repo_data.get('repositoryTopics', {}).get('nodes', [])
        topics = [node['topic']['name'] for node in topics_nodes if node['topic']['name'] != 'trame']
        widget = {
            'name': repo_data.get('name'),
            'description': description,
            'url': f"https://github.com/Kitware/{repo_key}" if 'Kitware' in str(repo_data) else f"https://github.com/other/{repo_key}",
            'openGraphImageUrl': repo_data.get('openGraphImageUrl', ''),
            'topics': topics
        }
        serialized = {}
        serialized["name"] = f"[{widget['name']}]({widget['url']} \"{widget['description']}\")"
        serialized["image"] = f"![]({widget['openGraphImageUrl']})" if widget['openGraphImageUrl'] else "No image available"
        serialized["topics"] = ", ".join(widget['topics']) if widget['topics'] else "No topics"
        widgets.append(serialized)
    return widgets

def main():
    widgets = process_widgets(retrieve_multiple_repos_graphql(retrieve_gh_repos_from_topic("trame")))
    with open("table.md", "w") as f:
        f.write(tabulate(widgets, tablefmt="github", headers="keys"))

if __name__ == "__main__":
    main()