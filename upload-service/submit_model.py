
from pydantic import BaseModel


class SubmitModel(BaseModel):
    url: str
    tag: str
