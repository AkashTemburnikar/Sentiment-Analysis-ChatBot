#!/usr/bin/env python3
# Copyright (c) Microsoft.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity, ActivityTypes

# Azure Text Analytics client
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from bots import EchoBot
from config import DefaultConfig

CONFIG = DefaultConfig()

# Adapter
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Error handler (will surface errors to Emulator if thrown in the bot)
async def on_error(context: TurnContext, error: Exception):
    print(f"\n[on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error and cannot continue this turn.")
    if context.activity.channel_id == "emulator":
        await context.send_activity(Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=str(error),
            value_type="https://www.botframework.com/schemas/error",
        ))

ADAPTER.on_turn_error = on_error

# Build Azure client if env vars exist (bot can still start without it;
# trying to use sentiment without a client will raise a RuntimeError in the bot)
ta_client = None
if CONFIG.ENDPOINT_URI and CONFIG.API_KEY:
    ta_client = TextAnalyticsClient(
        endpoint=CONFIG.ENDPOINT_URI,
        credential=AzureKeyCredential(CONFIG.API_KEY),
    )

# Bot instance
BOT = EchoBot(text_analytics_client=ta_client)

# HTTP endpoint for Bot Framework activities
async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, BOT)

APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(APP, host="localhost", port=CONFIG.PORT)