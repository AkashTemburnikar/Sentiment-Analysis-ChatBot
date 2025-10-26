# 🧠 SentimentChatbot

A lightweight **rule-based chatbot** built using the **Microsoft Bot Framework SDK for Python** and **Azure AI Text Analytics**.  
It runs locally using `aiohttp` and can be tested with the **Bot Framework Emulator**.

---

## 🚀 Features

- 🤖 Responds to greetings (`hi`, `hello`, `hey`, etc.)
- ⏰ Shares current **time** and **date**
- 🗣️ Performs **sentiment analysis** on text using **Azure Cognitive Services**
- ⚙️ Handles malformed or empty messages gracefully
- 🔁 Falls back to **reverse-echo** for unknown inputs
- 🧩 Easily extensible for new commands or integrations

---

## 📂 Project Structure

SentimentChatbot/
├── bots/
│   ├── init.py
│   └── echo_bot.py         # Core bot logic
├── app.py                  # Entry point / aiohttp server
├── config.py               # Environment config (Azure + Bot credentials)
├── requirements.txt        # Dependencies
└── README.md

---

## 🧠 How It Works

### 🗂️ 1. `echo_bot.py` (Main Bot Logic)
Implements the `EchoBot` class (subclass of `ActivityHandler`).

When a user sends a message, the bot:
- Detects keywords like **“help”**, **“time”**, **“date”**, **“bye”**
- Performs **sentiment analysis** if the message starts with `sentiment`
- Replies accordingly:
  - `sentiment I love Python!` → returns *Positive* sentiment with confidence scores  
  - `time` → current system time  
  - `date` → today’s date  
  - anything else → reversed echo response

If the input is invalid (empty, symbols, or URLs), it sends a friendly reminder.

---

### ⚙️ 2. `app.py` (Server Setup)
- Uses **aiohttp** to handle HTTP requests.
- Sets up **CloudAdapter** from `botbuilder`.
- Creates an instance of `EchoBot` and binds it to `/api/messages`.
- Loads environment variables from `config.py` (Bot credentials and Azure endpoint).
- Runs on port **3978** by default.

You can run it directly:
```bash
python app.py


⸻

🧾 3. config.py (Configuration)

Defines the DefaultConfig class, which reads all environment variables:

Variable	Description
MicrosoftAppId	(Optional) Bot Framework App ID
MicrosoftAppPassword	(Optional) App secret
MicrosoftAppType	Type of app (default: MultiTenant)
MicrosoftAppTenantId	Tenant ID (if applicable)
MicrosoftAIServiceEndpoint	Azure Cognitive Services endpoint
MicrosoftAPIKey	Azure Cognitive Services API key
PORT	Defaults to 3978


⸻

🧰 4. Azure Sentiment Integration

In echo_bot.py, the sentiment logic uses:

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

It calls client.analyze_sentiment([text]) and responds with:

Sentiment: Positive (pos=0.95, neu=0.03, neg=0.02)

If credentials are missing, the bot raises a clear runtime error prompting setup.

⸻

🧩 Installation & Setup

1️⃣ Clone or unzip the repo

git clone https://github.com/<your-username>/SentimentChatbot.git
cd SentimentChatbot

2️⃣ Create a virtual environment

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

3️⃣ Install dependencies

pip install -r requirements.txt

requirements.txt

botbuilder-integration-aiohttp>=4.15.0
azure-ai-textanalytics>=5.3.0


⸻

🌐 Environment Variables

You can set these manually or via a .env file:

export MicrosoftAIServiceEndpoint="https://<your-resource>.cognitiveservices.azure.com/"
export MicrosoftAPIKey="<your-azure-api-key>"

# Optional for Bot Framework Emulator
export MicrosoftAppId=""
export MicrosoftAppPassword=""
export MicrosoftAppType="MultiTenant"
export MicrosoftAppTenantId=""


⸻

▶️ Running the Bot

Run the bot locally:

python app.py

By default, it runs on:

http://localhost:3978/api/messages


⸻

💬 Test with Bot Framework Emulator
	1.	Install the Bot Framework Emulator
	2.	Open → “Open Bot”
	3.	Enter endpoint:

http://localhost:3978/api/messages


	4.	Leave AppId and Password blank for local testing
	5.	Try chatting with:

hi
what can you do
time
date
sentiment I love this project!
sentiment this is awful
bye

⸻

🧭 Future Enhancements
	•	Add offline/local sentiment model (e.g., VADER or TextBlob)
	•	Add conversation state & history
	•	Integrate intent recognition (scikit-learn / spaCy)
	•	Deploy via Docker + Azure Web App

⸻

🧾 License

MIT License © 2025 Akash Temburnikar
This project is for educational use.
✅ and a `run.sh` (auto-activate venv + run bot)?  

That would make your repo “run-ready” for classmates or teammates.
