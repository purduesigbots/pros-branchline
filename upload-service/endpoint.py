from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from submit_model import SubmitModel
from utils import validate_github_url
from github_app import init_github


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_github()
    yield
app = FastAPI(lifespan=lifespan)

@app.post("/submit-template")
def submit_endpoint(input: SubmitModel):
    return validate_github_url(input.url)
