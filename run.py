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

USERNAME = "mat_1234555666666"  # ton pseudo Twitch
PASSWORD = None  # pas besoin si cookie déjà présent
AUTO_EXIT_MINUTES = int(os.getenv("AUTO_EXIT_MINUTES", "30"))  # arrêt sécurité max
INACTIVITY_EXIT_MINUTES = 10  # arrêt si aucun streamer live

active_streamer_detected = False
inactivity_timer = None

def schedule_auto_exit():
    def _exit():
        print(f"[INFO] ⏹ Arrêt automatique après {AUTO_EXIT_MINUTES} minutes.")
        sys.stdout.flush()
        os._exit(0)
    t = threading.Timer(AUTO_EXIT_MINUTES * 60, _exit)
    t.daemon = True
    t.start()

def reset_inactivity_timer():
    global inactivity_timer
    if inactivity_timer:
        inactivity_timer.cancel()
    inactivity_timer = threading.Timer(INACTIVITY_EXIT_MINUTES * 60, stop_if_inactive)
    inactivity_timer.daemon = True
    inactivity_timer.start()

def stop_if_inactive():
    global active_streamer_detected
    if not active_streamer_detected:
        print(f"[INFO] 😴 Aucun streamer live depuis {INACTIVITY_EXIT_MINUTES} minutes, arrêt.")
        sys.stdout.flush()
        os._exit(0)

def on_streamer_online(streamer, points):
    global active_streamer_detected
    active_streamer_detected = True
    reset_inactivity_timer()

def on_streamer_offline(streamer):
    global active_streamer_detected
    # Ici on ne met pas direct False, on attend que tous soient off
    pass

# Bot config
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

# Lancement des timers
schedule_auto_exit()
reset_inactivity_timer()

# Lancement du bot
twitch_miner.mine(
    [
        Streamer("supercatkei"),
        Streamer("vkimm"),
        Streamer("joueur_du_grenier"),
        Streamer("maidusaa"),
        Streamer("wankilstudio"),
        Streamer("hortyunderscore"),
    ],
    followers=False,
    followers_order=FollowersOrder.ASC
)
