# 🔧 Guide de Dépannage

## ❌ Problème : "Streamer does not exist"

Si vous voyez le message `Streamer X does not exist` pour tous vos streamers, voici comment diagnostiquer :

### 1. Vérifier les noms exacts

Les noms Twitch sont sensibles à la casse et aux caractères. Vérifiez les URLs exactes :

- Allez sur `https://www.twitch.tv/nom_du_streamer`
- Le nom dans l'URL est le **login name** exact à utiliser

### 2. Activer les logs DEBUG

Dans `run.py`, changez le niveau de log pour voir les détails :

```python
logger_settings=LoggerSettings(
    console_level=logging.DEBUG,  # Changez de INFO à DEBUG
    # ...
)
```

Cela affichera les réponses exactes de l'API.

### 3. Tester avec un seul streamer

Testez d'abord avec un seul streamer connu pour isoler le problème :

```python
twitch_miner.mine(
    [
        Streamer("xqc"),  # Streamer très connu pour tester
    ],
)
```

### 4. Vérifier l'authentification

Si tous les streamers échouent, cela peut indiquer :
- Token expiré
- Permissions insuffisantes
- Problème avec l'API GraphQL

### 5. Vérifier les noms de vos streamers

Voici les noms à vérifier (certains peuvent avoir changé) :

- `joueur_du_grenier` → Vérifiez sur Twitch
- `wankilstudio` → Peut-être `wankil` ou autre
- `supercatkei` → Vérifiez l'orthographe exacte
- `vkimm` → Vérifiez l'orthographe exacte
- `maidusaa` → Vérifiez l'orthographe exacte
- `gracehan_` → Vérifiez l'orthographe exacte
- `hortyunderscore` → Confirmé existant

### 6. Solution temporaire

Si certains streamers ne sont pas trouvés, le bot continuera de fonctionner avec ceux qui sont valides. Les streamers invalides seront simplement ignorés.

### 7. Vérifier manuellement

Testez un streamer avec curl :

```bash
curl -H "Client-ID: votre_client_id" \
     -H "Authorization: OAuth votre_token" \
     "https://gql.twitch.tv/gql" \
     -d '{"operationName":"GetIDFromLogin","variables":{"login":"xqc"}}'
```

Si cela fonctionne, le problème vient peut-être de la configuration.
