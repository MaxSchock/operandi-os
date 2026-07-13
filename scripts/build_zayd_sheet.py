"""Build the recruitment-leads Google Sheet in Zayd's Drive folder (OAuth
operandi-tools, Sheets API v4). Reads the merged leads json."""
import json
import urllib.request

AT = open("/tmp/gtok").read().strip()
FOLDER = "11Dte10TncKxFrdX0q5uTz3OpLmniMEdE"  # "Zayd Shah"
LEADS = "/home/max/iamasters-os/scripts/zayd_leads.json"
TITLE = "Zayd - Recruitment Leads London UK (100) - 2026-07-02"

H = {"Authorization": f"Bearer {AT}", "Content-Type": "application/json"}


def post(url, body, method="POST"):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=H, method=method)
    return json.load(urllib.request.urlopen(req))


leads = json.load(open(LEADS))
leads.sort(key=lambda l: ((l.get("company") or "").lower(), (l.get("full_name") or "").lower()))

header = ["#", "Full name", "Job title", "Company", "Employees", "Industry",
          "Email", "Email status", "Mobile", "DNC", "Company phone",
          "LinkedIn", "City", "Company website"]
rows = [header]
for i, l in enumerate(leads, 1):
    hq = l.get("company_phone") or ""
    if not hq and l.get("phones"):
        hq = l["phones"][0].get("number", "")
    rows.append([
        i,
        l.get("full_name") or "",
        l.get("title") or "",
        l.get("company") or "",
        l.get("company_size") or "",
        l.get("company_industry") or "",
        l.get("email") or "",
        l.get("email_status") or "",
        l.get("mobile_phone") or "",
        "DNC" if l.get("mobile_dnc") else "",
        hq,
        l.get("linkedin_url") or "",
        l.get("city") or "",
        l.get("company_website") or "",
    ])

# create spreadsheet
ss = post("https://sheets.googleapis.com/v4/spreadsheets",
          {"properties": {"title": TITLE},
           "sheets": [{"properties": {"title": "Leads", "gridProperties": {"frozenRowCount": 1}}}]})
sid = ss["spreadsheetId"]
sheet_id = ss["sheets"][0]["properties"]["sheetId"]

# write values
post(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/Leads!A1?valueInputOption=RAW",
     {"values": rows}, method="PUT")

# bold header + autoresize
post(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}:batchUpdate", {"requests": [
    {"repeatCell": {"range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True},
                             "backgroundColor": {"red": 0.11, "green": 0.41, "blue": 0.98}}},
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
    {"repeatCell": {"range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {"userEnteredFormat": {"textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}}},
                    "fields": "userEnteredFormat.textFormat"}},
    {"autoResizeDimensions": {"dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": len(header)}}},
]})

# move to Zayd folder
meta = json.load(urllib.request.urlopen(urllib.request.Request(
    f"https://www.googleapis.com/drive/v3/files/{sid}?fields=parents&supportsAllDrives=true", headers=H)))
prev = ",".join(meta.get("parents", []))
urllib.request.urlopen(urllib.request.Request(
    f"https://www.googleapis.com/drive/v3/files/{sid}?addParents={FOLDER}&removeParents={prev}&supportsAllDrives=true",
    data=b"{}", headers=H, method="PATCH"))

print("SHEET_URL=https://docs.google.com/spreadsheets/d/" + sid)
print("rows_written=" + str(len(rows) - 1))
