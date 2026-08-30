from pydantic import BaseModel


class Alert(BaseModel):
    id: str
    severity: str
    title: str
    body: str
    timestamp: str
    action: str
