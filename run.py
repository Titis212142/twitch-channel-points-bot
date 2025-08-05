# -*- coding: utf-8 -*-
import logging
import os
import threading
import sys
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Settings import Priority, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import (
    Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
)
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

# --- Identifiants (en clair) ---
USERNAME = "mat_1234555666666"
# ⚠️ REMPLIS TON MOT DE PASSE ICI (ex: PASSWORD = "MonSuperMotDePasse123")
# Si ton mot de passe contient des \ ou " utilise un r-string: PASSWORD = r"pa\ss\"word"
PASSWORD = "Flatland Cavalryhe Wool"

# --- Option pour Railway/Cron : arrêt auto au bout de N minutes (sinon, laisse vide ou 0) ---
AUTO_EXIT_MINUTES = int(os.getenv("AUTO_EXIT_MINUTES", "8"))

def schedule_auto_exit():
    if AUTO_EXIT_MINUTES and AUTO_EXIT_MINUTES > 0:
        def _exit():
            print(f"[INFO] Arrêt automatique après {AUTO_EXIT_MINUTES} min pour économiser les heures.")
            sys.stdout.flush()
            # on termine proprement le process
            os._exit(0)
        t = threading.Timer(AUTO_EXIT_MINUTES * 60, _exit)
        t.daemon = True
        t.start()

twitch_miner = TwitchChannelPointsMiner(
    username=USERNAME,
    password=PASSWORD,                         # Mot de passe en clair -> pas de saisie interactive
    claim_drops_startup=True,                  # Claim auto des drops au démarrage
    priority=[
        Priority.STREAK,                       # 1) compléter les watch streaks
        Priority.DROPS,                        # 2) récupérer tous les drops
        Priority.ORDER                         # 3) suivre l'ordre défini ci-dessous
    ],
    enable_analytics=False,
    disable_ssl_cert_verification=False,
    disable_at_in_nickname=False,
    logger_settings=LoggerSettings(
        save=True,
        console_level=logging.INFO,
        console_username=False,
        auto_clear=True,
        time_zone="Europe/Zurich",
        file_level=logging.DEBUG,
        emoji=False,                           # plus fiable sur Windows/serveurs headless
        less=True,
        colored=True,
        color_palette=ColorPalette(
            STREAMER_online="GREEN",
            streamer_offline="RED",
            BET_wiN=Fore.MAGENTA
        ),
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,                 # participer aux prédictions
        follow_raid=True,                      # suivre les raids
        claim_drops=True,                      # compter le watch time pour drops
        claim_moments=True,                    # revendiquer les Moments
        watch_streak=True,                     # prioriser les streaks
        community_goals=True,                  # contribuer aux objectifs de communauté
        chat=ChatPresence.ONLINE,              # rejoindre le chat quand live ON
        bet=BetSettings(
            strategy=Strategy.SMART,           # stratégie intelligente
            percentage=5,                      # ~5% du solde
            percentage_gap=20,                 # écart min entre issues
            max_points=50000,                  # plafond
            stealth_mode=True,                 # éviter dépassement visible
            delay_mode=DelayMode.FROM_END,     # miser en fin de timer
            delay=6,                           # ~6s avant la fin
            minimum_points=2000,               # miser si ≥ 2k points
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,
                where=Condition.LTE,
                value=800
            ),
        ),
    ),
)

# Dashboard analytics (facultatif)
# twitch_miner.analytics(host="0.0.0.0", port=5000, refresh=5, days_ago=7)

# Démarrage + arrêt auto optionnel (utile pour Railway + scheduler)
schedule_auto_exit()

# Liste des streamers
twitch_miner.mine(
    [
        Streamer("supercatkei"),
        Streamer("vkimm"),
        Streamer("joueur_du_grenier"),
    ],
    followers=False,
    followers_order=FollowersOrder.ASC
)
