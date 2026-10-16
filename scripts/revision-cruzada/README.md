# pasar.py

Manda el código de un repo, trozo a trozo, a un modelo de OpenRouter con los 15 puntos del apartado D de `docs/revision-cruzada/patrones-de-error-2026-10-14.md`, y guarda lo que señala.

## Uso

```bash
# 1. Siempre primero en seco: trozos, tokens y coste estimado, sin llamar al modelo
python3 scripts/revision-cruzada/pasar.py <carpeta> --ext .ts,.tsx --nombre <repo> --tope 3 --seco

# 2. Pase real (solo con el filtro de proveedores sin registro de datos activo en OpenRouter)
python3 scripts/revision-cruzada/pasar.py <carpeta> --ext .ts,.tsx --nombre <repo> --tope 3

# 3. Si paró por el tope o se cortó: sigue donde lo dejó
python3 scripts/revision-cruzada/pasar.py <carpeta> --ext .ts,.tsx --nombre <repo> --tope 5 --reanudar [--fecha AAAA-MM-DD]
```

Modelo por defecto `deepseek/deepseek-v3.2`; otro con `--modelo`. Excluir rutas: `--excluir 'test/*'` (repetible). Si OpenRouter no da precio: `--tarifa-entrada 0.3 --tarifa-salida 1` ($/M tokens) y el coste sale marcado como estimado.

Tests: `python3 -m unittest scripts/revision-cruzada/test_pasar.py`

## Qué produce

En `docs/revision-cruzada/<repo>/<fecha>/`:

- `hallazgos.jsonl`: una línea por hallazgo (`punto, fichero, linea, resumen, escenario_de_fallo, confianza`, modelo y `trozo` con id, líneas, imports adjuntos y commit).
- `descartados.jsonl`: hallazgos tirados por el corredor (su `linea_prueba` no está en el trozo, o pasaban de 3 por trozo), con el motivo en `descartado`.
- `fallos.jsonl`: trozos cuya respuesta no fue JSON válido tras un reintento, o con error de red.
- `coste.txt`: tokens y dólares por fichero y total; si paró, dónde y por qué.
- `estado.json`: trozos hechos, gasto y commit; es lo que lee `--reanudar`.
- `seco.txt`: solo en `--seco`.

## Comportamiento que conviene saber

- Argumento desconocido o abreviado: sale con código 2 sin tocar nada.
- Clave: `OPENROUTER_API_KEY` o `~/.config/openrouter/api.key`. Sin clave, o sin precio, no llama.
- Cada petición lleva `provider.data_collection: "deny"`: si ningún proveedor del modelo cumple, falla en vez de usar uno que guarde datos.
- El tope se comprueba antes de cada llamada con el peor caso (dos intentos con la salida máxima); para antes de pasarlo.
- Un trozo se marca hecho después de escribir sus hallazgos; al reanudar se borran los hallazgos de trozos sin marcar y se repiten.
- Ficheros de más de 60 KB se parten por funciones y clases de nivel superior; cada parte lleva los imports del fichero y 15 líneas previas como contexto.
- Tokens en seco: estimados por caracteres (3,5 por token). El coste real sale de `usage.cost` de OpenRouter.
- Códigos de salida: 0 hecho, 2 argumentos, 3 falta algo (clave, precio, ficheros, pase ya existente), 4 OpenRouter rechaza la clave o el saldo, 5 parado por el tope.

# comprobar.py

Comprobaciones deterministas (sin modelo, sin red) de los puntos del apartado D que se pueden expresar como búsqueda o análisis de sintaxis: p03 parcial, p04, p06, p07, p10, p11, p12, p14 parcial y p15 parcial (solo «revisar»). Lo demás va a un agente Opus sobre paquete y punto concretos (lista en `docs/revision-cruzada/comprobaciones-deterministas-2026-10-15.md`).

## Uso

```bash
# Rama o commit concreto, leído con git archive (no toca rama ni ficheros del repo)
python3 scripts/revision-cruzada/comprobar.py ~/max-assistent --ref main --nombre linus

# Carpeta tal cual (sin git o para ver lo no comprometido)
python3 scripts/revision-cruzada/comprobar.py clients/falkenlead/google-ads/tojo-store --nombre tojo-store

# Solo algunos puntos, solo una subcarpeta, sin escribir nada
python3 scripts/revision-cruzada/comprobar.py ~/src/operandi-services --ref main --puntos 4,11 --sub services/strategist --seco
```

Salida en `docs/revision-cruzada/<nombre>/<fecha>/`: `comprobaciones.jsonl` (una línea por hallazgo: `punto, comprobacion, fichero, linea, fragmento, regla, gravedad`) y `comprobaciones-resumen.json` (commit, ficheros, recuento por punto y gravedad). Gravedad: `alta`, `media`, `baja`, `revisar` (p15 nunca dictamina).

Tests: `python3 -m unittest scripts/revision-cruzada/test_comprobar.py`

## Exclusiones

- Siempre fuera: `node_modules`, `.git`, `dist`, `build`, `.next`, `vendor`, `coverage`, `__pycache__`, `.venv`, `*.min.js`, `*.d.ts`, ficheros de más de 1,5 MB.
- Los tests (`tests/`, `__tests__/`, `test_*.py`, `*.test.ts`, `fixtures`, `bench/`...) no cuentan para p07, p11, p12 y p15; p04 y p10 los bajan a `baja`; p14 solo mira tests.
- `comprobar.ignore` en la raíz del repo: un patrón por línea, con puntos opcionales (`legacy/*` o `scripts/* p07,p12`). Con `--ref` se usa el de la copia de trabajo si el commit no lo trae.
- En una línea concreta: comentario `comprobar: ignore` (todos los puntos) o `comprobar: ignore p04`.
- Las credenciales nunca salen en el fragmento: se escribe «valor omitido».
