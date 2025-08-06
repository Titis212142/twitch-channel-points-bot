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

USERNAME = "mat_1234555666666"
PASSWORD = None

# On supprime l’arrêt d’inactivité (buggy) et on ne garde qu’un arrêt de sécurité optionnel
# Mets 0 pour désactiver complètement (recommandé avec ton cron de 30 min)
AUTO_EXIT_MINUTES = int(os.getenv("AUTO_EXIT_MINUTES", "0"))

def schedule_auto_exit():
    if AUTO_EXIT_MINUTES > 0:
        def _exit():
            print(f"[INFO] ⏹ Arrêt automatique après {AUTO_EXIT_MINUTES} minutes (sécurité).")
            sys.stdout.flush()
            os._exit(0)
        t = threading.Timer(AUTO_EXIT_MINUTES * 60, _exit)
        t.daemon = True
        t.start()

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

schedule_auto_exit()

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
