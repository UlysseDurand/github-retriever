import requests
import re
import json
import esprima
import base64
import subprocess

def make_gh_request(request: list[str]):
    result = subprocess.run(
        request,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error: {result.stderr}")
    
    return json.loads(result.stdout)


def find_pypi_packages(regexp: re.Pattern) -> list[str]:
    response = requests.get('https://pypi.org/simple/')
    package_list = re.findall(r'>([^<]+)</a>', response.text)
    matching_packages = [p for p in package_list if re.search(regexp, p)]
    return matching_packages

# Need to export a GitHub API key to GH_TOKEN
def find_github_packages(regexp: re.Pattern):
    repos = make_gh_request(
        ["gh", "search", "repos", "trame- in:name", 
         "--limit", "1000", 
         "--json", "name,owner,url,stargazersCount"]
    )
    exact_matches = [r for r in repos if regexp.match(r['name'])]
    return [r['name'] for r in exact_matches]

def get_pypi_package_infos(package_name: str) -> dict:
    r = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    info = r.json()['info']
    return info

# Retrieve what we want from a pyproject.toml
def get_useful_infos_pyproject(package_info: dict) -> dict[str, str]:
    return {
        "name": package_info["name"],
        "summary": package_info["summary"],
    }

# GitHub info extraction
def fetch_file_from_github(repo_url: str, file_path: str) -> str | None:
    pattern = r"github\.com[:/](.+)"
    repo_full_name = re.search(pattern, repo_url).groups()[0]
    for try_branch in ["main", "master"]:
        try:
            request_output = make_gh_request(["gh", "api", f"/repos/{repo_full_name}/contents/{file_path}?ref={try_branch}"])
            return base64.b64decode(request_output['content']).decode('utf-8')
        except Exception:
            pass
    raise Exception("File not found")


def extract_exports_js(content: str):
    tree = esprima.parseScript(content, {'loc': True})
    components = []

    def traverse(node):
        if hasattr(node, 'body'):
            for item in node.body:
                if hasattr(item, 'type'):
                    if item.type == 'ExportDefaultDeclaration':
                        if hasattr(item.declaration, 'properties'):
                            for prop in item.declaration.properties:
                                if hasattr(prop.key, 'name'):
                                    components.append(prop.key.name)
                    traverse(item)
    
    traverse(tree)
    return components

def intersect(a: list, b: list) -> list:
    return [e for e in a if e in b]


pypi_trame_packages = find_pypi_packages(re.compile(r"^trame-"))
github_trame_packages = find_github_packages(re.compile(r"^trame-"))
trame_packages = intersect(pypi_trame_packages, github_trame_packages)
print(f"Found {len(trame_packages)} trame packages: ")
for pkg in trame_packages:
    print(pkg)
