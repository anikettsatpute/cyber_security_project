import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from transformers import DistilBertForSequenceClassification
from transformers import DataCollatorWithPadding
import json
import os
import random

ner_model_dir = './chatbot/ner_model'
intent_model_dir = './chatbot/intent_model'

# get any model from the model directory
# search for dirs starting with name checkpoint
# get the latest checkpoint

latest_checkpoint_ner = max([os.path.join(ner_model_dir, d) for d in os.listdir(ner_model_dir) if os.path.isdir(os.path.join(ner_model_dir, d)) and d.startswith("checkpoint")])

latest_checkpoint_intent = max([os.path.join(intent_model_dir, d) for d in os.listdir(intent_model_dir) if os.path.isdir(os.path.join(intent_model_dir, d)) and d.startswith("checkpoint")])

ner_model_dir_latest = latest_checkpoint_ner
intent_model_dir_latest = latest_checkpoint_intent
print(f"Using NER model from: {ner_model_dir}")
print(f"Using Intent model from: {intent_model_dir}")

# Load the NER model
ner_model = BertForTokenClassification.from_pretrained(ner_model_dir_latest)

# tokenizer is also saved in the model directory
ner_tokenizer = BertTokenizerFast.from_pretrained(ner_model_dir)

# Load the intent classification model
intent_model = DistilBertForSequenceClassification.from_pretrained(intent_model_dir_latest)

intent_to_label_file = './chatbot/intent_model/intent_labels.json'
entity_to_label_file = './chatbot/ner_model/entity_labels.json'

with open(intent_to_label_file, "r") as file:
    intents = json.load(file)

with open(entity_to_label_file, "r") as file:
    entities = json.load(file)

intent_tokenizer = BertTokenizerFast.from_pretrained(intent_model_dir)

def handle_synonyms(entity, value):
    if entity == "order_id":
        if value in ["latest", "newest", "recent", "last"]:
            return -1
        if value in ["oldest", "first", "earliest"]:
            return 0
    return value

generic_bot_responses = {
    "track_order_missing_order_id" : [
        "Please provide the order ID to track the order.",
        "I need the order ID to track your order.",
        "Could you please provide the order ID?",
        "I need the order ID to track your order. Could you provide it?"
    ], 
    "track_order_no_order_found" : [
        "I couldn't find any order with the provided order ID.",
        "I couldn't find any order with the order ID you provided.",
    ],
    "track_order_order_found" : [
        "The order with ID {order_id} is currently {option}.",
        "The status of order with ID {order_id} is {option}.",
        "The order with ID {order_id} is {option}.",
    ],
    "list_orders" : [
        "Here are the results for the orders you requested.\n{orders}",
        "I found the following orders.\n{orders}",
        "I found the orders you requested.\n{orders}"
    ], 
    "cancel_order_missing_order_id" : [
        "Please provide the order ID to cancel the order",
        "I need the order ID to cancel the order.",
        "Could you please provide the order ID?",
        "I need the order ID to cancel the order. Could you provide it?"
    ],
    "cancel_order_missing_reason" : [
        "Please provide a reason for cancelling the order.",
        "I need a reason to cancel the order.",
        "Could you please provide a reason for cancelling the order?",
        "I need a reason to cancel the order. Could you provide it?"
    ],
    "cancel_order_no_order_found" : [
        "I couldn't find any order with the provided order ID.",
        "I couldn't find any order with the order ID you provided.",
    ],
    "cancel_order_confirmation" : [
        "Really sorry to hear that. Do you want to cancel the order with ID {order_id}?",
        "I'm sorry to hear that. Do you want to cancel the order with ID {order_id}?",
    ],
    "cancel_order_success" : [
        "The order with ID {order_id} has been successfully cancelled.",
        "The order with ID {order_id} has been cancelled.",
        "The order with ID {order_id} is now cancelled.",
    ],
    "confirm_command_affirmation" : [
        "The order with ID {order_id} has been successfully cancelled.",
        "The order with ID {order_id} has been cancelled.",
        "The order with ID {order_id} is now cancelled.",
    ],
    "confirm_command_negation" : [
        "The order with ID {order_id} has not been cancelled.",
        "The order with ID {order_id} is not cancelled.",
        "The order with ID {order_id} is still active.",
    ],
}

entity_label_to_entity = {
    "B-ORD": "order_id",
    "I-ORD": "order_id",
    "B-COUNT": "count",
    "I-COUNT": "count",
    "B-END_DATE": "end_date",
    "I-END_DATE": "end_date",
    "B-START_DATE": "start_date",
    "I-START_DATE": "start_date",
    "B-REASON": "reason",
    "I-REASON": "reason",
    "B-AFFIRMATION": "affirmation",
    "I-AFFIRMATION": "affirmation",
    "ORD": "order_id",
    "COUNT": "count",
    "END_DATE": "end_date",
    "START_DATE": "start_date",
    "REASON": "reason",
    "AFFIRMATION": "affirmation"
}

def order_id_parser(order_id):
    if order_id in ["latest", "newest", "recent", "last"]:
        return -1
    if order_id in ["oldest", "first", "earliest"]:
        return 0

def handle_track_order(history):
    if history["root_intent"] != "track_order":
        raise ValueError("This handler is only for the track_order intent.")
    if "order_id" not in history["entities"]:
        return True, random.choice(generic_bot_responses["track_order_missing_order_id"])
    
    order_id = history["entities"]["order_id"]
    # for the time being just enter return a static response
    return True, random.choice(generic_bot_responses["track_order_no_order_found"]).format(order_id=order_id).format(option="shipped")

def handle_cancel_order(history):
    if history["root_intent"] != "cancel_order":
        raise ValueError("This handler is only for the cancel_order intent.")
    if "order_id" not in history["entities"]:
        return False, random.choice(generic_bot_responses["cancel_order_missing_order_id"])
    if "reason" not in history["entities"]:
        return False, random.choice(generic_bot_responses["cancel_order_missing_reason"])
    if "affirmation" not in history["entities"]:
        return False, random.choice(generic_bot_responses["cancel_order_confirmation"]).format(order_id=history["entities"]["order_id"])
    if history["entities"]["affirmation"] == "yes":
        return True, random.choice(generic_bot_responses["cancel_order_success"]).format(order_id=history["entities"]["order_id"])
    return True, random.choice(generic_bot_responses["confirm_command_negation"]).format(order_id=history["entities"]["order_id"])

def handle_list_orders(history):
    if history["root_intent"] != "list_orders":
        raise ValueError("This handler is only for the list_orders intent.")
    # for the time being just enter return a static response
    return True, random.choice(generic_bot_responses["list_orders"]).format(orders="Order 1: Shipped\nOrder 2: Delivered")

class IntentRule:
    def __init__(self, intent, entities, generic_bot_responses, entity_rules, handler):
        self.intent = intent
        self.entities = entities
        self.generic_bot_responses = generic_bot_responses
        self.entity_rules = entity_rules
        self.handler = handler

    def get_bot_response(self, history):
        return self.handler(history)

intent_rules = {
    "track_order": IntentRule(
        intent="track_order",
        entities=["order_id"],
        generic_bot_responses=generic_bot_responses["track_order_missing_order_id"],
        entity_rules={"order_id": "Required"},
        handler=handle_track_order
    ),
    "cancel_order": IntentRule(
        intent="cancel_order",
        entities=["order_id", "reason"],
        generic_bot_responses=generic_bot_responses["cancel_order_missing_order_id"],
        entity_rules={"order_id": "Required", "reason": "Optional"},
        handler=handle_cancel_order
    ),
    "list_orders": IntentRule(
        intent="list_orders",
        entities=[],
        generic_bot_responses=generic_bot_responses["list_orders"],
        entity_rules={},
        handler=handle_list_orders
    ),
    "give_order_id": IntentRule(
        intent="give_order_id",
        entities=["order_id"],
        generic_bot_responses=generic_bot_responses["track_order_missing_order_id"],
        entity_rules={"order_id": "Required"},
        handler=handle_track_order
    ),
    "confirm_command": IntentRule(
        intent="confirm_command",
        entities=["affirmation"],
        generic_bot_responses=generic_bot_responses["confirm_command_affirmation"],
        entity_rules={"affirmation": "Required"},
        handler=handle_track_order
    ),
    "give_reason": IntentRule(
        intent="give_reason",
        entities=["reason"],
        generic_bot_responses=generic_bot_responses["cancel_order_missing_reason"],
        entity_rules={"reason": "Required"},
        handler=handle_cancel_order
    ),
    "give_list_order_params": IntentRule(
        intent="give_list_order_params",
        entities=["start_date", "end_date", "count"],
        generic_bot_responses=generic_bot_responses["list_orders"],
        entity_rules={"start_date": "Optional", "end_date": "Optional", "count": "Optional"},
        handler=handle_list_orders
    )
}

class MultiTurnChatbot:
    def __init__(self, ner_model, ner_tokenizer, intent_model, intent_tokenizer, intents, entities, reset_flag=False):
        self.ner_model = ner_model
        self.ner_tokenizer = ner_tokenizer
        self.intent_model = intent_model
        self.intent_tokenizer = intent_tokenizer
        self.history = {
            "entities": {}
        } # contains the entities discoverd and the intents predicted in the previous turns
        self.intent = None
        self.intents = intents
        self.entities = entities
        self.id_to_label = {v: k for k, v in self.entities.items()}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ner_model.to(self.device)
        self.intent_model.to(self.device)
        self.data_collator =  DataCollatorWithPadding(self.intent_tokenizer, padding='max_length', max_length=128)
        self.reset_flag = reset_flag

    def reset_context(self):
        self.history = {
            "entities": {}
        }
        self.intent = None

    def tokenize_ner(self, text):
        # Tokenize the text
        tokenized_inputs = self.ner_tokenizer(text,
                                   return_tensors="pt",
                                   padding=True,
                                   truncation=True,
                                   max_length=128)
        return tokenized_inputs
    
    def tokenize_intent(self, text):
        # Tokenize the text
        tokenized_inputs = self.intent_tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
        return tokenized_inputs
    
    def get_intent(self, query):
        inputs = self.tokenize_intent(query).to(self.device)

        inputs.pop("token_type_ids", None)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = self.intent_model(**inputs)

        logits = outputs.logits
        predicted_id = torch.argmax(logits, dim=-1).item()

        # get the predicted intent
        # self.intents is a dictionary that maps intent_name to intent_id
        predicted_intent = list(self.intents.keys())[list(self.intents.values()).index(predicted_id)]

        return predicted_intent
    
    def get_entities(self, text):
        inputs = self.tokenize_ner(text).to(self.device)
        
        with torch.no_grad():
            outputs = self.ner_model(**inputs)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)

        # Map predictions to labels
        tokens = self.ner_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        predicted_labels = [self.id_to_label[label_id.item()] for label_id in predictions[0]]

        # combine tokens and labels
        results = []
        for token, label in zip(tokens, predicted_labels):
            if token not in ["[CLS]", "[SEP]", "[PAD]"]:  # Ignore special tokens
                results.append((token, label))

        predictions = results
    
        # get all entities in the label
        all_entities = []
        for token, label in predictions:
            if label.startswith("B-") or label.startswith("I-"):
                all_entities.append(label.split("-")[1])
        all_entities = list(set(all_entities))

        return_values = []
        for entity_label in all_entities:
            # Extract entities with the specified label
            entities = []
            for token, label in predictions:
                if label == f"B-{entity_label}" or label == f"I-{entity_label}":
                    entities.append(token)
            # print(entities)
            
            # remove subword prefixes from the entities
            entity_combined = []
            prev_entity = None
            for i , entity in enumerate(entities):
                if entity.startswith("##"):
                    if prev_entity is None:
                        prev_entity = ""
                    prev_entity += entity[2:]
                else:
                    if prev_entity:
                        entity_combined.append(prev_entity)
                    prev_entity = entity

                if i == len(entities) - 1:
                    entity_combined.append(prev_entity)
            return_values.append((entity_label, entity_combined))
        return return_values

        
    def handle_turn(self, user_input):
        try:
            if isinstance(user_input, dict):
                print("User Input: ", user_input)
                self.history = user_input
                root_intent = user_input["root_intent"] if "root_intent" in user_input else None
                user_input = user_input["query"]
            
            print("First User Input: ", user_input)

            prev_intent = self.history["intent"] if self.history and "intent" in self.history else ""
            prev_bot_response = self.history["bot_response"] if self.history and "bot_response" in self.history else ""

            current_query = f"[INT] {prev_intent} [BOT] {prev_bot_response} [USR] {user_input}"

            # Get the intent prediction
            intent = self.get_intent(current_query)
            if root_intent is None:
                root_intent = intent
            print(f"Predicted Intent: {intent}")

            # Get the entities
            prev_entities = self.history["entities"] if self.history and "entities" in self.history else {}
            entities = self.get_entities(current_query)
            print(f"Predicted Entities: {entities}")
            self.history["root_intent"] = root_intent
            self.history["intent"] = intent
            self.history["query"] = current_query
            print("here", self.history)
            for entity_label, entity_values in entities:
                print(entity_label, entity_values)
                self.history["entities"][entity_label_to_entity[entity_label]] = handle_synonyms(entity_label_to_entity[entity_label]," ".join(entity_values).strip())
            # get bot response
            print("here2")
            intent_rule = intent_rules[root_intent]
            end_flag , bot_response = intent_rule.get_bot_response(self.history)
            print(f"Bot Response: {bot_response}")
            self.history["bot_response"] = bot_response
            print(self.history)
            if self.reset_flag:
                self.reset_context()
            return end_flag
        except Exception as e:
            print(e)
            return True


chatbot = MultiTurnChatbot(ner_model, ner_tokenizer, intent_model, intent_tokenizer, intents, entities, True)

def main():
    while True:
        user_input = input("Enter text for User: ").strip()
        if not user_input:
            print("Text cannot be empty. Try again.")
            continue

        flag = chatbot.handle_turn(user_input)
        if flag:
            print("End of conversation.")
            break

if __name__ == "__main__":
    main()


