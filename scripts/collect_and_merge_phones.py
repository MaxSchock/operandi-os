"""Collect Apollo async phone payloads from the n8n sink workflow executions
and merge the mobile numbers into the leads file. Prints only aggregate stats."""
import json
import urllib.request

WID = "igidvARgnMOdV5Dn"
BASE = open("/home/max/.config/n8n-cli/api-url").read().strip()
KEY = open("/home/max/.config/n8n-cli/api-key").read().strip()
LEADS = "/home/max/iamasters-os/scripts/zayd_leads.json"


def api(path):
    req = urllib.request.Request(BASE + path, headers={"X-N8N-API-KEY": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def best_phone(phone_numbers):
    """Prefer a valid mobile; fall back to any valid; then any."""
    mobiles = [p for p in phone_numbers if p.get("type_cd") == "mobile" and p.get("status_cd") == "valid_number"]
    valids = [p for p in phone_numbers if p.get("status_cd") == "valid_number"]
    pick = (mobiles or valids or phone_numbers or [None])[0]
    return pick


# gather all execution ids
ids = [e["id"] for e in api(f"/api/v1/executions?workflowId={WID}&limit=250").get("data", [])]
phone_map = {}
for eid in ids:
    d = api(f"/api/v1/executions/{eid}?includeData=true")
    try:
        body = d["data"]["resultData"]["runData"]["Webhook"][0]["data"]["main"][0][0]["json"]["body"]
    except (KeyError, IndexError, TypeError):
        continue
    if not isinstance(body, dict):
        continue
    for p in body.get("people", []) or []:
        pid = p.get("id")
        nums = p.get("phone_numbers") or []
        if pid and nums:
            pick = best_phone(nums)
            if pick and pid not in phone_map:
                phone_map[pid] = {
                    "number": pick.get("sanitized_number") or pick.get("raw_number"),
                    "type": pick.get("type_cd"),
                    "status": pick.get("status_cd"),
                    "dnc": pick.get("dnc_status_cd"),
                }

leads = json.load(open(LEADS))
merged_mobile = 0
for l in leads:
    m = phone_map.get(l.get("apollo_id"))
    if m:
        l["mobile_phone"] = m["number"]
        l["mobile_type"] = m["type"]
        l["mobile_dnc"] = m["dnc"]
        merged_mobile += 1
    else:
        l["mobile_phone"] = ""
        l["mobile_type"] = ""
        l["mobile_dnc"] = ""

json.dump(leads, open(LEADS, "w"), ensure_ascii=False, indent=2)
hq = sum(1 for l in leads if l.get("phones"))
mob = sum(1 for l in leads if l.get("mobile_phone"))
any_phone = sum(1 for l in leads if l.get("mobile_phone") or l.get("phones") or l.get("company_phone"))
print(f"executions_scanned={len(ids)} phone_map={len(phone_map)}")
print(f"leads={len(leads)} with_mobile={mob} with_hq_phone={hq} with_any_phone={any_phone}")
print(f"emails_verified={sum(1 for l in leads if (l.get('email_status') or '')=='verified')}")
