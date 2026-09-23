import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API key not found. Add API_KEY to the .env file.")

# Define the date for which you want to check usage
# You can change this to any date you want to check
date = datetime.now().strftime('%Y-%m-%d')

# Define the endpoint and headers
url = f"https://api.openai.com/v1/usage?date={date}"
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Make the request
response = requests.get(url, headers=headers)

# Parse and print the response
if response.status_code == 200:
    usage_info = response.json()
    records = usage_info.get("data", [])

    if not records:
        print(f"No usage recorded for {date}.")
    else:
        totals = {}
        for record in records:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    totals[key] = totals.get(key, 0) + value

        print(f"Usage for {date}:")
        for key, value in sorted(totals.items()):
            print(f"  {key}: {value}")

    print("Remaining quota is not provided by this API endpoint.")
    print("Check the OpenAI Platform billing/limits page for your limit and balance.")
else:
    print(f"Error {response.status_code}: {response.text}")
