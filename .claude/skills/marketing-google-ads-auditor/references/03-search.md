# 03 · Search
> Consultado el 08-10-2026. Fuentes oficiales (support.google.com/google-ads, support.google.com/adspolicy, developers.google.com/google-ads). Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente. Los nombres de campo de API se citan solo si aparecen en una página oficial leída; el resto va como [SIN VERIFICAR].

## Concordancias de palabras clave
### Cómo funciona
- Amplia (por defecto, sin símbolo): puede mostrarse en búsquedas relacionadas, incluso sin el significado literal de la palabra. Google dice que debe usarse con Smart Bidding. Considera actividad reciente del usuario, contenido de páginas de destino/recursos y otras palabras clave del mismo grupo.
- Frase ("zapatillas de tenis"): búsquedas que incluyen el significado de la palabra, que puede expresarse de forma más específica. Exacta ([zapato rojo]): mismo significado o misma intención. Es la que más control da y menos búsquedas cubre.
- Cada tipo más amplio cubre todas las consultas de los más estrechos, más otras. Palabras clave casi duplicadas ("coche rojo" y "rojo coche") se tratan como duplicados: entra la de mayor Ad Rank, solo entra una puja a la subasta.
- Prioridad (orden documentado): 1) palabra clave exacta idéntica a la búsqueda, por encima de cualquier amplia/frase; 2) frase y amplia idénticas comparten nivel; 3) relevancia por IA entre grupos de anuncios; 4) empate: gana el mayor Ad Rank. La página "How matching works" resume: se priorizan las palabras clave idénticas a la búsqueda en todos los tipos de concordancia. Las palabras clave con estado «volumen de búsquedas bajo» se excluyen de la recuperación.
- Ajuste de campaña "Palabras clave de concordancia amplia" (campaign-level broad match): convierte frase y exacta a amplia; se priorizan como si existieran versión amplia y exacta. Solo disponible con Smart Bidding basado en conversiones. Desde septiembre de 2026 se migra automáticamente a AI Max (ver AI Max). Al migrar, la priorización de "como si fuera exacta" desaparece; para conservarla hay que añadir copias exactas.
- Estructura recomendada por Google: un grupo por tema con todas las concordancias juntas y concordancia amplia (ver Estructura de cuenta).

### Estados de palabra clave y qué recomienda Google
| Estado | Significado oficial | Acción recomendada por Google |
|---|---|---|
| Apta (limitada) · Volumen de búsquedas bajo | Casi nunca apta para mostrarse por muy poco tráfico; puede ser irrelevante, demasiado específica o inusual. Se reactiva si sube el volumen | Buscar términos de más volumen en Keyword Planner; probar frase o amplia |
| Apta (limitada) · Rara vez se muestra por nivel de calidad bajo | El Nivel de calidad es tan bajo que casi no se muestra | Mejorar relevancia del anuncio, experiencia de página y CTR esperado, o quitarla y añadir una más relevante |
| Apta (limitada) · Por debajo de la puja de primera página | Activa pero no aparece en la primera página, probablemente por Ad Rank | Mejorar componentes del Ad Rank: puja y Nivel de calidad |
| Pausada (por poca actividad) | 0 impresiones en 13 meses, la pausa Google automáticamente | Sin arreglo directo indicado |
| No apta | Campaña o grupo en estado no servible | Reanudar, rehabilitar o ajustar fechas |
| Rechazada | Normalmente por política (destino o URL final) | Revisar el motivo en el estado y corregir el anuncio |

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Palabras clave en «volumen bajo» o «rara vez se muestra» | Son no aptas o casi no se muestran; Google propone cambiar o quitar | Pestaña Palabras clave, columna Estado. API: `ad_group_criterion.system_serving_status` (campo confirmado, valores [SIN VERIFICAR]) | https://support.google.com/google-ads/answer/2453978?hl=en |
| Pausadas por poca actividad | 13 meses sin impresiones | Estado "Paused" con motivo de baja actividad | https://support.google.com/google-ads/answer/2453978?hl=en |
| Misma palabra clave en varias concordancias y grupos | Google recomienda un grupo temático con todas las concordancias; duplicar divide los datos de Smart Bidding | Informe de palabras clave filtrado por texto repetido | https://support.google.com/google-ads/answer/14752782?hl=en |
| Amplia sin Smart Bidding | Google indica que amplia debe usarse con Smart Bidding; el ajuste de campaña solo existe con Smart Bidding de conversiones | Estrategia de puja de la campaña vs. concordancias de las palabras clave | https://support.google.com/google-ads/answer/7478529?hl=en |
| Ajuste de campaña «amplia» activo | Migración automática a AI Max desde septiembre de 2026 | Configuración de campaña > Palabras clave de concordancia amplia. API: `Campaign.broad_match_migration_date_time` (solo lectura, v25+); `Campaign.keyword_match_type` está obsoleto | https://support.google.com/google-ads/answer/13389795 |
| Prioridad esperada exacta > amplia | La exacta idéntica va primero; con ajuste de campaña/AI Max cambia | Informe de términos de búsqueda: columna Palabra clave y tipo de concordancia | https://support.google.com/google-ads/answer/2497836?hl=en |

## Palabras clave negativas
### Cómo funciona
- Amplia: bloquea si la búsqueda contiene todos los términos en cualquier orden (no bloquea si solo contiene algunos). Frase: mismo orden, admite palabras extra. Exacta: mismo orden y sin palabras extra.
- No admiten variantes cercanas ni derivaciones: "flores" como negativa amplia bloquea "flores rojas" pero no "flor roja". Hay que añadir sinónimos, singular/plural y erratas. Mayúsculas y faltas de ortografía sí se gestionan solas (según 2453972); la página de errores (9701952) dice que no casan erratas ni variantes (hay que añadirlas). Contradicción interna de la documentación, tratar erratas como no cubiertas.
- Acentos y "&" crean palabras distintas ("café" vs "cafe"). Si la búsqueda tiene más de 16 palabras y la negativa está después de la 16ª, puede no bloquear.
- Niveles: grupo de anuncios, campaña, listas compartidas (aplicables a campañas) y cuenta (aplican a toda la inventario de búsqueda y Shopping de los tipos de campaña relevantes: Search, PMax, App, Shopping, Smart, Local).
- Límites: cuenta 1.000; lista compartida 5.000 palabras; 20 listas por cuenta; una lista se aplica a hasta 1.000 campañas a la vez; 10.000 negativas por campaña (campaña, sin contar listas, según tabla de límites). Límite por grupo de anuncios [SIN VERIFICAR]. Display y vídeo: se consideran 1.000 en cuenta.
- Conflictos: una negativa que coincide con una palabra clave positiva impide que se muestre. No existe un informe dedicado de conflictos; el diagnóstico de palabras clave detecta «una palabra clave negativa impide que se muestre tu anuncio» probando solo la versión exacta.
- Google advierte que demasiadas negativas pueden reducir cuántos clientes ven los anuncios.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Negativa que bloquea una palabra clave activa | "Las negativas no deben solaparse con tus palabras clave" | Diagnóstico de palabras clave (solo prueba exacta); revisar listas y niveles a mano | https://support.google.com/google-ads/answer/7102995?hl=en |
| Listas creadas pero no aplicadas | Una lista sin asociar a campaña no tiene efecto | Biblioteca compartida > Listas de exclusión, columna campañas | https://support.google.com/google-ads/answer/9701952 |
| Variantes de negativas | No casan plurales, derivaciones ni erratas; añadir cada una | Informe de términos de búsqueda: términos que una negativa debería haber cortado | https://support.google.com/google-ads/answer/2453972?hl=en |
| Tamaño de negativas | Cuenta 1.000; lista 5.000; 20 listas; campaña 10.000 | Ajustes de cuenta > Palabras clave negativas; Biblioteca compartida | https://support.google.com/google-ads/answer/6372658?hl=en |
| Negativas de cuenta existentes | 1.000 máx., Admin > Configuración de cuenta > Palabras clave negativas | Misma ruta | https://support.google.com/google-ads/answer/11396330?hl=en |
| Cuenta sin ninguna negativa | Google no fija mínimo; práctica de auditoría | Conteo en los tres niveles | [SIN VERIFICAR] |

## Informe de términos de búsqueda
### Cómo funciona
- Muestra los términos que un número significativo de usuarios buscó y que generaron impresiones y clics, con la palabra clave que casó y el tipo (columna Palabra clave oculta por defecto: columnas > Atributos). Valores de tipo de concordancia: Exacta, Exacta (variante cercana), Frase, Frase (variante cercana), Amplia. Un término puede tener tipo distinto al de la palabra clave.
- Oculta los términos con poca actividad por privacidad (umbral no publicado). Esos aparecen solo agrupados en las estadísticas de términos de búsqueda ("search terms insights"), por temas y subtemas o en «otras consultas».
- Las etiquetas de temas se generan con los últimos 56 días, así que pueden incluir términos que ya no activan anuncios o están excluidos. Las cifras pueden diferir del informe por conversiones con retraso.
- DSA y Shopping no usan palabras clave: el campo palabra clave va vacío y el tipo muestra "Exacta". Con AI Max el informe añade "AI Max" como tipo y una columna de origen (ampliación de concordancia amplia o concordancia sin palabras clave).
- Conversiones de visitas a tienda y ventas en tienda no son compatibles con el informe. En sitios de partners de búsqueda los términos pueden aparecer más largos o con otro formato.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Proporción de gasto en términos no visibles | Los términos de poca actividad se omiten; el resto va a «otras consultas» | Comparar total del informe con total de campaña; ver Estadísticas de términos de búsqueda | https://support.google.com/google-ads/answer/2472708?hl=en |
| Términos irrelevantes con gasto | Añadir como negativas | Informe de términos filtrado por coste > 0 y conversiones = 0 | https://support.google.com/google-ads/answer/2472708?hl=en |
| Tipo "variante cercana" dominante | Es normal en exacta/frase (misma intención) | Columna Tipo de concordancia | https://support.google.com/google-ads/answer/2472708?hl=en |
| Origen AI Max | Columna de origen y tipo "AI Max" | UI. API: vista `ai_max_search_term_ad_combination_view` (confirmada) | https://developers.google.com/google-ads/api/docs/campaigns/ai-max-for-search-campaigns/getting-started |
| Vista de API del informe | `search_term_view` existe como recurso con métricas | API (campos detallados [SIN VERIFICAR], página de referencia demasiado larga para extraer) | https://developers.google.com/google-ads/api/reference/rpc/v22/SearchTermView |

## Nivel de calidad
### Cómo funciona
- Escala 1 a 10 por palabra clave. Es una herramienta de diagnóstico, no un KPI ni una entrada de la subasta. No debe optimizarse ni agregarse con otros datos.
- Tres componentes: CTR esperado, relevancia del anuncio, experiencia en la página de destino. Cada uno: Superior a la media, Media o Inferior a la media, frente a anunciantes que mostraron anuncios para la misma búsqueda en los últimos 90 días. Se calcula con historial de búsquedas exactas, por eso cambiar la concordancia no lo modifica.
- «--» (guion): no hay suficientes búsquedas que coincidan exactamente con la palabra clave para calcular. Google sugiere palabras clave de más volumen (Keyword Planner) y ampliar concordancias para reunir datos.
- Si Media o Inferior: oportunidad de mejora. Recomendaciones literales por componente: CTR esperado: oferta más atractiva, ajustar a la intención de la palabra clave, destacar un beneficio único, probar llamadas a la acción conectadas con la página, verbos de acción, ser más específico. Relevancia: adaptar el texto a los términos de búsqueda, dividir grupos con muchas palabras clave, agrupar por temas (mover el grupo a otra campaña no cambia la calidad). Página de destino: dar lo que el usuario busca, coherencia anuncio-página, web adaptada a móvil, mejorar velocidad de carga; no hace falta que la frase exacta aparezca en la página; la tasa de conversión no afecta al estado.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Nivel de calidad 1-4 o componentes «inferior a la media» | Diagnóstico, no objetivo; mejorar el componente concreto | Columnas Nivel de calidad, Exp. página destino, CTR esp., Relevancia (menú columnas > Nivel de calidad). API: `ad_group_criterion.quality_info.quality_score`, `creative_quality_score`, `post_click_quality_score`, `search_predicted_ctr` (campos confirmados; enums [SIN VERIFICAR]) | https://support.google.com/google-ads/answer/6167118?hl=en |
| «--» en muchas palabras clave | Falta de búsquedas exactas; no es un error | Columna Nivel de calidad vacía | https://support.google.com/google-ads/answer/6167118?hl=en |
| Experiencia de página inferior a la media | Móvil, velocidad, coherencia con anuncio | UI; comparar con la página de destino | https://support.google.com/google-ads/answer/6167130?hl=en |
| Relevancia baja con grupos grandes | Dividir por temas | Nº de palabras clave y temas por grupo | https://support.google.com/google-ads/answer/6167130?hl=en |
| Histórico del nivel | Columnas "(hist.)" y segmento por día | UI | https://support.google.com/google-ads/answer/6167118?hl=en |

## Ad Rank y umbrales
### Cómo funciona
- Ad Rank decide si un anuncio puede mostrarse y su posición. Se calcula en cada subasta y para cada posición. Seis factores: puja; calidad del anuncio y de la página de destino; Ad Rank mínimo; competitividad de la subasta; contexto de la búsqueda; impacto esperado de recursos y otros formatos.
- Umbrales: Google no publica cifras reales. Su ejemplo simplificado usa 0 para mostrarse en cualquier sitio y 40 para aparecer sobre los resultados orgánicos.
- La calidad influye en: pasar el Ad Rank mínimo, el CPC real (más calidad puede bajarlo) y la elegibilidad de recursos y formatos.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Cuota de impresiones perdida por Ad Rank | Ad Rank bajo = puja o calidad insuficiente | Columna "Cuota de impr. perdida (ránking)". API: `metrics.search_rank_lost_impression_share` [SIN VERIFICAR en doc] | https://support.google.com/google-ads/answer/1722122?hl=es |
| Recursos que no se muestran | Solo salen si el Ad Rank es suficiente | Informe de recursos, impresiones por recurso | https://support.google.com/google-ads/answer/1722122?hl=es |
| Palabras clave por debajo de la puja de primera página | Mejorar puja y calidad | Estado de la palabra clave | https://support.google.com/google-ads/answer/2453978?hl=en |

## Anuncios adaptables de búsqueda (RSA)
### Cómo funciona
- Titulares: 3 a 15, 30 caracteres cada uno. Descripciones: 2 a 4, 90 caracteres. Rutas visibles (path): 15 caracteres cada campo; los caracteres de doble ancho cuentan doble. Se muestran hasta 3 titulares y 2 descripciones (API). URL final máx. 2.048 caracteres (página de especificaciones, que además indica "1-15 titulares"; la ayuda de RSA y la API indican mínimo 3).
- Número por grupo: máximo 3 RSA habilitados por grupo de anuncios (tabla de límites). [SIN VERIFICAR, comprobado el 08-10-2026: la página 6372658 solo da el límite de 3 y no contiene esta recomendación] Google recomienda al menos 2 RSA con eficacia Buena o Excelente y URL final propia; pasar de 1 a 2 RSA se asoció a +6,6 % de conversiones y de 2 a 3 a +3,7 % a CPA similar.
- Eficacia del anuncio (Ad Strength): niveles Incompleta, Baja, Media, Buena, Excelente. Estima la eficacia potencial según coincidencia de los recursos con las palabras clave: titulares y descripciones con palabras clave relevantes, cantidad (hasta 15 y 4) y 6 o más enlaces de sitio en cuenta, campaña o grupo. No determina si el anuncio es apto, ni se usa en Ad Rank, nivel de calidad o subastas ganadas. Pasar de Baja a Excelente se asoció a +15 % de clics y conversiones de media.
- Fijación (pinning): fijar en Titular 1, Titular 2 o Descripción 1 garantiza esa posición; Titular 3 y Descripción 2 pueden no mostrarse siempre. Si se fijan todas las posiciones, los recursos sin fijar no se muestran. Reduce combinaciones y baja la eficacia: no recomendada de forma general; si se usa, fijar 2 o 3 recursos distintos por posición y solo 1 o 2 titulares esenciales. Con ampliación de URL final activa, la fijación no se respeta.
- Rotación: ajustes "Optimizar" (prefiere los de mejor rendimiento) y "No optimizar" (rotar indefinidamente, no recomendado para la mayoría). Con Smart Bidding se usa Optimizar automáticamente. Titular 1 y Descripción 1 suelen mostrarse enteros; el resto puede recortarse.
- Recursos creados automáticamente (flexibilidad): titulares en la línea de descripción, hasta 2 titulares no usados como enlaces tipo sitelink, y recursos no usados de otros RSA del mismo grupo. Personalización de texto (antes recursos creados automáticamente) está dentro de AI Max y no cuenta para los límites de 15 y 4; solo para anunciantes con recursos en inglés en el caso de IA generativa.
- Personalizadores: máx. 40 atributos de personalizador por cuenta; valores de hasta 90 caracteres; se resuelven por palabra clave, grupo, campaña, cuenta y valor por defecto. Si faltan valores el RSA no se puede revisar. No se admiten en la URL final. La función IF no se admite en RSA. Cuenta atrás y personalizadores existen en RSA; inserción de ubicación existe pero su sintaxis no se pudo confirmar [SIN VERIFICAR].
- Inserción de palabras clave: `{keyword:texto por defecto}`; mayúsculas según el patrón (`keyword`, `Keyword`, `KeyWord`). No en sanidad ni contenido sexual; marcas restringidas no se insertan; el texto por defecto debe caber en el límite.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Nº de RSA por grupo | Máx. 3 habilitados (la recomendación de >= 2 está [SIN VERIFICAR]) | Pestaña Anuncios por grupo | https://support.google.com/google-ads/answer/6372658?hl=en |
| Titulares y descripciones | 3 a 15 y 2 a 4; 30 y 90 caracteres | Detalle del anuncio. API: `ResponsiveSearchAdInfo.headlines/descriptions` | https://support.google.com/google-ads/answer/7684791?hl=es |
| Eficacia Baja/Incompleta | Añadir titulares únicos, palabras clave, 6+ enlaces de sitio | Columna Eficacia del anuncio. API: `ad_group_ad.ad_strength` (enum [SIN VERIFICAR]) | https://support.google.com/google-ads/answer/9921843?hl=es |
| Fijación excesiva | Fijar solo 1 o 2 titulares esenciales | Ver posiciones fijadas. API: `AdTextAsset.pinned_field` (HEADLINE_1..3, DESCRIPTION_1..2) | https://developers.google.com/google-ads/api/docs/responsive-search-ads/overview |
| Todos los anuncios con la misma URL final | Google recomienda URL final propia por RSA | Columna URL final | https://support.google.com/google-ads/answer/6167122?hl=en |
| Palabra clave en titulares | Incluir al menos una | Revisión de texto vs. palabras clave del grupo | https://support.google.com/google-ads/answer/7684791?hl=es |
| Rotación en "No optimizar" | No recomendada; con Smart Bidding se ignora | Ajuste de rotación en grupo/campaña | https://support.google.com/google-ads/answer/112876?hl=en |
| Recursos de texto automáticos activos | Personalización de texto en AI Max; se puede desactivar con "Off" | Configuración de campaña; informe de recursos a nivel de campaña. API: `Campaign.asset_automation_settings` (`TEXT_ASSET_AUTOMATION`) | https://support.google.com/google-ads/answer/16740321?hl=en |
| Personalizadores | 40 atributos; sin valores no se revisa el anuncio | Datos de empresa / atributos | https://support.google.com/google-ads/answer/10711524?hl=en |
| Inserción de palabras clave | Sintaxis `{keyword:..}`; no en URL final | Texto de titulares | https://support.google.com/google-ads/answer/6371157 |
| Anuncios ya no admitidos | Llamadas (call ads) retirados el 03-10-2025, usar recursos de llamada en RSA | Tipo de anuncio | https://support.google.com/google-ads/announcements/9048695?hl=en |

## Recursos (antes extensiones)
### Cómo funciona
- Gratis de añadir; se cobra el clic como siempre (máx. 2 clics por impresión). Solo se muestran si se predice que mejoran el rendimiento y el Ad Rank es suficiente. Niveles: cuenta, campaña, grupo (el más específico manda en llamada, promoción, callouts; los de todos los niveles de la misma rama de jerarquía pueden servir juntos en enlaces de sitio). La página general recomienda elegir cuenta o campaña.
- Enlaces de sitio: texto 25 caracteres (12 en idiomas de doble ancho); mínimo 2 para mostrarse; hasta 6 en ordenador y 8 en móvil en Search; recomendado al menos 6 con descripciones en grupos/campañas de mucho volumen (mejora la eficacia) y 4 como mínimo a nivel de cuenta.
- Textos destacados (callouts): 25 caracteres (12 doble ancho); hasta 10 según espacio y dispositivo; sin mínimo ni recomendación numérica en la página.
- Fragmentos estructurados: encabezado de una lista (Servicios, Marcas, Tipos, Modelos, Estilos, Destinos, Cursos, etc.); mínimo 3 valores, recomendado 4 o más; máximo y caracteres no indicados; encabezado y valores deben coincidir (causa principal de rechazo).
- Llamada: número E.164 estricto, sin números virtuales/premium/fax; verificación de dominio con Search Console enlazada o etiqueta gtag.js en el HTML (no vale vía gestor de etiquetas); inserción dinámica de número o seguimiento de terceros puede impedir la verificación automática; informes de llamadas solo en Red de búsqueda; programable por horario.
- Ubicación: requiere vincular un perfil de empresa (Business Profile) o ubicaciones de cadena; hasta 10 ubicaciones de Google Maps por cuenta; ubicaciones cerradas no se muestran; solo un tipo de recurso de ubicación por cuenta. Nivel campaña anula cuenta.
- Imagen (Search): cuadrada 1:1 obligatoria (mín. 300x300, recomendado 1200x1200), horizontal 1,91:1 opcional (mín. 600x314, rec. 1200x628); PNG o JPG hasta 5.120 KB; máx. 20 por campaña; recomendado al menos 4 únicas (una cuadrada y una horizontal) en grupo o campaña. Requisitos de cuenta: abierta 60 días o más, buen historial de política, campañas activas, anuncios de texto activos y gasto en Search mayor que 0 en 30 días, vertical apta. Sin texto, logos ni superposiciones añadidas digitalmente.
- Formulario de clientes potenciales: requiere URL de política de privacidad, buen historial y vertical apta; para formularios abiertos desde el titular de un anuncio de Search aplica gasto superior a 1.000 USD por cuenta (o 15.000 USD entre todas) y verificación del anunciante; estrategia de puja orientada a conversión y objetivo de conversión de formulario; solo RSA; Google conserva los leads 60 días (CSV: últimos 30 días); webhook disponible hacia CRM. La página de políticas indica un umbral distinto (más de 50.000 USD) [conflicto entre páginas; ver fuente de política].
- Precio: mínimo 3 elementos (recomendado 5 o más), máximo 8 tarjetas; encabezado y descripción hasta 25 caracteres; español admitido, EUR admitido; cada fila lleva encabezado, precio, descripción y URL final.
- Promoción: sin mínimo/máximo; admite ocasión (con fechas), código y límites; las promociones con ocasión deben crearse o editarse dentro de los 6 meses previos a su inicio; las que llevan 6 meses sin modificar dejan de servir o se pausan.
- Nombre y logotipo de empresa: nombre máx. 25 caracteres que debe coincidir con el dominio o nombre legal verificado en la verificación del anunciante (o marca verificada con marca registrada activa); logo 1:1, recomendado 1200x1200 y mínimo 128x128, PNG/JPG hasta 5.120 KB, válido en modo claro y oscuro. Requisitos: gasto en Search en los últimos 28 días y verificación del anunciante completada (el estado puede tardar 5 a 7 días laborables). En Search: un nombre y un logo en cuenta más uno por campaña. Aprobación no garantiza servir (se muestra icono de globo con la URL visible). Nombre y logo dinámicos pueden crearse solos (nombre dinámico solo en inglés, francés, japonés y alemán, y solo si no hay uno subido) [español no figura].
- Recursos automáticos a nivel de cuenta (Assets > Asociaciones > Recursos automáticos de cuenta > Configuración avanzada): enlaces de sitio dinámicos, fragmentos estructurados dinámicos, ubicación automática, valoraciones de vendedores, textos destacados dinámicos, información de empresa dinámica, imágenes dinámicas, promociones automáticas, visitas al sitio. Cada uno se desactiva por separado.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Enlaces de sitio | >= 2 para servir, recomendado >= 6 con descripciones; 25 caracteres | Assets > Enlaces de sitio, nivel y estado. API: tipo de recurso SITELINK [SIN VERIFICAR nombre] | https://support.google.com/google-ads/answer/2375416?hl=en |
| Textos destacados | 25 caracteres; hasta 10 | Assets > Textos destacados | https://support.google.com/google-ads/answer/6079510?hl=en |
| Fragmentos estructurados | >= 3 valores (4+ recomendado); encabezado coherente | Assets > Fragmentos | https://support.google.com/google-ads/answer/6280012?hl=en |
| Recurso de llamada | E.164, verificado, informes de llamadas, horario | Assets > Llamadas, estado "no verificado" | https://support.google.com/google-ads/answer/2453991?hl=en |
| Recurso de ubicación | Perfil de empresa vinculado; no desactivar sin motivo | Ubicaciones en biblioteca compartida | https://support.google.com/google-ads/answer/2404182?hl=en |
| Imágenes | >= 4 recomendadas, una cuadrada y una horizontal; requisitos de cuenta | Assets > Imágenes | https://support.google.com/google-ads/answer/9566341?hl=en |
| Formulario de clientes potenciales | Privacidad, vertical, puja de conversión, 60 días de retención | Assets > Formularios; descarga o webhook | https://support.google.com/google-ads/answer/9423234?hl=en |
| Precio | 3 a 8 elementos | Assets > Precios | https://support.google.com/google-ads/answer/7065415?hl=en |
| Promoción caducada | 6 meses sin editar deja de servir | Assets > Promociones, estado | https://support.google.com/google-ads/answer/7367521?hl=en |
| Nombre y logotipo | Verificación del anunciante; nombre 25 caracteres | Assets > Información de empresa; Admin > Política | https://support.google.com/google-ads/answer/12497613?hl=en |
| Requisitos de política de info. de empresa | Nombre = dominio o nombre legal; logo 1:1, 128x128 mín. | Estado aprobado/rechazado del recurso | https://support.google.com/adspolicy/answer/12499303?hl=en |
| Nº mínimo de tipos de recurso | Google aconseja usar tantos tipos como sea posible y al menos 4 enlaces de sitio y 3 imágenes (resumen de recursos) | Assets > Asociaciones | https://support.google.com/google-ads/answer/7507884?hl=en |
| Automáticos de cuenta activos/desactivados | Se recomienda mantenerlos, se pueden desactivar | Assets > Asociaciones > Recursos automáticos de cuenta | https://support.google.com/google-ads/answer/7175034?hl=en |
| Límites de recursos | 250.000 por cuenta a nivel de grupo; 50.000 a nivel de campaña | Informes | https://support.google.com/google-ads/answer/6372658?hl=en |

## Configuración de campaña
### Cómo funciona
- Redes: partners de búsqueda incluidos por defecto al crear una campaña de Search; se desactivan en Configuración > Redes. Google no informa de en qué sitio partner salió el anuncio. Red de Display en campañas de Search ("Display Expansion"): usa solo presupuesto de Search no gastado, con CPA similar; no aplica a presupuestos compartidos ni experimentos. API: `network_settings.target_google_search`, `target_search_network`, `target_partner_search_network`, `target_content_network` (los ejemplos de Google usan `target_content_network = True`, que activa Display Expansion).
- Ubicación: «Presencia o interés» (por defecto y recomendado para Search) frente a «Presencia» (solo personas probablemente situadas en la ubicación). Para exclusiones, el método por defecto es Presencia; «Presencia o interés» para excluir ya no está disponible en Search, Display, PMax y Shopping. En la API el valor interés solo (`SEARCH_INTEREST`) no puede fijarse en Search.
- Idiomas: desde septiembre de 2026 se elimina el ajuste de idioma a nivel de campaña en Search; los anuncios se emparejan por el idioma del propio anuncio y se prioriza el idioma de la búsqueda. Sin acción requerida. Impacto en la API: no indicado en la página [SIN VERIFICAR].
- Programación de anuncios: limita días y horas; con ella solo se sirve en esos tramos. Detalle oficial [SIN VERIFICAR] (solo se leyó un resumen de resultados de búsqueda).
- Audiencias: «Observación» (no limita el alcance, permite ajustes de puja y sirve de señal a Smart Bidding) frente a «Segmentación» (limita a miembros del segmento). Para Search se recomienda Observación y es el valor por defecto en campañas nuevas.
- Exclusión de ubicaciones / sitios en Search: se pueden excluir sitios o ubicaciones específicos de partners de búsqueda; método y límites concretos [SIN VERIFICAR].

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Partners de búsqueda activos | Incluidos por defecto; Google avisa de que el tráfico puede ser menos segmentado | Configuración > Redes; API `network_settings.target_partner_search_network` | https://support.google.com/google-ads/answer/1722047?hl=en |
| Display Expansion activado en Search | Usa presupuesto sobrante; objetivo CPA similar | Configuración > Redes ("Incluir Red de Display"); API `target_content_network` | https://support.google.com/google-ads/answer/7193800?hl=en |
| Opción de ubicación «Presencia o interés» vs «Presencia» | Defecto y recomendado: Presencia o interés; Presencia para verticales sensibles o excluir interesados | Configuración > Ubicaciones > Opciones de ubicación. API: `positive_geo_target_type`, `negative_geo_target_type` [SIN VERIFICAR el nombre de campo, el valor `PRESENCE_OR_INTEREST` consta en la fuente] | https://support.google.com/google-ads/answer/1722038?hl=en |
| Idioma de campaña | Ajuste retirado desde septiembre de 2026 | Configuración de campaña | https://support.google.com/google-ads/answer/1722078?hl=en |
| Audiencias en «Segmentación» en campañas con palabras clave | Recomendado Observación | Segmentos de audiencia > configuración | https://support.google.com/google-ads/answer/7365594?hl=en |
| Programación de anuncios | Limita cuándo se sirve | Configuración > Programación [detalle SIN VERIFICAR] | https://support.google.com/google-ads/answer/1704395 |

## AI Max para Search, expansión de URL final y DSA
### Cómo funciona
- AI Max es una capa de optimización sobre campañas Search existentes, no un tipo de campaña. Activo por defecto en campañas Search nuevas. Componentes: concordancia de términos de búsqueda (nivel grupo; usa concordancia amplia, tecnología basada en recursos y en la página de destino, y concordancia sin palabras clave), personalización de texto (campaña; antes recursos creados automáticamente), expansión de URL final (campaña; requiere personalización de texto; si se desactiva el texto se desactiva la expansión), inclusiones de URL (grupo) y exclusiones de URL (campaña), ubicaciones de interés (grupo).
- Google indica que concordancia de términos, expansión de URL final y personalización de texto necesitan Smart Bidding basado en conversiones para funcionar bien; no es eficaz si la campaña está limitada por presupuesto. Directrices de texto (text guidelines): exclusiones de términos y restricciones de mensajes. Con expansión de URL final la fijación de RSA no se respeta.
- Marca (brand controls): inclusiones de marca en campaña y grupo (el grupo anula la campaña solo para ese grupo; la campaña solo sirve en consultas con esa marca, riesgo de perder volumen sin marca); exclusiones de marca a nivel de campaña; si hay ambas, prevalecen las exclusiones [dato de la página de exclusiones, solo visto en resumen de búsqueda]. Las listas de marcas se crean a nivel de cuenta. Desde el 27-05-2025 la configuración de marca pasa a AI Max: añadir una lista nueva exige activar AI Max en la campaña. Marcas sin nombre común (ej. variantes) se meten en una misma lista.
- Reglas de la API: `Campaign.ai_max_setting.enable_ai_max`; `Campaign.asset_automation_settings` con `TEXT_ASSET_AUTOMATION` y `FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION`, ambos por defecto `OPTED_OUT` en Search (activar uno exige `enable_ai_max = true`; la expansión exige texto activo); `AdGroup.ai_max_ad_group_setting.disable_search_term_matching`; `Campaign.text_guidelines.term_exclusions` hasta 25 términos de 30 caracteres y `messaging_restrictions` hasta 40 objetos de 1 a 300 caracteres; ubicación de interés vía `AdGroupCriterion.location`; marca vía `brand_list` en criterio de grupo o campaña.
- Dynamic Search Ads (DSA): siguen activos; desde febrero de 2027 se actualizan automáticamente a AI Max (grupos dinámicos pasan a estándar, los DSA a RSA). Objetivos DSA: URL_Equals, URL_Contains, categorías, feed de páginas; máximo 100 feeds de páginas por cuenta. DSA no admite inserción de palabras clave. Puede rechazarse por "Destino no funciona/accesible" si AdsBot está bloqueado o hay errores.
- La personalización de texto (ACA) y el ajuste de campaña de concordancia amplia se actualizan automáticamente a AI Max desde septiembre de 2026.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| AI Max activo sin Smart Bidding de conversiones | Necesita puja de conversión; no rinde si limitada por presupuesto | Configuración > AI Max; estrategia de puja; API `enable_ai_max` | https://support.google.com/google-ads/answer/15909989?hl=en |
| Expansión de URL final sin exclusiones de URL | Puede enviar a cualquier URL del dominio; se pierde la fijación | Exclusiones de URL a nivel de campaña; informe Páginas de destino, columna "Seleccionada por" | https://support.google.com/google-ads/answer/15910187?hl=en |
| Marca: inclusiones/exclusiones | Inclusiones limitan a consultas con la marca; exclusiones a nivel de campaña | Configuración de marca en AI Max. API: `brand_list` en `CampaignCriterion` (`negative`=true exclusión) | https://support.google.com/google-ads/answer/14453047?hl=en |
| Exclusiones de marca | Prevalecen sobre inclusiones [solo resumen] | Igual | https://support.google.com/google-ads/answer/14505308?hl=en-GB |
| Directrices de texto | Hasta 25 términos de 30 caracteres; 40 restricciones | API `Campaign.text_guidelines` | https://developers.google.com/google-ads/api/docs/campaigns/ai-max-for-search-campaigns/getting-started |
| Fecha de migración de ACA o amplia | Septiembre de 2026 | API `Campaign.aca_migration_date_time`, `broad_match_migration_date_time` (v25+) | https://developers.google.com/google-ads/api/docs/campaigns/ai-max-for-search-campaigns/getting-started |
| Campañas con DSA | Actualización automática desde febrero de 2027 | Grupos de anuncios dinámicos | https://support.google.com/google-ads/answer/2471185?hl=en |
| Presupuesto limitado con AI Max | Aviso de Google al activar | Alerta en configuración | https://support.google.com/google-ads/answer/15910187?hl=en |
| Plantilla de seguimiento incompatible | Puede dar 404; usar `{lpurl}`, `{lpurl}?`, `{lpurl}&`, `{lpurl}#` | Plantilla de seguimiento de campaña | https://support.google.com/google-ads/answer/15910187?hl=en |

## Estructura de cuenta, estado de política, vista previa y diagnóstico
### Cómo funciona
- Estructura recomendada: fusionar grupos de una sola palabra clave en grupos temáticos; palabras clave que comparten presupuesto/objetivo van en la misma campaña, las que comparten página de destino o tema de creatividades, en el mismo grupo; todas las concordancias de un tema en un mismo grupo con amplia; quitar segmentación por dispositivo (Smart Bidding ya la tiene en cuenta); limpiar duplicados y palabras clave que no sirven; una campaña con un único objetivo. Dato oficial: 62 % de anunciantes con Smart Bidding usa amplia como principal (anunciantes con más de 100 clics, datos internos de enero-febrero de 2023). Se puede mantener estructura por tema para evitar ambigüedad entre grupos cuando dos temas tienen intención relacionada.
- Límites: 10.000 campañas por cuenta; 20.000 grupos por campaña; 20.000 elementos de segmentación por grupo; 5 millones por cuenta; 50 anuncios de texto activos por grupo; 3 RSA habilitados.
- Estados de anuncio: En revisión (suele tardar 1 día laborable; si pasa de 2 días laborables completos, revisar; más de una semana, contactar con soporte); Apto; Apto (limitado) (política restringe por ubicación, edad o dispositivo); Apto (limitado en todas las ubicaciones); Rechazado (sin impresiones; actualizar y reenviar o apelar); No apto (campaña o grupo pausado/eliminado/finalizado/pendiente, o grupo incompleto); Pausado, Pendiente, Finalizado, Eliminado. Recursos: Aprobado / Aprobado (limitado).
- «Destino no funciona»: destino que no funciona bien o que devuelve un código de error HTTP al rastreador AdsBot en dispositivos habituales. «Destino no rastreable»: AdsBot no puede rastrearlo. «Destino no accesible»: no accesible en la ubicación segmentada. «Discrepancia de destino»: dominio de URL visible vs. URL final, redirecciones a otro dominio, plantilla de seguimiento que lleva a otro contenido. Editar un anuncio o recurso reinicia la revisión.
- Vista previa y diagnóstico de anuncios (Herramientas > Solución de problemas): simula una búsqueda sin generar impresiones ni afectar a las estadísticas; muestra por qué no sale el anuncio. Limitaciones: simulación, puede no reflejar toda la actividad, el anuncio puede desaparecer al agotar el presupuesto diario; «Motivo desconocido» suele deberse a periodo de aprendizaje de puja o a «--» / volumen bajo.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API si lo conoces) | Fuente |
|---|---|---|---|
| Grupos de una sola palabra clave / mismas palabras en varias concordancias | Consolidar en grupos temáticos | Recuento de palabras clave por grupo | https://support.google.com/google-ads/answer/14752782?hl=en |
| Campañas segmentadas por dispositivo | Google recomienda quitar la segmentación | Ajustes de puja y campañas duplicadas por dispositivo | https://support.google.com/google-ads/answer/14752782?hl=en |
| Límites de cuenta (campañas, grupos, anuncios) | Ver cifras arriba | Informes de cuenta | https://support.google.com/google-ads/answer/6372658?hl=en |
| Anuncios rechazados o limitados | Rechazado = sin impresiones; limitado = restricciones | Columna Estado en Anuncios. API: `ad_group_ad.policy_summary.approval_status` / `review_status` [nombres SIN VERIFICAR en doc] | https://support.google.com/google-ads/answer/1722129?hl=en |
| Revisión demorada | >2 días laborables: comprobar; >1 semana: soporte | Estado "En revisión" con fecha de edición | https://support.google.com/google-ads/answer/1722120?hl=en |
| «Destino no funciona» / «no rastreable» / «no accesible» | Error HTTP a AdsBot, bloqueo de AdsBot, geobloqueo | Estado de política; simular AdsBot con Chrome DevTools (anular user agent) | https://support.google.com/adspolicy/answer/6368661?hl=en |
| «Discrepancia de destino» | Dominio visible distinto, redirecciones a otro dominio | Comparar URL visible, final y plantilla de seguimiento | https://support.google.com/adspolicy/answer/6368661?hl=en |
| Diagnóstico de por qué no sale un anuncio | Usar la herramienta, no buscar en Google | Herramientas > Solución de problemas > Vista previa y diagnóstico | https://support.google.com/google-ads/answer/148778?hl=en |
| Campaña/grupo en estado "No apta" | Pausa, fecha de fin o grupo incompleto | Columna Estado de campaña/grupo | https://support.google.com/google-ads/answer/1722129?hl=en |

## Cambios recientes
- 03-10-2025: los anuncios de llamada (call ads) quedan obsoletos; usar recursos de llamada en RSA. https://support.google.com/google-ads/announcements/9048695?hl=en
- 21-04-2025: cambia cómo se seleccionan anuncios de Search para posiciones inferiores de la página (antes, en general, un solo anuncio por anunciante y página). Mismo enlace: https://support.google.com/google-ads/announcements/9048695?hl=en
- 27-05-2025: recursos creados automáticamente, inclusiones y exclusiones de marca pasan a AI Max como personalización de texto y controles de marca. https://support.google.com/google-ads/answer/16740321?hl=en y https://support.google.com/google-ads/answer/14453047?hl=en
- Septiembre de 2026: ajuste de campaña de concordancia amplia y ACA (personalización de texto) se migran automáticamente a AI Max. https://support.google.com/google-ads/answer/13389795 y https://support.google.com/google-ads/answer/16740321?hl=en
- Febrero de 2027: los DSA se actualizan automáticamente a AI Max (la página de ayuda de DSA lo indica; las páginas de informe de términos DSA y de reporting AI Max pueden seguir mostrando septiembre de 2026). https://support.google.com/google-ads/answer/2471185?hl=en
- Septiembre de 2026: se elimina el ajuste de idioma a nivel de campaña en Search; los anuncios se emparejan por su idioma. https://support.google.com/google-ads/answer/1722078?hl=en
- Opciones de ubicación: «Presencia o interés» ya no existe como método de exclusión y el modo solo-interés no puede fijarse en Search; la API devuelve `SETTING_VALUE_NOT_COMPATIBLE_WITH_CAMPAIGN` si se intenta. https://support.google.com/google-ads/answer/1722038?hl=en
- AI Max activo por defecto en campañas Search nuevas. https://support.google.com/google-ads/answer/15909989?hl=en
- API v24.1 (13-05-2026): nuevos tipos de experimento `ADOPT_AI_MAX` y `ADOPT_BROAD_MATCH_KEYWORDS`. API v25.1 (19-08-2026): campos `Campaign.aca_migration_date_time` y `Campaign.broad_match_migration_date_time`. https://developers.google.com/google-ads/api/docs/release-notes
- Marzo de 2026 en adelante, extras anunciados (AI Brief, avisos legales de texto garantizado, etc.): solo constan en fuentes fuera de los dominios admitidos, no incluidos [SIN VERIFICAR en fuente permitida].
