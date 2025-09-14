#!/usr/bin/env python3
import os

class DefaultConfig:
    """Bot Configuration"""
    PORT = 3978

    # Bot Framework local dev creds (keep empty for Emulator)
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")

    # --- Azure AI Language (Sentiment) ---
    # Set these in your shell before running the bot.
    ENDPOINT_URI = os.environ.get("MicrosoftAIServiceEndpoint", "https://languageservice0101.cognitiveservices.azure.com/")
    API_KEY = os.environ.get("MicrosoftAPIKey", "")