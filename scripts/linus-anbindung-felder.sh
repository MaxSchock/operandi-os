#!/usr/bin/env bash
# Inspecciona un fichero de declaración de conector de Linus SIN volcar secretos.
# Uso: linus-anbindung-felder.sh <servidor|local> <ruta.json> [--feld <nombre>]
# Sin --feld: por entrada, la lista ordenada de nombres de campo (y el tipo de cada uno).
# Con --feld: el valor de UN campo de la lista blanca (nunca erneuerung, apiKey, clientSecret, refreshToken, webhookGeheimnis, auth).
set -euo pipefail
SRV="${1:?servidor o 'local'}"; F="${2:?ruta.json}"; FELD="${4:-}"; [ "${3:-}" = "--feld" ] || FELD=""
PY=$(cat <<'PYEOF'
import json,sys
ruta=sys.argv[1]; feld=sys.argv[2] if len(sys.argv)>2 else ""
BLANCA={"connectorId","email","address","displayName","nummer","eigeneNummer","ordner","schreibOrdner","kalenderId","zeitzone","vonStunde","bisStunde","umfang","standard","basisUrl","webhookPfad","agentId","accountId","nummernkreis","firma","umfang.ordner","umfang.abDatum","imap.host","imap.port","smtp.host","smtp.port","versand.host","versand.port","basisUrl","server","caldav","carddav","tenant","tenantId"}
try:
    raw=open(ruta).read()
except FileNotFoundError:
    print("(no existe)"); sys.exit(0)
if not raw.strip():
    print("(vacío)"); sys.exit(0)
d=json.loads(raw); d=d if isinstance(d,list) else [d]
for i,e in enumerate(d):
    if not isinstance(e,dict): print(i, type(e).__name__); continue
    if feld:
        if feld.split(".")[0] not in BLANCA and feld not in BLANCA: print(f"{feld}: campo fuera de la lista blanca"); continue
        v=e
        for teil in feld.split("."):
            v=v.get(teil) if isinstance(v,dict) else None
        print(i, feld+":", json.dumps(v, ensure_ascii=False) if not isinstance(v,dict) else sorted(v.keys()))
    else:
        print(i, ", ".join(f"{k}:{'dict['+','.join(sorted(v.keys()))+']' if isinstance(v,dict) else type(v).__name__}" for k,v in sorted(e.items())))
PYEOF
)
if [ "$SRV" = "local" ]; then python3 -c "$PY" "$F" "$FELD"; else ssh "$SRV" "python3 -c \"\$(cat <<'X'
$PY
X
)\" '$F' '$FELD'"; fi
