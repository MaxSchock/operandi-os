# Memory index

Indice local-first para recall de iAmasters OS.

- Base default: SQLite + FTS5 en `context/.memory-index/memory.db`.
- Sin servicios externos, cuentas, credenciales de BD ni descargas de modelos.
- Semantica opt-in: `sqlite-vec` + `intfloat/multilingual-e5-small` via `fastembed`.
- Auto-sync: un hook SessionStart re-indexa (incremental, best-effort) al abrir el repo; ademas `--query` re-indexa en cada consulta. No hace falta correr el ingest a mano.

## Instalar base

```bash
cd scripts/memory-index
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

La capa base solo necesita `pyyaml`; `sqlite3` viene en la stdlib de Python.

## Configura tu corpus

Copia `corpus.example.yaml` a `corpus.yaml` y ajusta las rutas a tus archivos. `corpus.yaml` es personal (gitignored); si no existe, se usa el ejemplo genérico.

## Ingest base

```bash
python ingest.py
```

## Consulta (recall)

```bash
python ingest.py --query "¿qué decidí sobre <tu tema>?"
```

Hace un ingest incremental y devuelve los 5 chunks más relevantes con su fuente y fecha. Es lo que usa la skill `/recuerda`.

## Ingest semantico opt-in

No ejecutar salvo que el usuario quiera activar busqueda semantica local y acepte instalar dependencias y descargar el modelo.

> ⚠️ Experimental: hoy `--semantic` **indexa** los embeddings, pero la busqueda (`--query` y la skill `/recuerda`) usa solo FTS5. La fusion hibrida FTS5 + vector (RRF) esta pendiente de cablear.

```bash
pip install sqlite-vec fastembed
python ingest.py --semantic
```
