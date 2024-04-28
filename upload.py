#!/usr/bin/env python3

import os
import requests
import shutil
import subprocess
import sys

BASE_PATH = 'pros-docs/v5/_static/branchline'
DOCS_REPO_URL = 'https://github.com/purduesigbots/pros-docs.git'

def upload(name: str, version: str, new_template: bool):
    """

    Uploads a template and updated registry files to docs.
    This will upload the contents to https://pros.cs.purdue.edu/

    TODO: error handling
    
    """
    # update registry files
    shutil.copyfile('pros-branchline/pros-branchline.json', f'{BASE_PATH}/pros-branchline.json')
    shutil.copyfile(f'pros-branchline/templates/{name}.json', f'{BASE_PATH}/templates/{name}.json')

    # move zip
    if new_template:
        os.mkdir(f'{BASE_PATH}/{name}')
    shutil.copyfile(f'{name}@{version}.zip', f'{BASE_PATH}/{name}/{name}@{version}.zip')

    print('Finished upload')

    # push changes
    # TODO: make a PR or push to main?

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("error: msising arguments")
        sys.exit(1)

    # Retrieve command-line arguments
    name = sys.argv[1]
    version = sys.argv[2]

    upload(name, version, False)

if __name__ == "__main__":
    main()

