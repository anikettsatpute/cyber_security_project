import os
import shutil

intent_model_file = "intent_model.zip"
intent_model_folder = "./backend/chatbot/intent_model"
entity_model_file = "ner_model.zip"
entity_model_folder = "./backend/chatbot/ner_model"

# extract and push the folder to ./chatbot
def load_models():
    # extract intent model
    shutil.unpack_archive(intent_model_file, "./chatbot")
    # extract entity model
    shutil.unpack_archive(entity_model_file, "./chatbot")
    # remove the zip files
    os.remove(intent_model_file)
    os.remove(entity_model_file)

def store_models():
    # zip intent model
    shutil.make_archive(intent_model_file.split(".")[0], 'zip', intent_model_folder)
    # zip entity model
    shutil.make_archive(entity_model_file.split(".")[0], 'zip', entity_model_folder)
    

if __name__ == "__main__":
    # take input from user
    user_input = input("Enter 'load' to load models or 'store' to store models: ")
    if user_input == "load":
        load_models()
    elif user_input == "store":
        store_models()
    else:
        print("Invalid input. Please enter 'load' or 'store'")