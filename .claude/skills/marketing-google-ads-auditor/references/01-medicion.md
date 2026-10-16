# 01 · Medición
> Consultado el 08-10-2026. Fuentes oficiales. Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente.
> Las páginas se leyeron en inglés (`hl=en`) salvo indicación. Los nombres de interfaz en español pueden diferir.

## Acciones de conversión: principal/secundaria, recuento, ventanas, valor
### Cómo funciona
- Cada acción se marca Principal (primary) o Secundaria. Principal: entra en la columna «Conversiones» y optimiza la puja si su objetivo se usa en la campaña. Secundaria: solo se ve en «Todas las conversiones», no puja, salvo que esté dentro de un objetivo personalizado.
- Las conversiones importadas de GA4 creadas desde la interfaz de Analytics nacen como secundarias; solo se cambian a principal en Google Ads.
- Recuento por defecto «Todas»: acciones web y app, transacciones de Analytics, clics en número de móvil, importadas. Por defecto «Una»: llamadas desde anuncios, objetivos de Analytics, llamadas a número de la web, descargas de app. Para leads Google recomienda «Una».
- Ventanas (Search y Display): clic 30 días por defecto (1 a 30, 60 o 90 según el origen); interacción con vídeo (engaged-view) 3 días (1 a 30); ver-a-través 1 día (1 a 30). Google recomienda al menos 7 días. Los cambios solo afectan a conversiones futuras.
- Valor: «mismo valor» (por defecto 1,0 si no se toca), «valores distintos» (exige que la etiqueta envíe el valor; hay que fijar un valor por defecto) o «sin valor» (no recomendado). Sin snippet de evento no se pueden usar valores distintos; con URL solo valores estáticos.
- Smart Bidding necesita 7 a 14 días de aprendizaje; cambiar objetivos o acciones lo reinicia.
- GA4 y Google Ads no se pueden usar a la vez para conversiones mejoradas si la conversión viene de objetivos de Analytics importados.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Hay al menos una acción principal por cada resultado real (lead) | Solo las principales con su objetivo aplicado puntúan en «Conversiones» y puja | Objetivos > Conversiones > Resumen, columna Optimización de la acción. API: `conversion_action.primary_for_goal` | https://support.google.com/google-ads/answer/11461796?hl=es |
| Micro-conversiones (clic en botón, página vista, scroll) como principales | Una principal contamina la puja; las secundarias no puntúan | Resumen: filtrar acciones principales y revisar su categoría | https://support.google.com/google-ads/answer/10995103?hl=en |
| Recuento en leads | «Una» recomendado para formularios de lead; «Todas» infla leads si hay reenvíos | Ajustes de la acción > Recuento. API: `conversion_action.counting_type` (ONE_PER_CLICK / MANY_PER_CLICK) | https://support.google.com/google-ads/answer/3438531?hl=en |
| Ventana de clic | Por defecto 30 días, máx. 30/60/90 según origen; mínimo recomendado 7 días | Ajustes de la acción. API: `click_through_lookback_window_days`, `view_through_lookback_window_days` | https://support.google.com/google-ads/answer/3123169?hl=en |
| Ventana frente al ciclo de venta real | Usar informe de retraso (time lag) y poner ventana al menos igual | Herramientas > Atribución > Informe de retraso | https://support.google.com/google-ads/answer/6239119?hl=en |
| Valor de una acción de lead | Si queda «mismo valor» sin tocar, registra 1 por lead | Columna «Valor de conv.»; ajustes de la acción. API: `value_settings.default_value`, `always_use_default_value` | https://support.google.com/google-ads/answer/13064107?hl=en |
| Duplicados de la misma acción real (etiqueta nativa + GA4 + importada) | Solo una principal por acción real | Resumen: buscar acciones con nombres/orígenes solapados y ambas «Principal» | https://support.google.com/google-ads/answer/9520128 |
| Cambios de objetivos recientes | Reinician aprendizaje 7 a 14 días | Historial de cambios de la cuenta | https://support.google.com/google-ads/answer/11461796?hl=es |

## Estado de la acción de conversión
### Cómo funciona
- Estados vigentes en la página oficial: Activa (Active), Requiere atención (Needs attention, amarillo, no ha dejado de registrar), Mal configurada (Misconfigured, ha dejado de registrar por error de configuración o etiqueta rota), A la espera de conversiones (Awaiting conversions: ninguna en 7 días; típico si se creó hace menos de 48 h, campañas en pausa o poco tráfico), Eliminada (Removed).
- La página avisa de que algunos estados se despliegan gradualmente. Los estados antiguos («Sin conversiones recientes», «Etiqueta inactiva», «Registrando conversiones», «Sin verificar») ya no aparecen en esa página. Pueden seguir viéndose en cuentas o páginas antiguas (la ayuda de Tag Assistant y la de «Unverified» todavía los usan).
- «Unverified»: la etiqueta aún no ha disparado; con muchas conversiones por hora se actualiza en unos 10 minutos. Si dura más de 24 h: etiqueta ausente, sintaxis mal, `send_to` incorrecto, ID/etiqueta que no coincide, GTM mal configurado. Las pruebas desde la vista previa de GTM o visitando la página sin clic de anuncio pueden no registrarse.
- Latencia de informes de conversión: 3 a 24 horas; importaciones sin conexión tardan unas 3 horas en verse.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Acciones en «Mal configurada» o «Requiere atención» | Mal configurada = dejó de registrar | Objetivos > Resumen, columna Estado > «Ver detalles» / «Ver todos los problemas». API: `conversion_action.tag_snippets`, y `ConversionActionStatus` para ENABLED/REMOVED/HIDDEN | https://support.google.com/google-ads/troubleshooter/13455130?hl=en |
| «A la espera de conversiones» en una acción de lead activa | 0 conversiones en 7 días | Estado en Resumen; contrastar con CRM del mismo periodo | https://support.google.com/google-ads/troubleshooter/13455130?hl=en |
| Estados legacy («Inactive», «Unverified») en cuentas que aún los muestran | Usar Tag Assistant: lanzar desde el Resumen en acciones Unverified, Tag inactive o Needs attention; el estado se actualiza en unos 30 min | Botón «Solucionar problemas» junto a la acción | https://support.google.com/google-ads/answer/10989978?hl=en |
| Unverified > 24 h | Causas: etiqueta ausente/mal formada, `send_to` erróneo, valor con símbolo de moneda o coma | Consola de Chrome («Uncaught SyntaxError»), pestaña Network con llamadas a googleadservices.com | https://support.google.com/google-ads/answer/10029065?hl=en |
| Acción creada automáticamente no asignable a GTM | Las acciones autocreadas no se pueden mapear a etiquetas de conversión de GTM; crear una manual para obtener ID y etiqueta | Estado «Misconfigured» con GTM | https://support.google.com/google-ads/answer/12674892?hl=en |
| Acción no marcada como principal pese a registrar | Marcar Principal y aceptar términos (p. ej. conversiones mejoradas) | Resumen > Optimización | https://support.google.com/google-ads/answer/12674892?hl=en |
| Campaña «Elegible (Mal configurada): falta la etiqueta de Google» | Suele significar que no hubo conversiones puntuables en los últimos 28 días | Estado de campaña | https://support.google.com/google-ads/answer/14681508?hl=en |

## Objetivos de conversión (cuenta y campaña)
### Cómo funciona
- Las acciones se agrupan automáticamente en objetivos estándar por categoría (Compras, Contactos, Enviar formulario de lead, etc.).
- Objetivo predeterminado de cuenta: sus acciones principales cuentan y pujan en todas las campañas sin objetivos propios. Una acción solo puja si es Principal Y su objetivo está aplicado a la campaña.
- Objetivos específicos de campaña: anulan los de cuenta. Se pueden combinar objetivos estándar y personalizados; solo un objetivo personalizado por campaña. Un objetivo personalizado puede mezclar principales y secundarias y TODAS cuentan para puja e informes.
- Si se vacía el objetivo específico, la campaña vuelve a los de cuenta. Cambiar objetivos de cuenta no se propaga a campañas con objetivos propios.
- Smart Bidding solo considera lo que sale en la columna «Conversiones». Google recomienda objetivos predeterminados de cuenta para que las campañas aprendan entre sí.
- Las campañas de app definen acciones siempre a nivel de campaña. Las campañas Smart optimizan un conjunto menor de objetivos.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Campañas con objetivos propios que ignoran cambios de cuenta | Los cambios de cuenta no llegan a campañas con objetivos de campaña | Ajustes de campaña > Objetivos; API: `campaign.conversion_goal_config.goal_config_level` (CUSTOMER / CAMPAIGN) y `campaign_conversion_goal` | https://support.google.com/google-ads/answer/9143218?hl=en |
| Objetivo predeterminado de cuenta desactivado o con acción equivocada | Bidding usa los objetivos de cuenta activos de las acciones principales | Objetivos > Resumen, columna «Objetivo de cuenta». API: `customer_conversion_goal` (campo `biddable`) | https://support.google.com/google-ads/answer/4677036?hl=en |
| Más de un objetivo personalizado en la misma campaña | Máximo uno | Ajustes de campaña > Objetivos | https://support.google.com/google-ads/answer/9143218?hl=en |
| Acciones secundarias dentro de un objetivo personalizado (puntúan en puja) | Todas cuentan en puja e informes | Objetivo personalizado > composición. API: `custom_conversion_goal.conversion_actions` | https://support.google.com/google-ads/answer/11461796?hl=es |
| Categoría de la acción coherente con el resultado real | La acción entra en el objetivo según su categoría | Resumen > categoría. API: `conversion_action.category` | https://support.google.com/google-ads/answer/10995103?hl=en |

## Conversiones mejoradas (web y leads)
### Cómo funciona
- Envían datos propios (correo, teléfono, nombre, dirección) con hash SHA256 junto a la conversión. Requieren aceptar los términos de datos de cliente; sin ello no se recopila nada. También requieren parámetros de consentimiento en «granted» cuando aplica.
- Datos mínimos: correo (recomendado), o dirección completa (nombre, apellidos, código postal, país), o teléfono acompañado de correo o de nombre y dirección. Teléfono en E.164 (11 a 15 dígitos, con «+»). Arrays: hasta 3 correos, 3 teléfonos, 2 direcciones. Antes del hash: recortar espacios, minúsculas, sin puntos en gmail.com/googlemail.com.
- Métodos de recogida con la etiqueta de Google: detección automática, selectores CSS/variables JavaScript o snippet de código (el snippet tiene prioridad).
- Verificación: la petición a googleadservices.com/pagead/conversion/ o google.com/pagead/1p-conversion/ debe llevar `em` que empiece por `tv.1~em` seguido del hash; si solo aparece `tv.1~em`, los datos llegaron vacíos.
- Informe de diagnóstico: a las ~72 h de implantar; resultados en la tabla de acciones a los ~30 días; el entrenamiento puede tardar hasta 30 días.
- Desde abril 2026 conversiones mejoradas para web y para leads son un único ajuste (on/off) y Google Ads acepta datos de usuario por etiqueta web, Data Manager y API a la vez; los usuarios existentes se migran automáticamente.
- Leads: se capturan datos hash del formulario con la etiqueta (o GTM) y se importan después, con los mismos datos hash y el GCLID, cuando el lead avanza en el CRM. Se importa con Data Manager (recomendado) o API.
- Importación: cada evento necesita marca de tiempo y al menos un identificador (GCLID, datos de usuario o GBRAID/WBRAID). El GCLID es obligatorio si no se recogen datos con etiqueta. No se importan conversiones a más de 90 días del último clic; para conversiones mejoradas de leads el límite es 63 días. Usar Order ID para evitar duplicados.
- Cambio de puja al nuevo origen: pasar a principal la nueva acción de leads tras el mayor de 3 ciclos de conversión o 4 semanas, y la antigua a secundaria.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Conversiones mejoradas activadas y términos aceptados | Sin términos no hay recogida | Objetivos > Ajustes > Conversiones mejoradas. API: `customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled` | https://support.google.com/google-ads/answer/9888656?hl=es |
| Estado de la acción: «Registrando (procesando datos...)», «Registrando (Conversiones mejoradas)» | Entrenamiento hasta 30 días; la conversión sigue funcionando | Columna Estado de la acción | https://support.google.com/google-ads/answer/10868881?hl=es |
| Calidad de datos del diagnóstico | Excellent, Good, Needs attention, No recent data (ninguna mejorada en 7 días) | Resumen > acción > Diagnóstico | https://support.google.com/google-ads/answer/11954870?hl=en |
| Volumen mínimo del diagnóstico | Alertas ocultas con menos de 20 conversiones en 7 días (se recomiendan 20 por semana); la tasa de coincidencia INSUFFICIENT_VOLUME si hay menos de 20 pings PII válidos | Mismo informe | https://support.google.com/google-ads/answer/11954870?hl=en |
| Tasa de coincidencia | LOW 0% a 15%, HIGH por encima del 15% | Mismo informe | https://support.google.com/google-ads/answer/11954870?hl=en |
| Alertas típicas del diagnóstico | Faltan campos de dirección (país, nombre, apellidos, código postal); falta transaction ID; correo o dirección sin normalizar antes del hash; etiqueta mal configurada; datos de la API enviados con más de 24 h | Mismo informe | https://support.google.com/google-ads/answer/11954870?hl=en |
| Parámetro `em` presente en la petición de conversión | Debe empezar por `tv.1~em` + hash | DevTools > Network, filtro `pagead/conversion` o `1p-conversion` | https://support.google.com/google-ads/answer/9888656?hl=es |
| Teléfono sin correo o sin nombre+dirección | No válido por sí solo | Revisar el formulario o la variable de GTM | https://support.google.com/google-ads/answer/9888656?hl=es |
| Plazo de importación de leads | 90 días tras el último clic; 63 para conversiones mejoradas de leads | Importaciones: errores de ventana. API/Data Manager: error de lookback | https://support.google.com/google-ads/answer/15081888?hl=en |
| Identificador en cada fila importada | marca de tiempo + (GCLID o datos de usuario o GBRAID/WBRAID); con BRAID el recuento debe ser «Todas» | Fichero o llamada de subida | https://support.google.com/google-ads/answer/15479791 |
| Order ID en importaciones | Evita duplicados; los duplicados se descartan con error | Resultados de la subida | https://support.google.com/google-ads/answer/15081888?hl=en |

## Importación sin conexión: Google Ads API frente a Data Manager API
### Cómo funciona
- Google migra las subidas de conversiones sin conexión y de conversiones mejoradas para leads a la Data Manager API. Según las páginas de ayuda de Google Ads, desde el 15-06-2026 la Google Ads API deja de aceptar estas subidas para tokens de desarrollador que no las hubieran enviado antes (`UploadClickConversions` falla para ellos). Los tokens sin ninguna petición entre enero y junio de 2026 no entran en la lista de acceso heredado.
- La página de la Google Ads API (`upload-offline`) confirma esa restricción y recomienda «Use the Data Manager API instead». Los campos de atributos de sesión (`session_attributes_*`) y `user_ip_address` solo para usuarios en lista de permitidos. Detalles de la Data Manager API (cuotas, retractaciones, cuenta gestora) no se documentan aquí por quedar fuera de los dominios admitidos [SIN VERIFICAR].
- Desde el 03-10-2025 se aceptan GBRAID, GCLID y datos de usuario en una sola fila sin error.
- La gestión de Max es por REST propia: si el token de desarrollador no tenía histórico de subidas antes de la fecha, `uploadClickConversions` fallará y hay que usar Data Manager.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Subidas de leads hechas con `uploadClickConversions` | Falla desde 15-06-2026 para tokens sin histórico | Respuesta de error de la API; revisar el origen del token y su uso previo | https://developers.google.com/google-ads/api/docs/conversions/upload-offline |
| Migración a Data Manager (`IngestEvents`) | Recomendada por Google en lugar de la Google Ads API para estas subidas | Revisar el código/flujo del cliente | https://support.google.com/google-ads/answer/15479791 |
| Estado de importación | Datos visibles en ~3 h; contrastar con columna «Todas las conv. (por hora de conversión)» | Informe de diagnóstico de importaciones sin conexión | https://support.google.com/google-ads/answer/15081888?hl=en |
| Plan de fechas del cambio | 15-06-2026 bloqueo Google Ads API; abril 2026 ajuste unificado | Páginas de ayuda | https://support.google.com/google-ads/answer/15713840 |

## Modo de consentimiento v2
### Cómo funciona
- Cuatro parámetros: `ad_storage` (cookies/ids de publicidad), `ad_user_data` (enviar datos de usuario a Google con fines publicitarios), `ad_personalization` (publicidad personalizada), `analytics_storage` (cookies de analítica). Hay además tres de privacidad: `functionality_storage`, `personalization_storage`, `security_storage`.
- Sin valores por defecto: «By default, no consent mode values are set»; hay que fijarlos. El `default` debe ir antes de cualquier `config` o `event`; luego el CMP y `update`. `wait_for_update` (ms) da tiempo a que el CMP llame a `update`; el ejemplo oficial usa 500. `region` admite códigos ISO 3166-2 (p. ej. 'ES'); gana la región más específica.
- Efecto de «denied»: `ad_storage` no escribe ni lee cookies publicitarias; `ad_user_data` desactiva uso de datos personales (user_id, datos aportados), limita la exportación por clic-ID y las conversiones salen como pings sin cookies; `ad_personalization` desactiva remarketing; `analytics_storage` no lee ni escribe cookies de GA y manda pings sin cookies. Con `ad_storage` denegado y `ads_data_redaction` activo se redactan GCLID/DCLID.
- Básico: las etiquetas se bloquean hasta que el usuario interactúa con el banner; si no consiente no se envía nada, ni el estado. Modelado con modelo general. Avanzado: las etiquetas cargan con los valores por defecto (denegado salvo configuración) y mandan pings sin cookies; tras consentir mandan datos completos. Modelado específico del anunciante.
- Los pings sin cookies llevan marca de tiempo, user agent, referrer y estado de consentimiento; los identificadores de clic (GCLID/DCLID) se redactan.
- Modelado de conversiones en Google Ads: requisitos de calidad, ambos: consentimiento correctamente implantado (o TCF v2.0) y un umbral diario de 700 clics de anuncio en 7 días, medido por país y agrupación de dominio. Después hay un periodo de entrenamiento; el modelado aparece en «Conversiones» y «Valor de conversión».
- Resultados de impacto del modo de consentimiento: aparecen tras 7 días completos; se actualizan semanalmente y se muestran 4 semanas desde el inicio del modelado; el incremento por debajo del 1% no se muestra; se calcula por dominio x país.
- Política de consentimiento de usuarios de la UE: obliga, para usuarios del EEE, Reino Unido y Suiza, a obtener consentimiento legalmente válido para cookies/almacenamiento local y para recoger/compartir/usar datos personales para personalización; conservar registros y dar instrucciones de revocación. Incumplir puede limitar, suspender o terminar el uso del producto.
- Desde marzo de 2024 en el EEE son necesarios `ad_user_data` y `ad_personalization`; `ad_user_data` es necesario para mediciones como conversiones mejoradas y seguimiento por etiqueta. Si las etiquetas esperan a la interacción con el banner, Google no puede verificar el consentimiento y puede haber pérdida de datos.
- Qué pasa con etiquetas que disparan antes de conocerse el consentimiento: en avanzado, con denegado por defecto, envían pings sin cookies y sin ID de clic; en básico no se carga nada.
- Cookiebot figura como socio CMP en la ayuda de Tag Manager (modo básico); ver «Set up Cookiebot to obtain user consent» enlazado en la página.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Los cuatro parámetros llegan en el `default` y en el `update` | `ad_storage`, `ad_user_data`, `ad_personalization`, `analytics_storage` | Tag Assistant / vista previa de GTM, pestaña Consent; parámetros `gcs` y `gcd` en las peticiones (su significado: [SIN VERIFICAR] en la fuente) | https://support.google.com/google-ads/answer/13802165?hl=en |
| Orden: `default` antes que cualquier etiqueta | Si el `default` no va antes de las etiquetas de Google, estas se comportan como si no hubiera consent mode | Diagnóstico de etiqueta «Consent mode installation out of order»; Tag Assistant | https://support.google.com/google-ads/answer/12962079?hl=en |
| Etiquetas de Google con comprobaciones de consentimiento adicionales o activadores de excepción antiguos | Las etiquetas de Google ya traen comprobación propia: poner «Additional Consent Checks» en «Not set» y quitar excepciones previas en etiquetas de Google Ads, Analytics, Floodlight y Conversion Linker; con CMP asíncrono pueden dispararse antes del `update` y no volver a dispararse | GTM > etiqueta > Ajustes de consentimiento; Tag Assistant: Tags Fired / Tags Not Fired | https://support.google.com/google-ads/answer/12962079?hl=en |
| Modo básico o avanzado | Básico: etiquetas bloqueadas hasta el banner; avanzado: pings sin cookies | Con el banner sin tocar, ¿salen peticiones de Google? (pestaña Network) | https://support.google.com/google-ads/answer/10000067?hl=en |
| Elegibilidad del modelado | 700 clics diarios durante 7 días por país y dominio + consentimiento bien implantado | Resumen > acción > Diagnóstico (impacto, «Conversion modeling for consent mode is active») | https://support.google.com/google-ads/answer/10548233?hl=en |
| Pocas clics para modelar (cuentas de 10 a 30 €/día) | Con ~700 clics por 7 días y país no se llega en cuentas pequeñas; no hay modelado de anunciante (el valor esperado para una cuenta pequeña es un cálculo propio, no cifra oficial) | Clics por país en 7 días frente al umbral | https://support.google.com/google-ads/answer/10548233?hl=en |
| Diagnóstico «Consent missing for EEA users» / «Some pages missing consent for EEA users» | EEE sin etiquetar con consentimiento | Diagnóstico de etiqueta > Tag quality | https://support.google.com/google-ads/answer/14681508?hl=en |
| «Website missing EEA consent for ads personalization» | Modo v1 autodelegado o sin consentimiento de personalización en v2 | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |
| «0% consent rate detected» | `ad_user_data` denegado enviado siempre, sin importar región | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |
| Banner que bloquea etiquetas hasta interacción | Google no puede verificar elecciones y hay pérdida de datos | Tag Assistant en visita nueva sin interactuar | https://support.google.com/google-ads/answer/13695607?hl=en |
| Caída de medición EEE tras actualizar consentimiento | Comprobar que el CMP pasa `gcs` y `gcd`; errores CORS en consola; listar dominios de Google en cabeceras | Tag Assistant, consola | https://support.google.com/google-ads/answer/17300195?hl=en |
| `allow_ad_personalization_signals` en conflicto con `ad_personalization` | Si chocan, la personalización se desactiva | Revisión de etiquetas | https://support.google.com/google-ads/answer/13695607?hl=en |
| Cookiebot + GTM | Con la plantilla de Cookiebot para GTM no hace falta más configuración; con instalación manual hay que poner el estado de consentimiento por defecto como script antes de la etiqueta de Google. La guía de Cookiebot recomienda sustituir activadores de carga de página por el evento personalizado `cookie_consent_update`. Ojo: esa guía pide «Require additional consent for tag to fire» en modo avanzado, mientras la guía «Unblock Google tags» dice que las etiquetas de Google no deben llevar comprobaciones adicionales (ver Cambios recientes) | Script del CMP antes de la etiqueta de Google; plantilla de Cookiebot en GTM | https://support.google.com/google-ads/answer/14546767?hl=en |

## Conversiones de llamada
### Cómo funciona
- Tipos: llamadas desde anuncios (activos de llamada/ubicación; requiere informe de llamadas y acción activa y principal); llamadas a un número de la web (etiqueta de Google + snippet de llamada web + número de reenvío de Google); clics en un número del móvil (se miden clics, no llamadas); clics en anuncios y activos de llamada (Google estima si hubo llamada); importación de llamadas (desde un CRM, para contar solo las que hayan vendido).
- Duración mínima: la fija el anunciante por acción, en segundos. El valor por defecto [SIN VERIFICAR] en las páginas leídas. Los números de la persona que llama se facilitan para llamadas de más de 15 segundos (excepto India).
- Llamadas desde la web: miden llamadas hasta 60 días después del clic. Número de reenvío: sigue conectando durante 60 días desde la última llamada de ese usuario; si la primera llamada llega pasados unos 30 minutos (hasta ~2 h en algunos mercados) desde que vio el anuncio, no conecta.
- España figura en la lista de países con número de reenvío de Google (la tabla es una imagen; si es gratuito o local: [SIN VERIFICAR]).
- Motivos por los que el número no se muestra o falla: informe de llamadas desactivado; en móvil el número del anuncio es el de la empresa y el de reenvío aparece al marcar; no hay número local y sale uno gratuito; no funciona para activos de llamada en Display; conflicto con el número de anuncio del Perfil de Empresa en anuncios de mapas; sistemas con «early media» (menús de voz) pueden dar llamadas perdidas; país no elegible (en ese caso el informe de llamadas debe estar desactivado). Los números pertenecen a Google, pueden cambiar y no se pueden usar fuera del informe y el seguimiento.
- Importación de llamadas: exige números de reenvío; hasta 25.000 filas por fichero; dentro de la ventana de la acción (hasta 90 días); solo llamadas de móvil para anuncios solo de llamada y activos de llamada. Si el usuario marca sin hacer clic en el anuncio no cuenta.
- Anuncios de llamada (call ads): según los anuncios de Google, en 03-10-2025 se anunció su retirada y la migración a activos de llamada en anuncios de búsqueda adaptables.
- Llamadas cualificadas por IA (AI-qualified call leads): requiere grabación; solo EE. UU. y Canadá. No aplica a España.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Informe de llamadas activado y país elegible | Obligatorio para llamadas desde anuncios, web e importación | Ajustes de la cuenta > Informe de llamadas | https://support.google.com/google-ads/answer/2454052?hl=en |
| Acción de llamada activa y principal | Si no es principal no puntúa | Resumen. API: `conversion_action.type` (AD_CALL, WEBSITE_CALL, PHONE_CALL_LEAD...) y `primary_for_goal` | https://support.google.com/google-ads/answer/6100664?hl=en |
| Duración mínima razonable | La fija el anunciante; demasiado alta pierde llamadas válidas | Ajustes de la acción. API: `phone_call_duration_seconds` | https://support.google.com/google-ads/answer/12674892?hl=en |
| Recuento de llamadas | Por defecto «Una» en llamadas de anuncios y a número de la web | Ajustes de la acción | https://support.google.com/google-ads/answer/3438531?hl=en |
| Snippet de llamada web + etiqueta de Google en todas las páginas con el número | Verificar con Tag Assistant | Tag Assistant | https://support.google.com/google-ads/answer/6100664?hl=en |
| Número de reenvío no se muestra | Ver causas arriba | Prueba con clic real de anuncio en móvil y escritorio | https://support.google.com/google-ads/answer/2382961?hl=en |
| Clics en número del móvil contados como conversión de llamada | Solo se miden clics | Origen de la acción en el Resumen | https://support.google.com/google-ads/answer/6100664?hl=en |
| Importaciones de llamadas fallidas | Ventana, formato de teléfono y zona horaria; 25.000 filas máx. | Informe de diagnóstico de importación | https://support.google.com/google-ads/answer/7545087?hl=en |
| Anuncios de llamada heredados | Retirada anunciada el 03-10-2025 | Tipos de anuncio en la cuenta | https://support.google.com/google-ads/announcements/9048695?hl=en |

## Etiquetado automático, etiqueta de Google, Conversion Linker y GA4
### Cómo funciona
- Etiquetado automático (auto-tagging): añade `gclid` a las URL; activado por defecto en cuentas nuevas y necesario para seguimiento en todos los navegadores, importar conversiones sin conexión y conectar con GA. Para llegar a la página final el GCLID debe sobrevivir a las redirecciones. Si el sitio rechaza parámetros desconocidos y da error, desactivar, permitir el parámetro y reactivar. Con GA4, el etiquetado automático tiene prioridad sobre el manual.
- GBRAID: parámetro para web a app en iOS 14.5+; WBRAID para app a web. Son identificadores agregados no únicos y distinguen mayúsculas y minúsculas. En importaciones, con BRAID el recuento debe ser «Todas». Aplicable a Search, Shopping, Display y Performance Max. La fuente no confirma en la página de ayuda leída el detalle de WBRAID.
- Conversion Linker: guarda la información de clic de la URL en cookies propias (`_gcl_aw`, `_gcl_gs`) y en almacenamiento local (`_gcl_ls`). Hay que desplegarlo en toda página donde pueda aterrizar un usuario tras un anuncio, con el activador «All Pages». Si el contenedor ya carga una etiqueta de Google en todas las páginas, no hace falta otro.
- Importación de eventos clave de GA4: requiere propiedad GA4 enlazada con flujo web y eventos clave; las conversiones creadas desde GA llegan como secundarias. «Google no puede garantizar que no se dupliquen»; elegir una sola fuente principal por acción.
- Etiqueta de Google y transaction ID: los transaction ID evitan duplicados y el diagnóstico avisa si falta o si coinciden menos del 10% entre la etiqueta y la otra fuente en 2 días.
- Google tag gateway (anunciado 02-05-2025) para mejorar la medición. El diagnóstico recomienda activarlo si detecta CDN tipo Cloudflare (despliegue gradual).

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Etiquetado automático activado | Obligatorio para web en todos los navegadores y para importaciones | Admin > Configuración de la cuenta. API: `customer.auto_tagging_enabled` | https://support.google.com/google-ads/answer/3095550?hl=en |
| Redirecciones que pierden el GCLID | El GCLID debe llegar a la página final | Diagnóstico de etiqueta «Website redirects are losing click data» (despliegue gradual); probar la URL final con `?gclid=test` | https://support.google.com/google-ads/answer/14681508?hl=en |
| Plantilla de seguimiento o parámetros de URL que rompen el sitio | Parámetros rechazados provocan error | Visitar la URL final con parámetros | https://support.google.com/google-ads/answer/3095550?hl=en |
| Conversion Linker presente | Debe dispararse en todas las páginas; detecta la información de clic en la URL y la guarda en cookies propias del dominio. Desactivarlo (`conversion_linker` = false) no se recomienda | GTM: etiqueta Conversion Linker; diagnóstico «Missing conversion linker» | https://support.google.com/google-ads/answer/7521212?hl=en |
| Cookies propias de clic tras llegar con un anuncio | La etiqueta de Google/Conversion Linker las crea en el dominio (nombres `_gcl_*`: [SIN VERIFICAR] en la ayuda de Google Ads) | DevTools > Application > Cookies | https://support.google.com/google-ads/answer/7521212?hl=en |
| Etiqueta de Google en todas las páginas | Páginas no etiquetadas | Diagnóstico de etiqueta «Some of your pages are not tagged» y «Some of your landing pages are not tagged» | https://support.google.com/google-ads/answer/14681508?hl=en |
| Doble conteo GA4 + etiqueta nativa | Solo una principal; GA4 importado queda secundario por defecto | Resumen: comparar acciones del mismo evento | https://support.google.com/google-ads/answer/9520128 |
| Doble conteo por transaction ID | Menos de 10% coincide en 2 días | Diagnóstico «Your conversions may be overcounted» | https://support.google.com/google-ads/answer/14681508?hl=en |
| Etiqueta dejó de enviar datos | 48 h = estado Urgente | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |
| Orden de config | «Config command out of order», «Tag found too low on page» | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |
| Seguridad (CSP) bloquea recursos de Google | Diagnóstico «Content Security Policy blocks some resources» | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |
| GBRAID/WBRAID en importaciones | Recuento «Todas»; sin variables personalizadas con BRAID | Fichero de importación | https://support.google.com/google-ads/answer/15479791 |

## Atribución, columnas y retraso de conversión
### Cómo funciona
- Modelos vigentes: último clic y basado en datos (data-driven). Primer clic, lineal, con caída temporal y según posición ya no se admiten; las acciones que los usaban pasaron a basado en datos. Basado en datos es el valor por defecto para la mayoría de acciones.
- Basado en datos: la página «About data-driven attribution» recomienda al menos 200 conversiones y 2.000 interacciones en 30 días, pero dice que todas las acciones son elegibles sea cual sea el volumen. La página «Switch to DDA» da 3.000 interacciones y 300 conversiones en 30 días para ser elegible y 2.000 / 200 para mantenerla, para ciertos tipos de acciones (sin precisar cuáles).
- «Conversiones»: solo acciones principales, con el recuento elegido, atribuidas al día del clic. «Todas las conversiones»: principales y secundarias más fuentes especiales como ver-a-través. Variantes «(por hora de conversión)» informan por la fecha de la conversión.
- Ver-a-través: tras una impresión, ventana por defecto 1 día. Se refleja en «Todas las conversiones».
- Retraso: los datos recientes están incompletos porque las conversiones se atribuyen al día del clic. Google sugiere que el informe termine al menos 30 días antes (más si la ventana es mayor). Los informes pueden tardar 24 a 48 h en consolidar. Existe un informe de retraso y estimaciones de retraso de conversión (disponibilidad y umbrales: [SIN VERIFICAR]).
- Conversiones fraccionarias: indican un modelo de atribución multitoque que reparte crédito.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Modelo de atribución de cada acción | Solo último clic o basado en datos | Ajustes de la acción. API: `conversion_action.attribution_model_settings.attribution_model` | https://support.google.com/google-ads/answer/6259715?hl=en |
| Volumen para DDA | Recomendado 200 conv. y 2.000 interacciones en 30 días; sin umbral duro en la página principal; 3.000/300 para ser elegible en «Switch to DDA» | Columna «Elegibilidad DDA» | https://support.google.com/google-ads/answer/6394265?hl=en y https://support.google.com/google-ads/answer/10762625?hl=en |
| Se juzga la campaña con los últimos días | Datos recientes incompletos; terminar el informe 30 días atrás o más | Informe de retraso (Atribución) y columnas por hora de conversión | https://support.google.com/google-ads/answer/6239119?hl=en |
| Se confunde «Todas las conversiones» con «Conversiones» | Todas incluye secundarias y ver-a-través | Columnas del informe | https://support.google.com/google-ads/answer/6270625?hl=en-EN |
| Ver-a-través contado como resultado | Ventana 1 día por defecto | Ajustes de la acción | https://support.google.com/google-ads/answer/3123169?hl=en |
| Conversiones decimales | Atribución multitoque | Columnas de conversión con decimales | https://support.google.com/google-ads/answer/17300195?hl=en |
| Contraste con CRM | Diferencias de tracking visibles | Comparar leads del CRM con «Conversiones» del mismo periodo | https://support.google.com/google-ads/answer/17300195?hl=en |

## Diagnósticos de medición en la interfaz
### Cómo funciona
- Tag Diagnostics (pestaña Diagnostics > Tag quality en la etiqueta de Google, accesible desde Google Ads, GA y GTM): estados de calidad Excellent, Good, Needs attention, Urgent, No recent data. Urgent = una etiqueta antes detectada que no envía datos en 48 horas. Lista de avisos: 22 vigentes y 2 en despliegue.
- Los avisos descartados siguen visibles 90 días mientras el problema persista.
- Diagnóstico de conversiones mejoradas: ver la sección correspondiente.
- Impacto/diagnóstico del modo de consentimiento: Objetivos > Resumen > «Todas las conversiones» > acción con icono de tendencia > pestaña Diagnóstico. «Conversion modeling for consent mode is active» en la tarjeta.
- Tag Assistant: lanza la prueba de conversión para acciones Unverified, Tag inactive o Needs attention.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Panel Tag quality | Excellent, Good, Needs attention, Urgent, No recent data | Etiqueta de Google > Diagnóstico | https://support.google.com/google-ads/answer/14681508?hl=en |
| Diagnóstico de conversiones mejoradas | Estados «Recording», «Not in use», «Waiting» (hasta 48 h), «Setup issues», «No recent data» | Resumen > acción > Diagnóstico | https://support.google.com/google-ads/answer/11954870?hl=en |
| Impacto de consentimiento | 7 días completos, 4 semanas de resultados, incremento mínimo 1% | Diagnóstico de la acción | https://support.google.com/google-ads/answer/11954524?hl=en |
| Cobertura de la etiqueta | Datos en horas; vista 7 o 30 días | Informes de cobertura de etiqueta | https://support.google.com/google-ads/answer/11954870?hl=en |
| Un solo administrador de etiqueta | Aviso «Only one administrator detected» | Diagnóstico de etiqueta | https://support.google.com/google-ads/answer/14681508?hl=en |

## Cambios recientes
- 2023-06 / 2023-07: retirada de primer clic, lineal, caída temporal y según posición en Google Ads (anunciada el 21-06-2023). https://support.google.com/google-ads/answer/6259715?hl=en
- 2024-03: `ad_user_data` y `ad_personalization` obligatorios para EEE (consent mode v2). https://support.google.com/google-ads/answer/13695607?hl=en
- 2025-05-02: Google tag gateway para anunciantes. https://support.google.com/google-ads/announcements/9048695?hl=en
- 2025-10-03: retirada anunciada de los anuncios de llamada (call ads) hacia activos de llamada. https://support.google.com/google-ads/announcements/9048695?hl=en
- 2025-10-03: una fila de importación puede llevar GBRAID, GCLID y datos de usuario a la vez. https://support.google.com/google-ads/answer/15479791
- 2026-01: cambios de IP y atributos de sesión en la Google Ads API; los campos `session_attributes_*` y `user_ip_address` quedan limitados a usuarios en lista de permitidos. https://developers.google.com/google-ads/api/docs/conversions/upload-offline
- 2026-04: conversiones mejoradas para web y leads unificadas en un solo ajuste; migración automática. https://support.google.com/google-ads/answer/9888656?hl=es
- 2026-05-15: existe una entrada del blog de desarrolladores de Google Ads sobre cambios en la importación de conversiones sin conexión; no está en un dominio admitido y no se usa como fuente. La restricción se documenta en https://developers.google.com/google-ads/api/docs/conversions/upload-offline
- 2026-06-15: la Google Ads API deja de aceptar subidas sin conexión y de conversiones mejoradas para leads de tokens sin histórico; la alternativa que recomienda Google es la Data Manager API. https://developers.google.com/google-ads/api/docs/conversions/upload-offline
- Estados de conversión: la página oficial actual lista Active, Needs attention, Misconfigured, Awaiting conversions, Removed y avisa de que algunos aún se despliegan. Las páginas antiguas usan «No recent conversions», «Inactive», «Unverified», «Recording conversions». Una fuente no oficial fecha el cambio en julio de 2026 [SIN VERIFICAR]. https://support.google.com/google-ads/troubleshooter/13455130?hl=en
- Contradicción: «About consent mode» (Google Ads) dice en la tabla que el avanzado empieza en denegado salvo configuración y en el cuerpo que parte de consentido salvo elección. Fijar siempre el `default` explícitamente. https://support.google.com/google-ads/answer/10000067?hl=en
- Contradicción: volumen de DDA (recomendación de 200/2.000 sin umbral duro frente a 300/3.000 para «Switch to DDA»). https://support.google.com/google-ads/answer/6394265?hl=en y https://support.google.com/google-ads/answer/10762625?hl=en
- Contradicción menor en la ventana de conversión de tienda frente a la de clic: la página «store visit» da 1 a 30 días, otras fuentes hasta 90; para leads web se aplica la de la acción (30 por defecto). https://support.google.com/google-ads/answer/9462121?hl=en
