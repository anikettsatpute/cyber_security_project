from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Define input schema for user request
class ChatRequest(BaseModel):
    user_input: dict
    reset_context: bool = False  # Option to reset the conversation history

# Define response schema for bot response
class ChatResponse(BaseModel):
    bot_response: str
    intent: str
    entities: dict
    root_intent: str
    terminate_context: bool = False  # Option to terminate

class login_req(BaseModel):
    user_id: str
    password: str

class register_req(BaseModel):
    user_id: str
    password: str
    name: str
    email: str
    address: str
    phone_number: str

class KeystrokeData(BaseModel):
    key: str
    time: int  # Epoch timestamp in milliseconds
    interKeyDelay: Optional[int]  # Time delay between this keystroke and the previous one

class UserInput(BaseModel):
    user_input: dict  # Contains details like entities, query, etc.
