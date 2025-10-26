SentimentChatbot

A lightweight rule-based chatbot built using the Microsoft Bot Framework SDK for Python and Azure AI Text Analytics.
It runs locally using aiohttp and can be tested with the Bot Framework Emulator.

⸻

1. Features
	•	Responds to greetings (hi, hello, hey, etc.)
	•	Shares the current time and date
	•	Performs sentiment analysis using Azure Cognitive Services
	•	Handles malformed or empty messages gracefully
	•	Falls back to reverse-echo for unknown inputs
	•	Easily extensible for new commands or integrations

⸻

2. Development Environment

This project was developed and tested on macOS using the following setup:
	•	Device: MacBook (Apple Silicon)
	•	Operating System: macOS
	•	Python Version: 3.10 or later
	•	IDE: Visual Studio Code

Tools Required:
	•	Python
	•	pip
	•	Visual Studio Code
	•	Git (optional, for cloning)
	•	Bot Framework Emulator
	•	Azure Cognitive Services (for sentiment analysis)

💡 You can still run the bot without Azure credentials — it will handle non-sentiment commands normally and display an error for missing credentials when sentiment is used.

⸻

3. Project Structure

SentimentChatbot/
├── bots/
│   ├── __init__.py
│   └── echo_bot.py         # Core bot logic
├── app.py                  # Entry point / aiohttp web server
├── config.py               # Configuration & environment variables
├── requirements.txt        # Python dependencies
└── README.md


⸻

4. How It Works

4.1 echo_bot.py — Main Bot Logic

Implements the EchoBot class, which handles user messages.

Logic Overview:
	•	Detects commands such as help, time, date, and bye
	•	Runs sentiment analysis when a message begins with the word sentiment
	•	Returns reversed text for unknown or unrecognized messages
	•	Handles malformed or empty input gracefully

Example Conversation:

User: sentiment I love Python
Bot: Sentiment: Positive (pos=0.92, neu=0.05, neg=0.03)


⸻

4.2 app.py — Web Server Setup
	•	Uses aiohttp to host an API endpoint at /api/messages
	•	Initializes CloudAdapter from the Bot Framework
	•	Loads configuration values from config.py
	•	Runs on port 3978 by default

Run the bot manually:

python app.py


⸻

4.3 config.py — Configuration Settings

Defines the DefaultConfig class, which reads the following environment variables:

Variable	Description
MicrosoftAppId	(Optional) Bot Framework App ID
MicrosoftAppPassword	(Optional) Bot secret
MicrosoftAppType	App type (default: MultiTenant)
MicrosoftAppTenantId	Tenant ID (if applicable)
MicrosoftAIServiceEndpoint	Azure Cognitive Services endpoint
MicrosoftAPIKey	Azure API key for sentiment analysis
PORT	Defaults to 3978


⸻

4.4 Azure Sentiment Integration

The bot uses Azure’s Text Analytics client to analyze message sentiment.

Imports:

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

Sentiment Call:

client.analyze_sentiment([text])

Sample Response:

Sentiment: Positive (pos=0.95, neu=0.03, neg=0.02)

If the credentials are missing, the bot raises a clear runtime error so the issue is visible during local testing.

⸻

5. Setup and Installation (macOS)

Step 1. Clone or unzip the repository

git clone https://github.com/<your-username>/SentimentChatbot.git
cd SentimentChatbot

Step 2. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate

Step 3. Install dependencies

pip install -r requirements.txt

Dependencies (requirements.txt):

botbuilder-integration-aiohttp>=4.15.0
azure-ai-textanalytics>=5.3.0

Step 4. Set environment variables

Create a .env file or export manually in the terminal:

export MicrosoftAIServiceEndpoint="https://<your-resource>.cognitiveservices.azure.com/"
export MicrosoftAPIKey="<your-azure-api-key>"

# Optional (for Emulator authentication)
export MicrosoftAppId=""
export MicrosoftAppPassword=""
export MicrosoftAppType="MultiTenant"
export MicrosoftAppTenantId=""


⸻

6. Running the Bot

Start the bot:

python app.py

Bot URL:

http://localhost:3978/api/messages


⸻

7. Testing with Bot Framework Emulator

Follow these steps to chat with your bot locally:
	1.	Install and open Bot Framework Emulator
	2.	Click Open Bot
	3.	Enter the endpoint:

http://localhost:3978/api/messages


	4.	Leave App ID and Password fields empty for local testing
	5.	Send messages like:

hi
what can you do
time
date
sentiment I love this project!
sentiment this is awful
bye

⸻

9. Future Enhancements
	•	Add local sentiment model (e.g., VADER or TextBlob)
	•	Implement conversation history or context awareness
	•	Integrate machine learning intent classification (e.g., spaCy, scikit-learn)
	•	Containerize and deploy using Docker or Azure Web App

⸻

10. License

MIT License © 2025 Akash Temburnikar
This project is intended for educational use and demonstration purposes.
