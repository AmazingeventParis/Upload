"""
Upload Tool — Outil d'upload de fichiers pour code-server.
Glisser-deposer des fichiers (images, excel, pdf, etc.)
puis copier la commande wget pour les recuperer sur code-server.
"""

import os
import uuid
import time
import threading
import functools
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response

app = Flask(__name__, static_folder="static")

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/codeserver/projects/uploads")
PASSWORD = os.environ.get("UPLOAD_PASSWORD", "Laurytal2")
MAX_FILE_SIZE = 300 * 1024 * 1024  # 300 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


def check_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_pw = request.headers.get("X-Upload-Password") or request.form.get("password")
        if auth_pw != PASSWORD:
            return jsonify({"error": "Mot de passe incorrect"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/upload", methods=["POST"])
@check_auth
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Nom de fichier vide"}), 400

    # Taille
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": f"Fichier trop gros ({size // 1024 // 1024}MB > 300MB)"}), 400

    # Nom unique pour eviter les collisions
    ext = os.path.splitext(f.filename)[1].lower()
    safe_name = f.filename.replace(" ", "_").replace("'", "").replace('"', "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_name}"

    filepath = os.path.join(UPLOAD_DIR, filename)
    f.save(filepath)

    # URL de telechargement
    host = request.host_url.rstrip("/")
    download_url = f"{host}/dl/{filename}"

    return jsonify({
        "success": True,
        "filename": filename,
        "original_name": f.filename,
        "size": size,
        "download_url": download_url,
        "codeserver_path": f"~/projects/uploads/{filename}",
    })


@app.route("/dl/<filename>")
def download_file(filename):
    # Securite : empecher path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return "Interdit", 403
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/files")
@check_auth
def list_files():
    files = []
    for fname in sorted(os.listdir(UPLOAD_DIR), reverse=True):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                "name": fname,
                "size": stat.st_size,
                "uploaded": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    return jsonify({"files": files[:50]})  # Max 50 derniers


@app.route("/api/delete/<filename>", methods=["DELETE"])
@check_auth
def delete_file(filename):
    if ".." in filename or "/" in filename or "\\" in filename:
        return "Interdit", 403
    fpath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(fpath):
        os.remove(fpath)
        return jsonify({"success": True})
    return jsonify({"error": "Fichier non trouve"}), 404


AUTO_DELETE_SECONDS = 300  # 5 minutes


def cleanup_old_files():
    """Supprime les fichiers de plus de 5 minutes."""
    while True:
        time.sleep(60)
        now = time.time()
        try:
            for fname in os.listdir(UPLOAD_DIR):
                fpath = os.path.join(UPLOAD_DIR, fname)
                if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > AUTO_DELETE_SECONDS:
                    os.remove(fpath)
        except Exception:
            pass


cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
