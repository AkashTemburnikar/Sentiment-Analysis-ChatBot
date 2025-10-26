# SentimentChatbot

A lightweight, rule-based chatbot built using the **Microsoft Bot Framework SDK for Python** and **Azure AI Text Analytics**.  
It runs locally using `aiohttp` and can be tested with the **Bot Framework Emulator**.

---

## Features

- Responds to greetings (`hi`, `hello`, `hey`, etc.)
- Shares the current **time** and **date**
- Performs **sentiment analysis** using Azure Cognitive Services
- Handles malformed or empty messages gracefully
- Falls back to **reverse-echo** for unknown inputs
- Easily extensible for new commands or integrations

---

## Development Environment

This project was developed and tested on macOS.

**System & Tools Used**
- **Device:** MacBook (Apple Silicon)
- **OS:** macOS
- **Python Version:** 3.10 or later
- **IDE:** Visual Studio Code
- **Tools Required:**
  - [Python](https://www.python.org/downloads/)
  - [pip](https://pip.pypa.io/en/stable/)
  - [VS Code](https://code.visualstudio.com/)
  - [Git](https://git-scm.com/) (optional, for cloning the repo)
  - [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator)
  - Azure Cognitive Services account (for sentiment API)

---

## Project Structure

SentimentChatbot/
├── bots/
│   ├── init.py
│   └── echo_bot.py         # Core bot logic
├── app.py                  # Entry point / aiohttp web server
├── config.py               # Environment variables and configuration
├── requirements.txt        # Dependencies
└── README.md

---

## How It Works

### 1. `echo_bot.py` (Main Bot Logic)

Implements the `EchoBot` class which processes every message received from the user.

- Recognizes simple keywords such as `help`, `time`, `date`, `bye`
- Performs sentiment analysis if a message starts with the word `sentiment`
- Handles malformed or empty messages
- Responds with a reversed message if no rules match

Example:

User: sentiment I love Python
Bot: Sentiment: Positive (pos=0.92, neu=0.05, neg=0.03)

---

### 2. `app.py` (Server Setup)

- Uses `aiohttp` to host a web server at `/api/messages`
- Initializes the **CloudAdapter** from the Bot Framework
- Connects the bot logic to the HTTP endpoint
- Loads configuration from environment variables (via `config.py`)
- Runs locally on port **3978**

Run the bot:
```bash
python app.py


⸻

3. config.py (Configuration)

Defines the DefaultConfig class, which reads environment variables:

Variable	Description
MicrosoftAppId	(Optional) Bot Framework App ID
MicrosoftAppPassword	(Optional) Bot secret
MicrosoftAppType	App type (default: MultiTenant)
MicrosoftAppTenantId	Tenant ID (if applicable)
MicrosoftAIServiceEndpoint	Azure Cognitive Services endpoint
MicrosoftAPIKey	Azure API key for sentiment analysis
PORT	Defaults to 3978


⸻

4. Azure Sentiment Integration

Uses the Azure Text Analytics client:

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

The bot calls:

client.analyze_sentiment([text])

and returns sentiment results in this format:

Sentiment: Positive (pos=0.95, neu=0.03, neg=0.02)

If credentials are missing, it will raise a clear runtime error prompting setup.

⸻

Setup and Installation (macOS)

Step 1. Clone or unzip the repository

git clone https://github.com/<your-username>/SentimentChatbot.git
cd SentimentChatbot

Step 2. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate

Step 3. Install dependencies

pip install -r requirements.txt

requirements.txt

botbuilder-integration-aiohttp>=4.15.0
azure-ai-textanalytics>=5.3.0

Step 4. Set environment variables

Create a .env file or export them manually:

export MicrosoftAIServiceEndpoint="https://<your-resource>.cognitiveservices.azure.com/"
export MicrosoftAPIKey="<your-azure-api-key>"

# Optional (for Emulator authentication)
export MicrosoftAppId=""
export MicrosoftAppPassword=""
export MicrosoftAppType="MultiTenant"
export MicrosoftAppTenantId=""


⸻

Running the Bot

python app.py

It runs at:

http://localhost:3978/api/messages


⸻

Testing with Bot Framework Emulator
	1.	Install and open Bot Framework Emulator
	2.	Click Open Bot
	3.	Enter endpoint:

http://localhost:3978/api/messages


	4.	Leave App ID and Password empty (for local testing)
	5.	Try chatting with:

hi
time
date
sentiment I love this project!
sentiment this is awful
bye

⸻

Future Enhancements
	•	Add offline/local sentiment model (e.g., VADER or TextBlob)
	•	Add conversation state and history
	•	Integrate intent classification (scikit-learn or spaCy)
	•	Deploy using Docker or Azure Web App

⸻

License

MIT License © 2025 Akash Temburnikar
This project is for educational purposes.
