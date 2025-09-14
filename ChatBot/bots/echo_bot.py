# Copyright (c) Microsoft.
# Licensed under the MIT License.

from datetime import datetime
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory

class EchoBot(ActivityHandler):
    """
    Traditional (non-LLM) rule-based bot that:
      • Responds to multiple prompts (greet, help, time, date, goodbye)
      • Provides a list of capabilities (help)
      • Handles malformed/unknown input (fallback)
      • Implements the reverse-echo tweak from the assignment example
    """

    async def on_message_activity(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip()
        low = text.lower()

        # 1) Multiple prompts / simple intents
        if any(g in low for g in ("hi", "hello", "hey", "good morning", "good afternoon", "good evening")):
            await turn_context.send_activity("Hello! How can I help you today?")
            return

        if "help" in low or "what can you do" in low or "capabilities" in low or "commands" in low:
            capabilities = (
                "Here’s what I can do:\n"
                "• Greet you (try: hello)\n"
                "• Tell you the time (try: time)\n"
                "• Tell you the date (try: date)\n"
                "• Say goodbye (try: bye)\n"
                "• Reverse any other message you type"
            )
            await turn_context.send_activity(capabilities)
            return

        if "time" in low:
            now = datetime.now().strftime("%H:%M:%S")
            await turn_context.send_activity(f"The current time is {now}.")
            return

        if "date" in low:
            today = datetime.now().strftime("%Y-%m-%d")
            await turn_context.send_activity(f"Today's date is {today}.")
            return

        if any(k in low for k in ("bye", "goodbye", "see you")):
            await turn_context.send_activity("Goodbye! 👋")
            return

        # 2) Handle malformed/empty input
        if not text:
            await turn_context.send_activity("I didn't receive any text. Try typing 'help' to see what I can do.")
            return

        # 3) Assignment tweak: reverse-echo fallback
        await turn_context.send_activity(MessageFactory.text(text[::-1]))