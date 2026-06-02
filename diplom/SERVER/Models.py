from pydantic import BaseModel


class POST(BaseModel):
    SQL: str

class UPDATE(BaseModel):
    SQL: str

class DELETE(BaseModel):
    SQL: str

class GET(BaseModel):
    SQL: str