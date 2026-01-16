# 🚀 Améliorations Proposées pour Twitch Channel Points Miner v2

## 📋 Table des matières
1. [Sécurité](#1-sécurité)
2. [Gestion d'erreurs](#2-gestion-derreurs)
3. [Qualité du code](#3-qualité-du-code)
4. [Performance](#4-performance)
5. [Maintenabilité](#5-maintenabilité)
6. [Fonctionnalités](#6-fonctionnalités)

---

## 1. 🔒 Sécurité

### 1.1 Gestion sécurisée des fichiers (CRITIQUE)

**Problème actuel :**
```python
# TwitchLogin.py:317
pickle.dump(self.cookies, open(cookies_file, "wb"))  # ❌ Fichier non fermé explicitement

# TwitchLogin.py:328
self.cookies = pickle.load(open(cookies_file, "rb"))  # ❌ Pas de gestion d'erreur
```

**Amélioration :**
```python
def save_cookies(self, cookies_file):
    logger.info("Saving cookies to your computer..")
    cookies_dict = self.session.cookies.get_dict()
    cookies_dict["auth-token"] = self.token
    if "persistent" not in cookies_dict:
        cookies_dict["persistent"] = self.user_id

    self.cookies = []
    for cookie_name, value in cookies_dict.items():
        self.cookies.append({"name": cookie_name, "value": value})
    
    # ✅ Utiliser context manager
    try:
        with open(cookies_file, "wb") as f:
            pickle.dump(self.cookies, f)
        # ✅ Définir permissions restrictives (Unix)
        if os.name != 'nt':  # Pas Windows
            os.chmod(cookies_file, 0o600)  # rw------- uniquement pour le propriétaire
    except (IOError, OSError) as e:
        logger.error(f"Failed to save cookies: {e}")
        raise

def load_cookies(self, cookies_file):
    if not os.path.isfile(cookies_file):
        raise WrongCookiesException("There must be a cookies file!")
    
    # ✅ Gestion d'erreur et validation
    try:
        with open(cookies_file, "rb") as f:
            self.cookies = pickle.load(f)
        # ✅ Validation basique
        if not isinstance(self.cookies, list):
            raise WrongCookiesException("Invalid cookie file format")
    except (pickle.UnpicklingError, EOFError, IOError) as e:
        logger.error(f"Failed to load cookies: {e}")
        raise WrongCookiesException(f"Cookie file corrupted: {e}")
```

### 1.2 Chiffrement des cookies (OPTIONNEL mais recommandé)

```python
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def _get_encryption_key(self, username: str) -> bytes:
    """Génère une clé de chiffrement basée sur le username"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'twitch_miner_salt',  # En production, utiliser un salt unique
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(username.encode()))

def save_cookies_encrypted(self, cookies_file, username: str):
    """Sauvegarde les cookies de manière chiffrée"""
    key = self._get_encryption_key(username)
    fernet = Fernet(key)
    
    cookies_json = json.dumps(self.cookies)
    encrypted_cookies = fernet.encrypt(cookies_json.encode())
    
    with open(cookies_file, "wb") as f:
        f.write(encrypted_cookies)
```

### 1.3 Validation des entrées utilisateur

```python
def __init__(self, username: str, user_agent: str, password: str = None):
    # ✅ Validation du username
    if not username or not isinstance(username, str):
        raise ValueError("Username must be a non-empty string")
    if len(username) > 25 or not username.replace('_', '').isalnum():
        raise ValueError("Invalid username format")
    
    # ✅ Validation du password si fourni
    if password is not None:
        if len(password) < 8:
            logger.warning("Password is shorter than 8 characters")
    
    self.username = username.lower().strip()
    # ... reste du code
```

---

## 2. ⚠️ Gestion d'erreurs

### 2.1 Remplacement des `except Exception` génériques

**Problème actuel :**
```python
# Twitch.py:664
except Exception:
    logger.error("Exception raised in send minute watched", exc_info=True)
```

**Amélioration :**
```python
# ✅ Capturer des exceptions spécifiques
try:
    # ... code ...
except requests.exceptions.ConnectionError as e:
    logger.error(f"Connection error: {e}")
    self.__check_connection_handler(chunk_size)
except requests.exceptions.Timeout as e:
    logger.error(f"Request timeout: {e}")
    # Retry logic
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        logger.error("Authentication failed, cookies may be expired")
        # Relancer le login
    elif e.response.status_code == 429:
        logger.warning("Rate limited, backing off")
        time.sleep(60)
    else:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
except (ValueError, KeyError) as e:
    logger.error(f"Data parsing error: {e}")
except Exception as e:
    logger.error(f"Unexpected error in send_minute_watched_events: {e}", exc_info=True)
    # Ne pas ignorer complètement, mais logger avec contexte
```

### 2.2 Retry logic avec exponential backoff

```python
from functools import wraps
import time

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator pour retry avec exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout) as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
        return wrapper
    return decorator

# Utilisation
@retry_with_backoff(max_retries=3, base_delay=2)
def post_gql_request(self, json_data):
    response = requests.post(
        GQLOperations.url,
        json=json_data,
        headers={...},
        timeout=30  # ✅ Ajouter timeout
    )
    response.raise_for_status()  # ✅ Lever exception pour codes HTTP d'erreur
    return response.json()
```

### 2.3 Gestion des erreurs GraphQL

```python
def post_gql_request(self, json_data):
    try:
        response = requests.post(
            GQLOperations.url,
            json=json_data,
            headers={...},
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        # ✅ Vérifier les erreurs GraphQL
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                error_msg = error.get("message", "Unknown GraphQL error")
                error_extensions = error.get("extensions", {})
                
                if error_extensions.get("code") == "UNAUTHENTICATED":
                    logger.error("Authentication expired, need to re-login")
                    # Déclencher re-login
                elif error_extensions.get("code") == "FORBIDDEN":
                    logger.error("Access forbidden, check permissions")
                else:
                    logger.error(f"GraphQL error: {error_msg}")
            
            return {}
        
        return result.get("data", {})
        
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {json_data.get('operationName')}")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {}
```

---

## 3. 📝 Qualité du code

### 3.1 Type hints complets

**Problème actuel :**
```python
def post_gql_request(self, json_data):  # ❌ Pas de type hints
```

**Amélioration :**
```python
from typing import Dict, Any, Optional, List

def post_gql_request(
    self, 
    json_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Effectue une requête GraphQL vers Twitch.
    
    Args:
        json_data: Données de la requête GraphQL
        
    Returns:
        Réponse JSON de l'API, ou dict vide en cas d'erreur
    """
    # ... code ...
```

### 3.2 Suppression du code mort et commentaires

```python
# ❌ À supprimer
# print(f"cookies_dict2pickle: {cookies_dict}")
# print(f"cookies2pickle: {self.cookies}")

# ✅ Remplacer par des logs si nécessaire
logger.debug(f"Saving {len(self.cookies)} cookies")
```

### 3.3 Constantes de configuration

```python
# constants.py - Ajouter
class Config:
    """Configuration centralisée"""
    # Timeouts
    REQUEST_TIMEOUT = 30
    WEBSOCKET_PING_INTERVAL = 240  # 4 minutes
    WEBSOCKET_PING_TIMEOUT = 10
    
    # Retry
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1
    RETRY_MAX_DELAY = 60
    
    # Rate limiting
    MIN_REQUEST_INTERVAL = 0.3  # secondes entre requêtes
    MAX_REQUEST_INTERVAL = 0.7
    
    # File permissions
    COOKIE_FILE_PERMISSIONS = 0o600  # Unix seulement
```

### 3.4 Validation des données avec dataclasses

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class StreamerConfig:
    """Configuration validée pour un streamer"""
    username: str
    make_predictions: bool = True
    follow_raid: bool = True
    claim_drops: bool = True
    watch_streak: bool = True
    
    def __post_init__(self):
        """Validation après initialisation"""
        if not self.username or len(self.username) > 25:
            raise ValueError(f"Invalid username: {self.username}")
        self.username = self.username.lower().strip()
```

---

## 4. ⚡ Performance

### 4.1 Cache pour les requêtes répétitives

```python
from functools import lru_cache
from datetime import datetime, timedelta

class Twitch:
    def __init__(self, ...):
        # ... code existant ...
        self._cache = {}
        self._cache_ttl = {}  # Time To Live
    
    def _get_cached_or_fetch(self, cache_key: str, fetch_func, ttl: int = 300):
        """Récupère depuis le cache ou fetch si expiré"""
        now = datetime.now()
        
        if cache_key in self._cache:
            if cache_key in self._cache_ttl:
                if now < self._cache_ttl[cache_key]:
                    return self._cache[cache_key]
        
        # Cache expiré ou inexistant
        result = fetch_func()
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = now + timedelta(seconds=ttl)
        return result
    
    def get_channel_id(self, username: str) -> str:
        """Récupère le channel_id avec cache"""
        cache_key = f"channel_id_{username}"
        
        def fetch():
            json_data = copy.deepcopy(GQLOperations.GetIDFromLogin)
            json_data["variables"]["login"] = username
            response = self.post_gql_request(json_data)
            # ... extraction channel_id ...
            return channel_id
        
        return self._get_cached_or_fetch(cache_key, fetch, ttl=3600)  # Cache 1h
```

### 4.2 Rate limiting explicite

```python
import time
from collections import deque

class RateLimiter:
    """Rate limiter pour respecter les limites de l'API"""
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Supprimer les appels trop anciens
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            # Attendre si nécessaire
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

# Utilisation
rate_limiter = RateLimiter(max_calls=100, period=60)  # 100 appels/minute

@rate_limiter
def post_gql_request(self, json_data):
    # ... code ...
```

### 4.3 Pool de connexions HTTP

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Twitch:
    def __init__(self, ...):
        # ... code existant ...
        self.session = requests.Session()
        
        # ✅ Configuration du pool de connexions
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        self.session.mount("https://", adapter)
```

---

## 5. 🔧 Maintenabilité

### 5.1 Logging structuré

```python
import json
from datetime import datetime

class StructuredLogger:
    """Logger avec format JSON pour faciliter l'analyse"""
    @staticmethod
    def log_event(event_type: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            **kwargs
        }
        logger.info(json.dumps(log_entry))

# Utilisation
StructuredLogger.log_event(
    "points_gained",
    streamer="username",
    points=50,
    reason="CLAIM",
    total_points=1000
)
```

### 5.2 Configuration via fichier

```python
# config.yaml
twitch:
  username: "your_username"
  priority:
    - STREAK
    - DROPS
    - ORDER
  streamer_settings:
    make_predictions: true
    follow_raid: true
    claim_drops: true

logging:
  level: INFO
  save: true
  emoji: true

# config_loader.py
import yaml

def load_config(config_path: str = "config.yaml") -> dict:
    """Charge la configuration depuis un fichier YAML"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

### 5.3 Tests unitaires

```python
# tests/test_twitch.py
import unittest
from unittest.mock import Mock, patch
from TwitchChannelPointsMiner.classes.Twitch import Twitch

class TestTwitch(unittest.TestCase):
    def setUp(self):
        self.twitch = Twitch("test_user", "test_agent")
    
    @patch('requests.post')
    def test_post_gql_request_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": {}}
        
        result = self.twitch.post_gql_request({"operationName": "Test"})
        self.assertEqual(result, {"data": {}})
    
    @patch('requests.post')
    def test_post_gql_request_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        
        result = self.twitch.post_gql_request({"operationName": "Test"})
        self.assertEqual(result, {})
```

---

## 6. ✨ Fonctionnalités

### 6.1 Health check endpoint

```python
# AnalyticsServer.py - Ajouter
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check pour monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "streamers_count": len(streamers),
        "websocket_connections": len(ws_pool.ws)
    }
```

### 6.2 Métriques Prometheus

```python
from prometheus_client import Counter, Gauge, Histogram

# Métriques
points_gained_total = Counter(
    'twitch_points_gained_total',
    'Total points gained',
    ['streamer', 'reason']
)

points_balance = Gauge(
    'twitch_points_balance',
    'Current points balance',
    ['streamer']
)

request_duration = Histogram(
    'twitch_request_duration_seconds',
    'Request duration',
    ['operation']
)

# Utilisation
@request_duration.time()
def post_gql_request(self, json_data):
    # ... code ...
    points_gained_total.labels(
        streamer=streamer.username,
        reason="CLAIM"
    ).inc(50)
```

### 6.3 Mode dry-run

```python
class TwitchChannelPointsMiner:
    def __init__(self, ..., dry_run: bool = False):
        # ... code existant ...
        self.dry_run = dry_run
    
    def make_predictions(self, event):
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would place bet: {bet_amount} on {choice}")
            return
        # ... code réel ...
```

---

## 📊 Priorités d'implémentation

### 🔴 Critique (À faire immédiatement)
1. ✅ Gestion sécurisée des fichiers (context managers)
2. ✅ Gestion d'erreurs spécifiques
3. ✅ Timeouts sur les requêtes HTTP

### 🟡 Important (À faire bientôt)
4. ✅ Retry logic avec backoff
5. ✅ Validation des entrées
6. ✅ Type hints
7. ✅ Rate limiting

### 🟢 Nice to have (Améliorations futures)
8. Chiffrement des cookies
9. Cache pour requêtes répétitives
10. Tests unitaires
11. Métriques Prometheus
12. Configuration YAML

---

## 🎯 Résumé

Ces améliorations apporteraient :
- **Sécurité** : Protection des données sensibles
- **Robustesse** : Meilleure gestion des erreurs et retry
- **Performance** : Cache et rate limiting
- **Maintenabilité** : Code plus propre et testable
- **Observabilité** : Meilleur monitoring et debugging

**Estimation** : ~2-3 jours de développement pour les améliorations critiques, ~1 semaine pour tout.
