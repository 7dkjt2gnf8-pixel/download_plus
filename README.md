# Download+

Web app installable (iOS / Android) pour sauvegarder une vidéo en MP4 ou seulement l'audio en MP3 à partir d'un lien (YouTube et autres sites supportés par yt-dlp).

## Mettre sur GitHub

Tous les fichiers sont à la racine : dépose-les tous d'un coup (Add file → Upload files), dans n'importe quel ordre. Aucun dossier à créer.

## Lancer en local (ordinateur)

Prérequis : Python 3.10+ et ffmpeg (`brew install ffmpeg` sur Mac, `winget install ffmpeg` sur Windows).

```bash
pip install -r requirements.txt
python app.py
```

Ouvre http://localhost:8000. Depuis ton téléphone sur le même Wi‑Fi : http://IP-DE-TON-ORDI:8000

## Mettre en ligne (pour l'utiliser partout)

L'installation sur l'écran d'accueil exige **HTTPS**. Le plus simple : déployer le `Dockerfile` sur Render, Railway, Fly.io ou un petit VPS. Ils fournissent HTTPS automatiquement.

## Installer sur le téléphone

- **iPhone (Safari)** : ouvre l'URL → bouton Partager → « Sur l'écran d'accueil ».
- **Android (Chrome)** : ouvre l'URL → menu ⋮ → « Installer l'application ». Une fois installée, Download+ apparaît aussi dans le menu « Partager » de l'app YouTube.

## Utilisation

1. Colle le lien (bouton « Coller »).
2. Choisis **Vidéo MP4** (avec la qualité) ou **Audio MP3**.
3. Appuie sur Télécharger. Sur iPhone, la feuille de partage s'ouvre : « Enregistrer dans Fichiers » ou « Enregistrer la vidéo ».

## Maintenance

YouTube change souvent son fonctionnement. Si les téléchargements échouent, mets à jour yt-dlp : `pip install -U yt-dlp` (ou redéploie).

Ne télécharge que des contenus dont tu as les droits ou sous licence libre.
