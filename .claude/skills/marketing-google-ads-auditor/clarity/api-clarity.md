# API de Clarity

> No es documentación de Google Ads. Nota operativa de la API de Clarity para la parte de comportamiento en la web.

> Consultado el 08-10-2026 en learn.microsoft.com/clarity y github.com/microsoft/clarity-mcp-server. Lo que no está en esas fuentes va marcado [SIN VERIFICAR].

---

## 1. API de exportación de datos

| Aspecto | Dato | Fuente |
|---|---|---|
| URL | `GET https://www.clarity.ms/export-data/api/v1/project-live-insights` | `https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api` |
| Autenticación | Cabecera `Authorization: Bearer <token>` (token JWT). Solo un administrador del proyecto crea tokens: Settings > Data Export > Generate new API token | idem |
| Nombre del token | 4 a 32 caracteres, letras, números, `-`, `_` y `.`. Sin espacios ni `@ # $ % & * !`. Único dentro del proyecto | idem |
| `numOfDays` | 1, 2 o 3: últimas 24, 48 o 72 horas desde la llamada | idem |
| `dimension1`, `dimension2`, `dimension3` | Hasta tres dimensiones de desglose por petición | idem |
| Zona horaria | Los resultados vienen en UTC | idem |
| Formato | JSON: un array de objetos `{"metricName": "...", "information": [ ... ]}` | idem |
| Documentación actualizada | 05-12-2025 (metadato de la página) | idem |

### Límites

| Límite | Valor |
|---|---|
| Llamadas | **10 por proyecto y por día** |
| Profundidad | Solo los últimos 1 a 3 días. No hay histórico por API |
| Dimensiones | Máximo 3 por petición |
| Filas | **1.000 como máximo, sin paginación** |
| Errores | 400 parámetros no válidos; 401 token ausente, no válido o caducado; 403 token sin permiso; 429 «Exceeded daily limit» |

Consecuencia para la skill: la API sirve para una foto de las últimas 72 horas, no para auditar 30 o 90 días. Un histórico solo se consigue guardando cada día lo que se descargue (con 10 llamadas diarias de tope).

### Dimensiones admitidas

Browser, Device, Country/Region, OS, Source, Medium, Campaign, Channel, URL. (Lista de la página oficial. Los nombres exactos de parámetro con mayúsculas y espacios, por ejemplo `Country/Region`: [SIN VERIFICAR] más allá del ejemplo oficial `dimension1=OS`.)

### Métricas que devuelve

La página oficial las lista sin definirlas:

Scroll Depth, Engagement Time, Traffic, Popular Pages, Browser, Device, OS, Country/Region, Page Title, Referrer URL, Dead Click Count, Excessive Scroll, Rage Click Count, Quickback Click, Script Error Count, Error Click Count.

La propia página avisa de que «la respuesta completa puede incluir más métricas y dimensiones».

El único bloque de ejemplo oficial es `Traffic`, con estos campos: `totalSessionCount`, `totalBotSessionCount`, `distantUserCount`, `PagesPerSessionPercentage` y la dimensión pedida (por ejemplo `OS`). Nombres de campo del resto de métricas (por ejemplo cómo se llama el campo de profundidad media de scroll): [SIN VERIFICAR]. Hay que inspectar una respuesta real y guardar el esquema.

Los valores de `totalSessionCount` del ejemplo vienen como cadenas de texto, y `PagesPerSessionPercentage` como número.

### Ejemplo

```python
import requests

resp = requests.get(
    "https://www.clarity.ms/export-data/api/v1/project-live-insights",
    params={"numOfDays": "3", "dimension1": "Campaign", "dimension2": "Source", "dimension3": "Medium"},
    headers={"Authorization": "Bearer TOKEN", "Content-type": "application/json"},
    timeout=60,
)
resp.raise_for_status()
datos = resp.json()
```

(Los valores `Campaign`, `Source`, `Medium` para `dimension1..3` se escriben tal como figuran en la lista de dimensiones oficial. El ejemplo de la documentación usa `dimension1=OS`.)

---

## 2. Definiciones oficiales de las métricas de comportamiento

Fuente: `https://learn.microsoft.com/en-us/clarity/insights/semantic-metrics` (actualizada 01-12-2025) y `https://learn.microsoft.com/en-us/clarity/faq`.

| Métrica | Definición oficial | Umbral |
|---|---|---|
| Clics de rabia (rage clicks) | Una vista de página o sesión se marca si el usuario hace clic varias veces en un área agrupada en rápida sucesión. Cada clic del grupo queda marcado. Señal de frustración, normalmente donde el usuario esperaba un elemento interactivo | No publicado [SIN VERIFICAR] (la documentación dice «varias veces», «área agrupada», «rápida sucesión» sin cifras) |
| Clics muertos (dead clicks) | Clic sobre un elemento que no da respuesta en un tiempo razonable: el estado visual no cambia y no hay navegación. Puede indicar elementos rotos, peticiones lentas o diseño engañoso | No publicado [SIN VERIFICAR] («tiempo razonable») |
| Scroll excesivo | Sesión con más desplazamiento vertical que la media esperada. La FAQ lo describe como desplazarse por el contenido a un ritmo superior al esperado para un consumo normal | No publicado [SIN VERIFICAR] («media esperada») |
| Clics rápidos de vuelta (quick backs) | Un clic que lleva al usuario fuera de la página actual y que vuelve a la página o sitio original en menos de un umbral. Se detecta cuando el usuario pasa de una página nueva a la anterior en menos tiempo que el definido para esa página (el tiempo de permanencia, «dwell time»). Según la página, en versiones futuras la métrica se adaptará a cada sitio | El umbral es el tiempo de permanencia definido por Clarity para esa página; cifra no publicada [SIN VERIFICAR]. Nota: la página de métricas habla de salir a otro sitio y la FAQ y los filtros hablan de volver a la página anterior: ambos textos coexisten |
| Errores de script (JavaScript errors) | Errores de JavaScript durante la ejecución en el navegador. Se ve el total y el desglose por error, con las grabaciones relacionadas | No aplica |
| Clics de error (click errors) | Errores de JavaScript que ocurren después de un clic. Cada vez que un clic provoca un error, la sesión se etiqueta automáticamente | No aplica |
| Profundidad de scroll | La API la devuelve como `Scroll Depth`. En la interfaz hay un filtro «Page scroll depth» (porcentaje exacto recorrido) y los mapas de scroll muestran «% scrolled» en saltos del 5 %, «# of visitors» y «% drop off». Definición exacta de la métrica agregada de la API: [SIN VERIFICAR] | idem |
| Tiempo activo / de interacción | La API lo devuelve como `Engagement Time`. Definición oficial en las páginas consultadas: [SIN VERIFICAR] | idem |

Otras cifras oficiales en los filtros de rendimiento (`https://learn.microsoft.com/en-us/clarity/filters/clarity-filters`): puntuación de rendimiento de 0 a 50 pobre, 51 a 80 mejorable, 81 a 100 buena; LCP ideal en menos de 2,5 s, mejorable por debajo de 4 s.

---

## 3. Tráfico de pago: Source, Medium, Campaign, Channel

| Dato | Qué dice la documentación | Fuente |
|---|---|---|
| Source | Dato de `utm_source`: el dominio del enlace que envió al visitante | `https://learn.microsoft.com/en-us/clarity/filters/clarity-filters` |
| Medium | Dato de `utm_medium`: el medio publicitario o de marketing | idem |
| Campaign | Datos de campaña si se usó un código UTM | idem |
| Channel | Agrupa el tráfico según `utm_source` o `utm_medium`. Canales: Organic Search, Direct, Social, Referral, Email, AIPlatform, PaidAIPlatform, PaidSearch, Social (aparece repetido en la página), Other | idem |
| Referring site | URL de la página previa a la visita, si está disponible. No hay dato cuando no se pasa en las cabeceras HTTP | idem |
| Bot traffic | Sesiones detectadas como bots (filtro). Con la detección de bots activada aún pueden colarse sesiones de bot | idem y FAQ |
| `gclid` | La documentación consultada no dice cómo trata Clarity el `gclid` ni qué clasifica como `PaidSearch` cuando un clic de Google Ads llega sin UTM [SIN VERIFICAR] | |

Conclusión operativa: para que Clarity atribuya sesiones a una campaña de Google Ads hay que etiquetar con UTM (`utm_source`, `utm_medium`, `utm_campaign`), no basta el etiquetado automático. La integración exige además un valor `utm_campaign` distinto por campaña.

### Integración con Google Ads

Fuente: `https://learn.microsoft.com/en-us/clarity/advertising-dashboard/ad-getting-started` (31-10-2025) y `.../ad-campaign-insights` (29-09-2025).

- Se vincula la cuenta de Google Ads (o Microsoft Ads) en Settings > Setup. Da acceso al widget de datos de campaña del panel y al panel de Publicidad.
- Funciona uniendo datos de campaña con los de Clarity. Exige UTM en las campañas y un valor de `utm_campaign` único por campaña.
- Permite ver grabaciones y mapas de calor por campaña y filtrar los paneles por «Ad campaign».
- Campaign Insights (resúmenes en lenguaje natural generados con Copilot): solo para Google Ads por ahora. Necesita normalmente 3 a 5 días de datos y UTM correctos (`utm_source`, `utm_campaign`); sin ellos no se generan. Pueden contener errores (IA generativa).
- Qué datos de Google Ads trae a Clarity (campos concretos): [SIN VERIFICAR] salvo los que cita la página: impresiones, coste y tasa de clics.

### Integración con GA4

Fuentes: `https://learn.microsoft.com/en-us/clarity/ga-integration/ga-integration` y `.../ga4-integration`.

- Une Clarity con una propiedad de Google Analytics para mostrar datos de GA en Clarity (panel de GA dentro de Clarity). Solo una propiedad web por proyecto de Clarity.
- Para GA4 manual hacen falta: ID de cuenta, nombre amistoso, ID de medición (`G-...`) y ID de propiedad.
- Limitaciones oficiales: Clarity no admite segmentos en GA4 y no envía la URL de reproducción a GA4 porque no acepta filas de cardinalidad alta.
- Si se desconecta, se elimina el vínculo de la cuenta de Google Analytics.

---

## 4. Consentimiento

Fuentes: `https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-consent-api-v2`, `.../consent-management`, `https://clarity.microsoft.com/blog/clarity-cookie-consent-update/` (31-10-2025).

| Aspecto | Dato |
|---|---|
| Obligación | Desde el **31-10-2025** Clarity exige una señal de consentimiento válida para visitas desde el EEE, el Reino Unido y Suiza para dar todas las funciones |
| Modo de consentimiento | Activado por defecto para usuarios del EEE, Reino Unido y Suiza. Conviene comprobarlo en los ajustes del proyecto |
| Sin consentimiento | La etiqueta carga, pero Clarity solo recoge datos sin cookies, asigna un identificador único por vista de página y no persiste la sesión. Funciones que dependen de cookies (grabaciones, embudos, mapas de calor) pueden quedar limitadas, incompletas o no estar disponibles |
| Consentimiento denegado tras darlo | Borra la cookie existente, termina la sesión y reinicia el seguimiento en modo sin consentimiento |
| Validez | Clarity trata el consentimiento como válido hasta 9 meses salvo actualización del usuario o exigencia local anterior |
| Estado por defecto en Consent Mode | `denied` hasta que se actualice el estado |
| Tipos | `analytics_storage` (denegado: solo datos sin cookies) y `ad_storage` (concedido: Clarity comparte datos con Microsoft Ads; denegado: no comparte) |
| API vigente | `window.clarity('consentv2', { ad_Storage: "granted" \| "denied", analytics_Storage: "granted" \| "denied" })`. Los dos parámetros son obligatorios y se escriben con esa capitalización en los ejemplos oficiales |
| API antigua | `window.clarity('consent', true)` aplica el mismo estado a todos los tipos. Marcada como en camino de retirada: no usar |
| Borrar cookies | `window.clarity('consent', false)` limpia las cookies de Clarity y detiene el seguimiento hasta nuevo consentimiento |
| Otras vías | Plataforma de gestión de consentimiento (CMP) compatible, plataformas de terceros y Google Consent Mode (recomendado para sitios que ya lo usan) |
| Apps móviles | La página indica que no se requiere acción inmediata |
| Comprobación recomendada | Que la señal se envíe justo después de cargar el script y antes de que se fijen cookies, y que las cookies de Clarity estén categorizadas como no esenciales en el banner |

Implicación para la auditoría: un sitio español con tráfico de la UE y sin señal de consentimiento hacia Clarity infrarrepresentará sesiones y funciones. Los datos de Clarity y de Google Ads/GA4 no cuadrarán por esa razón.

---

## 5. Servidor MCP oficial

Existe: `github.com/microsoft/clarity-mcp-server`, licencia MIT, paquete npm `@microsoft/clarity-mcp-server`. Requiere Node.js 16 o superior y el mismo token de la API de exportación. Ejecución: `npx @microsoft/clarity-mcp-server --clarity_api_token=<token>`.

Herramientas que documenta el README:

| Herramienta | Qué hace |
|---|---|
| `query-analytics-dashboard` | Devuelve datos del panel con una consulta en lenguaje natural (por ejemplo, sesiones desde un país en 3 días, navegadores más usados) |
| `list-session-recordings` | Lista grabaciones de sesión filtrando por URL, dispositivo, navegador, SO, país, ciudad, etc. |
| `query-documentation-resources` | Responde con fragmentos de la documentación de Clarity |

El README también menciona un parámetro `token` para una herramienta `get-clarity-data` que no figura en la lista anterior [SIN VERIFICAR si existe como herramienta separada]. El servidor hereda los límites del token de exportación (10 llamadas al día): [SIN VERIFICAR] que cada herramienta consuma una llamada.

---

## 6. Qué no está en la API (solo interfaz)

La página de la API describe un único punto de acceso, de datos del panel de los últimos 1 a 3 días. No documenta endpoints para:

- Mapas de calor (clics, scroll, áreas, atención, conversión). Se ven y descargan (CSV o PNG) desde la interfaz; hasta 100.000 vistas de página por mapa.
- Grabaciones de sesión (el MCP las lista, pero la API de exportación no las expone como endpoint documentado).
- Filtros y segmentos guardados. La API solo admite hasta tres dimensiones de desglose; los más de 30 filtros de la interfaz (navegador, ubicación, acciones, ruta, tráfico, rendimiento, etiquetas personalizadas) y los segmentos no son parámetros de la API.
- Embudos, eventos inteligentes y paneles de Copilot (Campaign Insights).
- Métricas de rendimiento web (puntuación, LCP, INP, CLS) como parámetros de la API: [SIN VERIFICAR].

Fuente de las capacidades de la interfaz: `https://learn.microsoft.com/en-us/clarity/filters/clarity-filters`, `.../heatmaps/scroll-maps`.

---

## 7. API de cliente (para el estado del seguimiento en el sitio)

Fuente: `https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-api`. El ID de Clarity hace de clave. Llamadas relevantes: `window.clarity('consentv2', ...)`, `window.clarity("identify", ...)`, `window.clarity("set", clave, valor)` para etiquetas, `window.clarity("event", nombre)` para eventos, y `window.clarity("upgrade", ...)` para priorizar grabaciones. Atributos HTML `data-clarity-mask="true"` y `data-clarity-unmask="true"`.

---

## Cambios recientes

| Fecha | Cambio | Fuente |
|---|---|---|
| 05-12-2025 | Última actualización de la página de la API de exportación | clarity-data-export-api |
| 01-12-2025 | Última actualización de la página de métricas semánticas | semantic-metrics |
| 31-10-2025 | Entra en vigor la exigencia de consentimiento para EEE, Reino Unido y Suiza; consentv2 sustituye a la API antigua | consent-management, blog oficial |
| 31-10-2025 | Última actualización de la guía de integración de publicidad | ad-getting-started |
| 29-09-2025 | Campaign Insights solo para Google Ads | ad-campaign-insights |
