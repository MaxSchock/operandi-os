#!/usr/bin/env bash
# =============================================================
# Smoke test E2E — Outreach v2
#
# Validates the pipeline from a synthetic lead through to a
# completed action callback. Run AFTER the strategist is deployed
# with the outreach/ module and webhook Unipile is configured.
#
# Steps:
#   1. Verify Supabase reachable + outreach schema present
#   2. Insert a synthetic lead under client_slug='samourai'
#      (only if --apply, otherwise dry-run)
#   3. Optionally trigger the decisor tick via /trigger/outreach-tick
#   4. Show recent lead_actions for the test lead
#   5. Cleanup on --rollback
#
# Usage:
#   bash scripts/smoke-outreach-v2.sh [--apply] [--rollback]
# =============================================================
set -euo pipefail

CLIENT_SLUG="samourai"
TEST_PROVIDER_ID="smoke-test-$(date +%s)"
TEST_NAME="Smoke Test Lead"

SUPABASE_URL="${SUPABASE_URL:-https://xepotlbqlwmriwievyvc.supabase.co}"
SERVICE_KEY="${SUPABASE_SERVICE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-}}"
STRATEGIST_URL="${STRATEGIST_URL:-https://sswebhook.figura-studio.com/strategist}"
WEBHOOK_TOKEN="${WEBHOOK_TOKEN:-}"

if [[ -z "$SERVICE_KEY" ]]; then
  echo "ERROR: set SUPABASE_SERVICE_KEY (or _ROLE_KEY) before running."
  echo "Use the value from operandi-services/services/strategist/.env"
  exit 2
fi

APPLY=0
ROLLBACK=0
for arg in "$@"; do
  case "$arg" in
    --apply)    APPLY=1 ;;
    --rollback) ROLLBACK=1 ;;
    *) echo "unknown arg: $arg"; exit 2 ;;
  esac
done

hdr=(
  -H "apikey: $SERVICE_KEY"
  -H "Authorization: Bearer $SERVICE_KEY"
  -H "Content-Type: application/json"
  -H "Accept-Profile: outreach"
  -H "Content-Profile: outreach"
)

echo "================================================================"
echo "Outreach v2 smoke test — client=$CLIENT_SLUG  apply=$APPLY  rollback=$ROLLBACK"
echo "================================================================"

# 1. Sanity check schema
echo
echo "[1/5] schema sanity"
curl -s "${SUPABASE_URL}/rest/v1/lead_state?limit=1&select=lead_id" "${hdr[@]}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('  lead_state reachable:', isinstance(d, list))"

# 2. Insert / find synthetic lead
echo
echo "[2/5] synthetic lead (provider_id=$TEST_PROVIDER_ID)"
if [[ $APPLY -eq 1 ]]; then
  RESP=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/leads" "${hdr[@]}" \
    -H "Prefer: return=representation" \
    -d "{
      \"client_slug\": \"$CLIENT_SLUG\",
      \"unipile_provider_id\": \"$TEST_PROVIDER_ID\",
      \"full_name\": \"$TEST_NAME\",
      \"company\": \"SmokeCo\",
      \"headline\": \"Office Manager (synthetic)\",
      \"source\": \"smoke_test\"
    }")
  LEAD_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
  echo "  inserted lead_id=$LEAD_ID"

  curl -s -X POST "${SUPABASE_URL}/rest/v1/lead_state" "${hdr[@]}" \
    -d "[{
      \"lead_id\": $LEAD_ID,
      \"client_slug\": \"$CLIENT_SLUG\",
      \"current_stage\": \"pre_contact\"
    }]" > /dev/null
  echo "  seeded lead_state stage=pre_contact"
else
  echo "  (dry-run — pass --apply to insert)"
fi

# 3. Trigger decisor tick
echo
echo "[3/5] decisor tick"
if [[ $APPLY -eq 1 && -n "$WEBHOOK_TOKEN" ]]; then
  curl -s -X POST "${STRATEGIST_URL}/trigger/outreach-tick" \
    -H "x-webhook-token: $WEBHOOK_TOKEN" | python3 -c "import sys,json; print('  triggered:', json.load(sys.stdin))"
  sleep 3
else
  echo "  (set WEBHOOK_TOKEN to trigger, or wait for the 15-min scheduler)"
fi

# 4. Inspect lead_actions for samourai
echo
echo "[4/5] recent lead_actions for samourai (last 10)"
curl -s "${SUPABASE_URL}/rest/v1/lead_actions?client_slug=eq.${CLIENT_SLUG}&order=created_at.desc&limit=10&select=id,action_type,status,policy_reason,created_at" "${hdr[@]}" \
  | python3 -m json.tool

# 5. Optional rollback of the synthetic lead
echo
echo "[5/5] rollback"
if [[ $ROLLBACK -eq 1 ]]; then
  curl -s -X DELETE "${SUPABASE_URL}/rest/v1/leads?unipile_provider_id=like.smoke-test-*" "${hdr[@]}" \
    -H "Prefer: return=representation" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('  deleted leads:', len(d) if isinstance(d, list) else d)"
else
  echo "  (skipped — pass --rollback to remove synthetic leads)"
fi

echo
echo "done."
