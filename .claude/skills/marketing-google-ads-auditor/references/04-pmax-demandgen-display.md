# 04 · PMax, Demand Gen, Display y vídeo
> Consultado el 08-10-2026. Fuentes oficiales. Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente (o solo salió en un resumen de búsqueda, sin leer la página completa).

Abreviaturas de URL: GAH = https://support.google.com/google-ads/answer/ ; DEV = https://developers.google.com/google-ads/api/ . Cada fila lleva la URL completa.

## Performance Max: funcionamiento y presupuesto
### Cómo funciona
- Campaña basada en objetivos que sirve en todo el inventario de Google Ads desde una sola campaña: YouTube, Display, Búsqueda, Discover, Gmail y Maps. Los informes de canal añaden Search partners.
- Objetivos admitidos al crear: Ventas, Oportunidades de venta (leads), Tráfico al sitio web, Visitas a tiendas y promociones locales, o sin objetivo.
- Pujas: solo Smart Bidding de conversión o de valor. "Performance Max exclusively supports conversion and value-based Smart Bidding".
- Presupuesto: el panel da hasta 3 niveles (bajo, medio, alto); el bajo es el mínimo recomendado. En el paso de presupuesto: "average daily budget of at least 3 times your CPA or cost/conv.". Un día puede gastar hasta 2 veces el presupuesto diario medio; el tope mensual es presupuesto diario medio por días medios del mes.
- Aprendizaje: 1 a 2 semanas, hasta 6 con poco volumen o setups complejos (guía de leads); la guía de problemas de configuración habla de 2 a 3 semanas tras cambios importantes. Cambios grandes durante ese periodo lo reinician.
- Con presupuesto limitado la IA desvía gasto a inventario más barato: "If budget is limiting the campaign, the AI may shift spend to cheaper inventory such as YouTube or Display".
- Cálculo derivado (no de Google): con el mínimo de 3 veces el CPA, un presupuesto de 10 €/día solo cuadra con un CPA objetivo de unos 3,33 €. Para leads B2B con CPA de decenas de euros, 10 €/día queda por debajo del mínimo oficial.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta (interfaz o campo de la API) | Fuente |
|---|---|---|---|
| Presupuesto diario frente al CPA | Al menos 3 veces el CPA de las conversiones elegidas; el nivel Bajo del panel es el mínimo recomendado | Interfaz: panel de presupuesto. API: campaign_budget.amount_micros frente a metrics.cost_per_conversion | https://support.google.com/google-ads/answer/15865152 |
| Presupuesto limitado que empuja a Display/YouTube | Si el presupuesto limita, la IA puede pasar a inventario más barato (YouTube, Display) | Estado "Limitado por presupuesto" y informe de canales (ver más abajo) | https://support.google.com/google-ads/answer/10732484?hl=en |
| Estrategia de puja | Solo Maximizar conversiones (CPA objetivo opcional) o Maximizar valor de conversión (ROAS objetivo opcional) | API: campaign.maximize_conversions / maximize_conversion_value; no admite estrategias de cartera | https://developers.google.com/google-ads/api/performance-max/getting-started |
| Presupuesto de la campaña | API: periodo DAILY y no compartido | campaign_budget.period y explicitly_shared | https://developers.google.com/google-ads/api/performance-max/getting-started |
| Tiempo antes de evaluar | 1 a 2 semanas, hasta 6; contar el retraso de conversión | Historial de cambios (change_event) frente a la fecha de evaluación | https://support.google.com/google-ads/answer/13775965?hl=en |
| Cambios drásticos recientes | Evitar cambios frecuentes o grandes durante el aprendizaje | Historial de cambios | https://support.google.com/google-ads/answer/10732484?hl=en |

## Grupo de recursos (asset group)
### Cómo funciona
- Mínimos y máximos por grupo (la web de ayuda y la guía de API coinciden):
  - Titulares: 30 caracteres, mínimo 3, máximo 15 (recomendado 11 o más; al menos uno de 15 caracteres o menos).
  - Titulares largos: 90 caracteres, mínimo 1, máximo 5 (recomendado 2 o más).
  - Descripciones: 90 caracteres, mínimo 2, máximo 5 (recomendado 4 o más).
  - Nombre de empresa: 25 caracteres, 1. Llamada a la acción: 1. URL final: 1. Ruta de URL visible: 15 caracteres, 1 a 2 (opcional).
  - Imagen horizontal 1,91:1: recomendada 1200x628, mínima 600x314, mínimo 1 en API (recomendado 4 o más en ayuda), máximo 20.
  - Imagen cuadrada 1:1: recomendada 1200x1200, mínima 300x300, mínimo 1 en API (recomendado 4 o más), máximo 20.
  - Imagen vertical 4:5 (opcional): 960x1200, mínima 480x600, máximo 20.
  - Logotipo cuadrado 1:1: obligatorio, mínimo 1, máximo 5, mínima 128x128. Logotipo horizontal 4:1 (opcional): 1200x300, mínima 512x128, máximo 5.
  - Imágenes: JPG o PNG (la API admite también GIF), 5120 KB como máximo.
  - Vídeos: opcionales, 16:9, 1:1 o 9:16, 10 segundos o más, máximo 15. Sin vídeo, Google puede generar uno o varios automáticamente con tus recursos.
  - Si el objetivo principal es llamada o lead, un grupo sin recurso de llamada o de formulario aparece como "Incompleto".
- Máximo 100 grupos de recursos por campaña; un grupo no se comparte entre campañas.
- Eficacia del anuncio (Ad Strength): Incompleto, Pobre, Medio, Bueno, Excelente. Excelente exige además 6 o más enlaces de sitio, vídeos propios en las tres orientaciones, los 15 titulares y las 5 descripciones. Google dice que de Pobre a Excelente la mediana sube un 6 % las conversiones, y que el cambio de nota en sí no cambia resultados.
- Esperar 2 a 3 semanas antes de sustituir recursos de bajo rendimiento.
- Detalle de API: si falta una descripción corta, el error es AssetGroupError.SHORT_DESCRIPTION_REQUIRED (descripción de 60 caracteres o menos). La tabla de ayuda no menciona la descripción corta.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Recursos por debajo del mínimo | 3 titulares, 1 titular largo, 2 descripciones, 1 nombre, 1 logo cuadrado, imágenes 1,91:1 y 1:1 | API: errores AssetGroupError.NOT_ENOUGH_*; interfaz: eficacia "Incompleto" | https://developers.google.com/google-ads/api/performance-max/asset-requirements |
| Eficacia del anuncio | Apuntar a Bueno o Excelente | Interfaz: columna Ad strength (la nota del editor es la más fiel); API: asset_group.ad_strength | https://support.google.com/google-ads/answer/14143250?hl=en |
| Sin vídeo propio | Sin vídeo, Google puede generar vídeos con los recursos | API: asset_group_asset.source = AUTOMATICALLY_CREATED con field_type YOUTUBE_VIDEO | https://support.google.com/google-ads/answer/14528220?hl=en |
| Estado del grupo y razones | Campos de estado primario | API: asset_group.primary_status y primary_status_reasons; asset_group_asset.primary_status, primary_status_reasons, primary_status_details | https://developers.google.com/google-ads/api/performance-max/troubleshooting |
| Valores posibles de primary_status | [SIN VERIFICAR] la página no los lista | Referencia de campos AssetGroup | https://developers.google.com/google-ads/api/performance-max/troubleshooting |
| Recurso de llamada o lead faltante | Obligatorio si la meta principal es llamada o lead | Eficacia "Incompleto" | https://support.google.com/google-ads/answer/14528220?hl=en |
| Nº de grupos de recursos | Máximo 100 por campaña; separar por tema, idioma o audiencia | API: contar asset_group por campaña | https://developers.google.com/google-ads/api/performance-max/asset-groups |

## Señales de audiencia y temas de búsqueda
### Cómo funciona
- Las señales de audiencia son pistas, no restricciones: "Performance Max campaigns don't limit your ads to a selected set of audiences". Se definen por grupo de recursos.
- Google recomienda señales de la parte baja del embudo (listas de Customer Match, visitantes del sitio).
- Temas de búsqueda: hasta 50 por grupo de recursos (subido de 25 el 07-08-2025). Mismo nivel de prioridad que concordancia de frase y amplia. Los negativos y exclusiones se siguen aplicando. Se añaden en Campañas > Grupos de recursos > Resumen > Señales. Límite de caracteres: [SIN VERIFICAR] en la página de ayuda; una fuente secundaria de búsqueda habla de 80 pero no se leyó en página oficial.
- La guía de API (upgrade-enhancements) todavía dice 25 por grupo; es una página sin actualizar.
- API: AssetGroupSignal con un único campo entre audience, search_theme y local_services_id; cada señal se añade por separado.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Señales de audiencia presentes | Cada grupo debería tener señales de datos propios (Customer Match, visitantes) | Interfaz: ficha Señales del grupo. API: asset_group_signal.audience | https://developers.google.com/google-ads/api/performance-max/asset-group-signals |
| Temas de búsqueda | Hasta 50 por grupo; evitar sinónimos casi iguales | API: asset_group_signal.search_theme.text | https://support.google.com/google-ads/answer/14767319?hl=en |

## Controles: negativos, marcas, URL, dispositivos, demografía, horario, ubicación
### Cómo funciona
- Palabras clave negativas a nivel de campaña: hasta 10.000 por campaña de PMax (subido de 100 el 09-04-2025). Solo afectan a inventario de Búsqueda y Shopping, no a Display, YouTube, Gmail ni Discover. Concordancia con símbolos; no casan variantes cercanas. Se añaden en Palabras clave > Palabras clave negativas > + > elegir campaña PMax. Hay listas de negativas reutilizables para campañas PMax (anuncio de 07-08-2025) y el Editor 2.11 las admite.
- Negativas a nivel de cuenta: hasta 1.000; se aplican a Búsqueda y Shopping, incluida PMax.
- Para Display y vídeo las "palabras clave de contenido excluido" se ponen en Content suitability (hasta 1.000 en la cuenta, concordancia exacta).
- Exclusiones de marca (brand exclusions): por campaña, con listas de marcas. Se aplican solo a Búsqueda, Shopping y búsqueda de YouTube. No limitan Display ni vídeo.
- Expansión de URL final: activada por defecto. Se desactiva al crear o en Ajustes > Optimización de recursos. Los cambios tardan 24 a 48 horas. No se admite en campañas solo de tienda. Con la expansión activa no se puede desactivar la personalización de texto. Exclusiones de URL: Ajustes > Optimización de recursos > Añadir exclusiones de URL (URL sueltas, etiquetas personalizadas del feed o reglas); la URL final de la campaña no se puede excluir. Con la expansión desactivada, las reglas "URL contains" restringen; con ella activada solo orientan.
- Recursos creados automáticamente: ahora "personalización de texto" (titulares y descripciones generados a partir de la página). Se desactiva en ajustes, aunque no con la expansión activa. Si no hay vídeo, puede generarse uno. Mejora de imágenes y "imágenes de la página de destino" son opciones aparte (Ajustes > Optimización de recursos). API: AssetAutomationSetting con TEXT_ASSET_AUTOMATION y GENERATE_ENHANCED_YOUTUBE_VIDEOS.
- Dispositivos: la página de ajustes (paso 3) lista ordenadores, móviles, tablets y TV, con refinamiento por sistema operativo; el post del 07-08-2025 dice "fully available".
- Demografía: exclusión por edad y por género. Edad completa desde 07-08-2025; género en beta en esa fecha. Para requisitos estrictos, excluir también "Desconocido". No hay otros ejes (renta, estado parental) en exclusión.
- Horario: el paso 3 de configuración lista "Ad schedule" (días y horas).
- Ubicación: ubicaciones objetivo y excluidas, con opción "Presencia" y ubicaciones negativas. Los puntos de venta nuevos tardan 24 a 48 horas en sincronizar.
- Exclusión de datos: se pueden excluir listas de Customer Match, visitantes web y remarketing de Analytics (aplica a Búsqueda, Display, Shopping, Vídeo y Discover). Para captar clientes nuevos Google recomienda el objetivo de captación en lugar de esto.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Negativas de campaña | Hasta 10.000; solo Búsqueda y Shopping | Interfaz: Palabras clave > Negativas. API: campaign_criterion negativo [SIN VERIFICAR el nombre exacto en la guía de PMax] | https://support.google.com/google-ads/answer/15726455?hl=en |
| Negativas de cuenta | Hasta 1.000; aplican a PMax en Búsqueda y Shopping | Interfaz: Palabras clave > Negativas > cuenta. API: customer_negative_criterion | https://support.google.com/google-ads/answer/13607727?hl=en |
| Exclusiones de marca | Solo Búsqueda, Shopping y búsqueda de YouTube | Interfaz: Ajustes > Más ajustes > Exclusiones de marca | https://support.google.com/google-ads/answer/14505308?hl=en |
| Expansión de URL final | Activada por defecto; desactivarla si se ven páginas irrelevantes | Interfaz: Ajustes > Optimización de recursos. API: asset_automation_settings (v22+) o Campaign.url_expansion_opt_out (anteriores) | https://support.google.com/google-ads/answer/14337539?hl=en |
| Exclusiones de URL | URL sueltas o reglas; la URL final no se puede excluir | Ajustes > Optimización de recursos > exclusiones de URL | https://support.google.com/google-ads/answer/14337773?hl=en |
| Activos creados con la expansión | Informe "Expanded Final URL assets"; quitar un recurso lo quita de toda la campaña | Interfaz: pestaña Expanded Final URL assets | https://support.google.com/google-ads/answer/14337539?hl=en |
| Personalización de texto y vídeo automático | Activa por defecto; vídeo autogenerado si no se sube uno | API: asset_group_asset.source; AssetAutomationSetting | https://support.google.com/google-ads/answer/14337369 |
| Dispositivos | Elegibles ordenador, móvil, tablet, TV | Interfaz: Ajustes > Dispositivos. API: campaign_criterion de tipo device [SIN VERIFICAR] | https://support.google.com/google-ads/answer/15864837?hl=en |
| Exclusiones de edad y género | Solo estos dos ejes; excluir "Desconocido" si es estricto | Interfaz: Ajustes > Exclusiones demográficas | https://support.google.com/google-ads/answer/15864837?hl=en |
| Horario | Programación de anuncios disponible en el ajuste de campaña | Interfaz: Ajustes > Ad schedule | https://support.google.com/google-ads/answer/15864837?hl=en |
| Ubicación | Presencia frente a presencia o interés; añadir negativas | Interfaz: Ajustes > Ubicaciones | https://support.google.com/google-ads/answer/10732484?hl=en |

## Exclusiones de emplazamientos, apps y contenido: a qué nivel y a qué canales afectan
### Cómo funciona
- En PMax no existen exclusiones de emplazamientos a nivel de campaña: "Campaign-level exclusions aren't yet available" (guía de problemas de configuración). Se hacen a nivel de cuenta o de cuenta de administrador (MCC) y PMax las respeta.
- Nivel de cuenta: Herramientas > Content suitability > Advanced settings > Excluded placements. Hasta 20.000 por entrada y 65.000 por cuenta. Una cuenta de administrador puede crear hasta 3 listas de hasta 250.000 cada una. Entran en vigor en unas 12 horas y se ven en el historial de cambios.
- Alcance: Display, YouTube, Google Video Partners y Search Partner Network (los sitios de Search partners, desde 03-2024). No aplica a YouTube Sponsorship. No se puede excluir youtube.com entero; sí canales y vídeos concretos.
- Apps: el formato es mobileapp::1-<iTunes ID> en iOS y mobileapp::2-<paquete> en Android. Esa sintaxis sale en la guía de exclusiones de Display (answer/2454012, no leída entera); la página de exclusiones de cuenta no explica cómo excluir apps. [SIN VERIFICAR] que se acepte igual en el nivel de cuenta. No se encontró exclusión por categoría de app a nivel de cuenta para PMax.
- Content suitability (cuenta): tipo de inventario Máximo (por defecto), Moderado o Limitado; categorías de contenido sensible (tragedia y conflicto, temas sociales sensibles, lenguaje soez, sugerente, impactante); etiquetas de contenido digital en Display (DL-G, DL-PG, DL-T, DL-MA, sin etiquetar); exclusión de vídeos en directo, vídeos incrustados y "por debajo del pliegue" (solo Display). No aplica a campañas de App ni YouTube Sponsorship. Google avisa de que es "best effort".
- La IA decide el reparto de canal. En el informe de canal Google lo dice así: "You can't set budget per channel directly". No hay botón para quitar Display o YouTube de una PMax estándar. Ver sección de palancas.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Lista de exclusiones de cuenta | Hasta 65.000 por cuenta; 20.000 por entrada; efectivas en unas 12 h | Interfaz: Herramientas > Content suitability > Advanced settings. API: [SIN VERIFICAR] recurso | https://support.google.com/google-ads/answer/7331110?hl=en |
| Exclusiones desde MCC | Listas desde administrador, hasta 3 listas de 250.000 | Interfaz de MCC: Content suitability | https://support.google.com/google-ads/answer/7331110?hl=en |
| Tipo de inventario | Máximo por defecto; Limitado puede recortar alcance | Interfaz: Content suitability > Inventory type | https://support.google.com/google-ads/answer/12764663?hl=en |
| Palabras clave de contenido excluido | Hasta 1.000 en cuenta, concordancia exacta | Interfaz: Content suitability | https://support.google.com/google-ads/answer/12764663?hl=en |
| Cobertura de Shorts y temas | Los temas y emplazamientos de Shorts no cubren PMax | Documentación de cobertura | https://support.google.com/google-ads/answer/12764663?hl=en |
| Exclusiones de apps concretas | Formato mobileapp::1- / mobileapp::2- | Lista de exclusiones; informe de emplazamientos de PMax | https://support.google.com/google-ads/answer/2454012?hl=en |

## Informes y diagnósticos de PMax
### Cómo funciona
- Informe de rendimiento por canal: Campañas > Insights y informes > Channel performance. Canales: Google Search, Google Display Network, YouTube, Discover, Maps, Gmail y Search partners. Datos desde el 06-06-2025. Secciones: resumen de rendimiento, gráfico canales a objetivos, serie temporal y tabla de distribución por canal (descargable, con segmentos "anuncios con datos de producto", "anuncios con vídeo", categoría y acción de conversión).
- Columna Estado por canal: No apto ("can't show ads"), Apto (limitado), Apto, Faltan recursos requeridos. Causas: política del grupo, problemas del feed, falta de recursos específicos del canal (nombre para Discover, imagen cuadrada para Display, ubicación para Maps), recursos de llamada o formulario, expansión de URL desactivada (limita Búsqueda), falta de vídeo, presupuesto limitado.
- Aviso de Google: "If a channel has no issues but isn't spending, Performance Max is likely prioritizing higher-ROI channels". Y que el ROI por canal puede engañar por el ROI marginal.
- Términos de búsqueda: informe completo en todas las campañas PMax, también por API (07-08-2025). Datos desde 03-2023. Muestra términos, páginas de destino y formato del anuncio. No incluye visitas ni ventas a tienda.
- Informe de emplazamientos (Report editor, "Performance Max campaigns placement"): tipos Página web, App móvil y Vídeo de YouTube; solo impresiones; Google dice que es una herramienta de brand safety y "shouldn't be used to evaluate performance"; no cubre todos los canales, no incluye Búsqueda. Hay "anonymous.google" que oculta el sitio.
- Recursos: estadísticas completas (clics, coste, conversiones) en todas las campañas; segmentables por dispositivo, hora, red. Informe de recursos de expansión de URL. Diagnósticos de objetivos (etiquetas o acciones de conversión rotas).
- Captación de clientes nuevos: columna de coste de captación (04-2025); sin conversiones "desconocidas" (08-2025).

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Reparto de gasto por canal | Mirar Display + YouTube + Discover frente a Search; el informe se interpreta con cautela | Interfaz: Channel performance. API: campaign con segments.ad_network_type (v23 o posterior) | https://support.google.com/google-ads/answer/16260130?hl=en |
| Estado de cada canal | No apto, Apto (limitado), Apto, Faltan recursos | Interfaz: columna Status del informe de canal | https://support.google.com/google-ads/answer/16260130?hl=en |
| Segmentación API del canal | segments.ad_network_type, segments.ad_using_product_data, segments.ad_using_video (v23+) | GAQL sobre campaign con campaign.advertising_channel_type = 'PERFORMANCE_MAX' | https://developers.google.com/google-ads/api/performance-max/campaign-reporting |
| Términos de búsqueda | Revisar y excluir irrelevantes; vigilar sobreexclusión | Interfaz: Insights > Términos. API: campaign_search_term_view | https://support.google.com/google-ads/answer/16327396?hl=en-GB |
| Emplazamientos | Solo impresiones, para brand safety | Report editor. API: performance_max_placement_view (campo placement_type WEBSITE, MOBILE_APPLICATION, YOUTUBE_VIDEO); el filtro por campaign.id es obligatorio | https://developers.google.com/google-ads/api/performance-max/campaign-reporting |
| Segmentar emplazamientos por red | API v24 o posterior; la página de reporting de campaña dice v23 (discrepancia entre páginas) | segments.ad_network_type en performance_max_placement_view | https://developers.google.com/google-ads/api/fields/v22/performance_max_placement_view |
| Recursos y combinaciones | Estadísticas completas por recurso | API: asset_group_asset, asset_group_top_combination_view | https://developers.google.com/google-ads/api/performance-max/reporting |
| Entidades que no existen | PMax no tiene AdGroup ni AdGroupAd; esas consultas no devuelven datos | GAQL: usar asset_group | https://developers.google.com/google-ads/api/performance-max/reporting |
| Diagnóstico de objetivos y etiquetas | Comprobaciones nuevas de acciones de conversión faltantes o rotas | Interfaz: Goal diagnostics | https://support.google.com/google-ads/answer/16451273 |

## PMax para leads
### Cómo funciona
- Medición: seguimiento de conversiones correcto; conversiones mejoradas para clientes potenciales y/o importación sin conexión de los leads que llegan a venta. Subir al menos a diario.
- Objetivo de conversión: el más cercano a la venta que tenga volumen. Recomendación literal: "at least 15 conversions in the last 30 days" para el objetivo más profundo. Categorías "Qualified lead" y "Converted lead" activan protecciones contra tráfico no válido. No mezclar etapas en un mismo CPA objetivo.
- Pujas: con valor por lead, Maximizar valor de conversión (con ROAS objetivo opcional); sin valores, Maximizar conversiones con CPA objetivo cercano al máximo aceptable de coste por lead. Sin datos suficientes, quitar el CPA objetivo.
- Calidad: formulario con preguntas calificadoras, reCAPTCHA, doble opt-in, validación en servidor; listas de Customer Match como señal. Revisar términos de búsqueda, añadir negativas, desactivar la expansión de URL si aparecen páginas irrelevantes, usar exclusiones de marca.
- Captación de clientes nuevos para leads: modo "New Customer Only", que exige una lista de Customer Match. Requisitos del objetivo en la guía de problemas: para no minoristas, conversiones de compra en los últimos 30 días o lista de clientes existentes. Un segmento de al menos 1.000 miembros activos en una red para pujar por clientes nuevos [SIN VERIFICAR, solo resumen de búsqueda de answer/15864839].
- Valores: reglas de valor de conversión (multiplicadores por audiencia, dispositivo, ubicación).
- Importación sin conexión: desde el 15-06-2026 las importaciones sin conexión y las subidas de conversiones mejoradas para leads pasan a la Data Manager API y se bloquean en la Google Ads API; los tokens de desarrollador sin actividad entre enero y junio de 2026 no entran en la lista de acceso heredado. Las dos fuentes oficiales discrepan en la ventana exacta (enero a junio de 2026 en ayuda; 17-12-2025 a 15-06-2026 en la página de deprecaciones). Error esperado: CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE.
- Guía "Answering your top questions": vídeo añade en torno a un 12 % más de conversiones de media; esa página parece una versión antigua (habla de controles "que llegan en marzo").

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Objetivo de conversión principal | El más profundo con al menos 15 conversiones en 30 días | Interfaz: Objetivos > Conversiones. API: metrics.all_conversions por conversion_action en 30 días | https://support.google.com/google-ads/answer/13775965?hl=en |
| Pujas con valor | Maximizar valor de conversión si hay valor por lead; si no, Maximizar conversiones y CPA objetivo cercano al máximo | Campaign.bidding_strategy_type | https://support.google.com/google-ads/answer/13775965?hl=en |
| Conversiones mejoradas para leads | Tag con captura de datos hash más importación (Data Manager); auto-etiquetado activo; datos email o teléfono | Interfaz: Objetivos > Conversiones > diagnóstico; checklist de implementación | https://support.google.com/google-ads/answer/15713840?hl=en |
| Importación con la Google Ads API | Desde 15-06-2026 puede fallar con CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE; migrar a Data Manager API | Registro de errores de UploadClickConversions del cliente propio | https://support.google.com/google-ads/answer/15713840?hl=en |
| Ventana de la deprecación | Discrepancia entre ayuda y deprecaciones de la API | Contrastar con el log de tokens | https://developers.google.com/google-ads/api/docs/deprecations |
| Subida de conversiones | Subir con frecuencia, al menos a diario, con GCLID | Informe de diagnóstico de conversiones | https://support.google.com/google-ads/answer/15713840?hl=en |
| Calidad del formulario | reCAPTCHA, doble opt-in, preguntas calificadoras | Revisión manual de la web | https://support.google.com/google-ads/answer/14587068?hl=en |
| Captación de clientes nuevos | Modo New Customer Only requiere Customer Match | Interfaz: Ajustes > Captación de clientes | https://support.google.com/google-ads/answer/14005157?hl=en |
| Conversión que no es de lead | Evitar contar visitas o micro-conversiones como biddables junto al lead profundo | Objetivos de la campaña: biddable frente a observación | https://support.google.com/google-ads/answer/13775965?hl=en |
| Tiempo y conversiones mínimas antes de ajustar | 1 a 2 semanas, hasta 6; "30 conversions" para evaluar un CPA objetivo (resumen de búsqueda) [SIN VERIFICAR el 30 en página leída] | Fecha del último cambio de puja | https://support.google.com/google-ads/faq/10286469?hl=en |

## Convivencia de PMax y Search
### Cómo funciona
- Una palabra clave de concordancia exacta de una campaña de Búsqueda, o corregida de ortografía a esa consulta, tiene preferencia sobre PMax: ejemplo oficial [plumbers] frente a "plumbrs".
- Los temas de búsqueda tienen la misma prioridad que frase y amplia. Si hay empate de relevancia, decide el Ad Rank.
- Si la consulta no coincide exacta con ninguna palabra clave, decide el Ad Rank.
- PMax y Demand Gen compiten en la subasta por Ad Rank normal.
- Excepciones citadas en un resumen de búsqueda de answer/2756257 (no leído entero): Search limitada por presupuesto, palabra clave no apta (sin tráfico, anuncios rechazados), Shopping no entra en esta regla. [SIN VERIFICAR]
- PMax no admite instalaciones de apps como objetivo.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Consultas que cazan exacta en Search y también en PMax | La exacta de Search gana | Cruzar términos de búsqueda de PMax con palabras clave exactas de Search | https://support.google.com/google-ads/answer/13810170?hl=en |
| Temas de búsqueda frente a frase o amplia | Misma prioridad | Revisar temas de búsqueda y palabras clave de Search | https://support.google.com/google-ads/answer/10724817?hl=en |
| Competencia por objetivos y pujas compartidos | Si comparten objetivos y objetivos de puja, la misma subasta puede solaparse | Comparar objetivos de conversión de ambas campañas | https://support.google.com/google-ads/answer/13810170?hl=en |
| Search limitada por presupuesto | PMax puede servir en consultas exactas [SIN VERIFICAR] | Estado de presupuesto de Search | https://support.google.com/google-ads/answer/2756257?hl=en |

## Palancas para una PMax que se va a Display
### Qué se puede hacer (oficial)
1. **Ver el reparto real**: informe de canal (Search, Display, YouTube, Discover, Maps, Gmail, Search partners) y, por API, segments.ad_network_type en la campaña (v23+). Datos solo desde 06-06-2025.
2. **Subir el presupuesto o bajar el CPA exigido**: si el presupuesto limita, la IA puede pasar a "cheaper inventory such as YouTube or Display". El mínimo recomendado es 3 veces el CPA; con 10 €/día la campaña probablemente está por debajo.
3. **Exclusiones de emplazamientos y apps a nivel de cuenta o MCC**, no de campaña. Afectan a Display, YouTube, Video Partners y Search partners de TODAS las campañas de la cuenta, no solo PMax.
4. **Content suitability de cuenta**: inventario Limitado, categorías sensibles, etiquetas, exclusión de "por debajo del pliegue", palabras clave de contenido excluido (hasta 1.000). Es "best effort".
5. **Quitar recursos que abren inventario**: el informe de canal indica que falta imagen cuadrada para Display y que sin vídeo hay vídeo autogenerado; la guía de exclusiones de cuenta dice que no subir vídeo reduce YouTube. Las dos afirmaciones chocan en parte (sin vídeo Google puede generar uno). No hay documentación oficial de cuánto reduce el gasto en Display quitar la imagen cuadrada, y la imagen cuadrada y la horizontal son obligatorias para crear el grupo.
6. **Dirigir con señales y datos**: señales de audiencia de la parte baja (Customer Match, visitantes), temas de búsqueda (hasta 50), exclusión de listas de datos, objetivo de captación de clientes nuevos. Son pistas, no restricciones.
7. **Aumentar la fracción de Búsqueda por medición**: puja a objetivo de lead cualificado o convertido con importación sin conexión, para que la IA aprenda qué tráfico da leads reales.
8. **Dispositivos, edad/género, horario y ubicación**: restringen el tráfico (hasta incluir exclusión de edad/género), pero no eligen canal.
9. **Desactivar la expansión de URL y la personalización de texto** si el tráfico llega a páginas irrelevantes (recomendación oficial); no controla el canal.
10. **Experimentos y otra estructura**: separar en campaña de Search (marca y exactas) y PMax por tema. Search con exacta tiene prioridad sobre PMax.
11. **Revisar a las 2 a 3 semanas** y atribuir con cautela: Google avisa de que el ROI por canal puede confundir por el ROI marginal.

### Qué NO existe (oficialmente)
- **No hay control de canal en PMax.** Ni excluir Display, ni YouTube, ni "solo Búsqueda", ni presupuesto por canal ("You can't set budget per channel directly"). Los controles de canal sí existen en Demand Gen, por grupo de anuncios (YouTube In-feed, In-stream, Shorts, Discover, Gmail, Display).
- **No hay exclusiones de emplazamientos a nivel de campaña en PMax** (guía de problemas de configuración: "aren't yet available").
- **Las negativas de campaña y de cuenta no tocan Display ni YouTube** (solo Búsqueda y Shopping). Las exclusiones de marca tampoco (solo Búsqueda, Shopping, búsqueda de YouTube).
- **No hay exclusión por categoría de app a nivel de cuenta para PMax** en la documentación leída. [SIN VERIFICAR] más allá de listar apps concretas.
- **El informe de emplazamientos solo da impresiones** y no sirve para medir rendimiento.
- **No hay un número oficial de "gasto máximo en Display"** ni una regla que reserve un porcentaje a Búsqueda.
- El informe de canal no tiene botón para "pausar" un canal.
- Existe una nota oficial antigua en "Answering your top questions" sobre controles de canal "que llegan en marzo", pero se refiere a Demand Gen, no a PMax.

## Demand Gen
### Cómo funciona
- Campaña de demanda en YouTube (incluidos Shorts), Discover, Gmail, Maps (beta) y Google Display Network. Sustituye a Discovery (migraciones automáticas completadas, la de SA360 con fecha 22-01-2024 y fin de 2024) y a Video Action (retirada de la creación en 04-2025, mejora automática desde 07-2025, últimas campañas en 04-2026; pierde frecuencia, captación de clientes nuevos y formularios de lead en beta, y gana imágenes, carruseles y lookalike).
- Controles de canal: por grupo de anuncios, con interruptores gmail, discover, display, youtube_in_feed, youtube_in_stream y youtube_shorts. Google recomienda no restringir canales ("Do not restrict your campaigns to specific channels") salvo razón concreta.
- Audiencias: no hay segmentación dura (hard targeting); señales de audiencia, segmentos lookalike (semilla de más de 100 personas activas; varios tamaños: reducido, equilibrado, amplio). En 2026 los lookalike pasan de "restricción de segmentación" a "sugerencia"; se puede optar por mantener la restricción con el formulario oficial. Un grupo de anuncios por audiencia.
- Pujas: conversiones, valor, clics (Maximizar clics, CPC objetivo). Ver también restricciones tras migración de Display.
- Mínimos oficiales (Google en USD): Maximizar conversiones o valor, 100 $/día o más; CPA/ROAS objetivo, al menos 10 veces el CPA objetivo; no evaluar hasta 50 conversiones; consolidar grupos con menos de 30 conversiones en 30 días; cambios de 5 a 10 % semanal, máximo 15 %.
- Recursos recomendados: al menos 1 anuncio con 3 imágenes verticales, 3 cuadradas y 3 horizontales, más 1 vídeo vertical, 1 cuadrado y 1 horizontal. Vídeo: 5 segundos mínimo; menos de 10 s no sirve en In-stream de YouTube.
- Frecuencia: no se admiten límites de frecuencia en Demand Gen.
- Cuándo lo recomienda Google: captar demanda en superficies de descubrimiento y vídeo, no sustituir a Búsqueda. Para leads con 10 a 30 €/día, el umbral de 100 $/día o 10 veces el CPA objetivo lo deja fuera de las recomendaciones oficiales.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Presupuesto frente al CPA objetivo | 10 veces el CPA objetivo; 100 $/día o más con estrategias "max" | campaign_budget.amount_micros | https://support.google.com/google-ads/answer/10546923?hl=en |
| Conversiones antes de evaluar | 50 conversiones; grupos con menos de 30 en 30 días: fusionar | Estado "Learning"; conversiones por ad_group | https://support.google.com/google-ads/answer/16797388?hl=en |
| Controles de canal | Se fijan por grupo de anuncios; Google desaconseja restringir | Interfaz: ajustes del grupo. API: toggles de canal en el grupo (gmail, discover, display, youtube_in_feed, youtube_in_stream, youtube_shorts) | https://support.google.com/google-ads/answer/13695777?hl=en |
| Segmentos lookalike | Semilla de más de 100 personas activas; refresco cada 1 a 2 días; separar en grupos propios | Audience manager: estado del segmento (populating, complete, inactive, failed) | https://support.google.com/google-ads/answer/16902001?hl=en |
| Modo del lookalike | Restricción frente a sugerencia (cambio en 2026; sin fecha en la página) | Ajustes del grupo; formulario de exclusión | https://support.google.com/google-ads/answer/16902001?hl=en |
| Recursos del anuncio | 3/3/3 imágenes y 1/1/1 vídeos recomendados | API: ad_group_ad.ad.demand_gen_multi_asset_ad [SIN VERIFICAR el nombre] | https://support.google.com/google-ads/answer/10546923?hl=en |
| Especificaciones de recursos | Logo 1:1 mín. 144x144 y 150 KB; imágenes JPG/PNG de 5 MB; vídeo mín. 5 s | Interfaz | https://support.google.com/google-ads/answer/13704860?hl=en |
| Límite de frecuencia | No admitido | n/a | https://support.google.com/google-ads/answer/6034106?hl=en |
| Categorías sensibles | Limitadas a YouTube | Revisión de política | https://support.google.com/google-ads/answer/13695777?hl=en |

## Display
### Cómo funciona
- Estado actual: las campañas de Display se integran en Demand Gen como campañas "GDN dentro de Demand Gen". Fase de herramienta de migración desde junio de 2026 para anunciantes elegibles. Más adelante (sin fecha en la página) solo se podrán crear campañas de Display en Demand Gen, y las restantes elegibles se migrarán solas. Hasta migrar se pueden ver y editar las existentes.
- Migración: la herramienta conserva campañas activas y hasta 42 días de historial, con 1 a 2 días de aprendizaje. La campaña migrada se llama "[nombre] #2", la original queda Eliminada y disponible hasta 5 años en informes; no se puede revertir; los anuncios se vuelven a aprobar. Se requiere logotipo de empresa.
- Tras migrar no hay: CPC manual, impresiones visibles, pago por conversión, ajustes de puja, ajustes estacionales, pujas de cartera, audiencias combinadas, segmentación dura por renta ni estado parental, HTML5 subido hasta finales de 2026. Content suitability solo a nivel de cuenta.
- Segmentación en Display clásico: audiencias (afinidad, en mercado, datos propios), temas, emplazamientos, palabras clave de contenido, segmentación optimizada. Valores de "Targeting" (restringe) u "Observation" (solo mide). Capas extra reducen alcance.
- Segmentación optimizada: busca más allá de tus segmentos; si encuentra tráfico mejor, puede reducir o dejar de servir en tus señales.
- Exclusiones de contenido: se pueden poner en campaña, grupo de anuncios o cuenta; hasta 1.000 palabras clave de contenido y 65.000 emplazamientos a nivel de cuenta.
- Frecuencia: Display admite límites a nivel de campaña, grupo de anuncios o anuncio; la IA puede optimizarla o se fija a mano; solo cuentan impresiones visibles; se configura tras crear la campaña. Valores enteros.
- Anuncios adaptables (RDA): titulares 1 a 5 de 30 caracteres, titular largo 1 de 90, descripciones 1 a 5 de 90, nombre de empresa 25, imágenes 1,91:1 y 1:1 de 1 a 15 (recomendado 5), logos de 1 a 5 (opcionales), vídeo de 1 a 5 (opcional). Mínimos de imagen 600x314 y 300x300.
- Apps: en Display se pueden mostrar anuncios en apps y excluirlas por ID (mobileapp::1- / mobileapp::2-).
- Requisito de listas para remarketing en Display: 100 usuarios activos en 30 días.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| ¿Es campaña de Display clásica o ya GDN en Demand Gen? | Display clásico se migra; la migrada se llama "[nombre] #2" y la original queda Eliminada | Interfaz: tipo de campaña. API: campaign.advertising_channel_type | https://support.google.com/google-ads/answer/17051545?hl=en |
| Segmentación optimizada | Puede ampliar más allá de las señales | Interfaz: ajustes de segmentación del grupo | https://support.google.com/google-ads/answer/10537509?hl=en |
| Targeting frente a Observation | Targeting restringe; Observation solo mide | Interfaz: segmentos del grupo | https://support.google.com/google-ads/answer/2404191?hl=en |
| Exclusiones de contenido | Cuenta, campaña o grupo; 1.000 palabras y 65.000 emplazamientos en cuenta | Interfaz: Contenido > Exclusiones | https://support.google.com/google-ads/answer/7444288?hl=en |
| Límite de frecuencia | Disponible en Display; cuenta solo impresiones visibles | Interfaz: Ajustes > Frequency management | https://support.google.com/google-ads/answer/6034106?hl=en |
| Anuncios adaptables | Mínimos: 1 titular, 1 titular largo, 1 descripción, 1 nombre, 1 imagen 1,91:1 y 1 cuadrada | API: ad_group_ad.ad.responsive_display_ad | https://support.google.com/google-ads/answer/17090561?hl=en |
| Apps | ID de app en exclusiones | Informe de emplazamientos de Display | https://support.google.com/google-ads/answer/2454012?hl=en |
| Etiquetas de contenido digital | No se pueden marcar todas o no sirve | Interfaz: Content suitability | https://support.google.com/google-ads/answer/12764663?hl=en |

## Vídeo
### Cómo funciona
- Tipos vigentes de campaña de vídeo en Google Ads: objetivo "alcance, visualizaciones e interacciones en YouTube" con metas Reach (campañas Video reach: alcance eficiente, no saltable, frecuencia objetivo, secuencia de anuncios, audio), Video views (CPV, in-stream saltable, in-feed y Shorts) y suscripciones/interacciones.
- Video Action ya no existe: pasó a Demand Gen (ver sección Demand Gen).
- Alcance eficiente solo in-stream: desde agosto de 2026 Google las mejora a anuncios multiformato, por defecto solo in-stream; las que usan presupuesto compartido no se mejoran.
- Frecuencia en Vídeo: solo a nivel de campaña; cuenta impresiones, visualizaciones o ambas; por día, semana o mes.
- Remarketing en YouTube: un vídeo de menos de 11 s no añade usuarios a listas; los bumper tampoco.
- Mínimo para auditar: objetivo de campaña (alcance frente a conversión), pujas (tCPM, tCPV), exclusiones de emplazamientos y canales de YouTube a nivel de cuenta, content suitability, límites de frecuencia, segmentos de audiencia y que no se esté midiendo captación de leads con campañas de alcance. Si la meta es lead, Google dirige a Demand Gen.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Tipo y meta de campaña | Reach, Video views u otra; Video Action sustituida por Demand Gen | Interfaz: tipo de campaña. API: advertising_channel_type VIDEO y subtipo | https://support.google.com/google-ads/answer/15110871 |
| Campañas VAC antiguas | Últimas mejoras en 04-2026; las no mejoradas se eliminan y se crea Demand Gen en pausa | Buscar campañas "#2" o Demand Gen en pausa | https://support.google.com/google-ads/answer/15110871 |
| Eficacia de alcance eficiente | Mejora a multiformato desde 08-2026; presupuesto compartido excluido | Interfaz: formatos de la campaña | https://support.google.com/google-ads/answer/15274526?hl=en |
| Límites de frecuencia | Solo nivel de campaña | Interfaz: Frequency management | https://support.google.com/google-ads/answer/6034106?hl=en |
| Exclusión de canales y vídeos | Cuenta; no por campaña ni grupo | Interfaz: Content suitability | https://support.google.com/google-ads/answer/7331110?hl=en |
| Listas desde YouTube | Vídeo de menos de 11 s no suma usuarios | Audience manager | https://support.google.com/google-ads/answer/2545661?hl=en |

## Remarketing: tamaño mínimo de lista
### Cómo funciona
- Búsqueda, YouTube y Display: 100 usuarios activos en los últimos 30 días por red (resumen de búsqueda sobre ayuda de Google Ads y de Analytics). Una página antigua de RLSA sigue diciendo 1.000 cookies; tratar 100 como umbral vigente. [SIN VERIFICAR] la página concreta no se leyó entera.
- Customer Match: 100 usuarios coincidentes para listas subidas o actualizadas después del 01-02-2024; las anteriores siguen con el requisito antiguo de 1.000. Caducan a los 540 días; mantener al menos 100 miembros añadidos o actualizados dentro de esa ventana.
- Lookalike (Demand Gen): más de 100 personas coincidentes activas en total en las semillas. La guía de API puede decir cifras distintas (100 o 1.000), página antigua.
- Pujar por clientes nuevos: segmento de al menos 1.000 miembros activos en al menos una red [SIN VERIFICAR].
- Estados de la lista: "Open" debe estar activo; las listas pueden salir de uso si caen del mínimo, con retraso de hasta 3 días.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Tamaño de las listas de remarketing por red | 100 usuarios activos en 30 días para Búsqueda, YouTube y Display | Interfaz: Audience manager > Tamaño por red. API: user_list.size_for_search y size_for_display | https://support.google.com/google-ads/answer/7476585/about-remarketing-list-compatibility?hl=en |
| Listas de clientes (Customer Match) | 100 coincidentes tras 01-02-2024; 540 días de caducidad | Audience manager: tamaño y estado | https://support.google.com/google-ads/answer/6379332?hl=en |
| Lista abierta | Debe estar "Open" | Audience manager | https://support.google.com/google-ads/answer/2545661?hl=en |
| Lookalike | Semilla de más de 100 activas; hasta 3 días de retraso al caer | Audience manager | https://support.google.com/google-ads/answer/16902001?hl=en |
| Pujas a clientes nuevos | 1.000 miembros activos en una red [SIN VERIFICAR] | Ajustes de captación | https://support.google.com/google-ads/answer/15864839?hl=en |

## Cambios recientes
| Fecha | Cambio | URL |
|---|---|---|
| 09-04-2025 | Negativas de campaña de 100 a 10.000; objetivos de retención; imágenes de la página de destino y mejora de imágenes | https://support.google.com/google-ads/answer/16127398?hl=en |
| 2025 (datos desde 06-06-2025) | Informe de rendimiento por canal de PMax disponible en Insights y informes | https://support.google.com/google-ads/answer/16260130?hl=en |
| 07-08-2025 | Listas de negativas en PMax; temas de búsqueda de 25 a 50; términos de búsqueda en todas las campañas y por API; dispositivos y edad disponibles; género en beta; recursos con estadísticas completas; diagnóstico de objetivos | https://support.google.com/google-ads/answer/16451273 |
| 05-09-2025 | PMax, Demand Gen, Search y Shopping con objetivos web y app | https://support.google.com/google-ads/announcements/9048695?hl=en |
| 06-11-2025 | Waze como inventario de PMax para objetivos de tienda (EE. UU.) | https://support.google.com/google-ads/announcements/9048695?hl=en |
| 07-11-2025 | Controles de adecuación de marca para YouTube Feed y Discover | https://support.google.com/google-ads/announcements/9048695?hl=en |
| 08-12-2025 | Resumen 2025: Demand Gen con controles de canal, CPC objetivo; PMax con dispositivo y demografía | https://support.google.com/google-ads/answer/16756291 |
| 01-2026 | Informe de canal de PMax con segmentación Search partners para todos los clientes [SIN VERIFICAR, resumen de búsqueda de la página de novedades de Search partners] | https://support.google.com/google-ads/answer/16286960?hl=en-GB |
| 04-2026 | Últimas campañas Video Action pasadas a Demand Gen | https://support.google.com/google-ads/answer/15110871 |
| 06-2026 | Herramienta de migración de Display a Demand Gen (despliegue por fases) | https://support.google.com/google-ads/answer/17051545?hl=en |
| 06-2026 | Cambio de etiquetas de puja a "Target CPA" y "Target ROAS" sin cambio de comportamiento [SIN VERIFICAR, resumen de búsqueda] | https://support.google.com/google-ads/answer/7381968?hl=en-AU |
| 15-06-2026 | Importación sin conexión y subidas de conversiones mejoradas para leads: se bloquean en la Google Ads API y pasan a la Data Manager API (con matices de ventana) | https://support.google.com/google-ads/answer/15713840?hl=en |
| 08-2026 | Mejora automática a multiformato de Video Reach de alcance eficiente solo in-stream | https://support.google.com/google-ads/answer/15274526?hl=en |
| 2026 (sin fecha en la página) | Lookalike de Demand Gen pasa a modo sugerencia, con formulario de exclusión | https://support.google.com/google-ads/answer/16902001?hl=en |
| API v23 y v24 | Segmentación de PMax por canal desde v23 y de emplazamientos por red desde v24; expansión de URL con asset_automation_settings desde v22 | https://developers.google.com/google-ads/api/performance-max/campaign-reporting |
