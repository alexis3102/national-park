from pydantic import BaseModel

class token_schema(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str