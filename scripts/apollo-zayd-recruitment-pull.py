"""One-off Apollo pull: recruitment-agency decision makers in London, UK.

Standalone (NOT the outreach topup pipeline). Search -> bulk_match reveal of
email + phone. Writes full records to OUT_PATH as JSON; prints only aggregate
stats + a redacted sample so no PII lands in stdout/chat.

Run inside the strategist container (APOLLO_API_KEY is in its env):
    python apollo-zayd-recruitment-pull.py test    # 1 page, reveal 10
    python apollo-zayd-recruitment-pull.py full     # full run to TARGET
"""
import json
import os
import sys
import time

import httpx

API_KEY = os.environ["APOLLO_API_KEY"]
BASE = "https://api.apollo.io/api/v1"
OUT_PATH = "/tmp/zayd_recruitment_leads.json"
RAW_PATH = "/tmp/zayd_recruitment_raw.json"
TARGET = 100
BUFFER = 130  # reveal a few extra to absorb rows with no email

TITLES = [
    "Founder", "Co-Founder", "Owner", "CEO",
    "Managing Director", "Director", "Managing Partner",
]
LOCATIONS = ["London, England, United Kingdom"]
# Apollo canonical industry tag id for "Staffing & Recruiting" (precise filter;
# the name-based organization_industries filter leaks adjacent industries).
RECRUITING_TAG = "5567e09973696410db020800"
ALLOWED_INDUSTRIES = {"staffing & recruiting", "human resources"}

HEADERS = {
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY,
}


def search_page(client, page, per_page=100):
    body = {
        "person_titles": TITLES,
        "person_locations": LOCATIONS,
        "organization_industry_tag_ids": [RECRUITING_TAG],
        "page": page,
        "per_page": per_page,
    }
    r = client.post(f"{BASE}/mixed_people/api_search", json=body)
    r.raise_for_status()
    return r.json()


PHONE_WEBHOOK = os.environ.get("APOLLO_PHONE_WEBHOOK", "")


def bulk_match(client, ids, reveal_phone=False):
    params = {"reveal_personal_emails": "true"}
    if reveal_phone and PHONE_WEBHOOK:
        params["reveal_phone_number"] = "true"
        params["webhook_url"] = PHONE_WEBHOOK
    r = client.post(
        f"{BASE}/people/bulk_match",
        params=params,
        json={"details": [{"id": i} for i in ids[:10]]},
    )
    r.raise_for_status()
    return r.json()


def extract_phones(p):
    out = []
    for ph in (p.get("phone_numbers") or []):
        if isinstance(ph, dict):
            num = ph.get("sanitized_number") or ph.get("raw_number")
            typ = ph.get("type") or ph.get("type_cd") or ""
            if num:
                out.append({"number": num, "type": typ, "status": ph.get("status")})
        elif ph:
            out.append({"number": str(ph), "type": "", "status": ""})
    org = p.get("organization") or {}
    if not out and org.get("sanitized_phone"):
        out.append({"number": org["sanitized_phone"], "type": "hq", "status": ""})
    return out


def flatten(p):
    org = p.get("organization") or {}
    return {
        "apollo_id": p.get("id"),
        "full_name": p.get("name") or f"{p.get('first_name','')} {p.get('last_name','')}".strip(),
        "first_name": p.get("first_name"),
        "last_name": p.get("last_name"),
        "title": p.get("title"),
        "seniority": p.get("seniority"),
        "email": p.get("email"),
        "email_status": p.get("email_status"),
        "phones": extract_phones(p),
        "linkedin_url": p.get("linkedin_url"),
        "city": p.get("city"),
        "state": p.get("state"),
        "country": p.get("country"),
        "company": org.get("name"),
        "company_industry": org.get("industry"),
        "company_size": org.get("estimated_num_employees"),
        "company_website": org.get("website_url"),
        "company_linkedin": org.get("linkedin_url"),
        "company_phone": org.get("sanitized_phone") or org.get("phone"),
    }


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"

    # ---- phone-only mode: reuse the already-revealed 100 ids, trigger the
    # async phone reveal (Apollo POSTs numbers to APOLLO_PHONE_WEBHOOK). ----
    if mode == "phone":
        with open(OUT_PATH, "r", encoding="utf-8") as fh:
            leads = json.load(fh)
        # only reveal leads that don't already have a mobile (no re-charge)
        ids = [l["apollo_id"] for l in leads if l.get("apollo_id") and not l.get("mobile_phone")]
        if not PHONE_WEBHOOK:
            print("ERROR: APOLLO_PHONE_WEBHOOK not set")
            return
        sent = 0
        with httpx.Client(headers=HEADERS, timeout=60.0) as client:
            for i in range(0, len(ids), 10):
                try:
                    bulk_match(client, ids[i:i + 10], reveal_phone=True)
                    sent += len(ids[i:i + 10])
                except httpx.HTTPStatusError as e:
                    print(f"phone bulk_match HTTP {e.response.status_code}: {e.response.text[:200]}")
                time.sleep(0.5)
        print(f"phone_reveal_requested={sent} webhook={PHONE_WEBHOOK}")
        return

    # ---- topup mode: reveal only NEW candidates until OUT_PATH has TARGET
    # on-target rows. Skips ids already in RAW_PATH (no re-charge). ----
    if mode == "topup":
        with open(OUT_PATH, "r", encoding="utf-8") as fh:
            leads = json.load(fh)
        try:
            with open(RAW_PATH, "r", encoding="utf-8") as fh:
                prev_raw = json.load(fh)
        except FileNotFoundError:
            prev_raw = []
        seen = {r.get("apollo_id") for r in prev_raw} | {l.get("apollo_id") for l in leads}
        need = TARGET - len(leads)
        print(f"topup: have={len(leads)} need={need} already_revealed={len(seen)}")
        if need <= 0:
            print("topup: nothing to do")
            return
        new_rows = []
        credits = 0.0
        with httpx.Client(headers=HEADERS, timeout=60.0) as client:
            page = 1
            new_ids = []
            while len(new_ids) < max(need * 3, 15) and page <= 200:
                stubs = search_page(client, page).get("people", [])
                if not stubs and page > 40:
                    break
                for s in stubs:
                    if s.get("id") and s.get("has_email") and s["id"] not in seen:
                        new_ids.append(s["id"])
                        seen.add(s["id"])
                page += 1
                time.sleep(0.4)
            for i in range(0, len(new_ids), 10):
                try:
                    m = bulk_match(client, new_ids[i:i + 10])
                except httpx.HTTPStatusError as e:
                    print(f"topup bulk_match HTTP {e.response.status_code}")
                    continue
                credits += float(m.get("credits_consumed") or 0)
                new_rows.extend(flatten(x) for x in (m.get("matches") or []) if x)
                if sum(1 for r in new_rows if r["email"] and (r["company_industry"] or "").lower() in ALLOWED_INDUSTRIES) >= need + 3:
                    break
                time.sleep(0.5)
        on = [r for r in new_rows if r["email"] and (r["company_industry"] or "").lower() in ALLOWED_INDUSTRIES]
        leads.extend(on)
        leads = leads[:TARGET]
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(leads, fh, ensure_ascii=False, indent=2)
        with open(RAW_PATH, "w", encoding="utf-8") as fh:
            json.dump(prev_raw + new_rows, fh, ensure_ascii=False, indent=2)
        print(f"topup: new_on_target={len(on)} total_now={len(leads)} credits={credits:.0f}")
        return

    limit_ids = 10 if mode == "test" else BUFFER
    reveal_phone = mode == "full"
    with httpx.Client(headers=HEADERS, timeout=60.0) as client:
        # ---- collect candidate ids ----
        first = search_page(client, 1)
        pag = first.get("pagination", {})
        total = pag.get("total_entries")
        total_pages = pag.get("total_pages")
        def keep(s):
            # only reveal stubs that actually carry an email (saves credits)
            return s.get("id") and s.get("has_email")

        stubs = [s for s in first.get("people", []) if keep(s)]
        page = 2
        while len(stubs) < limit_ids and mode != "test":
            nxt = [s for s in search_page(client, page).get("people", []) if keep(s)]
            if not nxt and page > 40:
                break
            stubs.extend(nxt)
            page += 1
            if page > 200:
                break
            time.sleep(0.4)
        # remember has_direct_phone per id for reporting
        direct_phone_ids = {s["id"] for s in stubs if s.get("has_direct_phone")}
        ids = [s["id"] for s in stubs][:limit_ids]

        # ---- reveal ----
        revealed = []
        credits = 0.0
        for i in range(0, len(ids), 10):
            chunk = ids[i:i + 10]
            try:
                m = bulk_match(client, chunk, reveal_phone=reveal_phone)
            except httpx.HTTPStatusError as e:
                print(f"bulk_match HTTP {e.response.status_code}: {e.response.text[:200]}")
                continue
            credits += float(m.get("credits_consumed") or 0)
            revealed.extend([x for x in (m.get("matches") or []) if x])
            time.sleep(0.5)

    all_rows = [flatten(p) for p in revealed]
    # NEVER discard paid-for reveals: dump raw first.
    with open(RAW_PATH, "w", encoding="utf-8") as fh:
        json.dump(all_rows, fh, ensure_ascii=False, indent=2)
    # industry distribution across everything revealed (transparency)
    from collections import Counter
    dist = Counter((r["company_industry"] or "unknown").lower() for r in all_rows)
    # search is already locked to the recruiting tag id; only drop CLEARLY
    # off-target rows (industry present AND not recruiting-adjacent). Keep unknowns.
    def on_target(r):
        ind = (r["company_industry"] or "").lower()
        return (ind == "") or (ind in ALLOWED_INDUSTRIES)
    rows = [r for r in all_rows if r["email"] and on_target(r)]
    if mode != "test":
        rows = rows[:TARGET]
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)

    print(f"industry_dist={dict(dist)}")
    with_email = sum(1 for r in rows if r["email"])
    with_phone = sum(1 for r in rows if r["phones"])
    verified = sum(1 for r in rows if (r["email_status"] or "").lower() in ("verified", "valid"))
    print(f"MODE={mode}")
    print(f"search_total_entries={total} total_pages={total_pages}")
    print(f"candidate_ids={len(ids)} revealed={len(rows)} credits_consumed={credits:.0f}")
    print(f"with_email={with_email} verified_email={verified} with_phone={with_phone}")
    print(f"industries_seen={sorted(set((r['company_industry'] or '?') for r in rows))}")
    # redacted sample: structure only, mask email/phone
    if rows:
        s = dict(rows[0])
        s["email"] = "***@" + (s["email"].split("@")[-1] if s["email"] else "none")
        s["phones"] = [{"type": p["type"], "status": p["status"], "len": len(p["number"])} for p in s["phones"]]
        print("SAMPLE=" + json.dumps(s, ensure_ascii=False))
    print(f"written={OUT_PATH}")


if __name__ == "__main__":
    main()
