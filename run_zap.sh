#!/usr/bin/env bash
set -euo pipefail


# Load secrets from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
# -------------------------
# CONFIG - edit these if necessary
# -------------------------
TARGET_URL="https://reptracker.duckdns.org/"
DOMAIN="reptracker.duckdns.org"
REPORT_DIR="./zap/wrk"
CONTAINER_NAME="zap_run_$(date +%s)"
CONTEXT_NAME="reptracker"
# -------------------------

mkdir -p "$REPORT_DIR"

# 1) Start ZAP daemon in Docker
docker run -d --name "$CONTAINER_NAME" -u zap \
  -v "$(pwd)/zap/wrk":/zap/wrk \
  -p 8090:8090 \
  zaproxy/zap-stable \
  zap.sh -daemon -host 0.0.0.0 -port 8090 \
  -config api.key="$ZAP_API_KEY" \
  -config api.addrs.addr.name=.* \
  -config api.addrs.addr.regex=true

echo "Waiting for ZAP API to be ready..."
for i in {1..60}; do
  STATUS=$(curl -s "http://127.0.0.1:8090/JSON/core/view/version/?apikey=$ZAP_API_KEY" || true)
  if [[ $STATUS == *"version"* ]]; then
    echo "ZAP API ready."
    break
  fi
  echo "Waiting... ($i)"
  sleep 2
done

# 2) Create a context and include target URL
curl -sS "http://127.0.0.1:8090/JSON/context/action/newContext/?contextName=$CONTEXT_NAME&apikey=$ZAP_API_KEY" >/dev/null
curl -sS "http://127.0.0.1:8090/JSON/context/action/includeInContext/?contextName=$CONTEXT_NAME&regex=${TARGET_URL}.*&apikey=$ZAP_API_KEY" >/dev/null

# 3) Add JWT token as HttpOnly session cookie in the context
ENCODED_TOKEN=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$ACCESS_TOKEN")
curl -sS "http://127.0.0.1:8090/JSON/session/action/addSessionCookie/?contextName=$CONTEXT_NAME&cookieName=access_token&cookieValue=${ENCODED_TOKEN}&domain=${DOMAIN}&path=/&httpOnly=true&secure=true&apikey=$ZAP_API_KEY" >/dev/null
echo "Cookie added to ZAP context $CONTEXT_NAME."

# 4) Traditional spider for main site
echo "Starting traditional spider for main site..."
SPIDER_ID=$(curl -s "http://127.0.0.1:8090/JSON/spider/action/scan/?contextName=$CONTEXT_NAME&url=${TARGET_URL}&recurse=true&apikey=$ZAP_API_KEY" | jq -r '.scan')

# Wait for spider to complete
echo "Waiting for spider to complete..."
while true; do
  STATUS=$(curl -s "http://127.0.0.1:8090/JSON/spider/view/status/?scanId=$SPIDER_ID&apikey=$ZAP_API_KEY" | jq -r '.status')
  echo "Spider progress: $STATUS%"
  if [[ "$STATUS" == "100" ]]; then
    break
  fi
  sleep 3
done

# Check URLs discovered
URL_COUNT=$(curl -s "http://127.0.0.1:8090/JSON/core/view/numberOfUrls/?apikey=$ZAP_API_KEY" | jq -r '.numberOfUrls')
echo "URLs discovered: $URL_COUNT"

# 4.5) Traditional spider for API endpoints
API_URL="${TARGET_URL}api/v1"
curl -s "http://127.0.0.1:8090/JSON/spider/action/scan/?contextName=$CONTEXT_NAME&url=${API_URL}&maxChildren=0&recurse=true&apikey=$ZAP_API_KEY" >/dev/null
echo "API endpoint spider scan completed."

# 5) Active scan the site (authenticated)
ASCAN_ID=$(curl -s "http://127.0.0.1:8090/JSON/ascan/action/scan/?contextName=$CONTEXT_NAME&url=${TARGET_URL}&recurse=true&apikey=$ZAP_API_KEY" | jq -r '.scan')
echo "Active scan started with ID $ASCAN_ID. Waiting for completion..."
while true; do
  PERCENT=$(curl -s "http://127.0.0.1:8090/JSON/ascan/view/status/?scanId=$ASCAN_ID&apikey=$ZAP_API_KEY" | jq -r '.status')
  echo "Active scan progress: $PERCENT%"
  if [[ "$PERCENT" == "100" ]]; then
    break
  fi
  sleep 5
done
echo "Active scan completed."

# 6) Generate HTML report
REPORT_PATH="/zap/wrk/baseline_report.html"
curl -s "http://127.0.0.1:8090/OTHER/core/other/htmlreport/?apikey=$ZAP_API_KEY" -o "$REPORT_DIR/baseline_report.html"
echo "Scan complete. Report at $REPORT_DIR/baseline_report.html"

# 7) Stop and remove container
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null
echo "ZAP container removed. Done."
