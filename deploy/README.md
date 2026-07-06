# Project Hivemind — Deploy runbook (ki-prod-01)

Decisión 2026-07-06: los items DSGVO son best-effort, NO gates (ver
`docs/compliance/README.md`). Estos pasos son **Tier 3** (infra de producción):
los corre Max o un técnico, no se automatizan.

Clientes KIsult reales (confirmado 2026-06-22): **hemmersbach, suritec, jaeger**.
`kisult-demo` queda FUERA del despliegue (entorno de prueba).

Prerrequisitos: acceso `ssh ki-prod-01`, Docker Swarm + Traefik ya activos (verificado
2026-07-06: entrypoint `websecure`, certresolver `letsencrypt`, red `traefik-public`),
`base_postgres` en el swarm (pgvector/pg17, extensión `vector` 0.8.2), y el A record
DNS `git.kisult.com -> 178.105.125.8` (mismo patrón que n8n.kisult.com). Nota de
capacidad: el swap del server rondaba el 82% el 2026-07-06; vigilar `free -h` al
añadir servicios.

Destino de datos: **DB dedicada `hivemind`** en base_postgres (no la DB `rag`, que es
del RAG de Suritec): aislamiento de blast radius, permisos y restore independientes.

Orden recomendado (el DNS solo bloquea el paso 1): crear la DB y aplicar el paso 2
primero; el stack de Forgejo (paso 1) puede desplegarse en paralelo y quedará
esperando el certificado hasta que el A record exista.

---

## 1. Forgejo (git server)

```bash
# copiar el stack al servidor y desplegar
scp deploy/forgejo/docker-stack.yml ki-prod-01:/opt/hivemind/forgejo-stack.yml
ssh ki-prod-01 'docker stack deploy -c /opt/hivemind/forgejo-stack.yml hivemind-git'
# ajustar el certresolver/entrypoint del label Traefik si el nombre difiere del existente
# crear el primer admin (interactivo dentro del contenedor):
ssh ki-prod-01 'docker exec -it $(docker ps -qf name=hivemind-git_forgejo) \
  forgejo admin user create --admin --username max --email <tu-email> --random-password'
```
Verifica: `https://git.kisult.com` carga y pide login (registro deshabilitado).

## 2. Esquema + RLS en Postgres

```bash
scp deploy/sql/001_hivemind_schema.sql ki-prod-01:/opt/hivemind/
# como superuser dentro del contenedor de base_postgres (no publica 5432 al host):
# 1) crear la DB dedicada:  CREATE DATABASE hivemind;
# 2) aplicar el schema (crea extensión, tablas, RLS y rol):
ssh ki-prod-01 'docker exec -i $(docker ps -qf name=base_postgres) \
  psql -U postgres -d hivemind < /opt/hivemind/001_hivemind_schema.sql'
# 3) fijar password del rol de servicio (out-of-band, en el server; guardarla en
#    /root/secrets/hivemind_app.pgpass, chmod 600, NUNCA en chat ni en git):
#    ALTER ROLE hivemind_app PASSWORD '<gen>';
```
Verifica aislamiento (como hivemind_app, no superuser):
`SELECT set_config('hivemind.user_id','nobody',false); SELECT count(*) FROM hivemind.documents;` → 0.

## 3. Repos + teams por cliente (aislamiento real)

En Forgejo, organización `KIsult`. Un repo privado por cliente + un team por cliente.
Vía API (token admin en variable, nunca en git):

```bash
ORG=KIsult; BASE=https://git.kisult.com/api/v1
for c in hemmersbach suritec jaeger; do
  curl -s -H "Authorization: token $FORGEJO_ADMIN_TOKEN" -H 'Content-Type: application/json' \
    -X POST "$BASE/orgs/$ORG/repos" -d "{\"name\":\"client-$c\",\"private\":true}"
  curl -s -H "Authorization: token $FORGEJO_ADMIN_TOKEN" -H 'Content-Type: application/json' \
    -X POST "$BASE/orgs/$ORG/teams" \
    -d "{\"name\":\"$c\",\"permission\":\"write\",\"units\":[\"repo.code\"]}"
done
# repo compartido Nivel 1 (lectura universal del equipo)
curl -s -H "Authorization: token $FORGEJO_ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -X POST "$BASE/orgs/$ORG/repos" -d '{"name":"hivemind-shared","private":true}'
```
Regla: cada persona se añade SOLO a los teams de sus clientes. El team da acceso al repo
`client-<X>` correspondiente. (Asignar repos a teams + miembros: UI o API `teams/{id}/repos`.)

## 4. Acceso en pgvector (debe reflejar los teams de Forgejo)

```sql
-- por cada persona y cada cliente asignado (1 fila = acceso total a ese cliente):
INSERT INTO hivemind.client_access (user_id, client_id) VALUES
  ('<user_id>', 'hemmersbach');
```
`user_id` = el mismo identificador que cada Claude Code usa como `HIVEMIND_USER_ID`.

## 5. Acceso de empleados al MCP (recuperación)

Elegir una de las dos rutas de `mcp-servers/hivemind-kb/README.md`:
- **MVP**: túnel SSH `ssh -L 5432:base_postgres:5432 ki-prod-01`; DSN apunta a localhost.
- **Rollout**: hospedar `hivemind-kb` en ki-prod-01 tras Traefik (patrón MCP-SSE) con token por empleado.

## 6. Piloto (1 persona) antes de abrir a los 4-8
- Cargar datos sintéticos de 2 clientes; dar a la persona acceso solo a 1.
- Verificar (gate de rollout): `search_kb` no devuelve nada del cliente no asignado, y no puede clonar el otro repo.

## Rollback
- Forgejo: `docker stack rm hivemind-git` (los datos quedan en el volumen `forgejo-data`).
- SQL: `DROP SCHEMA hivemind CASCADE;` (hacer dump antes: `pg_dump -n hivemind`).
