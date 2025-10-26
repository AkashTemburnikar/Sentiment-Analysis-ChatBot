SentimentChatbot

A lightweight, rule-based chatbot built using the Microsoft Bot Framework SDK for Python and Azure AI Text Analytics.
It runs locally using aiohttp and can be tested with the Bot Framework Emulator.

⸻

Features
	•	Responds to greetings (hi, hello, hey, etc.)
	•	Shares the current time and date
	•	Performs sentiment analysis using Azure Cognitive Services
	•	Handles malformed or empty messages gracefully
	•	Falls back to reverse-echo for unknown inputs
	•	Easily extensible for new commands or integrations

⸻

Development Environment

This project was developed and tested on macOS.

System and Tools Used
	•	Device: MacBook (Apple Silicon)
	•	OS: macOS
	•	Python Version: 3.10 or later
	•	IDE: Visual Studio Code
	•	Tools Required:
	•	Python
	•	pip
	•	VS Code
	•	Git (optional)
	•	Bot Framework Emulator
	•	Azure Cognitive Services account (for sentiment API)

⸻

Project Structure

SentimentChatbot/
├── bots/
│   ├── __init__.py
│   └── echo_bot.py         # Core bot logic
├── app.py                  # Entry point / aiohttp web server
├── config.py               # Environment variables and configuration
├── requirements.txt        # Dependencies
└── README.md


⸻

How It Works

1. echo_bot.py (Main Bot Logic)

Implements the EchoBot class, which processes every message received from the user.
	•	Detects commands such as help, time, date, bye
	•	Runs sentiment analysis when input starts with sentiment
	•	Replies with reversed text for unknown inputs
	•	Handles malformed or empty messages

Example

User: sentiment I love Python
Bot: Sentiment: Positive (pos=0.92, neu=0.05, neg=0.03)


⸻

2. app.py (Server Setup)
	•	Uses aiohttp to host a web server at /api/messages
	•	Initializes a CloudAdapter for the Bot Framework
	•	Loads configuration from environment variables via config.py
	•	Runs locally on port 3978

Run the bot:

python app.py


⸻

3. config.py (Configuration)

Defines the DefaultConfig class, which reads environment variables.

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

The bot uses Azure’s Text Analytics client:

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

It calls:

client.analyze_sentiment([text])

Example response:

Sentiment: Positive (pos=0.95, neu=0.03, neg=0.02)

If credentials are missing, it raises a clear runtime error.

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

# Optional (for Bot Framework Emulator authentication)
export MicrosoftAppId=""
export MicrosoftAppPassword=""
export MicrosoftAppType="MultiTenant"
export MicrosoftAppTenantId=""


⸻

Running the Bot

Start the bot:

python app.py

The bot will run locally at:

http://localhost:3978/api/messages


⸻

Testing with Bot Framework Emulator
	1.	Install and open Bot Framework Emulator
	2.	Click Open Bot
	3.	Enter the endpoint:

http://localhost:3978/api/messages


	4.	Leave App ID and Password empty (for local testing)
	5.	Try chatting with:

hi
what can you do
time
date
sentiment I love this project!
sentiment this is awful
bye

⸻

Future Enhancements
	•	Add offline/local sentiment model (VADER or TextBlob)
	•	Add conversation history or user context
	•	Integrate intent classification (scikit-learn or spaCy)
	•	Deploy using Docker or Azure Web App

⸻

License

MIT License © 2025 Akash Temburnikar
This project is for educational use.
