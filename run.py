# -*- coding: utf-8 -*-
import logging
import os
import threading
import sys
import time
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Settings import Priority, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import (
    Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
)
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

USERNAME = "mat_1234555666666"
PASSWORD = None  # on utilise le cookie .pkl
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))          # toutes les 2 min
MAX_IDLE_MINUTES = int(os.getenv("MAX_IDLE_MINUTES", "10"))       # si 10 min sans live -> stop
HARD_MAX_MINUTES = int(os.getenv("HARD_MAX_MINUTES", "30"))       # coupe dur à 30 min max

start_time = time.time()
last_online_time = time.time()

def watchdog():
    global last_online_time
    while True:
        # Coupe dur pour éviter de consommer trop en cas de bug
        if time.time() - start_time > HARD_MAX_MINUTES * 60:
            print(f"[INFO] Arrêt dur après {HARD_MAX_MINUTES} minutes (sécurité).")
            sys.stdout.flush()
            os._exit(0)

        # Détermine si au moins un streamer est en ligne
        try:
            any_online = any(getattr(s, "online", False) for s in twitch_miner.streamers)
        except Exception:
            any_online = False

        if any_online:
            last_online_time = time.time()
        else:
            idle_secs = time.time() - last_online_time
            if idle_secs > MAX_IDLE_MINUTES * 60:
                print(f"[INFO] Aucun live depuis {MAX_IDLE_MINUTES} min → arrêt pour économiser les heures.")
                sys.stdout.flush()
                os._exit(0)

        time.sleep(CHECK_INTERVAL)

twitch_miner = TwitchChannelPointsMiner(
    username=USERNAME,
    password=PASSWORD,
    claim_drops_startup=True,
    priority=[Priority.STREAK, Priority.DROPS, Priority.ORDER],
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
        emoji=False,
        less=True,
        colored=True,
        color_palette=ColorPalette(
            STREAMER_online="GREEN",
            streamer_offline="RED",
            BET_wiN=Fore.MAGENTA
        ),
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,
        follow_raid=True,
        claim_drops=True,
        claim_moments=True,
        watch_streak=True,
        community_goals=True,
        chat=ChatPresence.ONLINE,
        bet=BetSettings(
            strategy=Strategy.SMART,
            percentage=5,
            percentage_gap=20,
            max_points=50000,
            stealth_mode=True,
            delay_mode=DelayMode.FROM_END,
            delay=6,
            minimum_points=2000,
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,
                where=Condition.LTE,
                value=800
            ),
        ),
    ),
)

# Surveillant en arrière-plan
threading.Thread(target=watchdog, daemon=True).start()

# Lancement du bot
twitch_miner.mine(
    [
        Streamer("supercatkei"),
        Streamer("vkimm"),
        Streamer("joueur_du_grenier"),
    ],
    followers=False,
    followers_order=FollowersOrder.ASC
)
