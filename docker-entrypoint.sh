#!/bin/bash
# Docker entrypoint script to create config.py from environment variables if needed

# Create config.py from environment variables if it doesn't exist
if [ ! -f /usr/src/app/config.py ]; then
    echo "Creating config.py from environment variables..."
    cat > /usr/src/app/config.py << EOF
# -*- coding: utf-8 -*-
# Auto-generated from environment variables

TWITCH_USERNAME = "${TWITCH_USERNAME:-}"
TWITCH_PASSWORD = "${TWITCH_PASSWORD:-}"
TELEGRAM_CHAT_ID = ${TELEGRAM_CHAT_ID:-None}
TELEGRAM_TOKEN = ${TELEGRAM_TOKEN:-None}
DISCORD_WEBHOOK_URL = ${DISCORD_WEBHOOK_URL:-None}
WEBHOOK_ENDPOINT = ${WEBHOOK_ENDPOINT:-None}
MATRIX_USERNAME = ${MATRIX_USERNAME:-None}
MATRIX_PASSWORD = ${MATRIX_PASSWORD:-None}
MATRIX_HOMESERVER = ${MATRIX_HOMESERVER:-None}
MATRIX_ROOM_ID = ${MATRIX_ROOM_ID:-None}
PUSHOVER_USERKEY = ${PUSHOVER_USERKEY:-None}
PUSHOVER_TOKEN = ${PUSHOVER_TOKEN:-None}
GOTIFY_ENDPOINT = ${GOTIFY_ENDPOINT:-None}
EOF
    echo "config.py created from environment variables"
fi

# Execute the main script
exec python run.py
