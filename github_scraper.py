import subprocess
import json
import requests
import re

def make_gh_request(request: list[str]):
    print(f"Executing a {len("".join(request))} character long request")
    result = subprocess.run(
        request,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error: {result.stderr}")
    return result.stdout

def retrieve_gh_star_list(star_list_url: str):
    html = requests.get(star_list_url).text
    return re.findall(r"<a href=\"\/([^ ]*)\">", html)

def retrieve_gh_repos_from_topic(topic: str):
    request = f"gh search repos --topic {topic} --limit 1000 --json fullName"
    result = json.loads(make_gh_request(request.split(' ')))
    result = [t["fullName"] for t in result]
    return result
 
def retrieve_repo_readme(repo: str):
    request = f"gh repo view {repo}"
    return make_gh_request(request.split(' '))

def retrieve_repo_infos(repo: str):
    request = f"gh repo view {repo} --json description,openGraphImageUrl,repositoryTopics"
    result = json.loads(make_gh_request(request.split(' ')))
    result["repositoryTopics"] = [t["name"] for t in result["repositoryTopics"]]
    result["fullName"] = repo
    result["url"] = f"https://github.com/{repo}"
    return result

def retrieve_multiple_repos_graphql(repos: list[str]):
    query_parts = []
    for i, repo in enumerate(repos):
        owner, name = repo.split('/')
        query_parts.append(f"""
        repo{i}: repository(owner: "{owner}", name: "{name}") {{
          name
          description
          openGraphImageUrl
          repositoryTopics(first: 10) {{
            nodes {{
              topic {{
                name
              }}
            }}
          }}
          readme: object(expression: "HEAD:README.md") {{
            ... on Blob {{
              text
            }}
          }}
        }}
        """)
    
    full_query = "query { " + " ".join(query_parts) + " }"
    
    cmd = ["gh", "api", "graphql", "-f", f"query={full_query}"]
    data = json.loads(make_gh_request(cmd))
    return data

if __name__ == "__main__":
    print()
    repos = retrieve_gh_repos_from_topic("trame")
    retrieve_multiple_repos_graphql(repos)
    # print(retrieve_repo_readme("Kitware/trame-radial-menu"))
    # print(json.dumps(retrieve_repo_infos("Kitware/trame-radial-menu"), indent=2))