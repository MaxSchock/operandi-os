# Registro de productos construidos

> Qué hay construido, dónde vive y quién lo paga. Se consulta antes de decidir a qué producto va un hallazgo (`context/traslados.md`) y antes de afirmar «eso no existe» o «eso ya lo hace X». Se actualiza en la misma sesión en que un producto nace, cambia de sitio o se para. Nada de cifras ni personas: eso vive en los briefs de cada cliente.
> Estado: producción · canario (solo cliente de prueba) · parado · por confirmar. Revisado = fecha en que alguien comprobó la fila contra la fuente.

## Operandi

| Producto | Qué es | Dónde vive | Paga | Estado | Revisado |
|---|---|---|---|---|---|
| video-engine | Motor que convierte la petición del cliente en vídeo de redes (etapas, launch M12, revisor final) | repo `operandi-services/services/video-engine`, VpsFigura, servicio Swarm `video-engine_app` | Operandi (Cardeleine; canario `max`) | producción; revisor final solo en aviso/canario | 2026-10-14 |
| content-engine-daemon | Genera, programa y publica posts de LinkedIn con imagen por cliente, a partir de briefs `briefs/<cliente>.yaml` | `operandi-services/services/content-engine-daemon`, VpsFigura, stack `content-engine-daemon` | Operandi (clientes con brief en `briefs/`: HNT, Cardeleine, marca personal, Rotary, otros) | producción | 2026-10-14 |
| Dashboard Operandi (dashboardln) | Panel Next.js de clientes: peticiones de vídeo, aprobación de posts, usuarios por cliente | repo local `/mnt/c/Users/PC/operandi-dashboardln`, Vercel (URL por confirmar), Supabase `xepotlbqlwmriwievyvc` | Operandi | producción | 2026-10-08 |
| strategist | Piloto comercial: digest diario, alertas, agente por Telegram con herramientas | `operandi-services/services/strategist`, VpsFigura, `strategist_app` | Operandi (interno) | producción | por confirmar |
| claude-debug | Investiga errores de n8n que llegan del sub-workflow de errores y los resuelve o escala | `operandi-services/services/claude-debug`, VpsFigura, `claude-debug_app` | Operandi (interno) | producción | por confirmar |
| Outreach LinkedIn (Steps 1-5, «llamada primero») | Familia de workflows n8n por cliente: leads Apollo, mensajes, invitaciones, respuestas, llamada antes del DM, Safety Gate y Reconciler | n8n `ssn8n.figura-studio.com` (VpsFigura), Supabase, Unipile; índice en `clients/operandi/context/workflows-built.md` | Operandi (clientes outreach) | producción | 2026-09-30 |
| LN Auto-Reply v4 (marca personal de clientes) | Comentarios y respuestas automáticas en LinkedIn | n8n `CQ9SrTTQWJjjsgrQ` | Operandi | por confirmar | por confirmar |
| Voice agent Louis | Agente de voz en francés para Helexia | Retell (multi-prompt) | Operandi (Helexia) | por confirmar | por confirmar |
| preprocessor-pierre | Servidor Playwright para el RPA del cliente INJECO | VpsFigura, stack `preprocessor-pierre` | Operandi (Pierre/INJECO) | por confirmar | por confirmar |
| Motor de contenido Rotary | El content-engine publicando como página del club y compartiendo cada post por WhatsApp (`app/pipeline/share.py`) | content-engine-daemon, cliente `rotary` | sin pago (Rotary, institucional) | producción desde 14-10 | 2026-10-14 |
| Marca personal de Max | Posts de Max en LinkedIn con foto base de la oficina y hoja de cara | content-engine, brief `operandi-canary.yaml`; método en `projects/briefs/marca-personal/` | interno (canario) | canario | 2026-10-14 |

## KIsult

| Producto | Qué es | Dónde vive | Paga | Estado | Revisado |
|---|---|---|---|---|---|
| Linus | Asistente personal por voz y texto (correo, calendario, pendientes, «Heute») | repo `~/max-assistent`, ki-prod-01 (Hetzner); instancias canario `max`, `linus-andre`, `linus-jonas`, `linus-tobi`, `max-demo` | KIsult (RHP) | producción en las cuatro instancias, main `d61836c1` | 2026-10-14 |
| Suritec FRED / Cockpit | Asistente de conocimiento por chat, correo, WhatsApp y teléfono (TalkPilot) con bandeja central y escalada | `clients/kisult/clients/suritec/service`, ki-prod-01; RAG en Supabase | KIsult (Suritec) | producción; agente de voz Kunden apagado desde 25-09 | 2026-10-07 |
| Hemmersbach Email-Processor | Clasifica correos de la imprenta y prepara ofertas | n8n cloud del cliente (Workflow-A) más servicio en VM del cliente (migración pendiente del túnel) | KIsult (Hemmersbach) | producción en n8n cloud; corte a la VM parado | 2026-10-14 |
| RAG ULB | RAG documental en n8n + Supabase + Mistral OCR | n8n, Supabase `rag_ulb` | KIsult (ULB) | por confirmar | por confirmar |
| RAG + chatbot HNT | RAG y chatbot de WhatsApp | n8n, Supabase `rag_hnt`, Evolution | KIsult (HNT) | por confirmar | por confirmar |
| KIsult demo | Demo ventanas/puertas: Gmail + visión + Odoo + WhatsApp | `clients/kisult/clients/kisult-demo` | interno | demo | por confirmar |

## Falkenlead

| Producto | Qué es | Dónde vive | Paga | Estado | Revisado |
|---|---|---|---|---|---|
| Skill marketing-google-ads-auditor | Auditoría de cuentas Google Ads contra la documentación oficial, con Clarity y Analytics | `~/iamasters-os/.claude/skills/marketing-google-ads-auditor/` | Falkenlead (uso interno: GBS, Yo Respondo) | producción (sin commit en el repo) | 2026-10-09 |
| Feed y cron de precios Tojo | Hoja de Google como feed del Merchant Center y cron que corrige precios | Hoja de Max (token de Operandi), cron en VpsFigura | Falkenlead (Tojo) | producción | 2026-10-12 |

## Interno de Max

| Producto | Qué es | Dónde vive | Paga | Estado | Revisado |
|---|---|---|---|---|---|
| skool-radar | Recoge clases y publicaciones de comunidades Skool y cuentas de Instagram (Apify), solo lectura | `~/iamasters-os/projects/skool-radar/`, base `data/radar.db` | interno | producción | 2026-10-01 |
| Hooks del OS | Activador de reglas, destilador, salud-os, guards de frases de IA | `~/.claude/hooks/` | interno | producción | 2026-10-14 |
