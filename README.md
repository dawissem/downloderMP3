# Convertisseur Vidéo en MP3

Une application web simple pour télécharger des vidéos depuis YouTube et autres plateformes, puis les convertir en fichiers MP3.

## Installation

### Prérequis
- Python 3.8+
- FFmpeg (pour la conversion audio)

### Sur Linux/Mac
```bash
# Installer FFmpeg
brew install ffmpeg  # Mac
sudo apt-get install ffmpeg  # Ubuntu/Debian

# Cloner ou copier le projet
cd video-to-mp3

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

### Sur Windows
```bash
# Installer FFmpeg (via chocolatey)
choco install ffmpeg

# Ou télécharger depuis https://ffmpeg.org/download.html

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

## Utilisation

1. Ouvre ton navigateur à `http://localhost:5000`
2. Colle l'URL d'une vidéo YouTube
3. Choisis la qualité audio souhaitée
4. Clique sur "Télécharger"
5. Attends la conversion
6. Télécharge le fichier MP3

## Fonctionnalités

- Support de YouTube et autres plateformes (via yt-dlp)
- Conversion en temps réel avec barre de progression
- Suivi de la vitesse et de l'ETA
- Qualité audio configurable (192, 256, 320 kbps)
- Interface moderne et responsive
- Téléchargement direct du fichier final
- Gestion des téléchargements multiples

## Structure du projet

```
video-to-mp3/
├── app.py                  # Application Flask principale
├── requirements.txt        # Dépendances Python
├── templates/
│   └── index.html         # Interface HTML/CSS/JavaScript
├── downloads/             # Dossier des fichiers MP3
└── temp/                  # Dossier temporaire
```

## Comment ça marche

1. **Frontend (HTML/JS)** : L'utilisateur colle une URL et clique sur "Télécharger"
2. **Backend (Flask)** : Reçoit la requête et lance le téléchargement dans un thread séparé
3. **yt-dlp** : Télécharge la meilleure qualité audio disponible
4. **FFmpeg** : Convertit l'audio au format MP3
5. **Polling (JS)** : Le frontend vérifie l'état toutes les 0.5 secondes
6. **Retour** : Une fois prêt, l'utilisateur peut télécharger le fichier

## Limitations

- La taille des fichiers dépend de la plateforme source
- Les vidéos très longues peuvent prendre du temps
- Certains serveurs limitent les téléchargements
- Les droits d'auteur doivent être respectés

## Dépannage

### "FFmpeg not found"
Assure-toi d'avoir FFmpeg installé et accessible via le PATH système.

### "Erreur de téléchargement"
Vérifie que l'URL est valide et que la vidéo n'est pas protégée.

### Port 5000 déjà utilisé
Change le port dans `app.py` : `app.run(debug=True, port=5001)`

## Notes de sécurité

- Ne partage jamais les fichiers sans permission du créateur
- Respecte les droits d'auteur
- Utilise cette application uniquement pour un usage personnel

Bon téléchargement ! 🎵
