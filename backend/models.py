from pydantic import BaseModel

# Define input schema for user request
class ChatRequest(BaseModel):
    user_input: str
    reset_context: bool = False  # Option to reset the conversation history

# Define response schema for bot response
class ChatResponse(BaseModel):
    bot_response: str
    intent: str
    entities: dict
