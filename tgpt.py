import os
import requests
import json
import signal
import readline
from datetime import datetime


# Get OpenAI Api key
api_key = os.getenv("OPENAI_API_KEY")

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

# Function to truncate chat history
def truncate_chat_history(chat_history, limit=8):
    return chat_history[-limit:]

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
print("Type 'load current history full' or 'lchf' to load the full history of the current session.")
print("Type 'load current history truncated' or 'lcht' to load a truncated version of the current session.")
print("Type 'load history full <filename>' or 'lhf <filename>' to load the full history from another session.")
print("Type 'load history truncated <filename> or 'lht <filename>' to load a truncated version from another session.")
print("Type 'save history <filename>' or 'sh <filename>' to save history of the current session to a specific file")

#Continuous chat loop
while True:
    user_input = input("You: ")
    #Save if user exits
    if user_input.lower() == "exit":
        if current_session:
            save_chat_history(chat_history, current_session)
        print("Chat history saved. Exiting...")
        break

    #Load current session history in full as a part of the query
    elif user_input.lower().startswith("load current history full") or user_input.lower().startswith("lchf"):
        current_messages = [{"role": entry["role"], "content": entry["content"]} for entry in chat_history]
        print("Loaded full history of ")
        user_input = user_input[len("load current history full "):] if user_input.lower().startswith("load current history full") else user_input[len("lchf "):]

    #Load truncated version of current history
    elif user_input.lower().startswith("load current history truncated") or user_input.lower().startswith("lcht"):
        truncated_history = truncate_chat_history(chat_history)
        current_messages = [{"role": entry["role"], "content": entry["content"]} for entry in truncated_history]
        print(f"Loaded truncated history of the current session (last {len(truncated_history)} messages).")
        user_input = user_input[len("load current history truncated "):] if user_input.lower().startswith("load current history truncated") else user_input[len("lcht "):]

    #Load full version of a history with filename
    elif user_input.lower().startswith("load history full") or user_input.lower().startswith("lhf"):
        filename = user_input.split("load history full ", 1)[1].strip() if user_input.lower().startswith("load history full") else user_input.split("lhf ", 1)[1].strip()
        chat_history = load_chat_history(filename)
        current_session = filename
        current_messages = [{"role": entry["role"], "content": entry["content"]} for entry in chat_history]
        print(f"Loaded full history from {filename}")
        user_input = user_input[len(f"load history full {filename} "):] if user_input.lower().startswith("load history full") else user_input[len(f"lhf {filename} "):]   

    #Load truncated version of a history with filename
    elif user_input.lower().startswith("load history truncated") or user_input.lower().startswith("lht"):
        filename = user_input.split("load history truncated ", 1)[1].strip() if user_input.lower().startswith("load history truncated") else user_input.split("lht ", 1)[1].strip()
        chat_history = load_chat_history(filename)
        current_session = filename
        truncated_history = truncate_chat_history(chat_history)
        current_messages = [{"role": entry["role"], "content": entry["content"]} for entry in truncated_history]
        print(f"Loaded truncated history from {filename} (last {len(truncated_history)} messages).")
        user_input = user_input[len(f"load history truncated {filename} "):] if user_input.lower().startswith("load history truncated") else user_input[len(f"lht {filename} "):]

    #Save current conversation with specified filename
    elif user_input.lower().startswith("save history ") or user_input.lower().startswith("sh "):
        filename = user_input.split("save history ", 1)[1].strip() if user_input.lower().startswith("save history ") else user_input.split("sh ", 1)[1].strip()
        save_chat_history(chat_history, filename)
        current_session = filename
        print(f"Chat history saved to {filename}.")

    #Append the user's message to chat history with timestamp
    else:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        chat_history.append({"timestamp": timestamp, "role": "user", "content": user_input})

        #Define the data payload, by default without history
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": custom_prompt}, {"role": "user", "content": user_input}]
        }
        
        # If current_messages is defined include it in the payload
        if 'current_messages' in locals():
            data["messages"] = [{"role": "system", "content": custom_prompt}] + current_messages

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
