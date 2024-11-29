import json
import os
from difflib import get_close_matches

# Define intents with associated entity types
# Define the intents and entities
intents = {
    "track_order": ["order_id"],
    "list_orders" : ["count", "end_date", "start_date"],
    "give_list_order_params" : ["start_date", "end_date", "count"],
    "give_order_id": ["order_id"],
    "confirm_command": ["affirmation"], 
    
    "cancel_order": ["order_id", "reason"],
    "give_reason": ["reason"],
    
    "product_search": ["product_name", "product_category", "brand_name", "price", "lower_bound", "upper_bound", "rating", "features"],
    "give_product_search_params": ["product_name", "product_category", "brand_name", "price", "lower_bound", "upper_bound", "rating", "features"],

    
    "change_order": ["order_id", "change", "reason", "item_to_be_removed"],
    "give_change_order_params": ["change", "reason", "item_to_be_removed"],
    
    "change_address": ["order_id", "new_address"],
    "give_change_address_params": ["order_id", "new_address"],
    
    "get_invoice": ["order_id"],
    "give_invoice_params": ["order_id"],
    
    "complaint": ["order_id", "complaint", "item"],
    "give_complaint_params": ["order_id", "complaint", "item"],
    
    "refund_status": ["order_id"],
    "give_refund_status_params": ["order_id"],
    
    "review": ["order_id", "rating", "review", "item"],
    "give_review_params": ["order_id", "rating", "review", "item"],
    
    "contact_human": ["reason"],
}
def get_best_match(input_str, valid_intents):
    """Find the closest match for an input string from valid intents using Levenshtein distance."""
    return get_close_matches(input_str, valid_intents, n=1, cutoff=0.8)

def get_best_entity_match(input_str, valid_entities):
    """Find the closest match for an entity input string from valid entities using Levenshtein distance."""
    return get_close_matches(input_str, valid_entities, n=1, cutoff=0.8)

def get_best_intent_match(input_str):
    valid_intents = list(intents.keys())
    return get_best_match(input_str, valid_intents)

def load_or_initialize_file(file_path):
    """Load the existing dialogues file, or initialize a new one if it doesn't exist or is empty."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)  # Try loading the existing data
            except json.JSONDecodeError:
                print(f"Warning: {file_path} is empty or malformed, initializing a new file.")
                return []  # Return an empty list if the file is empty or malformed
    else:
        print(f"{file_path} not found, initializing a new file.")
        return []  # Initialize a new file if it doesn't exist

def save_to_file(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} dialogues to {file_path}")

def get_next_dialogue_id(dialogues):
    """Get the next dialogue ID."""
    if not dialogues:
        return 1
    return max(dialogue.get("dialogue_id", 0) for dialogue in dialogues) + 1

def add_dialogue(dialogues, file_path):
    print("\nAdd a new dialogue entry. Leave fields blank to skip optional ones.")
    dialogue_id = get_next_dialogue_id(dialogues)
    dialogue_entry = {"dialogue_id": dialogue_id, "turns": []}
    turn_count = -1

    # Multi-turn dialogue input
    while True:
        turn_count += 1
        if turn_count%2 == 0:
            speaker = "User"
        else:
            speaker = "Bot"
        
        text = input(f"Enter text for {speaker}: ").strip()
        if not text:
            print("Text cannot be empty. Try again.")
            continue

        intent = None
        if speaker == "User":
            intent = get_best_intent_match(input("Enter intent (e.g., 'track_order', 'cancel_order') [optional]: ").strip())[0]
        
        if speaker == "Bot":
            turn = {"speaker": speaker, "text": text, "entities": entities}
            turn["speaker"] = speaker
            turn["text"] = text
            dialogue_entry["turns"].append(turn)
            add_another_turn = input("Add another turn to this dialogue? (yes/no): ").strip().lower()
            if add_another_turn in ["no", "n"]:
                break
            continue

        entities = []
        print(f"Adding entities for intent '{intent}'")
        while True:
            add_entity = input("Do you want to add an entity? (yes/no): ").strip().lower()
            if add_entity in ["yes","y"]:
                print("Available entity types:", intents[intent])
                entity_type = get_best_entity_match(input("Enter entity type (e.g., 'order_id', 'reason'): ").strip(), intents[intent])[0]
                entity_value = input(f"Enter value for {entity_type}: ").strip()
                
                # Calculate start and end indices for entity
                try:
                    start_idx = text.index(entity_value)
                    end_idx = start_idx + len(entity_value)
                    entity = {
                        "entity": entity_value,
                        "type": entity_type,
                        "start": start_idx,
                        "end": end_idx
                    }
                    entities.append(entity)
                except ValueError:
                    print(f"Error: The entity value '{entity_value}' is not found in the text. Try again.")
            elif add_entity in ["no","n"]:
                break
            else:
                print("Invalid input. Type 'yes' or 'no'.")
        
        # If no entities were added, append an empty list
        if not entities:
            entities = []

        # Add turn to dialogue
        turn = {"speaker": speaker, "text": text, "entities": entities}
        if speaker == "User" and intent:
            turn["intent"] = intent
        
        dialogue_entry["turns"].append(turn)

        # Ask if user wants to add another turn
        add_another_turn = input("Add another turn to this dialogue? (yes/no): ").strip().lower()
        if add_another_turn in ["no", "n"]:
            break

    dialogues.append(dialogue_entry)
    save_to_file(file_path, dialogues)
    print(f"Dialogue with ID {dialogue_id} added successfully.")
    return dialogues

def main():
    # Set the file path
    file_path = "dialogues.json"

    # Load existing dialogues (or initialize if the file is empty)
    dialogues = load_or_initialize_file(file_path)

    # Ask to add a new dialogue
    while True:
        add_dialogue_choice = input("Do you want to add a new dialogue? (y/n): ").strip().lower()
        if add_dialogue_choice in ["y", "yes"]:
            add_dialogue(dialogues, file_path)
        elif add_dialogue_choice in ["n", "no"]:
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()
