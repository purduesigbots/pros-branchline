import requests
from github_app import get_active_install_token
def validate_github_url(url:str):
    pieces = url.split("/")
    owner = None
    repo = None
    index = pieces.index("github.com")
    owner = pieces[index+1]
    repo = pieces[index+2]
    request_url = "https://api.github.com/repos/"+owner+"/"+repo
    install_token = get_active_install_token()
    headers = {"Accept": "application/vnd.github+json", "Authorization" : "Bearer "+ install_token, "X-GitHub-Api-Version":"2022-11-28" }
    r = requests.get(request_url, headers=headers)  
    print(r.json())
    return r.status_code == 200
