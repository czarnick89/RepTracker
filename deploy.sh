#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/home/deploy/RepTracker
cd $APP_DIR

echo "[1/4] Pulling latest code..."
git fetch --all
git checkout main
git pull --ff-only

echo "[2/4] Backend setup..."
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
deactivate

echo "[3/4] Frontend build..."
cd "$APP_DIR/frontend"
npm ci
npm run build

echo "[4/4] Restarting services..."
sudo systemctl restart reptracker-gunicorn
sudo systemctl reload nginx

echo "✅ Deploy complete."