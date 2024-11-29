import json

def load_or_initialize_file(file_path):
    try:
        with open(file_path, "r") as file:
            dialogues = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        dialogues = []
    return dialogues


def fix_dialogue_ids(dialogues):
    for i, dialogue in enumerate(dialogues):
        dialogue["dialogue_id"] = i + 1
    return dialogues

def entity_start_end(dialogues):
    for dialogue in dialogues:
        for turn in dialogue["turns"]:
            if turn["speaker"] == "Bot":
                # remove everything except text and speaker
                turn = {"text": turn["text"], "speaker": turn["speaker"]}
                continue
            if "entities" not in turn:
                continue
            print(turn)
            for entity in turn["entities"]:
                entity["start"] = turn["text"].index(entity["entity"])
                entity["end"] = entity["start"] + len(entity["entity"])
    return dialogues


def save_to_file(file_path, dialogues):
    with open(file_path, "w") as file:
        json.dump(dialogues, file, indent=2)


def main():
    file_path = "dialogues.json"
    new_file_path = "dialogues_fixed.json"
    dialogues = load_or_initialize_file(file_path)
    dialogues = fix_dialogue_ids(dialogues)
    dialogues = entity_start_end(dialogues)
    save_to_file(new_file_path, dialogues)
    print(f"Fixed {len(dialogues)} dialogues in {file_path}")

if __name__ == "__main__":
    main()