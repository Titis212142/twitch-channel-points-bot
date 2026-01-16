# 🔐 Configuration Sécurisée

## ⚠️ Important - Sécurité

Vos identifiants sont maintenant stockés dans `config.py` qui **n'est PAS versionné** sur GitHub (ajouté au `.gitignore`).

## 📝 Configuration initiale

1. **Copiez le fichier d'exemple** :
   ```bash
   cp config.example.py config.py
   ```

2. **Éditez `config.py`** et remplissez vos identifiants :
   ```python
   TWITCH_USERNAME = "votre_nom_utilisateur"
   TWITCH_PASSWORD = "votre_mot_de_passe"
   ```

3. **Optionnel** : Configurez les notifications (Telegram, Discord, etc.)

## ✅ Fichiers

- `config.py` : **Votre fichier de configuration** (avec vos identifiants) - ⚠️ **NE PAS COMMITER**
- `config.example.py` : Fichier d'exemple (peut être committé)
- `example.py` : Script principal qui lit depuis `config.py`

## 🚀 Utilisation

Une fois `config.py` configuré, lancez simplement :
```bash
python example.py
```

## 🔒 Sécurité

- ✅ `config.py` est dans `.gitignore` → ne sera jamais sur GitHub
- ✅ `config.example.py` peut être committé (sans identifiants)
- ✅ Vos identifiants restent locaux sur votre machine

## 📋 Variables disponibles dans config.py

### Obligatoire
- `TWITCH_USERNAME` : Votre nom d'utilisateur Twitch
- `TWITCH_PASSWORD` : Votre mot de passe (ou `""` pour saisie interactive)

### Optionnel (Notifications)
- `TELEGRAM_CHAT_ID` : Chat ID Telegram
- `TELEGRAM_TOKEN` : Token du bot Telegram
- `DISCORD_WEBHOOK_URL` : URL du webhook Discord
- Et d'autres services (voir `config.example.py`)
