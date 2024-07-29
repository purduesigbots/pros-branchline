

#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from jwt import JWT, jwk_from_pem
import time
import requests

def init_github():
    print("TEST")
    load_dotenv()
    global cur_jwt
    global jwt_exp
    global install_token
    cur_jwt = None
    jwt_exp = None
    get_active_jwt()
    install_token = generate_install_token()


def get_active_install_token():
    return install_token
def get_active_jwt() -> str:
    global cur_jwt
    global jwt_exp
    if cur_jwt is None or jwt_exp < int(time.time()):
        new_cur_jwt, new_exp = generate_JWT()
        cur_jwt = new_cur_jwt
        jwt_exp = new_exp
        return new_cur_jwt
    return cur_jwt

def generate_JWT() -> tuple[str, int]:
    pem = os.getenv("PRIVATE_KEY_PATH")
    client_id = os.getenv("CLIENT_ID")

    # Open PEM
    with open(pem, 'rb') as pem_file:
        signing_key = jwk_from_pem(pem_file.read())
    exp = int(time.time()) + 500
    print(exp)
    payload = {
        # Issued at time
        'iat': int(time.time()),
        # JWT expiration time (10 minutes maximum)
        'exp': exp,
        
        # GitHub App's client ID
        'iss': client_id
    }

    # Create JWT
    jwt_instance = JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')
    print(encoded_jwt)
    print(jwt_instance.decode(encoded_jwt, signing_key))

    return (encoded_jwt, exp)

def get_install_id() -> int:
    headers = {"Accept": "application/vnd.github+json", "Authorization" : "Bearer "+ get_active_jwt(), "X-GitHub-Api-Version":"2022-11-28" }
    r = requests.get("https://api.github.com/repos/purduesigbots/pros-branchline/installation", headers=headers)
    print(r.json().get("id"))
    return r.json().get("id")

def generate_install_token():
    headers = {"Accept": "application/vnd.github+json", "Authorization" : "Bearer "+ get_active_jwt(), "X-GitHub-Api-Version":"2022-11-28" }
    r = requests.post("https://api.github.com/app/installations/" + str(get_install_id())+ "/access_tokens", headers=headers )
    print(r.json())
    return r.json().get("token")