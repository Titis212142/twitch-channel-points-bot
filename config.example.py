# -*- coding: utf-8 -*-
# Fichier d'exemple - Copiez ce fichier en config.py et remplissez vos identifiants
# ⚠️ config.py est dans .gitignore et ne sera PAS committé sur GitHub

# Identifiants Twitch
TWITCH_USERNAME = "votre_nom_utilisateur_twitch"
TWITCH_PASSWORD = "votre_mot_de_passe"  # Ou laissez "" pour saisie interactive

# Optionnel : Notifications
# Telegram
# Pour obtenir votre Chat ID :
#   1. Cherchez @userinfobot ou @getidsbot sur Telegram
#   2. Cliquez sur "Start" - le bot vous donnera votre Chat ID (un nombre)
#   3. Ou visitez : https://api.telegram.org/botVOTRE_TOKEN/getUpdates
TELEGRAM_CHAT_ID = None  # Votre Chat ID (nombre entier, ex: 123456789)
TELEGRAM_TOKEN = None     # Token du bot Telegram (obtenu avec @BotFather)

# Discord
DISCORD_WEBHOOK_URL = None  # URL du webhook Discord

# Autres services (optionnel)
WEBHOOK_ENDPOINT = None
MATRIX_USERNAME = None
MATRIX_PASSWORD = None
MATRIX_HOMESERVER = None
MATRIX_ROOM_ID = None
PUSHOVER_USERKEY = None
PUSHOVER_TOKEN = None
GOTIFY_ENDPOINT = None
