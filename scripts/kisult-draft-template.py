"""One-shot: crea el draft REAL a Mads (buzon kisult) con el snippet v4 del widget FRED.

Uso:
  python3 ~/.config/gcp/refresh-token.py kisult   # deja access token
  (guardar el access token en /tmp/kisult-at.txt)
  python3 scripts/kisult-draft-template.py
"""
import json, urllib.request, base64, html as H
from email.message import EmailMessage

at = open('/tmp/kisult-at.txt').read().strip()

SIG_PLAIN = ("-- \nBeste Grüße\n\nMaximilian Schock\nKI- & Automatisierungsexperte | KIsult\n\n"
             "max@kisult.com\n+34 636 11 01 88\nwww.kisult.com")
SIG_HTML = ('<pre class="moz-signature" cols="72">-- \nBeste Grüße\n\nMaximilian Schock\n'
            'KI- &amp; Automatisierungsexperte | KIsult\n\n'
            '<a class="moz-txt-link-abbreviated" href="mailto:max@kisult.com">max@kisult.com</a>\n'
            '+34 636 11 01 88\n'
            '<a class="moz-txt-link-abbreviated" href="http://www.kisult.com">www.kisult.com</a></pre>')

def to_html(body):
    paras = body.split('\n\n')
    parts = ['<p>' + H.escape(p).replace('\n', '<br>\n      ') + '</p>' for p in paras]
    return ('<!DOCTYPE html>\n<html>\n  <head>\n    <meta http-equiv="Content-Type" '
            'content="text/html; charset=UTF-8">\n  </head>\n  <body>\n    '
            + '\n    '.join(parts) + '\n    ' + SIG_HTML + '\n  </body>\n</html>\n')

def make_draft(to, cc, subject, body, attachments):
    msg = EmailMessage()
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
    msg['Subject'] = subject
    msg.set_content(body + '\n\n' + SIG_PLAIN)
    msg.add_alternative(to_html(body), subtype='html')
    for path, name, mt, st in attachments:
        msg.add_attachment(open(path, 'rb').read(), maintype=mt, subtype=st, filename=name)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    req = urllib.request.Request(
        'https://gmail.googleapis.com/gmail/v1/users/me/drafts',
        headers={'Authorization': 'Bearer ' + at, 'Content-Type': 'application/json'},
        data=json.dumps({'message': {'raw': raw}}).encode())
    return json.load(urllib.request.urlopen(req))['id']

BODY_MADS = """Hi Mads,

im Anhang der neue Einbau-Code für das FRED-Chatfenster auf suri-tec.de. Neu darin: das Kontaktfenster im Suritec-Design (öffnet sich beim Laden der Seite automatisch, einmal pro Besuch, X schließt), die Kanäle Chat und WhatsApp, und die größere Chat-Bubble (138 px, gleich groß wie eure Buttons links). Die inhaltlichen Verbesserungen sind serverseitig schon live; das Design hat Jo am 17.07. freigegeben.

Einbau: im Anhang ist alles zwischen den Markierungen "SURITEC FRED WIDGET v4 — START" und "SURITEC FRED WIDGET v4 — ENDE" gekennzeichnet (Styles + HTML + Script). Diesen Block 1:1 statt des bisherigen Widget-Blocks einfügen; der Rest der Datei ist nur unsere Testseite drumherum.

So sieht es aus: https://s3.kisult.com/suritec-fred-test/index.html

Es eilt nicht, nach deinem Urlaub reicht völlig."""

new_mads = make_draft('mads.gerke@suri-tec.de', None,
                      'Neuer Website-Code für das FRED-Chatfenster (Kontaktfenster + WhatsApp)',
                      BODY_MADS,
                      [('/home/max/iamasters-os/clients/kisult/clients/suritec/widget/snippet-v4-20260717.html',
                        'suritec-chat-einbau-v4.html', 'text', 'html')])
print('mads draft:', new_mads)
