#!/usr/bin/env bash
# Segunda opinión de otro proveedor sobre código que va a producción de un cliente.
#
# Nace del 31-08-2026: una pasada de Codex sobre el camino de envío de Linus sacó
# tres fallos reales, uno de ellos con "verificado antes de enviar" en el registro
# sin que la comprobación hubiera llegado a ejecutarse. Y sobre código escrito por
# Claude encontró lo que Claude había documentado como riesgo pero dejado sin
# arreglar. Ese es el valor: ve lo que da por sabido quien lo escribió.
#
#   revision-externa.sh <ruta> ["foco concreto"]
#
# Antes de mandar nada fuera avisa de lo que no debería salir: el código viaja a
# OpenAI, y en un proyecto de cliente eso incluye lo que lea de paso.
set -uo pipefail

CODEX="$HOME/.claude/tools/codex/node_modules/.bin/codex"
RUTA="${1:?uso: revision-externa.sh <ruta> [\"foco\"]}"
FOCO="${2:-}"

[ -x "$CODEX" ] || { echo "No está Codex en $CODEX"; exit 1; }
[ -d "$RUTA" ] || [ -f "$RUTA" ] || { echo "No existe: $RUTA"; exit 1; }

echo "== Lo que va a salir hacia OpenAI =="
echo "   ruta: $RUTA"
echo "   $(find "$RUTA" -type f -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l) ficheros"

# Lo que nunca debería viajar: credenciales y datos personales reales.
# las dependencias traen sus propios certificados y ejemplos: no son del proyecto
EXCLUIR='node_modules|\.venv|site-packages|\.git/|dist/|\.next/'
SECRETOS=$(find "$RUTA" \( -name '.env*' -o -name '*.pem' -o -name '*credentials*.json' \) 2>/dev/null \
           | grep -vE "$EXCLUIR" | head -5)
CORREOS=$(grep -rlE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "$RUTA" \
          --include='*.ts' --include='*.js' --include='*.py' --include='*.json' --include='*.md' 2>/dev/null \
          | grep -vE "$EXCLUIR" | head -5)

if [ -n "$SECRETOS" ]; then
  echo
  echo "PARA: hay ficheros de credenciales en el árbol:"
  echo "$SECRETOS" | sed 's/^/     /'
  echo "   Apunta a un subdirectorio de código o sácalos antes. No sigo."
  exit 2
fi
if [ -n "$CORREOS" ]; then
  echo
  echo "AVISO: estos ficheros llevan direcciones que no son de ejemplo:"
  echo "$CORREOS" | sed 's/^/     /'
  echo "   Si es código de cliente, trabaja sobre una copia con las direcciones"
  echo "   sustituidas. Sigue solo si sabes lo que hay dentro."
  read -r -p "   ¿Continuar igualmente? [s/N] " r
  [ "$r" = "s" ] || exit 3
fi

PROMPT="Busca UNICAMENTE fallos donde el codigo falle hacia el silencio: un catch que
se traga un error y devuelve vacio o cero, un camino donde no-hacer-algo y
hacerlo-pero-fallar acaban en el mismo estado, una verificacion previa que puede
saltarse sin dejar rastro, o un contador o estado que se marca como hecho antes de
que el proveedor confirme.

Para cada hallazgo: fichero, linea, y el escenario concreto en que el operador
creeria que todo fue bien cuando no fue. Maximo 6, ordenados por gravedad, en
espanol. Ignora estilo, tipos y preferencias de formato.${FOCO:+

Foco concreto de esta revision: $FOCO}"

SALIDA="${TMPDIR:-/tmp}/revision-$(date +%Y%m%d-%H%M).md"
echo
echo "== Revisando (esto tarda un par de minutos y consume API de Max) =="
# stdin cerrado a proposito: con stdin abierto, codex exec se queda esperando
# "additional input from stdin" y no termina nunca
( cd "$RUTA" && "$CODEX" exec --sandbox read-only --skip-git-repo-check "$PROMPT" </dev/null ) 2>&1 | tee "$SALIDA"
echo
echo "== Guardado en $SALIDA =="
echo "RECUERDA: verifica cada hallazgo en el codigo antes de darlo por bueno."
echo "En la primera pasada real, uno de los seis estaba mal encuadrado: marcaba como"
echo "critico un claim deliberado que sostenia el at-most-once."
