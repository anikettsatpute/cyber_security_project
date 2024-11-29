from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import BertTokenizerFast, BertForTokenClassification
from transformers import DistilBertForSequenceClassification
from chatbot import MultiTurnChatbot, handle_synonyms, intent_rules, generic_bot_responses  # Import your chatbot components

import os
import torch
import json

# Initialize FastAPI app
app = FastAPI(title="Chatbot API")

# Load models and tokenizers
ner_model_dir = '../ner_model'
intent_model_dir = '../intent_model'

latest_checkpoint_ner = max([os.path.join(ner_model_dir, d) for d in os.listdir(ner_model_dir) if os.path.isdir(os.path.join(ner_model_dir, d)) and d.startswith("checkpoint")])
latest_checkpoint_intent = max([os.path.join(intent_model_dir, d) for d in os.listdir(intent_model_dir) if os.path.isdir(os.path.join(intent_model_dir, d)) and d.startswith("checkpoint")])

# Load NER model and tokenizer
ner_model = BertForTokenClassification.from_pretrained(latest_checkpoint_ner)
ner_tokenizer = BertTokenizerFast.from_pretrained(ner_model_dir)

# Load Intent Classification model and tokenizer
intent_model = DistilBertForSequenceClassification.from_pretrained(latest_checkpoint_intent)
intent_tokenizer = BertTokenizerFast.from_pretrained(intent_model_dir)

# Load intents and entities
with open(os.path.join(intent_model_dir, "intent_labels.json"), "r") as f:
    intents = json.load(f)

with open(os.path.join(ner_model_dir, "entity_labels.json"), "r") as f:
    entities = json.load(f)

# Initialize the chatbot
chatbot = MultiTurnChatbot(ner_model, ner_tokenizer, intent_model, intent_tokenizer, intents, entities)

# Define input schema
class ChatRequest(BaseModel):
    user_input: str
    reset_context: bool = False  # Option to reset the conversation history

class ChatResponse(BaseModel):
    bot_response: str
    intent: str
    entities: dict

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    """
    Endpoint to interact with the chatbot.
    """
    if request.reset_context:
        chatbot.reset_context()  # Reset context if requested

    user_input = request.user_input.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="User input cannot be empty.")

    # Handle the user's input
    try:
        print("User input:", user_input, type(user_input))
        end_flag = chatbot.handle_turn(user_input)
        return ChatResponse(
            bot_response=chatbot.history["bot_response"],
            intent=chatbot.history["intent"],
            entities=chatbot.history["entities"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Chatbot API"}

