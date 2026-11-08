#!/bin/zsh
# Lädt die Tages-MP3s (audio/<datum>/*.mp3) ins eigene Cloudflare-Pages-Projekt „nekos-news-audio“ (Direkt-Upload, kostenlos, kein git).
# Grund (2026-11-08): MP3s in git ließen das Repo um ~1 GB pro Monat wachsen. Die Seite holt sie über functions/audio/[[pfad]].js,
# die Pfade /audio/<datum>/<id>.mp3 bleiben gleich. Hochgeladen wird immer der aktuelle Stand: was lokal gelöscht ist (älter als 7 Tage), ist danach auch dort weg.
set -e
REPO=/Users/nicolasumbach/Morgenzeitung
ZIEL=/Users/nicolasumbach/NekoTools/audio_upload
mkdir -p "$ZIEL/audio"
rsync -a --delete --include='*/' --include='*.mp3' --exclude='*' --prune-empty-dirs "$REPO/audio/20"*(/) "$ZIEL/audio/"
# Ohne 404.html würde Pages bei fehlenden Dateien die Startseite schicken
echo '<!doctype html><title>404</title>' > "$ZIEL/404.html"
cd "$ZIEL"
npx --yes wrangler pages deploy "$ZIEL" --project-name nekos-news-audio --branch main --commit-dirty=true
