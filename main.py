from github_scraper import retrieve_gh_repos_from_topic, retrieve_multiple_repos_graphql
from tabulate import tabulate

def process_widgets(repos, ignored_topics = []):
    table = []
    for _repo_key, repo_data in repos.items():
        topics = [node['topic']['name'] for node in repo_data['repositoryTopics']['nodes'] if node['topic']['name'] not in ignored_topics]
        url = f"https://github.com/{repo_data["nameWithOwner"]}"
        table.append({
            "name": f"[{repo_data['name']}]({url} \"{repo_data['description']}\")",
            "image": f"![Repository image]({repo_data['openGraphImageUrl']})" if "openGraphImageUrl" in repo_data else "",
            "topics": "<ul>" + "".join(list(map(lambda topic: f"<li>{topic}</li>", topics))) + "</ul>",
        })
    return table

def main():
    repos = retrieve_gh_repos_from_topic("trame")
    print(f"Found {len(repos)} repositories")
    widgets = process_widgets(retrieve_multiple_repos_graphql(repos, {"readme": "README.md"}), ["trame"])
    with open("table.md", "w") as f:
        f.write(tabulate(widgets, tablefmt="github", headers="keys"))

if __name__ == "__main__":
    main()
