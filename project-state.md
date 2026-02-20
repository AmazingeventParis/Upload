# Upload Tool - Etat du Projet

## Vue d'ensemble
Outil web d'upload de fichiers pour code-server. Drag & drop, Ctrl+V paste, auto-suppression apres 5min.

- **URL** : https://upload.swipego.app
- **Coolify UUID** : `ccogocg0ckcos4kg4o0cg44k`
- **Repo** : https://github.com/AmazingeventParis/Upload
- **Status** : FONCTIONNEL, rien de critique

## Stack
- Python 3.11 + Flask 3.1.0
- Gunicorn (2 workers)
- Docker (python:3.11-slim)
- Frontend: HTML/CSS/JS vanilla (dark theme)

## Structure
```
Upload/
  app.py            - Backend Flask (upload, list, delete, download)
  requirements.txt  - Flask + Gunicorn
  Dockerfile        - Container config
  static/
    index.html      - SPA complete (upload + liste + auth)
```

## Fonctionnalites
- Upload drag & drop + clic
- Ctrl+V pour coller des screenshots
- Upload multiple avec progression
- Liste des 50 fichiers recents
- Suppression manuelle
- Auto-suppression apres 5 min (thread daemon, check toutes les 60s)
- Copier commande prete a l'emploi
- Auth par mot de passe (localStorage)
- Max 50 MB par fichier
- Sanitization noms + protection path traversal

## API
| Methode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| POST | /api/upload | X-Upload-Password | Upload fichier |
| GET | /api/files | X-Upload-Password | Lister fichiers |
| DELETE | /api/delete/<name> | X-Upload-Password | Supprimer fichier |
| GET | /dl/<name> | Non | Telecharger (public) |

## Env vars
- UPLOAD_DIR=/codeserver/projects/uploads
- UPLOAD_PASSWORD=Laurytal2

## Volume partage
Fichiers dans /codeserver/projects/uploads (monte dans Upload ET code-server)

## Deploy
```bash
git push origin main
curl -s -X GET "https://coolify.swipego.app/api/v1/deploy?uuid=ccogocg0ckcos4kg4o0cg44k&force=true" \
  -H "Authorization: Bearer 1|FNcssp3CipkrPNVSQyv3IboYwGsP8sjPskoBG3ux98e5a576"
```
