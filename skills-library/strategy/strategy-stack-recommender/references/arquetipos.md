# Referencia de Arquetipos

Guía detallada por tipo de proyecto. Leer la(s) sección(es) que correspondan al proyecto analizado.

---

## SaaS Web App

**Forma típica:** Auth + dashboard + facturación por suscripción + configuraciones + gestión de usuarios

### Lenguaje principal
- **TypeScript** es el default. La seguridad de tipos en todo el stack elimina clases enteras de
  bugs en dashboards complejos. Casi innegociable para cualquier cosa más allá de un MVP.

### Frontend
- **Next.js (App Router)** — mejor opción por defecto. SSR/SSG/ISR integrado, excelente para
  páginas de marketing + app en el mismo repositorio, gran ecosistema, despliegues en Vercel en segundos.
- **Remix** — buena alternativa si se prioriza el progressive enhancement y los estándares web.
- **Vue/Nuxt** — válido si el equipo ya conoce Vue. Si no, Next.js tiene mayor pool de talento.
- **Estilos:** Tailwind CSS + shadcn/ui es el camino más rápido a un dashboard pulido. shadcn
  entrega componentes totalmente propios (sin caja negra), lo que importa en productos de larga vida.

### Backend
- **Next.js API Routes / Route Handlers** — suficiente para la mayoría de SaaS en etapas tempranas.
  Mantiene el repositorio unificado.
- **Node/Express o Fastify separado** — vale la pena separar cuando hay lógica de negocio compleja,
  background jobs, o se quiere escalar la API independientemente.
- **tRPC** — excelente si se mantiene TypeScript en todo el stack. Elimina el drift de contratos API.

### Base de datos
- **PostgreSQL** vía **Supabase** o **Neon** — el default correcto. La estructura relacional encaja
  perfectamente con SaaS multi-tenant. Supabase añade auth, storage y tiempo real de regalo.
- **Redis** — agregar cuando se necesite caché de sesiones, rate limiting o una cola de trabajos.
- **ORM:** Prisma (gran DX, TypeScript nativo) o Drizzle (más rápido, ligero, más fiel a SQL).

### Auth
- **Clerk** — más rápido para llegar a producción, maneja MFA, organizaciones, SSO. Vale el costo en etapas tempranas.
- **Supabase Auth** — excelente si ya se usa Supabase; tier gratuito generoso.
- **Auth.js (NextAuth)** — gratuito y flexible, pero más configuración. Bueno para equipos que quieren control total.

### Hosting
- **Vercel** para Next.js — cero configuración, excelentes preview deployments, edge functions integradas.
- **Railway** para backend/base de datos — extremadamente simple, buen tier gratuito, Postgres integrado.

### Pagos
- **Stripe** — estándar de la industria, mejor documentación, SDK TypeScript más sólido. Solo desviarse
  si se venden productos digitales a clientes de la UE a escala (entonces considerar Paddle para IVA).

---

## App Web para Consumidor

**Forma típica:** Alto tráfico, páginas públicas, contenido generado por usuarios, funciones sociales, SEO importa

### Diferencias vs SaaS
- El SEO es crítico → Next.js o Astro para páginas estáticas/SSG
- Las preocupaciones de escala aparecen antes → considerar estrategia de caché desde el inicio
- Más funciones en tiempo real → Supabase Realtime, Pusher o WebSockets

### Frontend
- **Next.js** — sigue siendo el default, especialmente para páginas con mucho contenido
- **Astro** — si la app es mayormente contenido estático con islas de interactividad (blog, docs, marketing)
- **SvelteKit** — excelente rendimiento, bundle pequeño, ideal para apps de consumo con mucha interacción

### Base de datos
- PostgreSQL sigue siendo el default, pero considerar **read replicas** o **PlanetScale** si se
  espera tráfico de lectura intenso
- **MongoDB** justificado cuando el contenido es verdaderamente de esquema flexible

### Hosting
- **Cloudflare Pages + Workers** — mejor rendimiento globalmente, tier gratuito generoso
- **Vercel** — sigue siendo excelente, ligeramente más caro a escala

---

## API / Servicio Backend

**Forma típica:** Backend puro, consumido por otras apps, requisitos de rendimiento estrictos

### Opciones de lenguaje principal

| Lenguaje | Cuándo elegirlo |
|----------|----------------|
| **TypeScript/Node.js** | Equipo con base JS, iteración rápida necesaria, rico ecosistema npm |
| **Python/FastAPI** | Integración IA/ML, equipo de data science, prototipado rápido |
| **Go** | Alta concurrencia, baja latencia, binario pequeño, simplicidad en operaciones |
| **Rust** | Máximo rendimiento, nivel de sistemas, equipo con experiencia en Rust |

### Framework
- **Fastify** (Node) — más rápido que Express, orientado a esquemas, gran soporte TypeScript
- **FastAPI** (Python) — async nativo, docs OpenAPI automáticos, excelente para servicios adyacentes a IA
- **Hono** — ultra rápido, corre en edge (Cloudflare Workers), ideal para APIs ligeras
- **stdlib de Go** — frecuentemente suficiente; si no, usar **Gin** o **Chi**

### Estilo de API
- **REST** — default, universalmente entendido, más fácil de consumir desde cualquier cliente
- **GraphQL** — justificado cuando múltiples clientes necesitan formas de datos diferentes
- **tRPC** — mejor DX cuando servidor y cliente son ambos TypeScript
- **gRPC** — microservicios con llamadas inter-servicio críticas de rendimiento

---

## App Móvil

**Forma típica:** iOS/Android, interfaces táctiles, capacidad offline, notificaciones push

### Multiplataforma (recomendado para la mayoría de equipos)
- **React Native + Expo** — mejor opción por defecto. Ecosistema JS/TS, actualizaciones OTA, gran pool de talento.
- **Flutter** — mejor rendimiento, UI más consistente, pero Dart tiene un ecosistema más pequeño.

### Nativo (solo si se tienen ingenieros nativos o el rendimiento es crítico)
- **Swift** (iOS) / **Kotlin** (Android) — mejor rendimiento e integración con la plataforma.

### Backend para móvil
- Supabase es especialmente bueno para móvil — SDKs cliente para React Native y Flutter, auth,
  tiempo real y almacenamiento integrados en un solo paquete.

---

## Producto con IA

**Forma típica:** Integración LLM, pipeline RAG, agentes IA, chatbots, funcionalidad IA dentro de un producto

### Lenguaje principal
- **TypeScript** con **Vercel AI SDK** — mejor ecosistema para lanzar funcionalidades IA rápidamente.
  Streaming, tool calling, soporte multi-proveedor integrados.
- **Python** — justificado cuando el trabajo de IA es intenso (fine-tuning, RAG complejo, serving de modelos).
  LangChain/LangGraph, LlamaIndex nativos.

### Librerías clave
- **Vercel AI SDK** — mejor opción para productos IA en TypeScript. Abstrae OpenAI/Anthropic/Gemini.
- **LangChain / LangGraph** — Python, potente para agentes y cadenas complejas.
- **LlamaIndex** — Python, excelente para pipelines RAG sobre documentos.

### Proveedores LLM
- **Anthropic (Claude)** — mejor en razonamiento, seguimiento de instrucciones, contexto largo. Recomendado para agentes.
- **OpenAI (GPT-4o)** — fuerte de propósito general, integración con el ecosistema más amplio.
- **Google Gemini** — buen soporte multimodal, ventana de contexto muy larga.
- **Open source vía Ollama/Together AI** — cuando el costo o la privacidad de datos es una preocupación.

### Base de datos vectorial (para RAG)
- **pgvector** en PostgreSQL — empezar aquí. Evita un servicio separado.
- **Pinecone** — gestionado, escala más, bueno si el RAG es el producto central.
- **Qdrant** — alternativa self-hosted, buen rendimiento.

### Observabilidad
- **Langfuse** o **Helicone** — no opcionales para productos IA en producción. Costos de tokens,
  latencia y calidad por llamada. Son un seguro barato.

---

## Automatización / Flujos

**Forma típica:** Scraping, trabajos programados, pipelines event-driven, herramientas internas, integraciones

### Lenguaje principal
- **Python** — default para automatización. Ecosistema rico (requests, BeautifulSoup, Playwright, Celery).
- **TypeScript/Node** — bueno cuando se integran APIs con mucho JS o el equipo tiene base en JS.

### Herramientas clave
- **Playwright** (Python o Node) — automatización de navegador headless, scraping de sitios con mucho JS.
- **Celery + Redis** (Python) — cola de tareas distribuida para cargas async pesadas.
- **BullMQ** (Node) — cola respaldada en Redis, excelente para pipelines de automatización en Node.
- **Inngest** o **Trigger.dev** — infraestructura de jobs gestionada, ejecución durable, gran DX.
- **n8n** (self-hosted) — si la automatización son principalmente conectores no-code entre servicios.

### Hosting
- **Railway** o **Render** — simple, workers siempre activos. Buenos para jobs programados.
- **Fly.io** — excelente para workers persistentes en background con bajos cold starts.
- **AWS Lambda / Cloudflare Workers** — si la automatización es event-driven y de corta duración.

---

## Datos y Analítica

**Forma típica:** ETL, dashboards de reportes, BI, data warehousing, pipelines de métricas

### Lenguaje principal
- **Python** — dominante en datos. Pandas, Polars, dbt, Airflow, SQLAlchemy.
- **SQL** — una parte significativa del trabajo es SQL independientemente del lenguaje.

### Opciones del stack de datos

**Ligero (startup / herramientas internas):**
- PostgreSQL + dbt + Metabase/Redash — simple, barato, sorprendentemente potente

**Escala media:**
- Snowflake o BigQuery + dbt + Looker/Metabase — stack moderno estándar, probado en producción

**ETL pesado:**
- **Apache Airflow** — scheduling y orquestación, DAGs complejos
- **Prefect** o **Dagster** — más modernos, mejor DX que Airflow
- **dlt** (data load tool) — excelente para pipelines de ingesta

### Dashboards
- **Metabase** — mejor BI self-hosted, amigable para usuarios no técnicos
- **Grafana** — dashboards de métricas/series de tiempo
- **Observable** — dashboards orientados a código, para equipos con conocimientos de datos

---

## CLI / Herramienta para Desarrolladores

**Forma típica:** Utilidad de línea de comandos, SDK para desarrolladores, generador de código, herramienta de build

### Lenguaje principal
- **Go** — casi perfecto para herramientas CLI. Binario único, inicio rápido, fácil compilación cruzada.
  Usado por Docker, Terraform, GitHub CLI, etc.
- **Rust** — cuando el rendimiento es crítico. ripgrep, fd, exa son todos Rust. Mayor inversión.
- **TypeScript/Node** — bueno cuando se distribuye vía npm y el target son desarrolladores JS.
- **Python** — bueno para CLIs adyacentes a datos. Usar **Typer** o **Click**.

### Librerías clave
- **Go:** `cobra` (framework CLI) + `bubbletea` (TUI si se necesita)
- **Node:** `commander` / `oclif` + `ink` (TUI basado en React)
- **Python:** `typer` + `rich` (output hermoso)
- **Rust:** `clap` (CLI) + `ratatui` (TUI)

---

## Extensión de Navegador

**Forma típica:** Extensión Chrome/Firefox, content scripts, web clipper, herramienta de productividad

### Lenguaje
- **TypeScript** — prácticamente requerido para extensiones no triviales. Usar **WXT** o **Plasmo**
  como framework de build (manejan la complejidad de Manifest V3).

### Framework
- **WXT** — mejor framework actual para extensiones. HMR, TypeScript, soporte Vue/React/Svelte.
- **Plasmo** — alternativa popular, orientada a React.

### Almacenamiento
- **chrome.storage.sync** — datos pequeños que se sincronizan entre dispositivos
- **chrome.storage.local** — datos locales más grandes
- **IndexedDB** — si se necesita una base de datos local real en la extensión

---

## IoT / Embebido

**Forma típica:** Interfaz con hardware, sensores, control en tiempo real, entornos con recursos limitados

### Lenguaje
- **MicroPython** — mejor punto de partida para Raspberry Pi Pico, ESP32. Sintaxis Python, huella pequeña.
- **C/C++** con **Arduino** — máximo soporte de hardware, mejor para firmware en producción.
- **Rust (Embassy)** — práctica emergente para embebido en producción. Memory safe, sin runtime.
- **Python** en Raspberry Pi (OS completo) — cuando se tiene un sistema Linux completo y se quiere facilidad.

### Backend en la nube para IoT
- **MQTT + AWS IoT Core** — backend IoT estándar para flotas de dispositivos
- **Supabase** — usable para proyectos IoT simples vía REST API desde los dispositivos
- **InfluxDB** — base de datos de series de tiempo, excelente para datos de sensores
