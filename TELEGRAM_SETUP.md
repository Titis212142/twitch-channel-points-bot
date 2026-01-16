# 📱 Configuration Telegram

## Étape 1 : Créer un bot Telegram

1. Ouvrez Telegram et cherchez **@BotFather**
2. Envoyez la commande `/newbot`
3. Suivez les instructions pour nommer votre bot
4. BotFather vous donnera un **token** (ex: `8529315436:AAHS-rJykfpB-jgiA7E1bdo_BhOvAp7jY40`)

## Étape 2 : Obtenir votre Chat ID

### Méthode 1 : Via @userinfobot (Recommandé)

1. Cherchez **@userinfobot** sur Telegram
2. Cliquez sur "Start" ou envoyez `/start`
3. Le bot vous enverra votre Chat ID (un nombre comme `123456789`)

### Méthode 2 : Via @getidsbot

1. Cherchez **@getidsbot** sur Telegram
2. Cliquez sur "Start"
3. Le bot affichera votre Chat ID

### Méthode 3 : Via votre bot

1. Envoyez un message à votre bot (n'importe quel message)
2. Visitez cette URL dans votre navigateur (remplacez `VOTRE_TOKEN` par votre token) :
   ```
   https://api.telegram.org/botVOTRE_TOKEN/getUpdates
   ```
3. Cherchez `"chat":{"id":` dans la réponse JSON
4. Le nombre après `"id":` est votre Chat ID

## Étape 3 : Configurer dans config.py

Ajoutez vos identifiants dans `config.py` :

```python
TELEGRAM_CHAT_ID = 123456789  # Votre Chat ID (nombre entier)
TELEGRAM_TOKEN = "8529315436:AAHS-rJykfpB-jgiA7E1bdo_BhOvAp7jY40"  # Votre token
```

## Étape 4 : Tester

1. Redémarrez le bot
2. Le bot devrait maintenant envoyer des notifications Telegram quand :
   - Un streamer passe en ligne/hors ligne
   - Vous gagnez des points
   - Vous perdez un pari
   - Vous êtes mentionné dans le chat

## 🔍 Vérification rapide

Pour tester rapidement, visitez cette URL (remplacez les valeurs) :
```
https://api.telegram.org/bot8529315436:AAHS-rJykfpB-jgiA7E1bdo_BhOvAp7jY40/sendMessage?chat_id=VOTRE_CHAT_ID&text=Test
```

Si vous recevez un message "Test" sur Telegram, la configuration est correcte !
