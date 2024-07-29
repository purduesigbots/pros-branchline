# pros-branchline
Branchline

Steps to run the upload service locally. 

To set up your envirmonment for local development:
1. cd into upload service.  
2. activate the virtual environment which is in the .venv folder
3. install all the requirements in the requirements.txt file via pip
4. generate a private key for the branchline_test github app via the website, also copy the client ID from that config page.
5. create a .env file (called .env in the upload-service folder) that has the following set: PRIVATE_KEY_PATH, CLIENT_ID. 

To Run the app:
1. cd into upload service
2. run `fastapi dev endpoint.py`

