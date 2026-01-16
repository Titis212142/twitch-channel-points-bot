#!/bin/bash
# Docker entrypoint script to create config.py from environment variables if needed

# Check if required environment variables are set
if [ -z "$TWITCH_USERNAME" ]; then
    echo "❌ ERROR: TWITCH_USERNAME environment variable is not set!"
    echo "📝 Please set the following environment variables:"
    echo "   - TWITCH_USERNAME (required)"
    echo "   - TWITCH_PASSWORD (optional, will be asked interactively if not set)"
    echo ""
    echo "Example:"
    echo "   docker run -e TWITCH_USERNAME=your_username ..."
    exit 1
fi

# Create config.py from environment variables if it doesn't exist
if [ ! -f /usr/src/app/config.py ]; then
    echo "Creating config.py from environment variables..."
    python3 << 'PYTHON_SCRIPT'
import os

config_content = """# -*- coding: utf-8 -*-
# Auto-generated from environment variables

TWITCH_USERNAME = "{username}"
TWITCH_PASSWORD = "{password}"
TELEGRAM_CHAT_ID = {telegram_chat_id}
TELEGRAM_TOKEN = {telegram_token}
DISCORD_WEBHOOK_URL = {discord_webhook}
WEBHOOK_ENDPOINT = {webhook_endpoint}
MATRIX_USERNAME = {matrix_username}
MATRIX_PASSWORD = {matrix_password}
MATRIX_HOMESERVER = {matrix_homeserver}
MATRIX_ROOM_ID = {matrix_room_id}
PUSHOVER_USERKEY = {pushover_userkey}
PUSHOVER_TOKEN = {pushover_token}
GOTIFY_ENDPOINT = {gotify_endpoint}
"""

def format_value(value):
    if value is None or value == "":
        return "None"
    return f'"{value}"'

username = os.getenv('TWITCH_USERNAME', '')
password = os.getenv('TWITCH_PASSWORD', '')

with open('/usr/src/app/config.py', 'w') as f:
    f.write(config_content.format(
        username=username,
        password=password,
        telegram_chat_id=format_value(os.getenv('TELEGRAM_CHAT_ID')),
        telegram_token=format_value(os.getenv('TELEGRAM_TOKEN')),
        discord_webhook=format_value(os.getenv('DISCORD_WEBHOOK_URL')),
        webhook_endpoint=format_value(os.getenv('WEBHOOK_ENDPOINT')),
        matrix_username=format_value(os.getenv('MATRIX_USERNAME')),
        matrix_password=format_value(os.getenv('MATRIX_PASSWORD')),
        matrix_homeserver=format_value(os.getenv('MATRIX_HOMESERVER')),
        matrix_room_id=format_value(os.getenv('MATRIX_ROOM_ID')),
        pushover_userkey=format_value(os.getenv('PUSHOVER_USERKEY')),
        pushover_token=format_value(os.getenv('PUSHOVER_TOKEN')),
        gotify_endpoint=format_value(os.getenv('GOTIFY_ENDPOINT'))
    ))

print(f"✅ config.py created with username: {username}")
if not password:
    print("⚠️  WARNING: TWITCH_PASSWORD not set, will be asked interactively")
PYTHON_SCRIPT
    echo "config.py created from environment variables"
fi

# Execute the main script
exec python run.py
