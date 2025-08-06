# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
import threading
from glob import glob
from datetime import datetime, timezone
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

# Couper s'il n'y a VRAIMENT aucune activité pendant N minutes
INACTIVITY_EXIT_MINUTES = int(os.getenv("INACTIVITY_EXIT_MINUTES", "10"))
# Garde-fou au cas où (ex: fuite) – coupe au bout de N minutes coûte que coûte
AUTO_EXIT_MINUTES = int(os.getenv("AUTO_EXIT_MINUTES", "30"))

_last_activity_lock = threading.Lock()
_last_activity_ts = time.time()  # mis à jour dès qu'on voit de l'activité dans les logs

def _bump_activity(reason: str):
    global _last_activity_ts
    with _last_activity_lock:
        _last_activity_ts = time.time()
    print(f"[KEEPALIVE] activité détectée: {reason}")
    sys.stdout.flush()

def _find_latest_log_file():
    os.makedirs("logs", exist_ok=True)
    files = sorted(glob(os.path.join("logs", f"{USERNAME}.*.log")))
    return files[-1] if files else None

def _tail_log_and_watch_activity():
    """
    Surveille le dernier fichier de logs et 'réveille' l'activité dès qu'on voit:
      - 'is Online!' / 'Join IRC Chat'
      - 'Reason:' (WATCH / CLAIM / PREDICTION / RAID / etc.)
    """
    path = None
    # Attendre que le miner crée le premier log
    for _ in range(120):
        path = _find_latest_log_file()
        if path and os.path.exists(path):
            break
        time.sleep(1)
    if not path:
        # Pas de log -> on s'arrête après la fenêtre d'inactivité
        return

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue

                # Signaux d'activité à capturer
                if (" is Online!" in line) or ("Join IRC Chat" in line) or ("Reason:" in line):
                    _bump_activity(line.strip())
    except Exception as e:
        print(f"[WATCHER] erreur lecture logs: {e}")
        sys.stdout.flush()

def _inactivity_guard():
    """Coupe si aucune activité n'a été vue pendant INACTIVITY_EXIT_MINUTES."""
    while True:
        with _last_activity_lock:
            idle = time.time() - _last_activity_ts
        if idle >= INACTIVITY_EXIT_MINUTES * 60:
            print(f"[INFO] 😴 Aucune activité depuis {INACTIVITY_EXIT_MINUTES} minutes → arrêt pour économiser les heures.")
            sys.stdout.flush()
            os._exit(0)
        time.sleep(15)

def _hard_guard():
    """Coupe coûte que coûte après AUTO_EXIT_MINUTES (garde-fou Railway)."""
    time.sleep(AUTO_EXIT_MINUTES * 60)
    print(f"[INFO] ⏹ Arrêt automatique après {AUTO_EXIT_MINUTES} minutes (garde-fou).")
    sys.stdout.flush()
    os._exit(0)

# --- Configuration du bot ---
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

# --- Threads de garde ---
threading.Thread(target=_tail_log_and_watch_activity, daemon=True).start()
threading.Thread(target=_inactivity_guard, daemon=True).start()
threading.Thread(target=_hard_guard, daemon=True).start()

# --- Lancement du miner ---
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
