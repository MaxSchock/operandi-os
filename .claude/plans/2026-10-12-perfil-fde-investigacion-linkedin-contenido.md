# Perfil Forward Deployed Engineer: investigación, encaje, LinkedIn y contenido

Estado: hecho 12-10-2026 (fases 1 a 4). Entregables en `projects/briefs/marca-personal/fde/`: `fase1/` (12 informes), `fase2-encaje.md` (matriz, consejo ronda 1 en `fase2-consejo/`), `fase3-perfil-linkedin.md` (borrador 2, consejo ronda 2 en `fase3-consejo/`, ojo frío antes y después), `fase4-contenido.md` (calendario de 4 semanas y cambios al brief). 13-10: perfil revisado con Max (borrador 4) y APLICADO en LinkedIn por Unipile (titular, About, puestos, aptitudes nuevas); brief del motor `operandi-canary.yaml` creado y desplegado (0d5dc57). Pide a Max: quitar a mano las 36 aptitudes viejas, URL, banner, destacados, idiomas y perfil alemán (lista en fase3, cabecera); pedir los 3 posts desde el panel; aprobar el calendario de la fase 4 releído con el lector nuevo; permiso de la imprenta para la pieza 1. Entidad: personal (marca de Max). Para quién: Max. Para qué: saber con datos qué exige el perfil FDE, qué parte cumple ya con pruebas, y dejar listas la propuesta de perfil de LinkedIn y los cambios en la estrategia de contenido del panel.

Continúa `projects/briefs/marca-personal/brief.md` (01-10), que ya fijó el posicionamiento FDE pero apoyado en una sola fuente (un blog) y sin tocar el perfil de LinkedIn. Todo lo que salga de aquí se guarda en `projects/briefs/marca-personal/fde/`.

## Fase 1 · Investigación (dos carriles en paralelo)

**1A. Qué exige el perfil (5 agentes de búsqueda, uno por pregunta, más un verificador).**

| # | Pregunta | Fuente que manda |
|---|---|---|
| 1 | Origen y definición: qué hace un FDE en Palantir y en qué se diferencia de solutions engineer, consultor de implantación y «AI deployment strategist» | Textos de las propias empresas y de gente que ha tenido el puesto |
| 2 | Requisitos reales hoy: 30-40 ofertas vigentes (OpenAI, Anthropic, Palantir, Databricks, Scale, Sierra, Cohere, Mistral, ElevenLabs, startups de agentes y las europeas) | La oferta publicada, citada con URL y fecha |
| 3 | Competencias agrupadas: técnicas (código en producción, datos, evaluación de LLM, integración, seguridad y permisos), de cliente (descubrimiento, trato con dirección, gestión de expectativas) y de producto (devolver lo aprendido al producto) | Recuento sobre las ofertas del punto 2, no opinión |
| 4 | Mercado: volumen y sueldos en Europa (DACH, Benelux, España, remoto), y si existe el FDE independiente o por proyecto o es solo puesto de plantilla | Ofertas, informes de empleo, perfiles reales |
| 5 | Cómo se presentan en LinkedIn 15-20 FDE reales (titular, «Acerca de», cómo cuentan los casos, qué destacan) y qué publican los que tienen audiencia; más 5-8 perfiles de cualquier oficio que se posicionan con humor sin dejar de vender (mecánica del tono jugón) | Perfiles y posts públicos |
| 6 | SEO del perfil (orden de Max, 12-10): cómo ordena LinkedIn los perfiles en su buscador y en Recruiter, qué términos buscan reclutadores y compradores (EN/DE/ES), cómo indexa Google el perfil, qué penaliza. Se cruza en la fase 3: las palabras van donde pesan (titular, aptitudes, títulos de puesto) y el «Acerca de» queda para el tono | Ayuda de LinkedIn y especialistas con pruebas, no opinión |

El verificador repasa cada cifra contra su fuente y tira lo que no se sostenga. Entra aquí el «800 % en 18 meses» que ya está publicado en la fila 8 y sale de un solo blog.

Los perfiles del punto 5 se leen por Unipile con la cuenta de Max (receta `reference_max_linkedin_unipile`), no con Apify ni scraping: cada lectura es una visita a ese perfil desde su cuenta. Las ofertas se buscan en la web con fecha de consulta; nada de memoria (corte de conocimiento junio 2026).

**1B. Qué he hecho yo de verdad (inventario con pruebas, solo lectura).** Lo hace un fork de la sesión (hereda el contexto de clientes), no un agente limpio.

- Perfil de LinkedIn actual tal cual está hoy, leído por Unipile (titular, «Acerca de», experiencia, aptitudes, destacados).
- **Ojo frío:** un agente sin contexto lee ese perfil y dice qué cree que hace Max y para qué lo contrataría. Se repite en la fase 3 sobre la propuesta: medida de antes y después.
- Casos por cliente con la prueba detrás: Hemmersbach, Suritec, RHP/Linus, Jaeger, Operandi (outreach, content-engine, motor de vídeo, panel), Falkenlead. De cada uno: qué sistema corre en producción, con qué datos y permisos del cliente, cifras medibles, trato directo con quién. Fuentes: session-logs, briefs de cliente, `docs/horas-ledger.csv`, repos.
- Formación y trayectoria (CLAUDE.md, `context/me.md`, `brand-context/voice/`).

## Fase 2 · Encaje (un documento, para Max)

Matriz competencia por competencia con tres estados: **cumplo con prueba** (caso y cifra), **cumplo a medias** (qué falta), **hueco**. Sin maquillar: los huecos previsibles son ingeniería de software clásica (carrera técnica, código propio en la base de código del cliente, revisión por pares) y que el puesto nace en empresas de producto mientras que yo despliego sistemas míos. La matriz dice si esos huecos invalidan la etiqueta, la matizan («independiente») o se cubren con algo concreto.

Tres contrapesos para no confirmarnos la hipótesis a nosotros mismos:

- **Oferta fantasma.** De las 30-40 ofertas sale la descripción del puesto FDE «medio». Un agente en papel de recruiter puntúa el inventario de Max contra ella sin saber que la hipótesis es nuestra.
- **Abogado del diablo.** Un agente con el encargo contrario: demostrar con las pruebas delante que la etiqueta FDE no corresponde. Si no lo consigue, la etiqueta aguanta; si lo consigue en parte, eso va a la matriz como hueco.
- **Consejo de sabios (ronda 1).** Cuatro voces, cada una recibe la matriz y las tres decisiones sin ver a las demás; yo integro. Voces: quien contrata FDE en un laboratorio de IA · un FDE veterano (Palantir) · un comprador de Max (dirección de una mediana alemana: ¿entiende «Forward Deployed Engineer» o hace falta una línea en llano?) · un escéptico de marca personal («¿esto vende o solo suena bien?»).

Sale también de aquí una recomendación sobre las tres decisiones que el brief tiene abiertas desde el 01-10, porque las fases 3 y 4 dependen de ellas:

1. Para qué es la marca: clientes propios o que una empresa de producto me contrate como FDE.
2. Idioma de LinkedIn: inglés o castellano.
3. Falkenlead: si el titular FDE choca con el puesto a jornada completa.

**Parada: Max lee la matriz y decide las tres.** Es la única parada del plan.

## Fase 3 · Propuesta de perfil de LinkedIn

Texto listo para pegar, sección por sección, con el actual al lado: titular, «Acerca de», cada puesto de experiencia (Operandi, KIsult, Falkenlead, Rotary), aptitudes en su orden, destacados (qué tres piezas), banner y URL. En el idioma decidido en la fase 2, casos de cliente anonimizados como en los posts.

**Tono (orden de Max, 12-10).** Que no suene a IA ni a LinkedIn: jugón, como quien no se toma demasiado en serio pero sí el trabajo. Reglas concretas:
- Registro B del perfil de voz (`brand-context/voice/register-b-linkedin.md`): humor, datos, cierre con gracia.
- Sin buzzwords: nada de «passionate», «leverage», «cutting-edge», «AI-driven», «transform», «empower», «results-oriented», ni listas de palabras clave en el titular. Lo que se diga se dice con un caso y una cifra, o con una broma, no con un adjetivo.
- La etiqueta FDE aparece una vez y se explica en llano al lado («me meto en tu empresa y no salgo hasta que funciona»). El resto del perfil demuestra, no proclama.
- Pasa por `frases-ia.json` (`guard-documento.py`) y por `tool-humanizer` antes de entregar; cualquier sección por debajo de 8/10 se reescribe.
- Referencias de tono: en la fase 1, punto 5, se buscan también 5-8 perfiles de LinkedIn (FDE o no) que se posicionan con humor y aun así venden, para copiar la mecánica.

Antes de entregar: **consejo de sabios (ronda 2)** sobre el borrador, las cuatro voces de la fase 2 más un lector nativo que lo lea como un reclutador de Londres; y el **ojo frío** de 1B repite su lectura sobre la propuesta.

No se toca el perfil: cambiarlo es visible para clientes y para Falkenlead, lo aplica Max o lo aplico yo con su OK explícito.

## Fase 4 · Estrategia de contenido del panel

Revisar contra lo investigado, sin rehacer lo que funciona:

- Los cuatro formatos del brief («¿Demo o desplegado?», parte de campo, cópialo, diario del personaje): cuáles demuestran competencias que la matriz dice que cumplo y cuáles huecos conviene cubrir publicando.
- Qué temas de las ofertas reales no toca hoy ningún formato (previsible: evaluación, permisos y datos, adopción por la gente del cliente).
- Lo que falta en el motor para que la marca personal vaya en serio: brief del cliente `operandi-canary` (no existe y el idioma está en `en`), `brand-context/positioning` e `icp` (vacíos), fotos reales como referencia.
- Entrega: lista de cambios propuestos al brief y calendario de 4 semanas de temas (títulos y ángulo, no posts escritos). Los posts se crean después, en el panel y con imagen, cuando Max apruebe el calendario.

## Agentes y modelos

| Trabajo | Agentes | Modelo | Por qué |
|---|---|---|---|
| Búsqueda y extracción (1A puntos 1-5) | 5 | Sonnet 5.5 | Leer mucho y volcar tablas; el criterio lo pone el formato |
| Inventario de Max (1B) | 1 fork | Fable 5.1 (hereda) | Ya conoce los clientes y los session-logs |
| Ojo frío (1B y fase 3) | 1 + 1 | Opus 5.5 | Sin contexto a propósito |
| Verificador de cifras | 1 | Opus 5.5 | Adversarial, pocos tokens |
| Recruiter de la oferta fantasma, abogado del diablo | 2 | Opus 5.5 | Juicio contra la hipótesis |
| Consejo de sabios (2 rondas) | 4 + 5 | Fable 5.1 | Juicio con matiz, aislados entre sí |
| Síntesis, matriz, perfil, calendario | yo | Fable 5.1 | |

Todo es lectura: va en paralelo sin tocar la regla de cargas pesadas. Unos 21 agentes cortos en total.

## Coste y tiempo

- Fase 1: unos 20-30 min de reloj con los agentes en paralelo; gasto solo en tokens y búsquedas (Unipile ya pagado; sin Apify).
- Fases 2 a 4: 1,5 a 2 h de sesión en total. Tokens de todo el plan: 8-15 $ orientativos.

## Qué no entra

Escribir posts nuevos, cambiar el perfil, tocar las filas 6 a 8 ya programadas o publicadas, y el personaje (Günther).
