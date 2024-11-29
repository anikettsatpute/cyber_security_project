import pandas as pd
import numpy as np
import os

# Load the data
data = pd.read_csv('./data/bert_input.csv')

# Get the BERT tokenizer
from transformers import BertTokenizerFast

tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
special_tokens = ["[INT]", "[BOT]", "[USR]"]
tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

# NER labels
keys = ['O',
        'B-ORD',
        'I-ORD', 
        'B-COUNT',
        'I-COUNT',
        'B-END_DATE',
        'I-END_DATE',
        'B-START_DATE',
        'I-START_DATE',
        ]

# Create an empty DataFrame to store NER data
ner_data = pd.read_csv('./data/ner_data.csv')

# Iterate over each row in the dataset
iter = input("Enter the row number to start from: ")
for i in range(data.shape[0]):
    if i < int(iter):
        continue
    row = data.iloc[i]
    text = row['instruction']
    tokenized_inputs = tokenizer(text, truncation=True, is_split_into_words=False)
    tokens = tokenizer.convert_ids_to_tokens(tokenized_inputs["input_ids"])
    word_ids = tokenized_inputs.word_ids()
    previous_word_idx = None
    label_ids = []
    
    # Print each token
    for j, word_id in enumerate(word_ids):
        # print all tokens and subwords
        print(f"{j}: {tokens[j]} word_id: {word_id}")
    
    # Initialize the labels as 'O' for all tokens
    num_words = len(set(word_ids))
    if None in set(word_ids):
        num_words -= 1
    labels = ['O'] * num_words
    print(f"number of labels: {len(labels)}")
    print("\n\n")
    # Take input for non-O labels (e.g., position label position label)
    non_o_labels = input()
    non_o_labels = non_o_labels.split()
    
    # Update the labels based on user input
    prev = '0'
    for j in range(0, len(non_o_labels), 2):
        position = int(non_o_labels[j])
        label = non_o_labels[j + 1].upper()  # Ensure the label is in uppercase
        if prev == '0' or prev != label:
            label = 'B-' + label
        else:
            label = 'I-' + label
        prev = label[2:]
        labels[position] = label
    
    # Create a new row with the instruction and the updated labels
    new_row = pd.DataFrame({'instruction': [text], 'labels': [labels]})
    
    # Use pd.concat to add the new row to the DataFrame
    ner_data = pd.concat([ner_data, new_row], ignore_index=True)
    
    # Optionally, you can print the labels for debugging
    print(labels)
    
    # Save the updated NER data to a CSV file after each row
    ner_data.to_csv('./data/ner_data.csv', index=False)

