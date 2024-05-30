import os
import requests
import json
import signal
from datetime import datetime


# Set your API key directly for testing purposes
api_key = os.getenv("OPENAI_API_KEY")
# Alternatively, you can uncomment the next line to set the key directly for testing

if api_key is None:
    raise ValueError("API key not found. Make sure to set the OPENAI_API_KEY environment variable.")

# Define the endpoint and headers
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Custom instructions or preferences
custom_prompt = "You are a helpful assistant. Please provice concise and accurate responses."
output_format = "ChatGPT: {response}"

# Function to generate default filename based on date and running number
def generate_default_filename():
    date_str = datetime.now().strftime("%d.%m.%Y")
    num = 0
    while True:
        filename = f"{date_str}_{num}.txt"
        if not os.path.exists(filename):
            return filename
        num += 1

# Function to save chat history to a file in plain text
def save_chat_history(chat_history, filename):
    with open(filename, "w") as file:
        for entry in chat_history:
            timestamp = entry.get("timestamp", "")
            role = "User" if entry["role"] == "user" else "Assistant"
            file.write(f"[{timestamp}] {role}: {entry['content']}\n")

# Function to load chat history from a file
def load_chat_history(filename):
    chat_history = []
    try:
        with open(filename, "r") as file:
            for line in file:
                timestamp, rest = line.split("] ", 1)
                role, content = rest.split(": ", 1)
                timestamp = timestamp.strip("[]")
                role = "user" if role == "User" else "assistant"
                chat_history.append({"timestamp": timestamp, "role": role, "content": content.strip()})
    except FileNotFoundError:
        print(f"No chat history found for {filename}. Starting a new session.")
    return chat_history
            
# Initialize chat history
chat_history = []

# Default session filename
default_filename = generate_default_filename()
current_session = default_filename

# Save chat history on exit
def exit_gracefully(signum, frame):
    if current_session:
        save_chat_history(chat_history, current_session)
    print("\nChat history saved. Exiting...")
    exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

print("ChatGPT Terminal Interface. Type 'exit' to end the chat.")
print("Type 'load history <filename>' to load a previous session.")
print("Type 'save history <filename>' to save the current session to a specific file")


#Continuous chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        if current_session:
            save_chat_history(chat_history, current_session)
        print("Chat history saved. Exiting...")
        break
    elif user_input.startswith("load history "):
        _, filename = user_input.split("load history ", 1)
        chat_history = load_chat_history(filename)
        current_session = filename
        print(f"Loaded chat history from {filename}.")
    elif user_input.startswith("save history "):
        _, filename = user_input.split("save history ", 1)
        save_chat_history(chat_history, filename)
        current_session = filename
        print(f"Chat history saved to {filename}.")
    else:
        #Append the user's message to chat history with timestamp
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        chat_history.append({"timestamp": timestamp, "role": "user", "content": user_input})

    #Define the data payload
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": custom_prompt}] + [{"role": entry["role"], "content": entry["content"]} for entry in chat_history]
    }

    # Make the request
    response = requests.post(url, headers=headers, json=data)

    # Parse the response
    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content']
        print(output_format.format(response=reply))

        #Append the assistant's reply to chat history with timestamp
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        chat_history.append({"timestamp": timestamp, "role": "assistant", "content": reply})

        if current_session:
            save_chat_history(chat_history, current_session)
    else:
        print(f"Error {response.status_code}: {response.text}")
