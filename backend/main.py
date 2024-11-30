import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, Response, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from models import ChatRequest, ChatResponse, login_req, register_req
from chatbot.chatbotInfra.chatbot import MultiTurnChatbot
import os
from transformers import BertTokenizerFast, BertForTokenClassification
from transformers import DistilBertForSequenceClassification
from user_agents import parse
from loggers import log_login_to_json
from datetime import datetime as dt, timezone
from AIModels.loginModel.final_model import get_model as get_login_model, get_predictions as get_login_predictions
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import matplotlib.pyplot as plt

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (Ensure requests only come from allowed hosts)
app.add_middleware(
    TrustedHostMiddleware,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "381836fe163039ab7bcd0a84bf54dded9fbd4269"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPI = 30

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE = "ecommerce.db"
KEYSTROKE_FILE_PATH = "./logs/keystroke.json"

# Function to read keystroke data from the file
def read_keystroke_data():
    # Check if the file exists
    if os.path.exists(KEYSTROKE_FILE_PATH):
        with open(KEYSTROKE_FILE_PATH, "r") as f:
            return json.load(f)
    else:
        # If the file doesn't exist, return an empty list
        return []

# Function to write keystroke data to the file
def write_keystroke_data(data):
    # Ensure the directory exists before creating the file
    os.makedirs(os.path.dirname(KEYSTROKE_FILE_PATH), exist_ok=True)

    # Write the keystroke data to the file
    with open(KEYSTROKE_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Load models and tokenizers
ner_model_dir = './chatbot/ner_model'
intent_model_dir = './chatbot/intent_model'

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

# initialize the login model
login_model_user, login_model_ip = get_login_model()
print("Login model loaded successfully")

# Function to load or refresh the model
def refresh_login_model():
    try:
        print("Refreshing login model...")
        login_model_user, login_model_ip = get_login_model()  # This will call the function to load your model
        print("Login model refreshed successfully")
    except Exception as e:
        print(f"Error refreshing login model: {str(e)}")

# Create the scheduler
scheduler = BackgroundScheduler()

# Add the job to refresh the model every 10 minutes (600 seconds)
scheduler.add_job(refresh_login_model, 'interval', minutes=10)

# Start the scheduler
scheduler.start()

# JWT token
def create_access_token(user_id: str):
    to_encode = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=20)
    }
    # create token
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/loginAnomalies")
async def get_login_anomalies(request: Request):
    """
    Endpoint to get the login anomalies from the login model.
    """
    # Get the login anomalies from the model
    data = pd.read_json('./logs/login.json')

    # Create DataFrame
    anomalies_users, anomalies_ips = get_login_predictions(login_model_user, login_model_ip, data)

    # get anomaly_score of user with user_id 20101
    print(anomalies_users[anomalies_users['user_id'] == 20101])

    # process the anomalies with score greater than 0.3
    anomalies_users = anomalies_users[anomalies_users['anomaly_score_user_id'] < 0]

    # process the anomalies with score greater than 0.3
    anomalies_ips = anomalies_ips[anomalies_ips['anomaly_score_ip_address'] < 0]

    # filter for maximum 20 users with highest anomaly score
    anomalies_users = anomalies_users.sort_values(by='anomaly_score_user_id', ascending=False)
    print(anomalies_users.sort_values(by='weighted_failures_user', ascending=False).head(20)[['user_id', 'anomaly_score_user_id', 'weighted_failures_user']])

    # for each user_id keep their highest anomaly score
    anomalies_users = anomalies_users.groupby('user_id').agg({'anomaly_score_user_id': 'max'}).reset_index()

    # get top 20 users with highest anomaly score
    anomalies_users = anomalies_users.sort_values(by='anomaly_score_user_id', ascending=True).head(20)

    # get top 20 ips with highest anomaly score
    anomalies_ips = anomalies_ips.sort_values(by='anomaly_score_ip_address', ascending=True).head(20)

    anomalies_user = anomalies_users[['user_id', 'anomaly_score_user_id']]
    anomalies_ip = anomalies_ips[['ip_address', 'anomaly_score_ip_address']]
    anomalies_user = anomalies_user.where(pd.notna(anomalies_user), None)
    anomalies_ip = anomalies_ip.where(pd.notna(anomalies_ip), None)

    # Further ensure no NaN values are left before returning data
    anomalies_user = anomalies_user.fillna(method='ffill')
    anomalies_ip = anomalies_ip.fillna(method='ffill')

    return {
        "anomalies_users": anomalies_user.to_dict(orient='records'),
        "anomalies_ips": anomalies_ip.to_dict(orient='records')
    }


@app.post("/keystroke")
async def receive_keystroke_data(user_input: UserInput):
    """
    API endpoint to receive keystroke timing data and store it in a JSON file.
    """
    try:
        # Validate and process the input
        data = user_input.dict()
        print(data)

        # Log the data for debugging
        print("Received keystroke data:", json.dumps(data, indent=4))

        # Read the existing keystroke data from the JSON file
        keystroke_data = read_keystroke_data()

        # Append the new data to the keystroke data list
        print(data['user_input']['avg_key_delay'])
        # only append data for avg_key_delay greater than 0
        if data['user_input']['avg_key_delay'] > 0:
            # append user data for avg_key_delay
            keystroke_data.append(data["user_input"])

        # Write the updated keystroke data back to the file
        write_keystroke_data(keystroke_data)

        return {"status": "success", "message": "Keystroke data stored successfully."}

    except Exception as e:
        # Handle errors and send appropriate HTTP response
        raise HTTPException(status_code=400, detail=f"Error processing data: {str(e)}")


@app.post("/login")
async def login(request: Request, login_data: login_req):
    # Extract metadata
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)
    device_type = "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "Desktop"

    # Log the request details
    print(f"IP Address: {ip_address}")
    print(f"Device Type: {device_type}")
    print(f"User-Agent: {user_agent_string}")
    print(f"Timestamp: {dt.now(timezone.utc).isoformat()}")

    # Database connection
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    print("Login data:", login_data)

    # Check if user exists
    c.execute("SELECT * FROM users WHERE user_id=?", (login_data.user_id,))
    user = c.fetchone()

    if user:
        if not verify_password(login_data.password, user[1]):
            conn.close()
            print("Status: Invalid credentials")
            log_login_to_json(login_data.user_id, ip_address, device_type, user_agent_string,-1)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            access_token = create_access_token(login_data.user_id)
            conn.close()
            response = Response()

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="None",    
                max_age=ACCESS_TOKEN_EXPI * 60
            )
            # Return the login details with metadata
            log_login_to_json(login_data.user_id, ip_address, device_type, user_agent_string, +1)
            return response

    else:
        conn.close()
        log_login_to_json(login_data.user_id, ip_address, device_type, user_agent_string,-1)
        raise HTTPException(status_code=401, detail="User does not exist")

@app.post("/register")
def register(request: register_req):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if user_id already exists
    c.execute("SELECT * FROM users WHERE user_id=?", (request.user_id,))
    user = c.fetchone()
    if user:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        hashed_password = pwd_context.hash(request.password)
        c.execute('''
            INSERT INTO users (user_id, password, name, email, address, phone_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (request.user_id, hashed_password, request.name, request.email, request.address, request.phone_number))

        conn.commit()
        conn.close()
        access_token = create_access_token(request.user_id)

        response = Response()

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=ACCESS_TOKEN_EXPI * 60
        )

        return response

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    """
    Endpoint to interact with the chatbot.
    """
    if request.reset_context:
        chatbot.reset_context()  # Reset context if requested

    user_input = request.user_input
    if not user_input:
        raise HTTPException(status_code=400, detail="User input cannot be empty.")

    # Handle the user's input
    try:
        # print("User input:", user_input, type(user_input))
        end_flag = chatbot.handle_turn(user_input)
        return ChatResponse(
            bot_response=chatbot.history["bot_response"],
            intent=chatbot.history["intent"],
            entities=chatbot.history["entities"],
            root_intent=chatbot.history["root_intent"],
            terminate_context=end_flag
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/protected")
async def protected(request: Request):
    token = request.cookies.get("access_token")
    print("token", token)
    if not token:
        print("No token")
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    return {"message": "This is a protected route", "user_id": payload['user_id']}

@app.get("/admin")
async def admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)

    # find userid in admin.csv
    admin_df = pd.read_csv("admin.csv")
    
    for i in admin_df['user_id']:
        if str(i) == str(payload['user_id']):
            return {"message": "This is an admin route", "user_id": payload['user_id']}

    raise HTTPException(status_code=403, detail="Not authorized")

@app.post("/logout")
def logout(response: Response):
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True, 
        samesite="None",
        max_age=0,
        expires=datetime.now(timezone.utc) - timedelta(days=1)
    )
    return {"message": "Logged out successfully"}


