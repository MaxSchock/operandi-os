# Referencia de Trade-offs Tecnológicos

Usar este archivo cuando el usuario esté decidiendo entre alternativas específicas, o cuando una
recomendación necesite justificación matizada. Cada sección enmarca la decisión con claridad.

---

## Framework Frontend

### Next.js vs Remix
| | Next.js | Remix |
|---|---|---|
| Mejor para | La mayoría de apps web, SEO intensivo, equipos con exp. en React | Apps con muchos formularios, puristas de estándares web |
| Enrutamiento | Basado en archivos, App Router (Server Components) | Rutas anidadas, patrón loaders/actions |
| Fetching de datos | Server Components + fetch, flexible | Patrón loader/action, muy limpio |
| Ecosistema | Enorme, nativo en Vercel | Más pequeño pero creciendo |
| Hosting | Vercel (nativo), en cualquier lugar con adaptadores | En cualquier lugar, adaptadores para todas las plataformas |
| **Elegir cuando** | Default para la mayoría de equipos | Se valoran los estándares web o se rechazan los React Server Components |

### Next.js vs SvelteKit
| | Next.js | SvelteKit |
|---|---|---|
| Tamaño del bundle | Mayor (overhead de React) | Muy pequeño |
| Rendimiento | Bueno | Excelente |
| Curva de aprendizaje | Media (JSX + modelo mental de React) | Baja (más cercano a HTML/CSS/JS) |
| Ecosistema | Masivo | Más pequeño pero suficiente |
| **Elegir cuando** | El equipo conoce React, se necesita gran ecosistema | Equipo pequeño, rendimiento crítico, proyecto nuevo |

### React vs Vue
- **React**: Mayor pool de talento, más empleos, más librerías, respaldo de Meta.
  Más verboso, pero extremadamente flexible.
- **Vue**: Curva de aprendizaje más suave, templates más limpios, excelente documentación.
  Ecosistema más pequeño, menor pool de talento. Fuerte en Asia y agencias.
- **Elegir React** cuando la contratación importa o se construye un producto de larga vida.
- **Elegir Vue** cuando el equipo ya lo conoce o viene de backends basados en templates.

---

## Lenguaje Backend

### Node.js vs Python
| | Node.js | Python |
|---|---|---|
| Mejor para | APIs web, tiempo real, equipos full-stack JS | IA/ML, datos, scripting, prototipado rápido |
| Rendimiento | Bueno (async por defecto) | Más lento (GIL), pero FastAPI async lo mitiga |
| Ecosistema | npm (registro de paquetes más grande) | pip (enorme para datos/IA) |
| Librerías IA | Vercel AI SDK, buenos wrappers | LangChain, LlamaIndex, nativo |
| **Elegir cuando** | El equipo tiene base JS o construye un producto web | IA/ML es central, equipo de datos, o devs Python |

### Python FastAPI vs Django
| | FastAPI | Django |
|---|---|---|
| Mejor para | APIs, microservicios, backends de IA | Apps web full-stack, paneles admin, monolitos |
| Rendimiento | Muy rápido (async) | Más lento pero suficiente para la mayoría de apps web |
| ORM | SQLAlchemy / SQLModel | Django ORM (baterías incluidas) |
| Panel admin | Ninguno (construir propio) | Excelente panel admin integrado |
| Curva de aprendizaje | Baja | Media |
| **Elegir cuando** | Se necesita una API rápida o servicio de IA | App con mucho contenido, se necesita panel admin |

### Go vs Node.js (para APIs)
| | Go | Node.js |
|---|---|---|
| Rendimiento | Excelente, baja memoria | Bueno, mayor memoria |
| Concurrencia | Goroutines (excelente) | Event loop (bueno para I/O) |
| Binario | Binario único, fácil despliegue | Necesita runtime de Node |
| Ecosistema | Más pequeño | Masivo |
| Contratación | Pool más pequeño | Pool grande |
| **Elegir cuando** | Rendimiento crítico, simplicidad en ops importa | Equipo con base JS, prioridad en velocidad al mercado |

---

## Base de Datos

### PostgreSQL vs MongoDB
| | PostgreSQL | MongoDB |
|---|---|---|
| Mejor para | La mayoría de aplicaciones, datos relacionales | Esquema flexible, almacenamiento de documentos |
| Transacciones | ACID completo | Multi-documento (v4+) |
| Potencia de consultas | SQL (extremadamente potente) | MQL (bueno, pero menos expresivo) |
| Flexibilidad de esquema | Rígido (migraciones requeridas) | Flexible (sin esquema) |
| Soporte JSON | Excelente (JSONB) | Nativo |
| **Elegir cuando** | Default — la mayoría de apps son relacionales | Esquemas verdaderamente dinámicos, contenido con campos variados |
| **Evitar cuando** | El esquema es muy inestable | Se necesitan joins complejos o consistencia fuerte |

### Supabase vs Firebase
| | Supabase | Firebase |
|---|---|---|
| Base de datos | PostgreSQL (SQL completo) | Firestore (NoSQL, documento) |
| Open source | Sí | No |
| Self-host | Sí | No |
| Tiempo real | Sí (replicación Postgres) | Sí (nativo) |
| Auth | Sí | Sí |
| Storage | Sí | Sí |
| **Elegir cuando** | Se quiere potencia SQL + open source | Se necesita sincronización offline, mobile-first, ecosistema Google |

### Prisma vs Drizzle
| | Prisma | Drizzle |
|---|---|---|
| DX | Excelente, schema-first | Bueno, SQL-first |
| Rendimiento | Ligeramente más lento (abstracciones) | Más rápido, capa más delgada |
| Seguridad de tipos | Muy buena | Excelente (TypeScript nativo) |
| Migraciones | Auto-generadas | Más control manual |
| **Elegir cuando** | Más rápido para empezar, el equipo prefiere abstracción | Se quiere control SQL, el rendimiento importa |

---

## Autenticación

### Clerk vs Auth.js vs Supabase Auth
| | Clerk | Auth.js (NextAuth) | Supabase Auth |
|---|---|---|---|
| Tiempo de setup | El más rápido (10 min) | Medio | Rápido si ya se usa Supabase |
| Costo | De pago después de 10k MAU | Gratuito | Gratuito (tier generoso) |
| Funcionalidades | MFA, orgs, SSO, UI de perfil | Básico, extensible | MFA, social login, teléfono |
| Control | Bajo (hosted) | Alto (auto-gestionado) | Medio |
| **Elegir cuando** | Velocidad al mercado, B2B (orgs/SSO) | Control total, el costo importa a escala | Ya se usa Supabase |

---

## Hosting

### Vercel vs Netlify vs Cloudflare Pages
| | Vercel | Netlify | Cloudflare Pages |
|---|---|---|---|
| Mejor para | Next.js (nativo), full-stack | Sitios estáticos, despliegues simples | Rendimiento global, Workers |
| Rendimiento | Bueno (CDN con foco en US) | Bueno | Mejor globalmente |
| Cold starts | Rápido | Rápido | Casi cero (Workers) |
| Costo a escala | Caro | Moderado | Muy económico |
| **Elegir cuando** | Proyecto Next.js | Frontend simple, no-Next | Rendimiento crítico, usuarios globales |

### Railway vs Render vs Fly.io
| | Railway | Render | Fly.io |
|---|---|---|---|
| Mejor para | Full stack, bases de datos | Servicios web simples | Edge global, VMs persistentes |
| DX | Excelente | Buena | Buena (CLI más pronunciado) |
| Bases de datos | Postgres integrado | Integrado | No nativo, usar externo |
| Tier gratuito | $5 crédito/mes | Tier gratuito | Pequeña cuota gratuita |
| **Elegir cuando** | Mejor DX general | Alternativa más simple | Se necesitan VMs cerca de los usuarios |

---

## Pagos

### Stripe vs Paddle vs Lemon Squeezy
| | Stripe | Paddle | Lemon Squeezy |
|---|---|---|---|
| Mejor para | Cualquier pago, suscripciones, marketplaces | Productos digitales, ventas globales, SaaS | Productos indie simples, licencias simples |
| Manejo de impuestos | Se maneja el IVA/impuestos uno mismo | Merchant of record (maneja impuestos) | Merchant of record |
| Complejidad | Mayor (más potente) | Media | Baja |
| Comisiones | 2.9% + $0.30 | 5% + $0.50 | 5% + $0.50 |
| **Elegir cuando** | Facturación compleja, marketplaces, foco en US | Ventas globales, sin querer lidiar con impuestos | Productos simples, indie hackers |

---

## Cuándo elegir Monolito vs Microservicios

**Siempre empezar con un monolito.** Los microservicios añaden complejidad operacional que destruye equipos pequeños.

**Considerar separar cuando:**
- Un servicio específico tiene necesidades de escalado radicalmente diferentes
- El despliegue independiente de un servicio es crítico
- Los equipos son suficientemente grandes para que el acoplamiento cree cuellos de botella en releases (generalmente 20+ ingenieros)

**Para la mayoría de startups SaaS hasta Serie A:** el monolito es lo correcto. Desplegarlo bien. Separar después si es necesario.

---

## TypeScript vs JavaScript

Siempre recomendar TypeScript para cualquier proyecto que vaya a:
- Crecer más allá de ~500 líneas de código
- Ser mantenido por más de una persona
- Vivir en producción por más de 6 meses

El costo inicial de TypeScript (los tipos) se recupera masivamente en refactorización, onboarding
y captura de bugs antes del runtime. El único caso para JS plano son scripts rápidos o prototipos
que se van a desechar.
