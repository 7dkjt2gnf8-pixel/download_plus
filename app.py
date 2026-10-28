"""Download+ — serveur web : récupère une vidéo (MP4) ou l'audio seul (MP3) depuis une URL."""
import os
import shutil
import tempfile
import threading
import time

from flask import Flask, jsonify, request, send_file, send_from_directory
import yt_dlp

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC = BASE  # tous les fichiers sont à la racine du dépôt
PUBLIC = {
    "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png",
    "icon-maskable-512.png", "apple-touch-icon.png",
}
app = Flask(__name__, static_folder=None)


def _cleanup_later(path, delay=120):
    def run():
        time.sleep(delay)
        shutil.rmtree(path, ignore_errors=True)
    threading.Thread(target=run, daemon=True).start()


@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/sw.js")
def sw():
    resp = send_from_directory(STATIC, "sw.js")
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/<name>")
def public_file(name):
    if name not in PUBLIC:  # n'expose que les fichiers de l'interface
        return jsonify(error="Introuvable"), 404
    mime = "application/manifest+json" if name.endswith(".webmanifest") else None
    return send_from_directory(STATIC, name, mimetype=mime)


@app.get("/api/info")
def info():
    url = (request.args.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return jsonify(error="URL invalide"), 400
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "noplaylist": True}) as ydl:
            data = ydl.extract_info(url, download=False)
    except Exception as e:  # noqa: BLE001
        return jsonify(error=f"Impossible de lire cette URL : {e}"), 400
    return jsonify(
        title=data.get("title"),
        uploader=data.get("uploader"),
        duration=data.get("duration"),
        thumbnail=data.get("thumbnail"),
    )


@app.get("/api/download")
def download():
    url = (request.args.get("url") or "").strip()
    kind = request.args.get("type", "video")
    if not url.startswith(("http://", "https://")):
        return jsonify(error="URL invalide"), 400

    tmp = tempfile.mkdtemp(prefix="dlplus_")
    opts = {
        "quiet": True,
        "noplaylist": True,
        "outtmpl": os.path.join(tmp, "%(title).120B.%(ext)s"),
        "restrictfilenames": False,
    }
    if kind == "audio":
        opts.update(
            format="bestaudio/best",
            postprocessors=[{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        )
    else:
        quality = request.args.get("q", "1080")
        h = int(quality) if quality.isdigit() else 1080
        opts.update(
            format=(f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/"
                    f"b[height<={h}][ext=mp4]/bv*[height<={h}]+ba/b"),
            merge_output_format="mp4",
        )

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception as e:  # noqa: BLE001
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify(error=f"Échec du téléchargement : {e}"), 500

    files = [f for f in os.listdir(tmp) if not f.endswith((".part", ".ytdl"))]
    if not files:
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify(error="Aucun fichier produit"), 500
    path = os.path.join(tmp, files[0])
    _cleanup_later(tmp)
    mime = "audio/mpeg" if kind == "audio" else "video/mp4"
    return send_file(path, as_attachment=True, download_name=files[0], mimetype=mime)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, threaded=True)
