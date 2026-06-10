import subprocess
import os
import json
import requests
import re
from jinja2 import Template

def minify_graphql(query):
    query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
    query = re.sub(r'\s+', ' ', query)
    for char in ['{', '}', '(', ')', ':', ',']:
        query = query.replace(f' {char}', char)
        query = query.replace(f'{char} ', char)
    query = query.strip()
    return query

def make_gh_request(request: list[str]):
    result = subprocess.run(
        request,
        capture_output=True,
        text=True,
        env=os.environ
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

def retrieve_multiple_repos_graphql(repos: list[str], additional_files: dict[str, str]):
    query = Template("""
        query {
        {%- for repo in repos %}
            {%- set owner = repo.split('/')[0] %}
            {%- set name = repo.split('/')[1] %}
            {%- set alias = repo.replace('/', '_').replace('-', '_') %}
            {{ alias }}: repository(owner: "{{ owner }}", name: "{{ name }}") {
                name
                nameWithOwner
                description
                openGraphImageUrl
                repositoryTopics(first: 10) {
                    nodes {
                        topic {
                            name
                        }
                    }
                }
                {%- for file in additional_files %}
                {{ file }}: object(expression: "HEAD:{{ additional_files[file] }}") {
                    ... on Blob {
                        text
                    }
                }
                {%- endfor %}
            }
            {%- endfor %}
        }
    """).render(repos=repos, additional_files=additional_files).strip()
    mini_query = minify_graphql(query)
    cmd = ["gh", "api", "graphql", "-f", f"query={mini_query}"]
    data = json.loads(make_gh_request(cmd))["data"]
    return data

if __name__ == "__main__":
    repos = retrieve_gh_repos_from_topic("trame")
    retrieve_multiple_repos_graphql(repos)