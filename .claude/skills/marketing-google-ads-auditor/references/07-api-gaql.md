# 07 · API de Google Ads (GAQL)

> Consultado el 08-10-2026 en developers.google.com/google-ads/api. Campos comprobados uno a uno en la referencia de campos de la v24 (la que usa el extractor) y cruzados con la v25: ninguno de los campos de este fichero desaparece en la v25. Lo que no se pudo confirmar en la documentación oficial va marcado [SIN VERIFICAR].

Base de URLs de fuente:
- Referencia de campos: `https://developers.google.com/google-ads/api/fields/v24/<recurso>`
- Guías: `https://developers.google.com/google-ads/api/docs/...`

---

## 1. Versión vigente y calendario de retirada

| Versión | Publicada | Retirada (sunset) |
|---|---|---|
| v22 | 15-10-2025 | octubre de 2026 (tentativa) |
| v23 / v23.1 / v23.2 / v23.3 | 28-01-2026 (v23) | febrero de 2027 |
| **v24** / v24.1 | 22-04-2026 / 13-05-2026 | **mayo de 2027** |
| v24.2 | 24-06-2026 | junio de 2027 |
| **v25** | 22-07-2026 | agosto de 2027 |
| v25.1 / v25.2 | 19-08-2026 / 23-09-2026 | agosto de 2027 |
| v26 (prevista) | octubre de 2026 | noviembre de 2027 |
| v26.1 (opcional, prevista) | noviembre de 2026 | noviembre de 2027 |

- **La última versión hoy es la v25 (v25.2, 23-09-2026), no la v24.** La v24 está obsoleta (deprecated, no es la última) pero funciona hasta su retirada en mayo de 2027. La página dice «mayo de 2027» sin día y avisa de que "la fecha tentativa significa que la retirada puede ocurrir en cualquier momento de ese mes".
- Google apunta a retirar cada versión un año después de su lanzamiento y saca versión nueva cada 3 o 4 meses.
- Fuente: `https://developers.google.com/google-ads/api/docs/sunset-dates`

### Cambios de política que afectan al extractor

| Cambio | Fecha | Efecto | Fuente |
|---|---|---|---|
| Los developer tokens se retiraron. El nivel de acceso va ahora asociado al proyecto de Google Cloud que generó las credenciales OAuth | 09-09-2026 | La cabecera `developer-token` es opcional y el servidor la ignora. El código existente sigue funcionando | `https://developers.google.com/google-ads/api/docs/api-policy/developer-token` |
| Con proyecto en nivel Test que llama a una cuenta de producción, la v25 devuelve `AuthorizationError.CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` | v25.1 | Error nuevo a vigilar si se migra a v25 | `https://developers.google.com/google-ads/api/docs/release-notes` |
| `CampaignCriterion.language` ya no se admite para Search, AI Max ni PMax en Search. Añadirlo o actualizarlo en Search falla con `ContextError.OPERATION_NOT_PERMITTED_FOR_CONTEXT` | 09-09-2026 | Auditoría: un criterio de idioma en Search ya no es un ajuste real. Los anuncios se emparejan por el idioma de creatividades y páginas | `https://developers.google.com/google-ads/api/docs/deprecations` |
| Retención de datos granulares (diario, semanal, horario) reducida a 37 meses. Mensual, trimestral y anual: 11 años | 01-06-2026 | Ver sección de fechas | `https://developers.google.com/google-ads/api/docs/deprecations` |
| Los anuncios solo de llamada (`CallAdInfo`) existentes dejan de servir en febrero de 2027 | feb-2027 | Marcar como hallazgo si aparecen en `ad_group_ad.ad.type` | `https://developers.google.com/google-ads/api/docs/deprecations` |
| Campañas inteligentes (Smart): no se pueden crear nuevas | 23-09-2026 | Las existentes siguen sirviendo | `https://developers.google.com/google-ads/api/docs/deprecations` |

---

## 2. Reglas de GAQL que provocan los errores habituales

| Tema | Regla | Fuente |
|---|---|---|
| Estructura | `SELECT ... FROM <un solo recurso> WHERE ... ORDER BY ... LIMIT n PARAMETERS ...`. `FROM` es obligatorio en `GoogleAdsService` y debe omitirse en `GoogleAdsFieldService` | `https://developers.google.com/google-ads/api/docs/query/grammar` |
| OR | No existe. El `WHERE` solo combina con `AND`. Usar `IN` o `REGEXP_MATCH` (sintaxis RE2) | idem |
| LIKE | Solo sobre campos de texto, no sobre campos repetidos. Para casar `[`, `]`, `%` o `_` literales hay que rodearlos de corchetes | idem |
| Seleccionable frente a filtrable | Cada campo tiene `Selectable`, `Filterable` y `Sortable` en la referencia. Hay campos seleccionables y no filtrables (por ejemplo `segments.auction_insight_domain`, `ad_group_ad.policy_summary.policy_topic_entries`, `ad_group_ad.ad.responsive_search_ad.headlines`, `customer.conversion_tracking_setting.accepted_customer_data_terms`) y campos filtrables pero no seleccionables dentro de estructuras (los `listing_scope.dimensions.*`) | referencia de campos v24 |
| Segmentos incompatibles | Cada segmento y cada métrica tiene una lista `selectable_with`. Lo que se puede pedir a la vez es la intersección de las listas de todo lo del `SELECT`. Los segmentos también dependen del recurso del `FROM`, y cambian entre versiones (ejemplo oficial: en v24 `segments.click_type` ya no es seleccionable con `ad_group_asset`, `campaign_asset` ni `customer_asset`) | `https://developers.google.com/google-ads/api/docs/reporting/segmentation` |
| Compatibilidad en tiempo de ejecución | La documentación remite a `GoogleAdsFieldService` (consulta sin `FROM`) y a la referencia con selector de versión. Ruta REST exacta de `googleAdsFields`: [SIN VERIFICAR] | `https://developers.google.com/google-ads/api/docs/query/grammar` |
| Segmento en `WHERE` | Debe estar también en el `SELECT`, salvo los segmentos de fecha núcleo: `date`, `week`, `month`, `quarter`, `year` | segmentation |
| Fecha obligatoria | Si hay un segmento de fecha en el `SELECT`, el `WHERE` debe llevar un rango finito de fechas núcleo | segmentation |
| `DURING` frente a `BETWEEN` | `DURING` solo admite rangos predefinidos y no admite fechas literales. Las fechas literales van con `BETWEEN` o con `= > >= < <=`, en `YYYY-MM-DD` o `YYYYMMDD` | `https://developers.google.com/google-ads/api/docs/query/date-ranges` |
| `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS` | **No incluyen hoy.** `THIS_WEEK_SUN_TODAY`, `THIS_WEEK_MON_TODAY`, `THIS_MONTH` y `TODAY` sí llegan a hoy | date-ranges |
| Zona horaria | Todo rango se evalúa en la zona de la cuenta (`customer.time_zone`), no en UTC | date-ranges |
| `segments.week`, `month`, `quarter` | Al filtrarlos con fecha literal hay que dar el primer día del periodo (lunes, día 1, 1 de enero/abril/julio/octubre). Si no, `QueryError.MISALIGNED_DATE_FOR_FILTER`. `segments.year` se filtra con entero de 4 cifras | date-ranges |
| Profundidad histórica | Diario, semanal y horario (`segments.date`, `week`, `hour`): hasta 37 meses. Antes: error `DateRangeError.REQUESTED_DATE_GRANULARITY_NOT_SUPPORTED` en v24 y posteriores (`DateRangeError.UNKNOWN` en v23). Mensual, trimestral, anual o sin segmento de fecha: hasta 11 años, con el rango empezando el día 1 y acabando el último día de un mes | date-ranges |
| `segments.keyword.*` | Con cualquier campo de ese grupo en el `SELECT`, el resultado se limita a filas ligadas a una palabra clave de la Red de Búsqueda. Desaparecen DSA, Shopping, PMax y Display | segmentation |
| Segmentar multiplica filas | Cada segmento añadido puede aumentar las filas de forma exponencial | segmentation |
| Filas con todo cero | No se devuelven. Un informe vacío puede ser simplemente una acción de conversión nueva sin datos | `https://developers.google.com/google-ads/api/docs/conversions/reporting` |
| `search` frente a `searchStream` | Misma consulta, mismo resultado. `search` pagina a 10.000 filas fijas por respuesta. `searchStream` entrega todo en una respuesta, y por REST va envuelto en un array JSON | `https://developers.google.com/google-ads/api/rest/common/search` |
| Paginación REST | Desde la v19 el tamaño de página es fijo (10.000) y `page_size` ya no se puede fijar: da `RequestError.PAGE_SIZE_NOT_SUPPORTED`. En REST hay que repetir la misma consulta con `pageToken` = `nextPageToken`. El token caduca a las ~2 horas sin uso. Si la consulta cambia con el mismo token, error. `nextPageToken` no viene en la última página | `https://developers.google.com/google-ads/api/docs/reporting/paging` |
| Endpoint REST | `POST https://googleads.googleapis.com/v25/customers/CUSTOMER_ID/googleAds:search` o `:searchStream`, cuerpo `{"query": "..."}`, cabecera `Authorization: Bearer`. Con cuenta gestora, `login-customer-id` (los ejemplos oficiales también envían `developer-token`, hoy opcional) | rest/common/search |
| Cuota | Una consulta `Search` o `SearchStream` cuenta como 1 operación, vengan las páginas que vengan. Las páginas siguientes con token válido no cuentan. Un token caducado o inválido da error y sí cuenta | `https://developers.google.com/google-ads/api/docs/best-practices/quotas` |
| Límites por nivel de acceso | Test: 15.000 operaciones/día solo en cuentas de prueba. Explorer: 2.880/día en producción. Basic: 15.000/día. Standard: sin límite. Además, límites de sistema por hora en todos los niveles. Exceso: `RESOURCE_EXHAUSTED` | `https://developers.google.com/google-ads/api/docs/access-levels` |
| Uso permitido «Reporting» | Solo `Search`/`SearchStream` y lecturas. Aplica a proyectos Standard | access-levels |
| Tamaño de respuesta | 64 MB por respuesta. Si se supera, `RESOURCE_EXHAUSTED` (HTTP 429) sin `GoogleAdsError`. Reducir campos o usar streaming | quotas |
| Métricas con tope de visualización | `search_impression_share` y `search_top_impression_share` van de 0,1 a 1 y todo valor inferior se informa como 0,0999. `search_budget_lost_*` y `search_rank_lost_*` van de 0 a 0,9 y todo valor superior se informa como 0,9001 | referencia de campos v24, `metrics.search_*` |

### Por qué `metrics.conversions` no se combina con ciertos segmentos

`metrics.conversions` y `metrics.all_conversions` cuentan solo las acciones con `include_in_conversions_metric = true`. Al añadir `segments.conversion_action` (o `conversion_action_name` o `conversion_action_category`) la fila pasa a ser una por acción y por campaña, y las filas con cero conversiones desaparecen. Eso cambia el total de filas, no el de conversiones, pero los otros métricos (clics, coste) se repiten en cada fila de acción si se piden a la vez: no se pueden sumar.

Sobre el recurso `campaign` en la v24, según las listas `selectable_with`:
- `segments.conversion_action` **no** admite, entre otros: `search_term`, `asset_group`, `geo_target_country`, `mobile_device_platform`, `search_subcategory`, `hotel_*`, `vertical_ads_*`, `activity_*`, `ad_using_product_data`, `ad_using_video`. Sí admite `date`, `device`, `hour`, `ad_network_type`, `day_of_week`, `geo_target_*` (ciudad, región, etc.) y `keyword.*`.
- `metrics.conversions_by_conversion_date` admite menos segmentos todavía (no admite `search_term`, `asset_group`, `mobile_device_platform`, `slot` ni `webpage`).
- Con `*_by_conversion_date` y `segments.date`, la fecha pasa a significar la fecha de la conversión, no la del clic.

Regla práctica para el extractor: una consulta para costes y clics por campaña y otra, aparte, para conversiones por acción, y unirlas por `campaign.id`. Fuente: `https://developers.google.com/google-ads/api/fields/v24/campaign` (descripciones y `selectable_with` de `metrics.conversions`, `segments.conversion_action`, `metrics.conversions_by_conversion_date`) y `https://developers.google.com/google-ads/api/docs/conversions/reporting`.

---

## 3. Ajustes de cuenta

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Etiquetado automático | `customer` | `customer.auto_tagging_enabled` | Booleano, filtrable | `https://developers.google.com/google-ads/api/fields/v24/customer` |
| Plantilla de seguimiento y sufijo de URL de cuenta | `customer` | `customer.tracking_url_template`, `customer.final_url_suffix` | También existen a nivel de campaña (`campaign.tracking_url_template`, `campaign.final_url_suffix`, `campaign.url_custom_parameters`), de anuncio (`ad_group_ad.ad.tracking_url_template`, `ad_group_ad.ad.final_url_suffix`) y, desde la v25.2, de grupo de recursos PMax (`asset_group.tracking_url_template`, `asset_group.final_url_suffix`, `asset_group.url_custom_parameters`) | idem y `https://developers.google.com/google-ads/api/docs/release-notes` |
| Estado del seguimiento de conversiones | `customer` | `customer.conversion_tracking_setting.conversion_tracking_status` (`NOT_CONVERSION_TRACKED`, `CONVERSION_TRACKING_MANAGED_BY_SELF`, `..._BY_THIS_MANAGER`, `..._BY_ANOTHER_MANAGER`), `conversion_tracking_id`, `cross_account_conversion_tracking_id`, `google_ads_conversion_customer` | **Con seguimiento entre cuentas, el valor cambia según el `login-customer-id` de la petición.** Fijar siempre el mismo | idem |
| Condiciones de datos de clientes | `customer` | `customer.conversion_tracking_setting.accepted_customer_data_terms` | Solo seleccionable, no filtrable. Con seguimiento entre cuentas se hereda de la gestora. Ver `https://support.google.com/adspolicy/answer/7475709` | idem |
| Conversiones mejoradas para clientes potenciales | `customer` | `customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled` | Solo seleccionable. Heredado de la gestora si hay seguimiento entre cuentas | idem |
| Términos de formularios de clientes potenciales | `customer` | `customer.customer_agreement_setting.accepted_lead_form_terms` | Filtrable | idem |
| Conversiones de llamadas | `customer` | `customer.call_reporting_setting.call_reporting_enabled`, `call_conversion_reporting_enabled`, `call_conversion_action` | La acción por defecto se usa si no se fija | idem |
| Declaración de publicidad política UE | `customer`, `campaign` | `customer.contains_eu_political_advertising`, `campaign.contains_eu_political_advertising`, `campaign.missing_eu_political_advertising_declaration` | Desde la v22.1. Filtrar campañas sin declaración | `https://developers.google.com/google-ads/api/docs/release-notes` |
| Zona horaria, moneda, tipo de cuenta | `customer` | `customer.time_zone`, `customer.currency_code`, `customer.manager`, `customer.test_account`, `customer.status` | La zona horaria rige todos los rangos de fecha | referencia `customer` |
| Recomendaciones aplicadas automáticamente | `recommendation_subscription`, `change_event` | `recommendation_subscription.type`, `.status`, `.create_date_time`, `.modify_date_time`. En `change_event`, `change_event.client_type = GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION` | Sí se pueden consultar. Tipos que admiten suscripción: `ENHANCED_CPC_OPT_IN`, `KEYWORD`, `KEYWORD_MATCH_TYPE`, `LOWER_TARGET_ROAS`, `MAXIMIZE_CLICKS_OPT_IN`, `OPTIMIZE_AD_ROTATION`, `RAISE_TARGET_CPA`, `RESPONSIVE_SEARCH_AD`, `RESPONSIVE_SEARCH_AD_IMPROVE_AD_STRENGTH`, `SEARCH_PARTNERS_OPT_IN`, `SET_TARGET_CPA`, `SET_TARGET_ROAS`, `TARGET_CPA_OPT_IN`, `TARGET_ROAS_OPT_IN`, `USE_BROAD_MATCH_KEYWORD` | `https://developers.google.com/google-ads/api/docs/recommendations` |

```sql
SELECT
  customer.id, customer.descriptive_name, customer.time_zone, customer.currency_code,
  customer.auto_tagging_enabled, customer.tracking_url_template, customer.final_url_suffix,
  customer.conversion_tracking_setting.conversion_tracking_status,
  customer.conversion_tracking_setting.conversion_tracking_id,
  customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
  customer.conversion_tracking_setting.accepted_customer_data_terms,
  customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
  customer.customer_agreement_setting.accepted_lead_form_terms,
  customer.call_reporting_setting.call_reporting_enabled,
  customer.contains_eu_political_advertising,
  customer.optimization_score
FROM customer
```

```sql
SELECT recommendation_subscription.type, recommendation_subscription.status,
       recommendation_subscription.create_date_time, recommendation_subscription.modify_date_time
FROM recommendation_subscription
```

---

## 4. Acciones de conversión y objetivos

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Acciones con estado, principal o secundaria, categoría, origen, recuento, ventanas, atribución, valor | `conversion_action` | `conversion_action.id`, `name`, `status`, `type`, `category`, `origin`, `primary_for_goal`, `include_in_conversions_metric`, `counting_type`, `click_through_lookback_window_days`, `view_through_lookback_window_days`, `attribution_model_settings.attribution_model`, `attribution_model_settings.data_driven_model_status`, `value_settings.default_value`, `value_settings.default_currency_code`, `value_settings.always_use_default_value`, `phone_call_duration_seconds`, `owner_customer`, `google_analytics_4_settings.event_name`, `.property_id`, `.property_name`, `firebase_settings.*`, `third_party_app_analytics_settings.*`, `app_id`, `mobile_app_vendor` | `primary_for_goal` decide si la acción entra en pujas y en la columna Conversiones. `include_in_conversions_metric` es lo que usa `metrics.conversions`. `tag_snippets` es seleccionable pero no filtrable. Con seguimiento entre cuentas, las acciones viven en la cuenta de `customer.conversion_tracking_setting.google_ads_conversion_customer`: consultar allí | `https://developers.google.com/google-ads/api/fields/v24/conversion_action` |
| Objetivos de cuenta | `customer_conversion_goal` | `.category`, `.origin`, `.biddable` | Los crea el sistema solo (categoría + origen). Solo admiten actualización | `https://developers.google.com/google-ads/api/docs/conversions/goals/overview` |
| Objetivos de campaña | `campaign_conversion_goal` | `.campaign`, `.category`, `.origin`, `.biddable` | Sustituyen a los de cuenta cuando se tocan. Al modificar uno, el sistema deja de propagar cambios de cuenta a esa campaña | `https://developers.google.com/google-ads/api/docs/conversions/goals/campaign-goals` |
| Nivel de configuración de objetivos por campaña | `conversion_goal_campaign_config` | `.campaign`, `.goal_config_level` (`CUSTOMER` o `CAMPAIGN`), `.custom_conversion_goal` | Un `CAMPAIGN` indica objetivos propios o un objetivo personalizado | idem |
| Objetivos personalizados | `custom_conversion_goal` | `.id`, `.name`, `.status`, `.conversion_actions` | Agrupan acciones concretas sin importar categoría ni origen | referencia |
| Optimización selectiva (solo App) | `campaign` | `campaign.selective_optimization.conversion_actions` | Solo se puede fijar en campañas de App. En el resto, objetivos de campaña | goals/overview |

```sql
SELECT conversion_action.id, conversion_action.name, conversion_action.status,
  conversion_action.type, conversion_action.category, conversion_action.origin,
  conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric,
  conversion_action.counting_type,
  conversion_action.click_through_lookback_window_days,
  conversion_action.view_through_lookback_window_days,
  conversion_action.attribution_model_settings.attribution_model,
  conversion_action.attribution_model_settings.data_driven_model_status,
  conversion_action.value_settings.default_value,
  conversion_action.value_settings.default_currency_code,
  conversion_action.value_settings.always_use_default_value,
  conversion_action.owner_customer
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

```sql
SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable
FROM customer_conversion_goal
```

```sql
SELECT campaign.id, campaign.name, campaign.advertising_channel_type,
  campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable
FROM campaign_conversion_goal
WHERE campaign.status = 'ENABLED'
```

```sql
SELECT campaign.id, campaign.name, conversion_goal_campaign_config.goal_config_level,
  conversion_goal_campaign_config.custom_conversion_goal
FROM conversion_goal_campaign_config
```

### Conversiones por acción y campaña

```sql
SELECT campaign.id, campaign.name,
  segments.conversion_action, segments.conversion_action_name, segments.conversion_action_category,
  metrics.conversions, metrics.conversions_value, metrics.all_conversions, metrics.all_conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.status != 'REMOVED'
```

Fuente: `https://developers.google.com/google-ads/api/docs/conversions/reporting`. Columnas de la interfaz y su métrica: Conversiones = `metrics.conversions`; Todas las conv. = `metrics.all_conversions`; Conv. (por hora de conv.) = `metrics.conversions_by_conversion_date`; Valor de conv. / coste = `metrics.conversions_value_per_cost`; Conv. de visualización = `metrics.view_through_conversions`. Las columnas personalizadas no existen en la API.

---

## 5. Campañas

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Estado de servicio | `campaign` | `campaign.status`, `campaign.serving_status`, `campaign.primary_status` (`ELIGIBLE`, `ENDED`, `LEARNING`, `LIMITED`, `MISCONFIGURED`, `NOT_ELIGIBLE`, `PAUSED`, `PENDING`, `REMOVED`), `campaign.primary_status_reasons` | `primary_status` explica por qué no sirve o sirve mal. Los cambios tardan en reflejarse | `https://developers.google.com/google-ads/api/fields/v24/campaign` |
| Fechas | `campaign` | `campaign.start_date_time`, `campaign.end_date_time` | **`campaign.start_date` y `campaign.end_date` se eliminaron en la v23.** Pedirlos en v23+ da error | `https://developers.google.com/google-ads/api/docs/release-notes` |
| Tipo y subtipo | `campaign` | `campaign.advertising_channel_type`, `campaign.advertising_channel_sub_type` | Filtrar `PERFORMANCE_MAX` obligatorio para informes de PMax | referencia |
| Estrategia de puja | `campaign` | `campaign.bidding_strategy_type`, `campaign.bidding_strategy` (cartera), `campaign.bidding_strategy_system_status`, `campaign.maximize_conversions.target_cpa_micros`, `campaign.maximize_conversion_value.target_roas`, `campaign.target_cpa.target_cpa_micros`, `campaign.target_roas.target_roas`, `campaign.target_impression_share.*`, `campaign.manual_cpc.enhanced_cpc_enabled`, `campaign.target_spend.*` | Para estrategias de cartera: recurso `bidding_strategy` con `bidding_strategy.id`, `.name`, `.type`, `.status`, `.campaign_count`, `.non_removed_campaign_count`, `.effective_currency_code`. El estado de sistema por campaña (`campaign.bidding_strategy_system_status`) tiene valores como `ENABLED`, `LEARNING_NEW`, `LEARNING_BUDGET_CHANGE`, `LEARNING_CONVERSION_SETTING_CHANGE`, `LEARNING_SETTING_CHANGE`, `LIMITED_BY_BUDGET`, `LIMITED_BY_CPC_BID_CEILING`, `LIMITED_BY_CPC_BID_FLOOR`, `LIMITED_BY_DATA`, `LIMITED_BY_LOW_QUALITY`, `MISCONFIGURED_CONVERSION_SETTINGS`, `MISCONFIGURED_CONVERSION_TYPES`, `MISCONFIGURED_SHARED_BUDGET`, `MISCONFIGURED_STRATEGY_TYPE`, `MISCONFIGURED_ZERO_ELIGIBILITY`, `MULTIPLE*` | referencia |
| Presupuesto | `campaign` + `campaign_budget` | `campaign.campaign_budget`, `campaign_budget.amount_micros`, `.delivery_method`, `.explicitly_shared`, `.reference_count`, `.period`, `.type`, `.status`, `.total_amount_micros`, `.has_recommended_budget`, `.recommended_budget_amount_micros`, `.recommended_budget_estimated_change_weekly_clicks`, `.recommended_budget_estimated_change_weekly_cost_micros`, `.recommended_budget_estimated_change_weekly_interactions` | `reference_count > 1` o `explicitly_shared = true` indica presupuesto compartido. En v24 se quitó el segmento `ad_sub_network_type` de `campaign_budget` | `https://developers.google.com/google-ads/api/fields/v24/campaign_budget` |
| Redes | `campaign` | `campaign.network_settings.target_google_search`, `target_search_network`, `target_partner_search_network`, `target_content_network`, `target_youtube`, `target_google_tv_network` | | referencia |
| Tipo de segmentación geográfica | `campaign` | `campaign.geo_target_type_setting.positive_geo_target_type`, `negative_geo_target_type` (positiva: `PRESENCE`, `PRESENCE_OR_INTEREST`, `SEARCH_INTEREST`; negativa: `PRESENCE`, `PRESENCE_OR_INTEREST`) | Un valor de interés en la positiva hace llegar anuncios a gente fuera de las ubicaciones segmentadas | referencia |
| Ubicaciones incluidas y excluidas | `campaign_criterion` | `campaign_criterion.type = 'LOCATION'`, `.location.geo_target_constant`, `.negative`, `.status`, `.bid_modifier`; radio: `.proximity.*`; grupos: `.location_group.*` | Excluidas = `negative = true`. Sin criterios de ubicación, la campaña apunta a todas las regiones. `location_view` no devuelve nada si no hay criterio de ubicación | `https://developers.google.com/google-ads/api/fields/v24/campaign_criterion` |
| Idiomas | `campaign_criterion` | `campaign_criterion.type = 'LANGUAGE'`, `.language.language_constant` | Ver política del 09-09-2026: ya no cuenta para Search | deprecations |
| Programación de anuncios | `campaign_criterion` | `.ad_schedule.day_of_week`, `.start_hour`, `.end_hour`, `.start_minute`, `.end_minute`, `.bid_modifier` | Rendimiento: `ad_schedule_view` | referencia |
| Dispositivos | `campaign_criterion` | `campaign_criterion.type = 'DEVICE'`, `.device.type`, `.bid_modifier` | `bid_modifier` en cero o negativo excluye el dispositivo. Rendimiento: `segments.device` | referencia |
| Optimización de entrega | `campaign` | `campaign.ad_serving_optimization_status`, `campaign.optimization_score` | | referencia |
| Etiquetas y experimentos | `campaign` | `campaign.labels`, `campaign.experiment_type`, `campaign.base_campaign` | | referencia |

```sql
SELECT
  campaign.id, campaign.name, campaign.status, campaign.serving_status,
  campaign.primary_status, campaign.primary_status_reasons,
  campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
  campaign.bidding_strategy_type, campaign.bidding_strategy, campaign.bidding_strategy_system_status,
  campaign.maximize_conversions.target_cpa_micros, campaign.maximize_conversion_value.target_roas,
  campaign.target_cpa.target_cpa_micros, campaign.target_roas.target_roas,
  campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
  campaign.network_settings.target_partner_search_network, campaign.network_settings.target_content_network,
  campaign.geo_target_type_setting.positive_geo_target_type,
  campaign.geo_target_type_setting.negative_geo_target_type,
  campaign.tracking_url_template, campaign.final_url_suffix,
  campaign.start_date_time, campaign.end_date_time,
  campaign.optimization_score, campaign.feed_types,
  campaign_budget.id, campaign_budget.amount_micros, campaign_budget.delivery_method,
  campaign_budget.explicitly_shared, campaign_budget.reference_count,
  campaign_budget.has_recommended_budget, campaign_budget.recommended_budget_amount_micros
FROM campaign
WHERE campaign.status != 'REMOVED'
```

```sql
SELECT campaign.id, campaign.name, campaign_criterion.type, campaign_criterion.negative,
  campaign_criterion.status, campaign_criterion.bid_modifier,
  campaign_criterion.location.geo_target_constant, campaign_criterion.proximity.radius,
  campaign_criterion.proximity.radius_units, campaign_criterion.language.language_constant,
  campaign_criterion.device.type, campaign_criterion.ad_schedule.day_of_week,
  campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour
FROM campaign_criterion
WHERE campaign.status != 'REMOVED'
  AND campaign_criterion.type IN ('LOCATION','LANGUAGE','DEVICE','AD_SCHEDULE','PROXIMITY','LOCATION_GROUP')
```

---

## 6. Palabras clave

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Estado, concordancia, texto, negativa | `ad_group_criterion` | `ad_group_criterion.criterion_id`, `.type = 'KEYWORD'`, `.status`, `.keyword.text`, `.keyword.match_type`, `.negative`, `.approval_status`, `.disapproval_reasons`, `.cpc_bid_micros`, `.effective_cpc_bid_micros`, `.effective_cpc_bid_source`, `.final_urls`, `.labels` | | `https://developers.google.com/google-ads/api/fields/v24/ad_group_criterion` |
| Estado del sistema | `ad_group_criterion` | `.system_serving_status`, `.primary_status`, `.primary_status_reasons` | | idem |
| Nivel de calidad y componentes | `ad_group_criterion` | `.quality_info.quality_score`, `.quality_info.search_predicted_ctr`, `.quality_info.creative_quality_score`, `.quality_info.post_click_quality_score` | Los tres componentes son enumerados (`ABOVE_AVERAGE`, `AVERAGE`, `BELOW_AVERAGE`, más `UNKNOWN`/`UNSPECIFIED`) y `quality_score` es entero. La referencia avisa de que `quality_score` puede venir sin rellenar si Google no tiene datos suficientes | idem |
| Puja de primera página | `ad_group_criterion` | `.position_estimates.first_page_cpc_micros`, `.top_of_page_cpc_micros`, `.first_position_cpc_micros`, `.estimated_add_clicks_at_first_position_cpc`, `.estimated_add_cost_at_first_position_cpc` | **Siguen existiendo en la v24 y la v25** | idem |
| Rendimiento | `keyword_view` | `keyword_view.resource_name` más `metrics.*` y `segments.*` | Se combina con campos de `ad_group_criterion`, `ad_group` y `campaign` | `https://developers.google.com/google-ads/api/fields/v24/keyword_view` |

```sql
SELECT campaign.name, ad_group.name,
  ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
  ad_group_criterion.status, ad_group_criterion.system_serving_status,
  ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
  ad_group_criterion.approval_status,
  ad_group_criterion.quality_info.quality_score,
  ad_group_criterion.quality_info.search_predicted_ctr,
  ad_group_criterion.quality_info.creative_quality_score,
  ad_group_criterion.quality_info.post_click_quality_score,
  ad_group_criterion.position_estimates.first_page_cpc_micros,
  ad_group_criterion.position_estimates.top_of_page_cpc_micros,
  ad_group_criterion.effective_cpc_bid_micros,
  metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND ad_group_criterion.negative = FALSE
  AND ad_group_criterion.status != 'REMOVED'
```

---

## 7. Términos de búsqueda y negativas

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Términos de Search | `search_term_view` | `search_term_view.search_term`, `.status`, `ad_group.*`; segmentos `search_term_match_type`, `search_term_match_source`, `keyword.info.text`, `keyword.info.match_type`, `device`, `date` | **No incluye PMax.** Se segmenta por grupo de anuncios: el mismo término puede salir en varios grupos (no es duplicado). Los términos con poco volumen se omiten por privacidad: la suma no cuadra con el total de campaña | `https://developers.google.com/google-ads/api/fields/v24/search_term_view`, `https://developers.google.com/google-ads/api/docs/reporting/segmentation` |
| Términos de PMax (y de campaña en general) | `campaign_search_term_view` | `campaign_search_term_view.search_term`, `campaign.*`; segmentos `search_term_match_source`, `search_term_match_type`, `search_term_targeting_status`, `ad_network_type`, `device`, `date`, `conversion_action*` | La descripción oficial dice que sirve para los términos de PMax. Con segmentos de palabra clave (`segments.keyword.*`) se excluye PMax | `https://developers.google.com/google-ads/api/fields/v24/campaign_search_term_view` |
| Categorías de búsqueda (demanda, no términos exactos) | `campaign_search_term_insight` | `.category_label`, `.id`, `.campaign_id`; segmentos `search_subcategory`, `search_term`, `ad_group`, `asset_group`, `date`; métricas `impressions`, `clicks`, `conversions`, `conversions_value`, `ctr`, `search_volume` | Agrupa términos parecidos en categorías con volumen de búsqueda. Histórico desde marzo de 2023. Existe también `customer_search_term_insight` | `https://developers.google.com/google-ads/api/fields/v24/campaign_search_term_insight` |
| AI Max | `ai_max_search_term_ad_combination_view` | `.search_term`, `.headline`, `.landing_page`, `.ad_group`; único segmento: `date` | Vista más granular de AI Max. **No sumar con `search_term_view`**: se solapan. No sirve para conciliar | `https://developers.google.com/google-ads/api/docs/campaigns/ai-max-for-search-campaigns/ai-max-reporting` |
| Origen del emparejamiento AI Max | `search_term_view` | `segments.search_term_match_source IN ('AI_MAX_KEYWORDLESS','AI_MAX_BROAD_MATCH')`; otros valores citados: `ADVERTISER_PROVIDED_KEYWORD`, `VERTICAL_ADS_DATA_FEED` | | idem |
| Negativas de grupo | `ad_group_criterion` | `.negative = TRUE`, `.keyword.text`, `.keyword.match_type`, `.type` | | referencia |
| Negativas de campaña (incluida PMax) | `campaign_criterion` | `.negative = TRUE`, `.type = 'KEYWORD'`, `.keyword.text`, `.keyword.match_type` | PMax admite hasta 10.000 negativas de palabra clave por campaña, y los criterios `KEYWORD` y `BRAND` solo pueden ser negativos | `https://developers.google.com/google-ads/api/performance-max/create-campaign-criteria` |
| Listas de negativas compartidas | `shared_set` + `shared_criterion` + `campaign_shared_set` | `shared_set.type` (`NEGATIVE_KEYWORDS`, `NEGATIVE_PLACEMENTS`, `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS`, `BRANDS`, `WEBPAGES`), `shared_set.status`, `shared_set.member_count`, `shared_set.reference_count`, `campaign_shared_set.campaign`, `.shared_set`, `.status` | `NEGATIVE_KEYWORDS` está documentada para Search, Display, Shopping, App multicanal y Local. **PMax no figura en esa lista**: para PMax usar `campaign_criterion` | `https://developers.google.com/google-ads/api/docs/targeting/shared-sets` |
| Negativas de cuenta | `customer_negative_criterion` | `.negative_keyword_list.shared_set`, `.placement_list.shared_set`, `.placement.url`, `.ip_block.ip_address`, `.content_label.type`, `.youtube_channel.channel_id`, `.youtube_video.video_id`, `.mobile_application.*`, `.mobile_app_category.*`, `.type` | Máximo una lista `ACCOUNT_LEVEL_NEGATIVE_KEYWORDS` por cuenta. El recurso no expone palabras clave sueltas, solo la lista. Para ver las palabras, consultar `shared_criterion` de esa lista | shared-sets, `https://developers.google.com/google-ads/api/fields/v24/customer_negative_criterion` |
| Exclusión de marcas | `campaign_criterion` | `.brand_list.shared_set` (lista `BRANDS`), `.negative` | Documentado para AI Max. En PMax `BRAND` existe como criterio solo negativo | create-campaign-criteria |

```sql
SELECT campaign.name, ad_group.name, search_term_view.search_term, search_term_view.status,
  segments.search_term_match_type, segments.search_term_match_source,
  metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
LIMIT 5000
```

```sql
SELECT campaign.id, campaign.name, campaign_search_term_view.search_term,
  segments.search_term_targeting_status, segments.search_term_match_source,
  metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value
FROM campaign_search_term_view
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, campaign_search_term_insight.category_label, segments.search_subcategory,
  segments.date, metrics.impressions, metrics.clicks, metrics.conversions, metrics.search_volume
FROM campaign_search_term_insight
WHERE campaign_search_term_insight.campaign_id = CAMPAIGN_ID
  AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, campaign.name, campaign_criterion.criterion_id, campaign_criterion.type,
  campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.brand_list.shared_set
FROM campaign_criterion
WHERE campaign_criterion.negative = TRUE AND campaign.status != 'REMOVED'
  AND campaign_criterion.type IN ('KEYWORD','BRAND','WEBPAGE','PLACEMENT')
```

```sql
SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status
FROM shared_set
WHERE shared_set.status != 'REMOVED'
```

```sql
SELECT campaign.id, campaign.name, shared_set.id, shared_set.name, shared_set.type, campaign_shared_set.status
FROM campaign_shared_set
WHERE campaign_shared_set.status != 'REMOVED'
```

```sql
SELECT customer_negative_criterion.type, customer_negative_criterion.negative_keyword_list.shared_set,
  customer_negative_criterion.placement_list.shared_set, customer_negative_criterion.placement.url
FROM customer_negative_criterion
```

---

## 8. Anuncios

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Estado y política | `ad_group_ad` | `ad_group_ad.status`, `.primary_status`, `.primary_status_reasons`, `.policy_summary.approval_status`, `.policy_summary.review_status`, `.policy_summary.policy_topic_entries` | `policy_topic_entries` es seleccionable pero no filtrable. Filtrar por `approval_status` | `https://developers.google.com/google-ads/api/fields/v24/ad_group_ad` |
| Eficacia del anuncio | `ad_group_ad` | `ad_group_ad.ad_strength`, `ad_group_ad.action_items` | `action_items` no filtrable | idem |
| Contenido RSA | `ad_group_ad` | `ad_group_ad.ad.responsive_search_ad.headlines`, `.descriptions`, `.path1`, `.path2`, `ad_group_ad.ad.final_urls`, `.tracking_url_template`, `.final_url_suffix`, `.type`, `.id` | `headlines` y `descriptions` son repetidos y no filtrables. Cada elemento lleva su fijación en `pinned_field` | idem |
| Rendimiento por recurso de RSA | `ad_group_ad_asset_view` | `ad_group_ad_asset_view.ad_group_ad`, `.asset`, `.field_type`, `.pinned_field`, `.enabled`, `.policy_summary`, `.source`, `.performance_label`; métricas completas | Desde la v22 trae métricas de rendimiento y conversión para RSA (antes solo impresiones) y para `RESPONSIVE_DISPLAY_AD` desde la v23. **No fiarse de `performance_label`**: las notas de la v23 dicen que el enum de etiqueta de rendimiento ya no se devuelve para Search y Display, aunque el campo siga listado | `https://developers.google.com/google-ads/api/fields/v24/ad_group_ad_asset_view`, release-notes |
| Anuncios solo de llamada | `ad_group_ad` | `ad_group_ad.ad.type = 'CALL_AD'` [valor exacto del enum: SIN VERIFICAR] | v23 eliminó el soporte de `CallAd`; los existentes dejan de servir en feb-2027 | release-notes, deprecations |

```sql
SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.ad.type,
  ad_group_ad.status, ad_group_ad.primary_status, ad_group_ad.primary_status_reasons,
  ad_group_ad.ad_strength, ad_group_ad.action_items,
  ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status,
  ad_group_ad.policy_summary.policy_topic_entries,
  ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
  ad_group_ad.ad.final_urls, ad_group_ad.ad.tracking_url_template,
  metrics.impressions, metrics.clicks, metrics.conversions
FROM ad_group_ad
WHERE ad_group_ad.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.name, ad_group.name, ad_group_ad.ad.id,
  ad_group_ad_asset_view.asset, ad_group_ad_asset_view.field_type, ad_group_ad_asset_view.pinned_field,
  ad_group_ad_asset_view.enabled,
  metrics.impressions, metrics.clicks, metrics.conversions, metrics.cost_micros
FROM ad_group_ad_asset_view
WHERE ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD' AND segments.date DURING LAST_30_DAYS
```

---

## 9. Recursos por nivel

| Nivel | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Cuenta | `customer_asset` | `.asset`, `.field_type`, `.status`, `.primary_status`, `.primary_status_details`, `.primary_status_reasons`, `.source` | Métricas con `phone_calls`, `phone_impressions`, `phone_through_rate` | `https://developers.google.com/google-ads/api/fields/v24/customer_asset` |
| Campaña | `campaign_asset` | `.campaign`, `.asset`, `.field_type`, `.status`, `.primary_status*`, `.source` | Desde la v23 también devuelve `HEADLINE` y `DESCRIPTION`. Con marco de marca activado en PMax (por defecto en campañas nuevas), nombre y logo de empresa van aquí (`BUSINESS_NAME`, `LOGO`), no en el grupo de recursos | `https://developers.google.com/google-ads/api/fields/v24/campaign_asset`, deprecations |
| Grupo de anuncios | `ad_group_asset` | `.ad_group`, `.asset`, `.field_type`, `.status`, `.primary_status*`, `.source` | | `https://developers.google.com/google-ads/api/fields/v24/ad_group_asset` |
| Contenido del recurso | `asset` | 249 campos entre atributos y métricas; tipo, texto, imagen, política | Para texto de sitelinks, llamadas, etc., seleccionar `asset.*` del tipo correspondiente [nombres por tipo: ver referencia] | `https://developers.google.com/google-ads/api/fields/v24/asset` |

Tipos de campo de recurso y su uso quedan en `.field_type` (enumerado `AssetFieldType`). En v24 `click_type` ya no es segmento de los tres recursos de nivel; en v23 sí.

```sql
SELECT campaign.id, campaign.name, campaign_asset.asset, campaign_asset.field_type,
  campaign_asset.status, campaign_asset.primary_status, campaign_asset.primary_status_reasons, campaign_asset.source
FROM campaign_asset
WHERE campaign_asset.status != 'REMOVED'
```

```sql
SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status,
  customer_asset.primary_status, customer_asset.primary_status_reasons
FROM customer_asset
WHERE customer_asset.status != 'REMOVED'
```

```sql
SELECT ad_group.id, ad_group.name, ad_group_asset.asset, ad_group_asset.field_type,
  ad_group_asset.status, ad_group_asset.primary_status
FROM ad_group_asset
WHERE ad_group_asset.status != 'REMOVED'
```

---

## 10. Performance Max

PMax no tiene `ad_group` ni `ad_group_ad`: consultarlos no devuelve nada para esas campañas. La estructura es `campaign` > `asset_group` > `asset_group_asset`. Fuente: `https://developers.google.com/google-ads/api/performance-max/reporting` (también en `/docs/performance-max/reporting`).

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Grupos de recursos | `asset_group` | `.id`, `.name`, `.status`, `.primary_status`, `.primary_status_reasons`, `.ad_strength`, `.asset_coverage.ad_strength_action_items`, `.final_urls`, `.final_mobile_urls`, `.path1`, `.path2`, `.campaign` | Tiene métricas completas y segmentos como `ad_network_type`, `device`, `conversion_action*` | `https://developers.google.com/google-ads/api/fields/v24/asset_group` |
| Recursos por grupo | `asset_group_asset` | `.asset`, `.asset_group`, `.field_type`, `.status`, `.primary_status`, `.primary_status_details`, `.primary_status_reasons`, `.policy_summary.*`, `.source` | Métricas completas por recurso. Segmentos: `ad_network_type`, `device`, `conversion_action*`, fechas. **Las etiquetas de rendimiento (Bajo, Bueno, Mejor) se eliminaron para PMax en la v22** | `https://developers.google.com/google-ads/api/performance-max/asset-reporting` |
| Combinaciones principales | `asset_group_top_combination_view` | `.asset_group_top_combinations` (más `asset_group.id`, `asset_group.ad_strength`) | Equivale al informe Combinaciones | idem |
| Señales de audiencia y temas de búsqueda | `asset_group_signal` | `.asset_group`, `.audience.audience`, `.search_theme.text`, `.approval_status`, `.disapproval_reasons`, `.local_services_id.service_id`, `.vertical_ads_item_group_rule_list.shared_set` | Sin métricas ni segmentos | `https://developers.google.com/google-ads/api/fields/v24/asset_group_signal` |
| Desglose por canal | `campaign`, `asset_group`, `asset_group_asset` | `segments.ad_network_type`, `segments.ad_using_product_data`, `segments.ad_using_video` | **Desglose por canal de PMax disponible desde la v23** (los dos últimos segmentos nacen en la v22). Con `ad_sub_network_type` hay que pedir también `ad_network_type` | `https://developers.google.com/google-ads/api/docs/performance-max/campaign-reporting`, release-notes |
| Emplazamientos | `performance_max_placement_view` | `.display_name`, `.placement`, `.placement_type`, `.target_url`; segmentos `ad_network_type`, `date`; única métrica `impressions` | Solo impresiones. Segmentable por `ad_network_type` desde la v24.2 (nota de versión). Tras la v24.2, también en la referencia v24 aparece el segmento | `https://developers.google.com/google-ads/api/fields/v24/performance_max_placement_view`, release-notes |
| Emplazamientos detallados | `detail_placement_view`, `group_placement_view` | `detail_placement_view.display_name`, `.placement`, `.placement_type`, `.target_url`, `.group_placement_target_url` | Descripción oficial: datos de Red de Display, por grupo de anuncios. **No es la vista para PMax** (para eso `performance_max_placement_view`) | `https://developers.google.com/google-ads/api/fields/v24/detail_placement_view` |
| Términos de búsqueda de PMax | `campaign_search_term_view` | ver sección 7 | | idem |
| Categorías de búsqueda | `campaign_search_term_insight` | ver sección 7 | | idem |
| Tipo de feed | `campaign` | `campaign.feed_types` (`MERCHANT_CENTER_FEED`, `TRAVEL_FEED`, ...) | Desde la v22 | campaign-reporting |
| Ajustes de marca y texto automático | `campaign` | `campaign.asset_automation_settings` (repetido, no filtrable), `campaign.brand_guidelines_enabled`, `campaign.text_guidelines.term_exclusions`, `campaign.text_guidelines.messaging_restrictions`, `campaign.pmax_campaign_settings.brand_targeting_overrides.ignore_exclusions_for_shopping_ads` | `url_expansion_opt_out` se eliminó en la v22: ahora la expansión de URL final se controla con el ajuste de automatización `FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION`. `text_guidelines` desde la v23.1. Automatización `AUTOMATED_VIDEO_CRAWL` desde la v25.2 | release-notes |
| Exclusiones de PMax | `campaign_criterion` | tipos admitidos en PMax: `AD_SCHEDULE`, `AGE_RANGE`, `BRAND`, `DEVICE`, `KEYWORD`, `LANGUAGE`, `LOCATION`, `LOCATION_GROUP`, `WEBPAGE` | `WEBPAGE` negativo excluye URLs de la expansión de URL final. Exclusión de género en PMax con `CampaignCriterion.gender`: la nota de la v24 dice que se habilitó en todas las versiones de la API | create-campaign-criteria, release-notes |
| Exclusiones de cuenta | `customer_negative_criterion` | ver sección 7 | | idem |

```sql
SELECT campaign.id, campaign.name, segments.ad_network_type, segments.ad_using_product_data, segments.ad_using_video,
  metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversions_value, metrics.cost_micros
FROM campaign
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, asset_group.id, asset_group.name, asset_group.status, asset_group.primary_status,
  asset_group.primary_status_reasons, asset_group.ad_strength,
  metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversions_value, metrics.cost_micros
FROM asset_group
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND asset_group.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, asset_group.id, asset_group_asset.asset, asset_group_asset.field_type,
  asset_group_asset.status, asset_group_asset.primary_status, asset_group_asset.primary_status_reasons,
  asset_group_asset.policy_summary.approval_status,
  metrics.impressions, metrics.clicks, metrics.conversions, metrics.cost_micros
FROM asset_group_asset
WHERE asset_group_asset.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, asset_group.id, asset_group_signal.audience.audience,
  asset_group_signal.search_theme.text, asset_group_signal.approval_status
FROM asset_group_signal
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
```

```sql
SELECT campaign.id, performance_max_placement_view.display_name, performance_max_placement_view.placement,
  performance_max_placement_view.placement_type, performance_max_placement_view.target_url,
  segments.ad_network_type, metrics.impressions
FROM performance_max_placement_view
WHERE segments.date DURING LAST_30_DAYS
```

---

## 11. Desgloses

| Desglose | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Dispositivo | cualquiera con métricas | `segments.device`. En 2026 también `segments.mobile_device_platform` (v24.1) | `mobile_device_platform` no combina con `conversion_action` | segmentation, release-notes |
| Hora del día | `campaign`, `ad_group`, `keyword_view`... | `segments.hour` | Solo 37 meses de histórico (granularidad horaria) | date-ranges |
| Día de la semana | idem | `segments.day_of_week` | | referencia |
| Ubicación física del usuario | `user_location_view` | `.country_criterion_id`, `.targeting_location` (segmentado o no) + `segments.geo_target_city`, `_region`, `_metro`, `_postal_code`, `_most_specific_location`, `_country`... | Descripción oficial: agrega por país, informa por **ubicación física real** del usuario, dentro o fuera de lo segmentado. Acepta métricas `*_by_conversion_date` desde la v23 | `https://developers.google.com/google-ads/api/fields/v24/user_location_view` |
| Ubicación física o de interés | `geographic_view` | `.country_criterion_id`, `.location_type` (`LOCATION_OF_PRESENCE` o `AREA_OF_INTEREST`) + `segments.geo_target_*` | Informa la ubicación física real **o** el área de interés según `location_type`: separar siempre por ese campo | `https://developers.google.com/google-ads/api/fields/v24/geographic_view` |
| Ubicaciones segmentadas (criterios) | `location_view` | `location_view.resource_name` + métricas; segmentos limitados (fechas, `conversion_action*`, `new_versus_returning_customers`) | Resume por criterio de ubicación de la campaña. **Si no hay criterio de ubicación, no devuelve nada**: usar entonces `geographic_view` o `user_location_view` | `https://developers.google.com/google-ads/api/fields/v24/location_view` |
| Página de destino | `landing_page_view` / `expanded_landing_page_view` | `landing_page_view.unexpanded_final_url`; `expanded_landing_page_view.expanded_final_url`; métricas incluyen `mobile_friendly_clicks_percentage`, `speed_score`, `valid_accelerated_mobile_pages_clicks_percentage` | Si incluyen o no campañas PMax: [SIN VERIFICAR] (la descripción oficial no lo dice). Para AI Max filtrar `campaign.ai_max_setting.enable_ai_max = TRUE` | `https://developers.google.com/google-ads/api/fields/v24/landing_page_view` |
| Llamadas | `call_view` | `.call_duration_seconds`, `.call_status`, `.call_tracking_display_location`, `.caller_area_code`, `.caller_country_code`, `.start_call_date_time`, `.end_call_date_time`, `.type` | Datos de seguimiento de llamadas de anuncios solo de llamada o de extensiones de llamada. Sin segmentos ni métricas | `https://developers.google.com/google-ads/api/fields/v24/call_view` |
| Programación | `ad_schedule_view` | métricas por criterio de programación | Existe solo con criterios `AD_SCHEDULE` | referencia |
| Ubicaciones de interés (AI Max) | `matched_location_interest_view` | segmentos `geo_target_*` y `ad_network_type` | Desde la v23, solo AI Max | ai-max-reporting |

```sql
SELECT segments.device, segments.day_of_week, segments.hour,
  metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND campaign.status = 'ENABLED'
```

```sql
SELECT campaign.id, campaign.name, geographic_view.country_criterion_id, geographic_view.location_type,
  segments.geo_target_region, segments.geo_target_city,
  metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, user_location_view.country_criterion_id, user_location_view.targeting_location,
  segments.geo_target_region, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM user_location_view
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT campaign.id, campaign.name, landing_page_view.unexpanded_final_url,
  metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.speed_score,
  metrics.mobile_friendly_clicks_percentage
FROM landing_page_view
WHERE segments.date DURING LAST_30_DAYS
```

```sql
SELECT call_view.resource_name, call_view.start_call_date_time, call_view.call_duration_seconds,
  call_view.call_status, call_view.type, call_view.caller_country_code
FROM call_view
```

---

## 12. Cuota de impresiones, parte superior y comparativa de subasta

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Cuota de impresiones | `campaign`, `ad_group`, `keyword_view`, `customer` | `metrics.search_impression_share`, `search_budget_lost_impression_share`, `search_rank_lost_impression_share`, `search_click_share`, `search_exact_match_impression_share` | Topes de visualización 0,0999 y 0,9001 (sección 2) | `https://developers.google.com/google-ads/api/fields/v24/campaign` |
| Parte superior | idem | `metrics.search_top_impression_share`, `search_absolute_top_impression_share`, `search_budget_lost_top_impression_share`, `search_budget_lost_absolute_top_impression_share`, `search_rank_lost_top_impression_share`, `search_rank_lost_absolute_top_impression_share`, `metrics.top_impression_percentage`, `metrics.absolute_top_impression_percentage` | `top_impression_percentage` mide % de tus impresiones en la parte superior; `search_top_impression_share` compara con las elegibles | idem |
| Comparativa de subasta | `campaign`, `ad_group`, `keyword_view` | `segments.auction_insight_domain` y `metrics.auction_insight_search_impression_share`, `_overlap_rate`, `_position_above_rate`, `_outranking_share`, `_top_impression_percentage`, `_absolute_top_impression_percentage` | **No accesible**: la referencia marca estas métricas como «not publicly available». El segmento aparece listado pero no es filtrable. Los datos de Auction Insights se piden desde la interfaz | `https://developers.google.com/google-ads/api/fields/v24/keyword_view` |

```sql
SELECT campaign.id, campaign.name, campaign.advertising_channel_type,
  metrics.search_impression_share, metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,
  metrics.search_absolute_top_impression_share, metrics.search_budget_lost_top_impression_share,
  metrics.search_rank_lost_top_impression_share, metrics.search_click_share,
  metrics.top_impression_percentage, metrics.absolute_top_impression_percentage
FROM campaign
WHERE campaign.advertising_channel_type = 'SEARCH' AND segments.date DURING LAST_30_DAYS
```

---

## 13. Historial de cambios

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Qué cambió y quién | `change_event` | `.change_date_time`, `.change_resource_type`, `.change_resource_name`, `.resource_change_operation`, `.changed_fields`, `.old_resource`, `.new_resource`, `.user_email`, `.client_type`, `.campaign`, `.ad_group`, `.asset` | **Filtro por fecha obligatorio, ventana dentro de los últimos 30 días. `LIMIT` obligatorio, máximo 10.000 filas.** Para paginar a mano, usar la última marca de tiempo como inicio de la siguiente consulta. Un cambio tarda hasta 3 minutos en aparecer. `old_resource`, `new_resource`, `changed_fields`, `change_resource_name` no son filtrables | `https://developers.google.com/google-ads/api/docs/change-event` |
| Tipos de cliente | `change_event.client_type` | Registran cambios: API de Google Ads, cliente web de Google Ads, y suscripción de recomendaciones (`GOOGLE_ADS_RECOMMENDATIONS_SUBSCRIPTION`) | No todos los cambios de la interfaz tienen evento. **Google Ads Editor no se registra aquí** aunque el enum tenga `GOOGLE_ADS_EDITOR`: para eso y para cambios a nivel de criterio, `change_status`. La interfaz de Historial de cambios aplica lógica extra y puede mostrar otra cosa | idem |
| Qué recursos cambiaron (sin detalle) | `change_status` | `.last_change_date_time`, `.resource_type`, `.resource_status`, más un campo por tipo de recurso (`campaign`, `ad_group`, `ad_group_ad`, `ad_group_criterion`, `campaign_criterion`, `campaign_budget`, `asset_group`, `asset`, `customer_asset`, `campaign_asset`, `ad_group_asset`, `shared_set`, `campaign_shared_set`, `combined_audience`...) | Solo dice qué recurso cambió y cuándo (`ADDED`, `CHANGED`, `REMOVED`), y devuelve solo el último cambio de cada recurso. Filtro por fecha obligatorio dentro de los últimos **90 días** y `LIMIT` obligatorio de 10.000 como máximo. Un cambio tarda hasta 3 minutos en reflejarse. Un cambio en un hijo puede aparecer como cambio del padre. Para el valor actual hay que volver a consultar el recurso | `https://developers.google.com/google-ads/api/docs/change-status` |

```sql
SELECT change_event.change_date_time, change_event.user_email, change_event.client_type,
  change_event.change_resource_type, change_event.change_resource_name,
  change_event.resource_change_operation, change_event.changed_fields,
  change_event.old_resource, change_event.new_resource, change_event.campaign
FROM change_event
WHERE change_event.change_date_time >= '2026-09-10'
  AND change_event.change_date_time <= '2026-10-08'
ORDER BY change_event.change_date_time DESC
LIMIT 10000
```

Ajustar las fechas para que la ventana quede dentro de los últimos 30 días. Fuente: `https://developers.google.com/google-ads/api/docs/change-event`.

---

## 14. Recomendaciones y nivel de optimización

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Recomendaciones | `recommendation` | `.type`, `.campaign`, `.campaign_budget`, `.ad_group`, `.campaigns`, `.dismissed`, `.impact` (no filtrable), `.campaign_budget_recommendation` (no filtrable) y un campo por tipo de recomendación (62 campos en total en la v24) | Nuevas en la v25.2: `raise_target_cpa_performance_bid_too_low_recommendation` y `lower_target_roas_performance_bid_too_low_recommendation` (puja demasiado baja para entrar en subastas de Search) | `https://developers.google.com/google-ads/api/fields/v24/recommendation`, release-notes |
| Nivel de optimización de cuenta | `customer` | `customer.optimization_score`, `customer.optimization_score_weight` | Por campaña: `campaign.optimization_score` | `https://developers.google.com/google-ads/api/fields/v24/customer` |
| Uso permitido | | `RecommendationService` | En proyectos Standard con «uso permitido: informes» solo se permiten lecturas con `Search`/`SearchStream` | access-levels |

```sql
SELECT recommendation.type, recommendation.dismissed, recommendation.campaign,
  recommendation.campaign_budget, recommendation.impact
FROM recommendation
```

```sql
SELECT customer.optimization_score, customer.optimization_score_weight FROM customer
```

```sql
SELECT campaign.id, campaign.name, campaign.optimization_score FROM campaign WHERE campaign.status = 'ENABLED'
```

---

## 15. Listas de audiencia y de clientes

| Comprobación | Recurso | Campos | Notas y trampas | Fuente |
|---|---|---|---|---|
| Lista, tamaño, estado, caducidad | `user_list` | `user_list.id`, `.name`, `.type`, `.description`, `.membership_status`, `.account_user_list_status`, `.membership_life_span`, `.size_for_search`, `.size_for_display`, `.size_range_for_search`, `.size_range_for_display`, `.eligible_for_search`, `.eligible_for_display`, `.match_rate_percentage`, `.closing_reason`, `.access_reason`, `.read_only`, `.integration_code` | `membership_life_span` son los días que la cookie de un usuario permanece en la lista desde su última incorporación (entre 0 y 540). La referencia indica que se ignora en listas lógicas y de reglas. Tamaños en cifra (`size_for_*`) y en rango (`size_range_for_*`) | `https://developers.google.com/google-ads/api/fields/v24/user_list` |
| Audiencias aplicadas | `campaign_criterion`, `ad_group_criterion` | `campaign_criterion.user_list.user_list`; vista `campaign_audience_view`, `ad_group_audience_view` | | referencia |

```sql
SELECT user_list.id, user_list.name, user_list.type, user_list.membership_status,
  user_list.membership_life_span, user_list.size_for_search, user_list.size_for_display,
  user_list.size_range_for_search, user_list.size_range_for_display,
  user_list.eligible_for_search, user_list.eligible_for_display, user_list.match_rate_percentage,
  user_list.closing_reason, user_list.account_user_list_status
FROM user_list
```

---

## 16. Subida de conversiones sin conexión

Lo que dice la documentación de la API de Google Ads, y nada más:

- Desde el **15-06-2026**, `ConversionUploadService.UploadClickConversions` está restringida para nuevos usuarios: devuelve `NotAllowlistedError.CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE` si el proyecto no había enviado antes subidas de conversiones sin conexión o conversiones mejoradas para clientes potenciales. La documentación indica que las **nuevas integraciones de subida de conversiones deben usar la Data Manager API**. Fuentes: `https://developers.google.com/google-ads/api/docs/best-practices/quotas`, `https://developers.google.com/google-ads/api/docs/conversions/upload-clicks`, `https://developers.google.com/google-ads/api/docs/deprecations`.
- Desde el 02-02-2026 los campos de atributos de sesión y dirección IP en subidas de conversiones también quedan restringidos a proyectos en lista de permitidos; la alternativa que indican es la Data Manager API. Fuente: deprecations.
- Desde el 01-04-2026, los flujos de Customer Match (`OfflineUserDataJobService`, `UserDataService`) quedan restringidos para proyectos sin solicitudes entre el 01-10-2025 y el 31-03-2026. Fuente: deprecations.
- Límite: 2.000 conversiones por petición (`TOO_MANY_CONVERSIONS_IN_REQUEST`). Fuente: quotas.
- Las llamadas a `UploadClickConversions` y `UploadCallConversions` cuentan como 1 operación cada una contra la cuota diaria. Fuente: quotas.
- Para una auditoría (solo lectura): el estado de la salud de las subidas se revisa con el informe de diagnóstico de la propia guía, y los datos subidos se ven en `conversion_action` y en las métricas de conversión. Detalles de la Data Manager API fuera de este fichero.

---

## Cambios recientes

| Fecha | Cambio | Fuente |
|---|---|---|
| 23-09-2026 | v25.2: URL options (`tracking_url_template`, `url_custom_parameters`, `final_url_suffix`) en `asset_group`; `AutomatedVideoCrawlSetting` en `Campaign.AssetAutomationSetting`; recomendaciones de puja demasiado baja (`RAISE_TARGET_CPA_PERFORMANCE_BID_TOO_LOW`, `LOWER_TARGET_ROAS_PERFORMANCE_BID_TOO_LOW`); segmentos de itinerario de hoteles; métricas de anuncios de vertical | release-notes |
| 09-09-2026 | Retirada de los developer tokens. Fin del soporte de idioma manual en Search, AI Max y PMax en Search | developer-token, deprecations |
| 19-08-2026 | v25.1: `Campaign.aca_migration_date_time` y `broad_match_migration_date_time` (migración automática a AI Max), `Metrics.original_conversion_value`, `Segments.loyalty_membership`, recursos de Brand Lift y Conversion Lift, `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` | release-notes |
| 22-07-2026 | v25: segmento `ad_sub_format_type` (requiere `ad_format_type`); métricas `youtube_comments`, `youtube_likes`, `youtube_shares`; se eliminan `CustomerLifecycleGoal` y `CampaignLifecycleGoal` | release-notes |
| 24-06-2026 | v24.2: `performance_max_placement_view` segmentable por `ad_network_type`; origen y tipo de conversión `LOCAL_SERVICES_ADS`; Google Maps como canal de Demand Gen | release-notes |
| 15-06-2026 | `UploadClickConversions` restringida para nuevos usuarios; usar Data Manager API | quotas, deprecations |
| 01-06-2026 | Retención granular reducida a 37 meses | deprecations |
| 13-05-2026 | v24.1: segmento `mobile_device_platform`; error `REQUESTED_DATE_GRANULARITY_NOT_SUPPORTED`; tipos de experimento `ADOPT_AI_MAX`, `ADOPT_BROAD_MATCH_KEYWORDS`, `PMAX_REPLACEMENT_SHOPPING` | release-notes |
| 22-04-2026 | v24: `CartDataSalesView`, métricas «all_*» no optimizables; tipos de conversión de leads de GA4 y Firebase; se quita `click_type` de las vistas de recursos | release-notes |
| 28-01-2026 | v23: desglose por canal (`ad_network_type`) en PMax; `MatchedLocationInterestView` (AI Max) y `PerStoreView`; `UserLocationView` y `GeographicView` aceptan métricas por fecha de conversión; se eliminan `Campaign.start_date`/`end_date` (ahora `start_date_time`/`end_date_time`) y las métricas agregadas de etiqueta de rendimiento | release-notes |
| 15-10-2025 | v22: se eliminan las etiquetas de rendimiento de recursos de PMax; `Campaign.url_expansion_opt_out` sustituido; segmentos `ad_using_product_data` y `ad_using_video`; `AdGroupAdAssetView` con métricas para RSA; `TargetingExpansionView` (AI Max); `AssetGroupAsset` segmentable por dispositivo y acción de conversión | release-notes |

Notas de versiones anteriores a la v22 (incluida la v21): ya retiradas o archivadas en «Sunsetted versions»; no se revisaron [SIN VERIFICAR para v21].

Páginas base: `https://developers.google.com/google-ads/api/docs/release-notes`, `https://developers.google.com/google-ads/api/docs/sunset-dates`, `https://developers.google.com/google-ads/api/docs/deprecations`.
