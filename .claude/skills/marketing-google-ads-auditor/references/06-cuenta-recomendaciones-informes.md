# 06 · Cuenta, recomendaciones e informes
> Consultado el 08-10-2026. Fuentes oficiales. Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente.

## Nivel de optimización
### Cómo funciona
- Se calcula en tiempo real a partir de estadísticas, configuración y estado de cuentas y campañas, más el impacto potencial de las recomendaciones disponibles y el historial reciente de recomendaciones. Rango 0 % a 100 %; el impacto por recomendación va de <0,1 % a 100 %.
- Es una estimación del rendimiento potencial, no una medida del rendimiento actual. No se usa para determinar el nivel de calidad.
- La suma de impactos de todas las recomendaciones puede superar 100, porque aplicar unas anula otras.
- El foco depende de la estrategia de puja; sin estrategia, por defecto se enfoca en conversiones.
- Disponible a nivel de campaña, cuenta y cuenta de administrador. Solo muestran nivel las campañas activas de Búsqueda, Display, Vídeo de acción, App, Performance Max, Demand Gen y Shopping.
- Descartar una recomendación la quita de la lista pero no sube el nivel. Las descartadas pueden volver a aparecer. "Descartar todo" muestra el valor total atribuido a lo descartado.
- API: `Customer.optimization_score`, `Customer.optimization_score_weight`, `metrics.optimization_score_url`, `metrics.optimization_score_uplift`; segmentable por `segments.recommendation_type`. Para varias cuentas: nivel x peso.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Nivel no equivale a calidad de la cuenta | "No se usa para determinar el nivel de calidad"; es estimación de potencial | Recomendaciones > nivel; API `customer.optimization_score` | https://support.google.com/google-ads/answer/9061546?hl=es |
| Subir el nivel no es objetivo | Aplicar una recomendación de 5 % sube la cuenta 5 %; la suma puede pasar de 100 | Cada tarjeta muestra su % de impacto | https://support.google.com/google-ads/answer/9061546?hl=es |
| Muchas recomendaciones descartadas | Reaparecen tras 28 o 60 días según el motivo | Recomendaciones > burbuja "Dismissed" | https://support.google.com/google-ads/answer/10169817 |
| Nivel por tipo de recomendación | Segmentación por tipo | GAQL `segments.recommendation_type` con `metrics.optimization_score_uplift` | https://developers.google.com/google-ads/api/docs/recommendations |

## Recomendaciones: catálogo y riesgo
### Cómo funciona
- La página de Recomendaciones revisa el historial de rendimiento, la configuración de campañas y tendencias de Google. Las estimaciones usan datos pasados y no predicen resultados. Si la cuenta no tiene historial, puede no haber ninguna.
- Aplicar: Recomendaciones > Ver > Aplicar, o "Aplicar todo" por tarjeta. Las de puja o presupuesto admiten "Guardar como experimento". Lo aplicado queda en el historial de cambios y se puede deshacer en 30 días; las aplicaciones parciales no se pueden deshacer.
- Descartar: "Descartar todo" en la tarjeta. Una aceptación parcial mantiene la tarjeta hasta descartar. Descartar a nivel de campaña oculta ese tipo solo en esa campaña; a nivel de cuenta, en todas hasta pasar el plazo. Se recupera con "Undismiss all" desde la burbuja Dismissed.
- Pestaña Resultados: mide el impacto de lo aplicado en presupuesto y objetivos (Optimize/Adjust your budgets, Adjust CPA targets, Adjust ROAS targets), a la semana de aplicar; media móvil de 7 días sobre 28 días; informe disponible solo 28 días; se corta si cambias a mano puja o presupuesto.
- Catálogo (Google Ads Help, agrupado por Google):

**Pujas y presupuestos** (marcadas [Budget]/[Bidding] por Google): Adjust your budgets [Budget]; Adjust CPA targets; Adjust ROAS targets; Maximize clicks / Maximize conversions / Maximize conversion value / Target CPA / Target impression share / Target ROAS (cambio de estrategia); Move unused budgets [Budget] (se activa si se perdió 5 % o más del tráfico potencial la semana pasada); Raise your budgets [Budget] (mismo 5 %); Raise budgets for upcoming traffic increases (5 % o más de tráfico semanal futuro); Set a bidding strategy target; Set a target CPA; Set a target CPA/ROAS to capture upcoming traffic increases [Bidding][Budget]; Use a portfolio bid strategy with a shared budget; Add store visits in conversions; Include Firebase app conversion actions in account-level goals; Smart Bidding Exploration Beta; Data-driven attribution.

**Palabras clave y segmentación**: Add broad match keywords; Add new keywords; Create a custom audience; Expand reach with Google search partners; Google video partners; Reach new audiences; Refresh Customer Match lists (más de 90 días sin actualizar); Remove conflicting negative keywords; Remove non-serving keywords (un año o más sin tráfico); Remove redundant keywords; Set up audience sources; Target all eligible Shopping products; Turn on AI Max for Search campaigns; Upload customer lists / Customer Match; Use Display Expansion (usa presupuesto de Búsqueda no gastado en Display); Use optimized targeting; Create a new ad group for a broader audience.

**Anuncios y recursos**: Add assets to RSAs; call assets; callouts; sitelink descriptions; dynamic image assets; dynamic sitelink assets; image assets; lead form assets; price assets; responsive display ads; responsive search ads (grupos con menos de 3 RSA); sitelinks; structured snippets; location assets; video; Enable text customization; Improve RSAs (ad strength inferior a "Good"); Improve RDAs / Demand Gen / Apps / PMax asset groups (inferior a "Excellent"); Use optimized ad rotation; Audience Gap; Merchant Integration; Add products to your videos.

**Campañas automatizadas**: Create a Performance Max campaign (también con store goals); Improve PMax asset groups; Target more products with PMax; Turn on AI Max.

**Medición**: Turn on auto-tagging; Set up conversion tracking; conversion value measurement; enhanced conversions; global site tag (y su reparación); Google Analytics property; in-app conversion tracking; Fix certification issues; Optimize for new customers.

**Reparaciones**: Add ads to each ad group; Add keywords to each ad group; Fix disapproved sitelinks / PMax assets / Demand Gen assets / Shopping products; Fix your ad text; Fix your ad destinations; Fix low CPA targets; Fix your audience targeting; Fix your conversion action with a conversion rate drop; Fix your conversion tracking; Merchant Center suspension (fix y prevent); Complete advertiser verification; Fix misconfigured deep links (10 % o más mal configurados); Fix overlapping App campaigns.

- Tipos en la API (v25, "totalmente soportados"): CAMPAIGN_BUDGET, KEYWORD, TEXT_AD, TARGET_CPA_OPT_IN, MAXIMIZE_CONVERSIONS_OPT_IN, MAXIMIZE_CONVERSION_VALUE_OPT_IN, ENHANCED_CPC_OPT_IN, MAXIMIZE_CLICKS_OPT_IN, OPTIMIZE_AD_ROTATION, MOVE_UNUSED_BUDGET, TARGET_ROAS_OPT_IN, FORECASTING_CAMPAIGN_BUDGET, RESPONSIVE_SEARCH_AD, MARGINAL_ROI_CAMPAIGN_BUDGET, USE_BROAD_MATCH_KEYWORD, RESPONSIVE_SEARCH_AD_ASSET, RESPONSIVE_SEARCH_AD_IMPROVE_AD_STRENGTH, DISPLAY_EXPANSION_OPT_IN, SEARCH_PARTNERS_OPT_IN, CUSTOM_AUDIENCE_OPT_IN, PERFORMANCE_MAX_OPT_IN, RAISE_TARGET_CPA, LOWER_TARGET_ROAS, SET_TARGET_CPA, SET_TARGET_ROAS, RAISE_TARGET_CPA_BID_TOO_LOW, SITELINK_ASSET, CALLOUT_ASSET, CALL_ASSET, LEAD_FORM_ASSET, IMPROVE_GOOGLE_TAG_COVERAGE, REFRESH_CUSTOMER_MATCH_LIST y los SHOPPING_* y de migración a PMax. KEYWORD_MATCH_TYPE está obsoleto (usar USE_BROAD_MATCH_KEYWORD).
- Las recomendaciones cambian a diario; el `resource_name` puede quedar obsoleto, hay que actuar pronto. `RecommendationService` no da errores por datos insuficientes. Al aplicar keywords el anunciante es responsable de cumplir políticas.

### Comprobaciones de auditoría
Riesgo para cuentas pequeñas: criterio propio (marcado "criterio") apoyado en lo que dice la descripción de Google.

| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Add broad match keywords | Solo con Maximize conversions, Maximize conversion value, Target CPA o Target ROAS; Google dice que "puede requerir presupuesto adicional" y que con puja manual lo desaconseja; sus cifras (25 % más conversiones en tCPA, 12 % más valor en tROAS) son medias internas de 2020. Criterio: riesgo alto con 10-30 EUR/día | Tipo `USE_BROAD_MATCH_KEYWORD`; Recomendaciones > Keywords | https://support.google.com/google-ads/answer/10195720?hl=en |
| Raise your budgets / upcoming traffic / Adjust your budgets | Se disparan con 5 % o más de tráfico perdido; Google no da recomendación de presupuesto si rara vez se alcanza el medio diario o hay pocos datos. Criterio: sube gasto | Tipos `CAMPAIGN_BUDGET`, `FORECASTING_CAMPAIGN_BUDGET`, `MARGINAL_ROI_CAMPAIGN_BUDGET` | https://support.google.com/google-ads/answer/3416396?hl=en |
| Cambios de estrategia de puja (Maximize clicks, Target CPA, Target ROAS, Target impression share) y ajustar objetivos | Google los presenta como "más conversiones a coste similar" según simulaciones. Criterio: cambian la puja de toda la campaña | Tipos `*_OPT_IN`, `RAISE_TARGET_CPA`, `LOWER_TARGET_ROAS`, `SET_TARGET_*` | https://support.google.com/google-ads/answer/3416396?hl=en |
| Turn on AI Max / Enable text customization | Google espera ROI similar o mejor; amplía emparejamiento y texto | Campaña > ajustes AI Max | https://support.google.com/google-ads/answer/3416396?hl=en |
| Display Expansion y Search partners | Display Expansion gasta presupuesto de Búsqueda "no gastado" en Display; partners "a menor CPC" | Tipos `DISPLAY_EXPANSION_OPT_IN`, `SEARCH_PARTNERS_OPT_IN` | https://support.google.com/google-ads/answer/3416396?hl=en |
| Smart Bidding Exploration, portfolio con presupuesto compartido, Create a PMax | Cambian estructura o puja | Pestaña Recomendaciones | https://support.google.com/google-ads/answer/3416396?hl=en |
| Recomendaciones de reparación (anuncios, keywords, rechazos, conversión) | Son correcciones, no mejoras | Tipos de reparación | https://support.google.com/google-ads/answer/3416396?hl=en |
| Recomendación aplicada que no se puede deshacer | Deshacer solo en 30 días y no en aplicaciones parciales | Historial de cambios | https://support.google.com/google-ads/answer/10169817 |
| Recomendaciones sin objetivo calculado | Objetivos recomendados no se calculan con menos de 7 conversiones | Revisar a mano | https://support.google.com/google-ads/answer/17125145?hl=en-GB |

## Recomendaciones aplicadas automáticamente
### Cómo funciona
- Opt-in a nivel de cuenta (no por campaña). Se aplican de forma periódica y solo cuando son relevantes; cada día el sistema decide a cuáles eres elegible y aparecen en una cola al final de la página Recomendaciones. Se pueden elegir una a una o con los paquetes "Maintain your ads" y "Grow your business". "Maintain your ads" no sube ni cambia presupuesto.
- Tipos auto-aplicables según Google: Ads y assets (Improve RSAs, Add dynamic search ads, optimized ad rotation); Pujas (Adjust CPA/ROAS targets, Maximize clicks/conversions/conversion value, Target CPA/impression share/ROAS, Set target CPA/ROAS, Set a bidding strategy target, store visits); Keywords y segmentación (Add audiences, Add broad match keywords, Add keywords, search partners, Remove redundant / non-serving / conflicting negative keywords, targeting expansion, Display expansion); Medición (Upgrade your conversion tracking). No incluye subir presupuesto.
- Ver cuáles hay activas: Recomendaciones > Auto-apply settings (pestañas Manage e History), o Admin > Account settings > Auto-apply. History muestra cuándo se activó cada una, veces aplicadas en la última semana y última aplicación. Quién la activó: historial de cambios filtrado por la fecha de activación.
- Desactivar: en Manage, desmarcar y Guardar; o en History, seleccionar y "Disable" (punto rojo en las desactivadas). Resumen semanal por email solo con las notificaciones de mantenimiento activadas.
- El texto oficial no dice si alguna viene activada por defecto [SIN VERIFICAR].
- API: `RecommendationSubscription` (status ENABLED) para ENHANCED_CPC_OPT_IN, KEYWORD, KEYWORD_MATCH_TYPE, LOWER_TARGET_ROAS, MAXIMIZE_CLICKS_OPT_IN, OPTIMIZE_AD_ROTATION, RAISE_TARGET_CPA, RESPONSIVE_SEARCH_AD, RESPONSIVE_SEARCH_AD_IMPROVE_AD_STRENGTH, SEARCH_PARTNERS_OPT_IN, SET_TARGET_CPA, SET_TARGET_ROAS, TARGET_CPA_OPT_IN, TARGET_ROAS_OPT_IN, USE_BROAD_MATCH_KEYWORD. Lo aplicado: `change_event` con `change_event.client_type = GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION`.
- Diferencia con otras automatizaciones: auto-apply cambia keywords, pujas, anuncios y segmentación mediante recomendaciones. Los **recursos automáticos de cuenta** (account-level automated assets) crean y muestran recursos (sitelinks, callouts, estructurados dinámicos, información de negocio, imágenes dinámicas, ubicación automatizada, promociones automatizadas, valoraciones de vendedor, visitas al sitio) cuando se predice mejora; se ven en Assets > filtro "Added by" = Google AI; se apagan en Assets > Associations > menú ⋮ > Account level automated assets > Advanced settings. Los **recursos creados automáticamente** (hoy "personalización de texto") generan titulares y descripciones extra para RSA y son ajuste de **campaña**; ahora van dentro de AI Max.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Qué auto-apply hay activado | Opt-in a nivel de cuenta | Recomendaciones > Auto-apply settings > Manage; API `recommendation_subscription` | https://support.google.com/google-ads/answer/10276359?hl=en |
| Qué se aplicó y cuándo | History: veces en la última semana y última aplicación | Auto-apply settings > History; `change_event.client_type = GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION` | https://support.google.com/google-ads/answer/10276359?hl=en |
| "Add broad match keywords" auto-aplicado | Está en la lista de auto-aplicables | Manage tab | https://support.google.com/google-ads/answer/10279006?hl=en |
| Cambios de puja auto-aplicados | Lista de pujas auto-aplicables (objetivos, estrategia) | Manage tab | https://support.google.com/google-ads/answer/10279006?hl=en |
| Keywords auto-añadidas con DKI | Con Dynamic Keyword Insertion no se auto-aplica "Add keyword" | Revisar grupos con DKI | https://support.google.com/google-ads/answer/10279006?hl=en |
| Recursos automáticos de cuenta activos | Lista de nueve tipos; se desactivan por tipo con motivo | Assets > filtro "Added by: Google AI" | https://support.google.com/google-ads/answer/7175034?hl=en |
| Recursos automáticos a nivel de cuenta vs campaña | Las campañas heredan el ajuste de cuenta y se puede anular por campaña | Assets > Associations > Account level automated assets | https://support.google.com/google-ads/answer/16049135?hl=en |
| Personalización de texto (antes recursos creados automáticamente) | Ajuste de campaña; requiere AI Max | Informe de recursos de RSA; columna "Added by" | https://support.google.com/google-ads/answer/11259373?hl=en |
| Cobro de interacciones con recursos automáticos | Se cobra el clic en botón de llamada creado automáticamente; máximo 2 clics cobrados por impresión; valoraciones de vendedor no se cobran | Informe de recursos | https://support.google.com/google-ads/answer/7175034?hl=en |

## Ajustes de cuenta
### Cómo funciona
- **Etiquetado automático**: activado por defecto en cuentas nuevas; crear una acción de evento clave lo activa salvo seguimiento entre cuentas (entonces hay que activarlo a mano en cada cuenta hija). Casilla "Tag the URL that people click through from my ad" en Admin > Account settings. Requisito para seguimiento de conversiones en algunos navegadores, importación offline y vincular GA4. Algunos sitios devuelven error con parámetros extra; con redirecciones, el GCLID debe llegar a la página final.
- **Plantilla de seguimiento**: se puede definir en cuenta, campaña, grupo, anuncio, palabra clave y sitelink; el más específico manda (palabra clave > anuncio > grupo > campaña > cuenta). La plantilla y todas las redirecciones deben ser HTTPS, con redirecciones en servidor. El seguimiento paralelo es obligatorio en Búsqueda, Shopping, Display, Vídeo y PMax (opcional en hoteles). Cambios en cuenta, campaña y grupo no requieren reaprobación; en anuncio, palabra clave y sitelink sí.
- **Sufijo de URL final**: Admin > Account settings > Tracking template > "Final URL suffix"; también en campaña, grupo, anuncio, palabra clave y sitelink.
- **Negativas de cuenta**: máximo 1.000 por cuenta; amplia, frase o exacta; no emparejan variantes cercanas; aplican a inventario de búsqueda y shopping en Búsqueda, PMax, App, Shopping, Smart y Local. Listas de negativas: hasta 5.000 por lista y 20 listas por cuenta; negativas por campaña hasta 10.000; en Display y Vídeo solo se consideran 1.000.
- **Exclusiones de emplazamientos de cuenta**: afectan a Display, YouTube y Red de partners de búsqueda (desde marzo de 2024; sin efecto en subdominios/subpáginas en partners); en PMax solo se gestionan a nivel de cuenta. Hasta 20.000 a la vez y 65.000 por cuenta; las nuevas tardan "typically" hasta 12 horas; sin "www." para cubrir subdominios; cada dominio de país necesita su exclusión.
- **Idoneidad de contenido (Content suitability)**: tipos de inventario (Máximo, Moderado, Limitado), tipos y etiquetas de contenido, temas y palabras clave excluidas (hasta 1.000), emplazamientos. Aplica a Display, YouTube y partners de vídeo; PMax también. Google avisa de que no puede garantizar excluir todo el contenido relacionado. No excluir todas las etiquetas de contenido (la campaña no se serviría).
- **Exclusiones de IP**: hasta 500 por campaña; cuenta en Admin > Account settings > IP exclusions; comodín `*` en el último octeto. No disponible a nivel campaña en Vídeo, hoteles, App, PMax y Smart Display; el nivel de cuenta sí cubre PMax. Si coexisten, se fusionan. Hay que excluir todas las versiones de la IP.
- **Vinculaciones**: se gestionan en Herramientas > Data manager (Connected products). GA4: requiere acceso administrativo en Ads, autoetiquetado activo y permiso Edit en la propiedad; permite importar eventos clave como conversiones. Merchant Center: invitación desde cualquiera de los dos lados; se desvincula desde Data manager > Google Merchant Center > Details; hasta 500 cuentas de Ads por cuenta de Merchant. YouTube: Google puede vincular canales y cuentas automáticamente con aviso de 30 días y opt-out. Search Console: no hay página oficial en los dominios permitidos [SIN VERIFICAR].
- **Accesos**: niveles Email-only, Billing, Read-only, Standard y Admin. Solo Admin añade/quita vinculaciones de producto, da acceso, cambia niveles y revisa método de autenticación y último inicio de sesión. Una sola cuenta de administrador pone en riesgo el acceso a las etiquetas.
- **Seguridad**: 2SV muy recomendada, no se dice obligatoria; los MCC pueden imponer mandatos (exigir 2SV o Protección Avanzada; fecha "Required as of" por defecto a 7 días). Cada Cuenta de Google puede tener acceso directo a hasta 20 cuentas de Ads. "Confirm it's you" y passkeys para acciones sensibles. Security Agent (Admin > Access and security > Security > Security insights).
- **Zona horaria y moneda**: se fijan al crear la cuenta; no se pueden cambiar en cuentas de servicio estándar ("Time zone changes are no longer supported in standard serving accounts"). Un MCC puede reajustarse una vez, solo hacia el este. Los informes segmentados por tiempo siguen la zona de la cuenta; la zona no afecta a la entrega. Moneda no modificable [SIN VERIFICAR en la página de zona horaria; la frase aparecía en un resumen de búsqueda de https://support.google.com/google-ads/answer/9842104?hl=en].

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Etiquetado automático activo | Activado por defecto en cuentas nuevas; con seguimiento entre cuentas, manual en cada hija | Admin > Account settings > Auto-tagging; API `customer.auto_tagging_enabled` | https://support.google.com/google-ads/answer/3095550?hl=en |
| Plantilla de seguimiento válida | HTTPS en plantilla y redirecciones; seguimiento paralelo obligatorio | Account settings > Tracking template; `customer.tracking_url_template` | https://support.google.com/google-ads/answer/6076199?hl=en |
| Parámetros propios en sufijo en lugar de plantilla | Sufijo se añade a la URL final | Account settings > Final URL suffix; `customer.final_url_suffix` | https://support.google.com/google-ads/answer/9054021?hl=en |
| Negativas de cuenta | 1.000 máx.; sin variantes cercanas | Admin > Account settings > Negative keywords | https://support.google.com/google-ads/answer/11396330?hl=en |
| Listas de negativas | 5.000 por lista; 20 listas | Biblioteca compartida | https://support.google.com/google-ads/answer/2453983?hl=en |
| Exclusiones de emplazamientos de cuenta | 20.000 a la vez, 65.000 por cuenta; 12 h de retardo; incluyen PMax y partners | Campañas > Audiences, keywords and content > Content; historial de cambios | https://support.google.com/google-ads/answer/7331110?hl=en |
| Idoneidad de contenido | Tres tipos de inventario; palabras clave excluidas hasta 1.000; sin garantía total | Herramientas > Content suitability | https://support.google.com/google-ads/answer/12764663?hl=en |
| Exclusiones de IP | 500 por campaña; límite de cuenta no indicado | Admin > Account settings > IP exclusions | https://support.google.com/google-ads/answer/2456098?hl=en |
| Límites generales de cuenta | Ver tabla de límites (negativas 10.000 por campaña, 20 listas, etc.) | Página de límites | https://support.google.com/google-ads/answer/6372658?hl=en |
| Vinculación GA4 | Admin en Ads + autoetiquetado + Edit en GA4 | Herramientas > Data manager > Google Analytics (GA4) y Firebase > Manage & link | https://support.google.com/google-ads/answer/7519537?hl=en |
| Vinculación Merchant Center | Invitación bilateral; desvincular desde Data manager | Data manager > Google Merchant Center > Details | https://support.google.com/google-ads/answer/10576895?hl=en |
| Vinculación automática de YouTube | Aviso de 30 días y opt-out | Data manager | https://support.google.com/google-ads/answer/16749726 |
| Usuarios y niveles | Solo Admin gestiona accesos y vinculaciones; evitar un único Admin | Admin > Access and security > Users | https://support.google.com/google-ads/answer/9978556?hl=en |
| Usuarios inactivos y mínimos privilegios | Quitar a quien ya no trabaja en la cuenta; no compartir logins; revisar "Related managers" | Access and security > Users y Related managers | https://support.google.com/google-ads/answer/12864492?hl=en |
| 2SV | Muy recomendada; sin estado por usuario descrito en la página | Admin > Access and security > Security | https://support.google.com/google-ads/answer/12864186?hl=en |
| Mandatos de seguridad del MCC | Exigir 2SV a todos; fecha "Required as of" a 7 días por defecto | MCC > Access and security | https://support.google.com/google-ads/answer/12865295 |
| Hallazgos de seguridad automáticos | Dominios de correo, usuarios inusuales, exceso de acceso (Admin que no usa admin), cuentas dormidas | Admin > Access and security > Security > Security insights | https://support.google.com/google-ads/answer/17034850?hl=en |
| Zona horaria | No se cambia en cuentas estándar; afecta a informes, no a entrega | Account settings; `customer.time_zone` | https://support.google.com/google-ads/answer/17006726?hl=en |

## Historial de cambios
### Cómo funciona
- Registra cambios en cuenta, campañas y grupos (pausar, añadir keyword, presupuestos anteriores), con línea temporal junto a impresiones, clics, conversiones, CTR y coste. Retención: 2 años ("Data older than 2 years won't be available").
- Pestaña Change overview: vistas By user, By campaign y Performance. Filtros: campaña, grupo, tipo de cambio, usuario, herramienta, elemento cambiado, experimento de campaña, fecha.
- Autor: cambios desde la interfaz muestran el email del usuario; la API muestra "Google Ads API" o el nombre de la herramienta de terceros; sistemas automáticos o internos aparecen como "Google Ads system" o "ads-dartsearch-budget". La página no menciona reglas automatizadas ni recomendaciones como tipos de autor, aunque indica que los cambios por reglas, API y Editor aparecen. No se registran cambios de contraseña. A veces no se listan todos los cambios de ajustes de cuenta; los hechos por representantes de Google pueden no aparecer; para ver todos los detalles, cambios menores de 2.000 entidades.
- Deshacer: botón Undo en la columna "User / Date & Time"; vale para la mayoría de tipos en los últimos 30 días; una fila con varios cambios se revierte entera; no se puede si el elemento se eliminó o ya se deshizo.
- API `change_event`: filtro de fecha dentro de los últimos 30 días, `LIMIT` máximo 10.000, hasta 3 minutos de retardo, `user_email` solo si es visible en la web, no soporta cambios de Google Ads Editor (usar `change_status`). `change_status`: ventana de 90 días, máximo 10.000 filas, devuelve ADDED/CHANGED/REMOVED y solo el último cambio por recurso. Valores de `client_type`: solo se confirma GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION y GOOGLE_ADS_EDITOR; lista completa [SIN VERIFICAR].

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Quién cambia qué (usuario, API, sistema) | Email de usuario; "Google Ads API"/herramienta; "Google Ads system" | Campañas > Change history > By user | https://support.google.com/google-ads/answer/19888?hl=en |
| Cambios de la ventana de 2 años | Retención 2 años | Change history con rango de fechas | https://support.google.com/google-ads/answer/2454137?hl=en |
| Deshacer un cambio reciente | Undo solo en 30 días | Columna "User / Date & Time" | https://support.google.com/google-ads/answer/2454137?hl=en |
| Cambios por API en bloque | `change_event`: 30 días, 10.000 filas | GAQL `change_event` | https://developers.google.com/google-ads/api/docs/change-event |
| Cambios de Editor y vista completa | `change_status` 90 días | GAQL `change_status` | https://developers.google.com/google-ads/api/docs/change-status |
| Cambios aplicados por recomendaciones automáticas | Filtro `client_type` | GAQL `change_event.client_type = GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION` | https://developers.google.com/google-ads/api/docs/recommendations |

## Experimentos y borradores
### Cómo funciona
- La página Experimentos (antes "borradores y experimentos") agrupa: variaciones de anuncio (solo Búsqueda, RSA, cambio único en varias campañas; se divide por cookies), AI Max (prueba de un clic en Búsqueda, divide la campaña 50/50 en vez de copiarla), recursos de App, personalizados (Smart Bidding, tipos de concordancia, páginas de destino, audiencias, grupos; App, Búsqueda o Display según la página; también Demand Gen y Vídeo), Demand Gen, Performance Max (uplift, upgrade, optimización) y Vídeo (2 a 4 brazos, éxito por Brand lift o conversiones). Se puede crear un experimento personalizado sin borrador.
- Requisitos de experimento personalizado: campaña activa, presupuesto individual (no compartido), estrategia estándar (no cartera), sin anuncios de texto expandido. Un reparto 50/50 controla la elegibilidad en la subasta pero no garantiza impresiones ni gasto iguales. En Búsqueda: reparto por cookies (recomendado) o por búsquedas (puede alcanzar significación antes pero un usuario puede ver ambas versiones); Display siempre por cookies. La página cita "más de 100 conversiones diarias" como mínimo de la campaña base; cifra no contrastada en el texto íntegro [SIN VERIFICAR].
- AI Max: no se puede crear si la campaña tiene personalización de texto, Display, estrategia de cartera, presupuesto compartido, bidding exploration o experimentos activos. Si no se aplica, los ajustes AI Max vuelven a como estaban.
- PMax: uplift (mide valor añadido de PMax junto a otras campañas), upgrade (simula pasar Shopping estándar, DSA o GDA a PMax) y optimización (final URL expansion con personalización de texto, y pruebas de recursos). Tras aplicar migración, PMax toma el 100 % y el control se pausa.
- Lectura de resultados: primera línea del cuadro es el total del experimento; segunda, diferencia estimada frente al original con rango de confianza ("--" si faltan datos). "80 % es el intervalo de confianza por defecto"; asterisco azul = estadísticamente significativo. Causas de no significación: poco tiempo, poco tráfico, reparto pequeño o sin diferencia real. Columna Results: control, tratamiento o "No clear winner / In progress".
- Duración: "2 a 3 semanas" para reunir datos; si el estado es In progress, Undecided o Unavailable, al menos 4 a 6 semanas; 7 a 14 días para que el brazo de tratamiento se estabilice. Campaign Guidance (Búsqueda y PMax) da "Experiment Power": Baja 0-49 %, Media 50-79 %, Alta 80-99 %.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Cambios de puja o estructura hechos sin experimento | Los experimentos existen para probar Smart Bidding, concordancias, páginas y audiencias antes de aplicar | Campañas > Experiments | https://support.google.com/google-ads/answer/10682377?hl=en |
| Requisitos de experimento personalizado | Activa, presupuesto individual, estrategia estándar, sin texto expandido | Setup del experimento | https://support.google.com/google-ads/answer/10683687 |
| Significación | 80 % por defecto; asterisco azul; 2-3 semanas | Experiments > Scorecard | https://support.google.com/google-ads/answer/6318747?hl=en |
| Potencia del experimento | Baja 0-49 %, Media 50-79 %, Alta 80-99 % | Campaign Guidance | https://support.google.com/google-ads/answer/15911255?hl=en |
| Experimento AI Max | Incompatibilidades listadas; 50/50 | Experiments > AI Max | https://support.google.com/google-ads/answer/16450159?hl=en |
| Variaciones de anuncio | Solo RSA; alcance cuenta, campaña o personalizado | Experiments > Ad variations | https://support.google.com/google-ads/answer/7438541?hl=en |
| Experimentos de PMax | Uplift, upgrade, optimización | Experiments > Performance Max | https://support.google.com/google-ads/answer/12997711?hl=en |
| Borradores | Límite de 25 borradores en la cuenta | Página de límites | https://support.google.com/google-ads/answer/6372658?hl=en |

## Informes
### Cómo funciona
- **Comparativa de subasta** (Auction insights): disponible en Búsqueda (6 estadísticas), Shopping (3) y PMax (a nivel de cuenta y campaña, segmentado Búsqueda/Shopping). Cuota de impresiones = impresiones / impresiones elegibles estimadas. Tasa de solapamiento: con cuánta frecuencia el anuncio de otro anunciante salió cuando el tuyo (60 % = 6 de cada 10). Cuota de superación: veces que quedaste por encima o saliste cuando el otro no. Tasa de posición superior (solo Búsqueda). Tasa de parte superior de página y de primera posición absoluta (solo Búsqueda). Disponibilidad mínima: no hay datos si la cuota de impresiones es inferior al 10 %, y keywords, grupos o campañas deben superar un umbral mínimo de actividad (número no indicado). Los partners de búsqueda se excluyen. Datos de Shopping desde octubre de 2014; PMax desde noviembre de 2021.
- **Páginas de destino**: Campañas > Insights & reports > Landing pages. Columnas: tasa de clics móvil amigable, tasa de clics AMP válida, clics, impresiones, CTR. Incluye sitelinks desde enero de 2021 (para anuncios servidos). La tasa móvil puede tener hasta 14 días de antigüedad. Incluye URLs seleccionadas por expansión de URL final (columna "Selected by"). No se indica retención.
- **Términos de búsqueda**: lista de términos que "un número significativo de personas" usó. Se omiten los de bajo volumen por privacidad; las categorías de "Search terms insights" usan los últimos 56 días. La columna Keyword está oculta por defecto. En Report Editor no se pueden añadir negativas. No compatible con visitas y ventas en tienda. Muchos términos mal escritos no cumplen el umbral de privacidad.
- **Ubicaciones**: ubicaciones **segmentadas** (targeted) = rendimiento por las ubicaciones que elegiste; ubicaciones **coincidentes** (matched) = dónde apareció el anuncio, ya sea ubicación física del usuario o ubicación de interés (búsquedas, visitas pasadas, contenido visto). Pueden aparecer filas "Unspecified". Los valores por debajo de país pueden no sumar el total de la campaña.
- **Cuándo y dónde**: Campañas > Insights & reports > When and where ads showed, con pestañas de dispositivos, programación de anuncios (día y hora) y "Where ads showed" (emplazamientos). "Where ads showed" omite emplazamientos con muy pocas impresiones, no se limpia de tráfico no válido y las conversiones rara vez se limpian; Google desaconseja sobreoptimizar con ella.
- **Informe de recursos**: puntuaciones por recurso (Learning, Low, Good, Best, relativo a recursos del mismo tipo; Unrated con pocos recursos). Fuente de las etiquetas en la ayuda de Display: https://support.google.com/google-ads/answer/13063616?hl=en-AU. El de RSA: ruta exacta [SIN VERIFICAR].
- **Diagnóstico de campaña**: comprueba más de 90 señales en ocho áreas (Account, Ads, Audiences, Bidding & budget, Business Data, Goals, Products, Signals), centrado en la última semana.
- **Estadísticas (Insights)**: se actualizan a diario; categorías: Budget pacing, Diagnostic, Search trends, Demand forecasts, Search terms, Audience, Target pacing y Performance; rango 7 o 28 días; no siempre se generan.
- **Vista previa de anuncios (Ad Preview and Diagnosis)**: Herramientas > Troubleshooting. No suma impresiones. No muestra anuncios mientras la cuenta esté en verificación de facturación o suspendida por seguridad; con "Reason unknown" puede haber periodo de aprendizaje.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Comparativa de subasta | Sin datos con cuota de impresiones <10 %; 6 estadísticas en Búsqueda | Campañas > Insights and reports > Auction insights; excluye partners | https://support.google.com/google-ads/answer/2579754?hl=en |
| Páginas de destino y tasa móvil | Tasa móvil <100 % = la página no pasa siempre la prueba móvil; dato de hasta 14 días | Insights and reports > Landing pages | https://support.google.com/google-ads/answer/7543502?hl=en |
| Términos de búsqueda: negativas pendientes | Se ocultan términos de bajo volumen; datos no exhaustivos | Insights and reports > Search terms; columna Keyword y tipo de concordancia | https://support.google.com/google-ads/answer/2472708?hl=en |
| Ubicaciones físicas vs de interés | Matched incluye interés; Targeted no | Informe Locations (Matched / Targeted) | https://support.google.com/google-ads/answer/2453994?hl=en |
| Dispositivo, día y hora | Informes por dispositivo y programación | Insights and reports > When and where ads showed | https://support.google.com/google-ads/answer/13787926?hl=en |
| Emplazamientos | Informe incompleto y sin limpieza de tráfico no válido | When and where ads showed > Where ads showed | https://support.google.com/google-ads/answer/13787926?hl=en |
| Diagnóstico | 90+ señales, ocho áreas | Overview de campaña > View campaign diagnostics | https://support.google.com/google-ads/answer/12327514?hl=en |
| Insights | Se refrescan a diario, 7 o 28 días | Insights and reports > Insights | https://support.google.com/google-ads/answer/10256472?hl=en |
| Vista previa de anuncios | No computa impresiones | Tools > Troubleshooting > Ad Preview and Diagnosis | https://support.google.com/google-ads/answer/148778?hl=en-GB |

## Definiciones de métricas
### Cómo funciona
- **Interacciones**: "la acción principal del usuario asociada con un formato de anuncio" (clics en texto y Shopping, visualizaciones en vídeo). **Tasa de interacción** = interacciones / impresiones. **Coste medio** = coste total / interacciones.
- **CTR**: clics / impresiones (5 clics en 100 impresiones = 5 %).
- **CPC medio**: importe pagado / total de clics; puede diferir del CPC máximo.
- **Conversiones**: acciones principales (puede incluir conversiones modeladas); **Todas las conv.**: principales y secundarias más otras fuentes como visualizaciones. Las columnas de conversiones se basan en la fecha del clic; las "por tiempo de conversión" en la fecha de la conversión (diferencias de hasta ~20 % esperables). Retrasos de informe de 24 a 48 h.
- **Coste / conv.** = coste total / Conversiones, contando solo interacciones elegibles.
- **Tasa de conv.** = conversiones / interacciones rastreables a una conversión; puede superar el 100 % con varias acciones o con "Cada" conversión.
- **Valor de conv. / coste** = valor de conversión / coste. La página no lo relaciona con ROAS.
- **Impr. (parte superior) %** = impresiones en la parte superior / impresiones elegibles; **Impr. (primera posición absoluta) %** = impresiones en posición absoluta / impresiones (no elegibles). Absoluta es subconjunto de parte superior. Las tasas describen colocación y no deben usarse como objetivo de puja; las cuotas "Search top IS" y "Search abs. top IS" sí.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Interacciones vs clics | Interacciones dependen del formato | Columnas Interactions, Interaction rate, Avg. cost | https://support.google.com/google-ads/answer/6162977?hl=en-GB |
| CTR | clics / impresiones | Columna CTR | https://support.google.com/google-ads/answer/2615875?hl=en-AU |
| CPC medio | coste / clics | Columna Avg. CPC | https://support.google.com/google-ads/answer/14074?hl=en |
| Cost/conv. y Conversiones vs Todas conv. | Conversiones = acciones principales; fecha del clic | Columnas Conversions, All conv., Cost / conv. | https://support.google.com/google-ads/answer/6270625?hl=en |
| Tasa de conversión | Puede superar 100 % con varias acciones | Columna Conv. rate | https://support.google.com/google-ads/answer/2684489?hl=en |
| Valor de conv. / coste | valor / coste | Columna Conv. value / cost | https://support.google.com/google-ads/answer/13405059?hl=en |
| Impr. superior y absoluta | Fórmulas con denominadores distintos | Columnas Impr. (Top) %, Impr. (Abs. Top) %; API `metrics.top_impression_percentage`, `metrics.absolute_top_impression_percentage` (nombres de campo de la API: [SIN VERIFICAR] en esta página) | https://support.google.com/google-ads/answer/7501826?hl=en |

## Clics no válidos
### Cómo funciona
- Tráfico que no representa interés genuino: bots y software automatizado, clics accidentales (anuncios mal colocados), colocaciones fraudulentas (clickjacking, ad stacking), competidores o usuarios pagados.
- Google usa filtros automáticos, aprendizaje automático y revisión manual. Lo detectado antes del cierre de facturación sale de las métricas y de la factura; lo detectado después se compensa con un crédito "Invalid activity" en el siguiente ciclo (Facturación > Resumen > Adjustments). Los créditos no cambian retroactivamente las métricas: para ver cifras ajustadas hay que usar el Invalid Activity Credit Report (Report Editor, plantilla "Invalid Activity Credit Report: Search & PMax"; columnas Credited clicks, Credited interactions, Credited amount, Adjusted cost, Adjusted clicks, etc.; solo Búsqueda y PMax).
- Columnas: "Invalid clicks" e "Invalid click rate" (solo página Campañas); "General invalid clicks" y su tasa (solo Búsqueda y Display).
- Solicitud de investigación: formulario Click Quality Form, cubre los últimos 60 días; la revisión tarda varios días hábiles; Google no confirma qué clics concretos marcó. No hay umbral oficial de "tasa normal".
- Medidas que sí cita Google para el anunciante: ajustar ubicaciones, negativas, idoneidad de contenido; para leads, reCAPTCHA, validación en servidor, doble opt-in y conversiones mejoradas. Las IP aparecen solo como dato para la investigación, no como medida recomendada en esa página.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Tasa de clics no válidos | Sin umbral oficial | Columnas Invalid clicks / Invalid click rate en Campañas | https://support.google.com/google-ads/answer/2549113?hl=en |
| Créditos por actividad no válida | Se acreditan después de facturar, sin tocar métricas | Billing > Summary > Adjustments; Invalid Activity Credit Report | https://support.google.com/google-ads/answer/16826168?hl=En |
| Solicitud de investigación | 60 días, Click Quality Form | Formulario, con GCLID y logs | https://support.google.com/google-ads/answer/11182074?hl=en |
| Filtro de clics no válidos | Columna "Invalid clicks" disponible en Campañas y Dimensiones | Añadir columna | https://support.google.com/google-ads/answer/42995?hl=en |

## Facturación (mínimos)
### Cómo funciona
- Pago posterior: se cobra el día 1 de cada mes o antes, cuando el coste alcanza el umbral. El umbral inicial varía por cuenta, país y moneda; la página ejemplifica 50 USD, que sube a 200, 350 y 500 con cada alcance; no avisan por email de la subida. No se publican importes iniciales en EUR [SIN VERIFICAR]. Prepago: sin umbral; los anuncios paran al agotarse el saldo.
- Facturación mensual (línea de crédito): suele exigir negocio registrado un año, cuenta activa y en buen estado 6 meses y gasto de unos 5.000 USD al mes (varía por país) en 3 de los últimos 12 meses.
- Sobreentrega: un día puede gastarse hasta el doble del presupuesto diario medio; el mes no supera 30,4 veces el presupuesto diario medio. Si el coste servido supera el límite, se acredita la diferencia ("Overdelivery" en ajustes). Se calcula como coste servido menos coste facturado (Report Editor > plantilla Billed cost).
- Otros ajustes: cortesía (solo gasto futuro), sobreentrega, invalid activity y overrun (solo prepago).

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Umbral de pago y fecha de cobro | Cobro el día 1 o al llegar al umbral; el umbral sube | Facturación > Resumen | https://support.google.com/google-ads/answer/2375432?hl=en |
| Gasto diario máximo | Hasta 2x presupuesto medio diario; 30,4x mensual | Billed cost vs Served cost en Report Editor | https://support.google.com/google-ads/answer/1704443?hl=en |
| Créditos recibidos | Tipos: cortesía, invalid activity, overdelivery, overrun | Facturación > Resumen > mes | https://support.google.com/google-ads/answer/1704323?hl=en |

## Buenas prácticas oficiales de estructura y mantenimiento
### Cómo funciona
- Google no publica una lista oficial de "salud de la cuenta" en estos dominios [SIN VERIFICAR]. Sí hay guías de estructura y seguridad.
- Estructura ("The ABCs of Account Structure"): estructuras simples y consolidadas por tema favorecen pujas con IA; convertir grupos de una sola palabra clave en grupos temáticos, fusionar tipos de concordancia, eliminar segmentación por dispositivo innecesaria, limpiar duplicadas y keywords sin servir.
- Configuración de cuenta: una campaña, un objetivo; evitar campañas limitadas por presupuesto; con cuota de impresiones superior al 80 % Google sugiere ampliar alcance; al menos 3 anuncios por grupo y rotación optimizada; reorganizar tarde borra datos acumulados.
- Seguridad: revisar accesos con regularidad, retirar usuarios inactivos, mínimo privilegio, revisar cambios inesperados.

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Estructura consolidada | Grupos temáticos, concordancias fusionadas, sin duplicadas ni keywords sin servir | Estructura de campañas y grupos | https://support.google.com/google-ads/answer/14752782?hl=en |
| Un objetivo por campaña, no limitada por presupuesto, 3 anuncios por grupo | Guía de configuración | Estado de la campaña, anuncios por grupo | https://support.google.com/google-ads/answer/6167145?hl=en |
| Revisión periódica de accesos | Quitar inactivos, mínimo acceso | Access and security | https://support.google.com/google-ads/answer/12864492?hl=en |

## Secuencias de comandos, reglas automatizadas y alertas
### Cómo funciona
- **Scripts**: 30 minutos de ejecución por script (60 con `executeInParallel` y callback en MCC); lo hecho antes de la cancelación queda aplicado. 250 scripts autorizados OAuth2 por cuenta (el exceso desautoriza uno anterior). Iteradores 50.000 por defecto; `withIds()` hasta 10.000; log truncado a 100 KB; `executeInParallel` hasta 50 cuentas; subida en bloque 50 MB y un millón de filas, tiempo 2 horas. Vista previa: no cambia datos reales de AdsApp. Los límites pueden cambiar sin aviso.
- **Reglas automatizadas**: cambian estado, presupuesto, pujas, etc., y pueden enviar emails. Límite oficial de reglas activas por usuario o cuentas por regla: aparece solo en resúmenes de búsqueda (100 reglas activas, 1.000 cuentas en MCC) [SIN VERIFICAR en la página abierta, que remitía a otros artículos]. En MCC la programación sigue la zona horaria del MCC.
- **Alertas personalizadas**: en la app móvil, notificaciones personalizadas por métrica, umbral y periodo (diario, semanal, mensual) y de estado ("Limited by budget"); a nivel campaña o grupo, una cuenta por notificación. Las preferencias de email (Admin > Notifications) son solo de escritorio. Alertas personalizadas en la interfaz de escritorio: no documentadas [SIN VERIFICAR].

### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Scripts activos y autorizados | 30/60 min; 250 autorizados por cuenta | Herramientas > Scripts | https://developers.google.com/google-ads/scripts/docs/limits |
| Reglas automatizadas existentes | Pueden cambiar pujas, presupuestos y estado; aparecen en historial de cambios | Herramientas > Rules; historial de cambios | https://support.google.com/google-ads/answer/2472779?hl=en |
| Notificaciones por email | Al menos un usuario con todas o solo críticas en mantenimiento y anuncios rechazados | Admin > Notifications | https://support.google.com/google-ads/answer/7541103?hl=en |

## Cambios recientes
- 26-01-2026: "Add responsive search ads" deja de sugerir y aplicar anuncios nuevos y se retira de Auto Apply. https://support.google.com/google-ads/answer/10279006?hl=en
- 17-08-2026 (despliegue global terminado el 27-08-2026): las campañas Target CPA y Target ROAS "limitadas por presupuesto" pujan más ajustadas a su objetivo; Google no ajusta presupuestos ni objetivos; no se recomienda añadir exclusiones de datos por este cambio. Afecta a Búsqueda, Shopping, PMax, Demand Gen, Display, Hotel y Travel. https://support.google.com/google-ads/answer/17061251?hl=en y https://support.google.com/google-ads/answer/17125145?hl=en-GB
- Septiembre de 2026: las campañas con personalización de texto se actualizarán automáticamente a AI Max (según la ayuda; inicio a verificar en tu cuenta). https://support.google.com/google-ads/answer/11259373?hl=en
- Security Agent para higiene de cuenta (fecha de lanzamiento no indicada en la página) [SIN VERIFICAR la fecha]. https://support.google.com/google-ads/answer/17034850?hl=en
- 2025-2026: passkeys para acciones sensibles; una vez activado el ajuste es permanente y bloquea SMS, OTP por email y avisos de teléfono. https://support.google.com/google-ads/answer/16917887?hl=en-GB
- API v25: guía de recomendaciones actualizada el 30-09-2026. https://developers.google.com/google-ads/api/docs/recommendations
- Pestaña Resultados de Recomendaciones (impacto de presupuesto y objetivos aplicados). https://support.google.com/google-ads/answer/16904315?hl=en
