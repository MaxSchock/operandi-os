# MCPs curados para iAmasters OS

> Lista validada de Model Context Protocol servers útiles para operadores IA.
> Cada entrada incluye: para qué sirve, cuándo usarlo, instalación, riesgo de tokens, alternativas.
>
> Última revisión: 2026-06-03

## Cómo usar

```
/install-mcp <name>
```

O manualmente: copia la config a `.mcp.json` y rellena variables de entorno en `.env`.

---

## ⭐ Top 5 recomendados (instalar siempre)

### 1. context7 · Docs vivos para LLMs

**Para qué**: cuando construyes con un framework/lib (Next.js, Supabase, Tailwind, etc.), Context7 inyecta la documentación oficial actualizada en el contexto. Evita que Claude alucine APIs obsoletas.

**Cuándo activarlo**: en cualquier sesión donde escribas código con frameworks.

**Riesgo de tokens**: medio-alto si lo usas en CADA prompt. Mejor: invocarlo explícitamente con "use context7 para [tema]".

**Plan**: gratis, no requiere API key.

**Config**:
```json
"context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"],
  "env": {}
}
```

**Variables**: ninguna.

---

### 2. github · Operaciones git y repos

**Para qué**: leer issues, PRs, archivos de cualquier repo público o tuyo. Crear/comentar issues, mergear PRs.

**Cuándo activarlo**: si trabajas con varios repos y quieres que Claude pueda actuar sobre ellos sin `gh` CLI.

**Riesgo de tokens**: bajo. Solo invoca tools cuando lo pides.

**Plan**: gratis (Personal Access Token).

**Config**:
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
  }
}
```

**Variables**: `GITHUB_TOKEN` (PAT con scopes: repo, read:user).

**Alternativa**: usar `gh` CLI desde Bash directamente. Más simple si solo necesitas comandos puntuales.

---

### 3. supabase · Tu base de datos

**Para qué**: queries SQL, gestión de tablas, RLS, edge functions, storage. Operador del Supabase project desde Claude.

**Cuándo activarlo**: si tienes apps en Supabase (self-hosted o cloud) y construyes con Claude Code.

**Riesgo de tokens**: bajo si configuras RLS correctamente.

**Plan**: gratis (OSS) + plan Supabase de tu proyecto.

**Config**:
```json
"supabase": {
  "command": "npx",
  "args": ["-y", "@supabase/mcp-server-supabase@latest", "--project-ref=$SUPABASE_PROJECT_REF"],
  "env": {
    "SUPABASE_ACCESS_TOKEN": "$SUPABASE_ACCESS_TOKEN"
  }
}
```

**Variables**:
- `SUPABASE_PROJECT_REF` — el ref del proyecto (en URL del dashboard)
- `SUPABASE_ACCESS_TOKEN` — token de acceso desde Account → Access Tokens

**⚠️ Importante**: usa READ-ONLY token para empezar. Solo eleva permisos cuando confíes en el flujo.

---

### 4. notion · Si trabajas en Notion

**Para qué**: leer páginas, crear bases de datos, mover páginas, crear comentarios. Si tu wiki/CRM/sistema de tareas está en Notion.

**Cuándo activarlo**: si usas Notion como home-base operativo.

**Riesgo de tokens**: medio (Notion devuelve estructuras grandes).

**Plan**: gratis hasta cierto uso (Notion Connect API).

**Config**:
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-notion"],
  "env": {
    "NOTION_API_KEY": "$NOTION_API_KEY"
  }
}
```

**Variables**: `NOTION_API_KEY` (Internal Integration Token desde notion.so/my-integrations).

**⚠️ Importante**: solo da acceso a las páginas que comparta el integration. No da acceso a todo el workspace por defecto.

---

### 5. firecrawl · Scraping de webs

**Para qué**: scrapear webs con bot blockers (mejor que WebFetch nativo). Usado por `tool-firecrawl-scraper` y otras skills.

**Cuándo activarlo**: si haces investigación competitiva, brand-voice extraction, o cualquier scraping.

**Riesgo de tokens**: bajo (devuelve solo contenido principal).

**Plan**: 500 créditos free one-time. Hobby $16/mo, 3000 créditos.

**Config**: este MCP NO se invoca como MCP server de Claude Code, sino como API directa desde skills. No va en `.mcp.json`. Configuración solo en `.env`:

```bash
FIRECRAWL_API_KEY=fc-xxxxx
```

---

## 🔧 Útiles para casos específicos

### codegraph · Grafo de código local (ideal si programas)

**Para qué**: da al agente un **grafo del código** de tu proyecto (símbolos, llamadas, imports) en una SQLite local. El agente responde "¿cómo funciona X?", "¿quién llama a Y?", "¿qué rompo si cambio Z?" sin grep ni lectura masiva → menos tokens y menos tool calls.

**Cuándo activarlo**: si construyes apps o webs (Next.js, scripts…) y quieres que Claude navegue tu código de forma eficiente. Pensado para vibe-coders.

**Riesgo de tokens**: bajo — de hecho los **reduce** (benchmarks del autor: ~16% más barato, ~58% menos tool calls).

**Plan**: gratis, MIT, **100% local, sin API keys, sin servicios externos** (solo un `.db` SQLite).

**Instalación** (un comando, self-contained, cross-OS):
```bash
npm i -g @colbymchenry/codegraph    # o: curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
codegraph install                   # auto-configura Claude Code / Cursor / Codex…
cd tu-proyecto && codegraph init -i # indexa ese proyecto
```

**Config MCP manual** (alternativa, en `.mcp.json`):
```json
"codegraph": { "type": "stdio", "command": "codegraph", "args": ["serve", "--mcp"] }
```

**Variables**: ninguna.

**✅ Validado** (2026-06-03, repo `recursos-platform`): instalación 4 s · indexado de 72 archivos en 281 ms · búsqueda + `callers` + `impact` precisos · SQLite local 1,2 MB.

**⚠️ Notas**:
- Es para **código** (TS/JS/Python/Go/Rust/Swift…), NO para memoria narrativa de negocio.
- Auto-sync con file watcher (se mantiene fresco solo). El índice `.codegraph/` va **gitignored**.

---

### linear · Gestión de proyectos

**Para qué**: si usas Linear para issue tracking en lugar de GitHub Issues.
**Plan**: gratis hasta cierto uso.
**Config**: `@modelcontextprotocol/server-linear`

### gmail · Lectura de emails

**Para qué**: leer/buscar emails, crear drafts. NO enviar (eso requiere user explicit ok).
**Plan**: gratis con Google Workspace.
**Config**: requiere OAuth setup más complejo.
**Riesgo**: alto si das write permissions. Mantén READ-ONLY hasta confiar.

### slack · Mensajería interna

**Para qué**: leer canales, crear posts, threads. Útil para equipos pequeños.
**Plan**: gratis.
**Config**: `@modelcontextprotocol/server-slack`
**⚠️**: misma regla que email — read-only hasta confiar.

### filesystem · Acceso a sistema de archivos local

**Para qué**: explorar carpetas fuera del repo actual de forma controlada.
**Cuándo activarlo**: solo si necesitas Claude vaya a otra carpeta sin abrir nueva sesión.
**Config**: `@modelcontextprotocol/server-filesystem` con paths whitelisted.
**⚠️**: riesgo de seguridad. Whitelist específica obligatoria.

### obsidian · NO se instala

**Por qué no**: el segundo cerebro Obsidian montado 2026-06-03 sigue el **patrón Karpathy** (wiki vivo, no RAG). Claude Code accede al vault `~/iamasters-os/_wiki/` directamente vía filesystem (`Read`, `Edit`, `Write`), no via MCP. El tutorial iAmasters lo descarta literal: "No hay plugin ni API. Claude Code abre la misma carpeta y edita los .md directamente."

Si en uso real demuestra limitación (búsquedas semánticas que vector search resolvería mejor que grep, navegación graph-aware), evaluar `dbmcco/obsidian-mcp` o `StevenStavrakis/obsidian-mcp`. Por ahora, fuera del scope.

---

## ⚠️ MCPs que evitar (en producción)

### Cualquier MCP que dé write a redes sociales sin gates

LinkedIn, Twitter, Instagram, Facebook auto-post: **alto riesgo de fuga de identidad**. Mejor: skill que prepara el draft y operador hace post manualmente.

### MCPs que no documentan claramente sus scopes

Si la documentación no especifica qué permisos pide y qué hace, no instalar.

### MCPs custom de developers desconocidos

`/install-mcp custom <url>` solo si confías en el dev o validas el código manualmente.

---

## Pattern para tu propio MCP curated list

Si trabajas con clientes que tienen stacks específicos, mantén tu propio `mcps-curated.md` por cliente en `clients/<nombre>/docs/mcps-curated.md`.

Estructura recomendada por entrada:
1. Nombre + tagline
2. Para qué sirve (1-2 frases)
3. Cuándo activarlo (caso de uso)
4. Riesgo de tokens (bajo/medio/alto)
5. Plan / coste
6. Config (`.mcp.json` snippet)
7. Variables (`.env`)
8. ⚠️ Notas de seguridad si aplica

---

## Token budget consideration

Cada MCP server activo en `.mcp.json` añade contexto al system prompt al iniciar Claude Code (las descripciones de sus tools). Más MCPs = más tokens base.

**Regla práctica**: 5-7 MCPs activos máximo. Si necesitas más, considera comentar los que no usas frecuentemente.

**Pro tip**: tener un `.mcp.json` por cliente (en `clients/<nombre>/.mcp.json` si Claude Code lo soporta) o cambiar `.mcp.json` antes de cada sesión según necesidad.

---

## Cómo añadir nuevos MCPs a esta lista

Para incluir un MCP en la curated list (PR al repo):

1. Probar el MCP en producción mínimo 2 semanas
2. Documentar:
   - Casos donde aporta valor real
   - Casos donde NO aporta (o es contraproducente)
   - Riesgos identificados
3. Submit PR con la entrada nueva siguiendo el formato de las top 5

Las contribuciones deben venir con experiencia real, no "instalé y parece OK".
