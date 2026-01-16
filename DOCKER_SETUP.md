# 🐳 Guide de Configuration Docker

## ✅ Modifications apportées

Le Dockerfile a été mis à jour pour :
- ✅ Inclure `run.py` directement dans l'image Docker
- ✅ Créer automatiquement `config.py` à partir de variables d'environnement
- ✅ Fonctionner avec ou sans montage de volumes

## 🔧 Configuration avec Variables d'Environnement

### Pour les services cloud (Railway, Render, Fly.io, etc.)

⚠️ **IMPORTANT** : Vous DEVEZ configurer les variables d'environnement dans votre service cloud !

#### Variables OBLIGATOIRES
```
TWITCH_USERNAME=mat_1234555666666
```

#### Variables OPTIONNELLES
```
TWITCH_PASSWORD=Flatland Cavalryhe Wool
```
(Si non défini, le script demandera le mot de passe interactivement - mais cela ne fonctionne pas dans un conteneur non-interactif, donc définissez-le !)

#### Optionnel (Notifications)
```
TELEGRAM_CHAT_ID=votre_chat_id
TELEGRAM_TOKEN=votre_token
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Le script d'entrée créera automatiquement `config.py` au démarrage

## 🚀 Utilisation

### Option 1 : Docker Compose (local)

1. Créez `docker-compose.yml` :
```yaml
version: "3.9"
services:
  miner:
    build: .
    # OU utilisez l'image officielle :
    # image: rdavidoff/twitch-channel-points-miner-v2
    stdin_open: true
    tty: true
    environment:
      - TWITCH_USERNAME=mat_1234555666666
      - TWITCH_PASSWORD=Flatland Cavalryhe Wool
    volumes:
      - ./cookies:/usr/src/app/cookies
      - ./logs:/usr/src/app/logs
      - ./analytics:/usr/src/app/analytics
    restart: unless-stopped
```

2. Lancez :
```bash
docker-compose up -d
```

### Option 2 : Docker Run (local)

```bash
docker run -d \
  --name twitch-miner \
  -e TWITCH_USERNAME="mat_1234555666666" \
  -e TWITCH_PASSWORD="Flatland Cavalryhe Wool" \
  -v $(pwd)/cookies:/usr/src/app/cookies \
  -v $(pwd)/logs:/usr/src/app/logs \
  -v $(pwd)/analytics:/usr/src/app/analytics \
  rdavidoff/twitch-channel-points-miner-v2
```

### Option 3 : Service Cloud

1. **Railway / Render / Fly.io** :
   - Configurez les variables d'environnement dans le dashboard
   - Le script créera automatiquement `config.py` au démarrage

2. **Rebuild l'image** si nécessaire :
   - Les changements du Dockerfile nécessitent un rebuild

## 📝 Notes importantes

- `run.py` est maintenant **dans l'image** (plus besoin de le monter)
- `config.py` est créé automatiquement depuis les variables d'env
- Vous pouvez toujours monter `config.py` manuellement si vous préférez
- Les dossiers `cookies/`, `logs/`, `analytics/` doivent être montés pour persister les données

## 🔍 Vérification

Pour vérifier que tout fonctionne :
```bash
docker logs twitch-miner
```

Vous devriez voir les logs du bot au lieu de l'erreur "can't open file '/usr/src/app/run.py'".
