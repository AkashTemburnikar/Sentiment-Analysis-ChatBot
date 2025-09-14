# bots/echo_bot.py
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from botbuilder.core import ActivityHandler, TurnContext

# Simple URL detector for "malformed" handling
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


class EchoBot(ActivityHandler):
    """
    Rule-based bot with explicit Azure Sentiment command.

    Commands / behaviors:
      - 'sentiment <text>' -> analyze sentiment via Azure Text Analytics (hard error if not configured)
      - 'help' / 'capabilities' / 'commands' -> list abilities
      - 'time' -> current time
      - 'date' -> today's date
      - 'bye' / 'goodbye' -> farewell
      - greetings ('hi', 'hello', 'hey', etc.) -> friendly greeting
      - malformed (empty, symbols only, or just a link) -> guidance
      - anything else -> reverse-echo fallback
    """

    def __init__(self, text_analytics_client: Optional[object] = None):
        super().__init__()
        # text_analytics_client should be an instance of azure.ai.textanalytics.TextAnalyticsClient
        # (app.py constructs it and passes it in). It may be None if not configured.
        self.ta_client = text_analytics_client

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        # Welcome message when conversation starts in the Emulator
        for m in members_added:
            if m.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello! I’m a simple rule-based bot. Type 'help' to see what I can do."
                )

    async def on_message_activity(self, turn_context: TurnContext):
        # Raw and normalized text
        text_raw = turn_context.activity.text or ""
        text = text_raw.strip()
        low = text.lower()

        # === Attachment / empty handling ===
        if not text and turn_context.activity.attachments:
            await turn_context.send_activity(
                "I received your attachment(s). I mainly handle text — type 'help' for commands."
            )
            return
        if not text:
            await turn_context.send_activity(
                "I didn’t receive any text. Try typing 'help' to see what I can do."
            )
            return

        # === Explicit sentiment command should be handled FIRST ===
        # Accept 'sentiment' alone (asks for more) or 'sentiment <text>'
        if low == "sentiment" or low.startswith("sentiment "):
            target = text[len("sentiment"):].strip()
            if not target:
                await turn_context.send_activity(
                    "Please provide text after 'sentiment'. Example: sentiment I love this class"
                )
                return

            # This will raise RuntimeError if the client isn't configured or the call fails.
            line = await self._sentiment_line(target)
            await turn_context.send_activity(line)
            return

        # === Help / capabilities ===
        if "help" in low or "capabilities" in low or "what can you do" in low or "commands" in low:
            await turn_context.send_activity(
                "Here’s what I can do: greet you; list my capabilities; tell the time and date; "
                "say goodbye; handle malformed input; reverse any other message; and analyze "
                "sentiment via Azure AI when you type 'sentiment <your message>'."
            )
            return

        # === Time / Date ===
        if "time" in low:
            await turn_context.send_activity(f"The current time is {datetime.now().strftime('%H:%M:%S')}.")
            return
        if "date" in low:
            await turn_context.send_activity(f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.")
            return

        # === Farewell ===
        if any(k in low for k in ("bye", "goodbye", "see you")):
            await turn_context.send_activity("Goodbye! 👋")
            return

        # === Greetings ===
        if any(g in low for g in ("hi", "hello", "hey", "good morning", "good afternoon", "good evening")):
            await turn_context.send_activity("Hello! How can I help you today?")
            return

        # === Malformed heuristics ===
        if len(text) < 2 or all(not ch.isalnum() for ch in text):
            await turn_context.send_activity(
                "That doesn’t look like a valid message. Try words like hello, time, or date. Type 'help' for more."
            )
            return
        if URL_RE.search(text):
            await turn_context.send_activity(
                "Looks like you sent a link. I don’t browse the web, but we can still chat. Type 'help' for commands."
            )
            return

        # === Fallback: reverse echo ===
        # (We keep fallback simple. Sentiment runs only on explicit 'sentiment ...' per your request.)
        await turn_context.send_activity(text[::-1])

    async def _sentiment_line(self, content: str) -> str:
        """
        Build a one-line sentiment summary from Azure Text Analytics.
        Raises RuntimeError if the client isn't configured or the Azure call fails.
        The adapter's on_error in app.py will surface the error in the Emulator.
        """
        if not self.ta_client:
            raise RuntimeError(
                "Azure Text Analytics client is not configured. "
                "Set MicrosoftAIServiceEndpoint and MicrosoftAPIKey."
            )

        try:
            result = self.ta_client.analyze_sentiment([content], show_opinion_mining=False)
            doc = result[0]
            label = doc.sentiment.capitalize()
            pos = doc.confidence_scores.positive
            neu = doc.confidence_scores.neutral
            neg = doc.confidence_scores.negative
            return f"Sentiment: {label} (pos={pos:.2f}, neu={neu:.2f}, neg={neg:.2f})"
        except Exception as ex:
            # Hard error so you immediately know sentiment didn't run
            raise RuntimeError(f"Sentiment analysis failed: {ex}")