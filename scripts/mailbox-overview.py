#!/usr/bin/env python3
"""Sent + draft overview across every mailbox Max operates.

Used by the /start-here ritual so the session starts with the real state of the
mailbox, not just the inbox: what already went out and what is sitting half
finished. Read-only, metadata only (never marks as read, never sends).

Covered here:
  - operandi      Gmail API, OAuth ~/.config/gcp/token-operandi.json
  - kisult        Gmail API, OAuth ~/.config/gcp/accounts/kisult.json
  - falkenlead-max / falkenlead-admin   IMAP imap.buzondecorreo.com

NOT covered here (do it from the ritual, not this script):
  - personal maximilian.schock@gmail.com -> OAuth revoked. Use the MCP Gmail
    tools (list_drafts, search_threads with "in:sent newer_than:3d") or Unipile.

Usage:
    python3 scripts/mailbox-overview.py [--days N] [--account NAME ...]
"""
import argparse
import datetime
import email
import email.header
import imaplib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

GMAIL_ACCOUNTS = {
    "operandi": "/home/max/.config/gcp/token-operandi.json",
    "kisult": "/home/max/.config/gcp/accounts/kisult.json",
}
IMAP_ACCOUNTS = {
    "falkenlead-max": ("max@falkenlead.com", "/home/max/.config/falkenlead/max.pass"),
    "falkenlead-admin": ("administracion@falkenlead.com",
                         "/home/max/.config/falkenlead/administracion.pass"),
}
IMAP_HOST = "imap.buzondecorreo.com"
API = "https://gmail.googleapis.com/gmail/v1/users/me/"
MAX_ITEMS = 25


def line(when, subject, to):
    print("    %s  %s" % (when, subject))
    print("             -> %s" % to)


# --- Gmail (OAuth) ----------------------------------------------------------

def access_token(cfg_path):
    c = json.load(open(cfg_path))
    body = urllib.parse.urlencode({
        "client_id": c["client_id"],
        "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    uri = c.get("token_uri", "https://oauth2.googleapis.com/token")
    return json.load(urllib.request.urlopen(
        urllib.request.Request(uri, data=body)))["access_token"]


def api(token, path, params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    return json.load(urllib.request.urlopen(req))


def gmail_report(name, cfg_path, days):
    try:
        token = access_token(cfg_path)
    except (urllib.error.HTTPError, OSError, KeyError) as exc:
        print("  token KO: %s" % exc)
        return
    for label, query in (("ENVIADOS", "in:sent newer_than:%dd" % days),
                         ("BORRADORES", "in:draft")):
        try:
            res = api(token, "messages", {"q": query, "maxResults": MAX_ITEMS})
        except urllib.error.HTTPError as exc:
            print("  %s: KO (%s)" % (label, exc))
            continue
        msgs = res.get("messages", [])
        print("\n  %s (%d)" % (label, len(msgs)))
        if not msgs:
            print("    -")
        for m in msgs:
            d = api(token, "messages/" + m["id"], {"format": "metadata"})
            h = {x["name"].lower(): x["value"] for x in d["payload"].get("headers", [])}
            when = datetime.datetime.fromtimestamp(int(d["internalDate"]) / 1000)
            line(when.strftime("%d-%m %H:%M"),
                 h.get("subject", "(sin asunto)"),
                 h.get("to", "(sin destinatario)"))
            if label == "BORRADORES":
                print("             %s" % d.get("snippet", "")[:120])


# --- IMAP -------------------------------------------------------------------

def decode(raw):
    if not raw:
        return "(vacio)"
    out = []
    for part, enc in email.header.decode_header(raw):
        if isinstance(part, bytes):
            out.append(part.decode(enc or "utf-8", "replace"))
        else:
            out.append(part)
    return "".join(out)


def pick_folder(conn, wanted):
    """buzondecorreo names Sent/Drafts differently per account; probe them."""
    typ, boxes = conn.list()
    if typ != "OK":
        return None
    names = []
    for b in boxes:
        text = b.decode("utf-8", "replace")
        names.append(text.split(' "." ')[-1].strip('"') if ' "." ' in text
                     else text.split()[-1].strip('"'))
    for candidate in wanted:
        for n in names:
            if n.lower() == candidate.lower():
                return n
    for candidate in wanted:
        for n in names:
            if candidate.lower() in n.lower():
                return n
    return None


def imap_report(name, user, pass_path, days):
    try:
        password = open(pass_path).read().strip()
    except OSError as exc:
        print("  password KO: %s" % exc)
        return
    try:
        conn = imaplib.IMAP4_SSL(IMAP_HOST)
        conn.login(user, password)
    except (imaplib.IMAP4.error, OSError) as exc:
        print("  login KO: %s" % exc)
        return
    since = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%d-%b-%Y")
    targets = (("ENVIADOS", ["INBOX.Sent", "Sent", "Enviados", "Sent Items"],
                "(SINCE %s)" % since),
               ("BORRADORES", ["INBOX.Drafts", "Drafts", "Borradores"], "ALL"))
    try:
        for label, candidates, criteria in targets:
            folder = pick_folder(conn, candidates)
            if not folder:
                print("\n  %s: carpeta no encontrada" % label)
                continue
            typ, _ = conn.select('"%s"' % folder, readonly=True)
            if typ != "OK":
                print("\n  %s: no se pudo abrir %s" % (label, folder))
                continue
            typ, data = conn.search(None, criteria)
            ids = data[0].split() if typ == "OK" else []
            ids = ids[-MAX_ITEMS:]
            print("\n  %s (%d)  [%s]" % (label, len(ids), folder))
            if not ids:
                print("    -")
            for i in reversed(ids):
                typ, d = conn.fetch(i, "(BODY.PEEK[HEADER.FIELDS (DATE TO SUBJECT)])")
                if typ != "OK" or not d or not isinstance(d[0], tuple):
                    continue
                msg = email.message_from_bytes(d[0][1])
                when = "?"
                parsed = email.utils.parsedate_to_datetime(msg.get("Date", "")) \
                    if msg.get("Date") else None
                if parsed:
                    when = parsed.strftime("%d-%m %H:%M")
                line(when, decode(msg.get("Subject")), decode(msg.get("To")))
    finally:
        try:
            conn.logout()
        except Exception:
            pass


# --- main -------------------------------------------------------------------

def main():
    all_names = sorted(GMAIL_ACCOUNTS) + sorted(IMAP_ACCOUNTS)
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--account", nargs="*", choices=all_names)
    a = p.parse_args()
    for name in (a.account or all_names):
        print("=" * 72)
        print(name.upper())
        if name in GMAIL_ACCOUNTS:
            gmail_report(name, GMAIL_ACCOUNTS[name], a.days)
        else:
            user, pass_path = IMAP_ACCOUNTS[name]
            imap_report(name, user, pass_path, a.days)
    print("=" * 72)
    print("PERSONAL (maximilian.schock@gmail.com): OAuth revocado.")
    print("  Enviados/borradores -> MCP Gmail (list_drafts, search_threads")
    print("  'in:sent newer_than:%dd') o Unipile. Fuera de este script." % a.days)
    return 0


if __name__ == "__main__":
    sys.exit(main())
