#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/home/deploy/RepTracker
cd $APP_DIR

echo "[1/4] Pulling latest code..."
git fetch --all
git checkout main
git reset --hard origin/main

echo "[2/4] Backend setup..."
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cd backend
# Drop conflicting constraint if it exists to allow migration to proceed
python manage.py shell -c "
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE IF EXISTS workouts_workouttemplate DROP CONSTRAINT IF EXISTS workouts_workouttemplate_user_id_2215190a_fk_users_user_id;')
    print('Dropped conflicting constraint if it existed')
except Exception as e:
    print(f'Error dropping constraint: {e}')
"
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