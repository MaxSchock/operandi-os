---
name: marketing-google-ads-auditor
description: "Audita una cuenta de Google Ads contrastando sus datos reales (API) con la documentación oficial de Google Ads revisada el 08-10-2026, y cruza el resultado con el comportamiento del usuario en la web (Clarity y Analytics). Úsala cuando Max pida auditar, revisar o diagnosticar una cuenta o campaña de Google Ads, decidir si una PMax sigue, entender por qué una campaña no convierte, o comprobar si una configuración cumple lo que Google recomienda. No sirve para Meta Ads (usar marketing-meta-ads-analyzer)."
---

# Auditoría de Google Ads con la documentación oficial

La skill aporta dos cosas: la **norma oficial** (siete referencias con regla, umbral y URL de Google por comprobación) y el **procedimiento**. El criterio de negocio no vive aquí: está en `clients/falkenlead/google-ads/agent/criteria.md` (cómo trabajan Mario y Max) y en el `business-context.md` de cada cliente. Si la norma oficial y el criterio chocan, se dice en el informe con los dos argumentos; decide Max.

## Antes de tocar datos

1. Identifica la entidad y la cuenta (`agent/README.md` lista los customer ID; MCC 222-302-0662).
2. Lee el historial del cliente: su `brief.md`, su `business-context.md` y los session-logs que lo nombran. Anota lo ya decidido y lo ya resuelto. **Lo resuelto no se presenta como hallazgo; lo decidido por Max solo se reabre con un dato nuevo, nombrando la decisión anterior.**
3. Di en una línea para qué sirve la auditoría y a quién.

## Extracción (solo lectura)

Desde `clients/falkenlead/google-ads/`:

```bash
D=<cliente>/diagnostico-$(date +%F)
python3 agent/pull.py <customer_id> --days 30 --out $D            # campañas activas, puja, palabras, anuncios, recursos
python3 agent/pull_auditoria.py <customer_id> --days 30 --out $D  # ajustes de cuenta, estados, redes, horas, historial, llamadas, PMax
python3 agent/ga4.py propiedades                                  # localizar la propiedad
python3 agent/ga4.py informe <prop> --dims sessionCampaignName,deviceCategory,landingPage \
        --mets sessions,engagedSessions,userEngagementDuration,keyEvents --filtro "sessionMedium==cpc"
python3 agent/clarity.py <cliente> --out $D                       # 4 cortes = 4 de las 10 llamadas diarias
```

- `pull_auditoria.py` deja los bloques rechazados en `_errores.json`: léelo antes de afirmar nada sobre ese bloque.
- La API va en v24 (`gads_lib.py`), que se retira en mayo de 2027; la v25 ya responde con el mismo token.
- Un corte que falte se pide con una consulta GAQL suelta (`references/07-api-gaql.md` tiene recurso y campos por comprobación). `DURING LAST_N_DAYS` no incluye hoy; usar `BETWEEN`.
- Clarity: detalle de la API y sus límites en `clarity/api-clarity.md` (no es documentación de Google Ads). Sin token del cliente en `~/.config/clarity/`, la parte de comportamiento se hace con Analytics y se pide el token a Max.

## Orden de la auditoría

Cada bloque se contrasta con su referencia. Se abre la referencia del bloque que se está mirando, no las siete de golpe.

| Paso | Qué se decide | Datos | Referencia |
|---|---|---|---|
| 0 | ¿La puja persigue leads reales? Acciones principales, objetivos de cuenta frente a los de campaña, estado de cada acción, llamadas, consentimiento | `conversion_actions`, `bidding_goals`, `x_customer_goals`, `x_goal_config`, `x_conv_by_action`, `x_calls`, `x_customer` | `01-medicion.md` |
| 1 | ¿La estrategia y el presupuesto encajan con el volumen de conversiones? Estado de la estrategia, gasto diario real, cuota perdida | `x_campaign_status`, `x_daily`, `x_top_share` | `02-puja-presupuesto.md` |
| 2 | Search: concordancias, términos, negativas, nivel de calidad, RSA, recursos, redes, ubicación | `x_keywords_all`, `x_search_terms_all`, `x_ads_all`, `x_rsa_assets`, `x_campaign_assets_detail`, `campaign_settings`, `x_campaign_criteria` | `03-search.md` |
| 3 | PMax: reparto por red, emplazamientos, grupo de recursos, señales, qué palancas existen | `x_network`, `x_pmax_placements`, `x_pmax_search_terms`, `pmax_asset_groups`, `x_pmax_signals`, `x_account_negatives` | `04-pmax-demandgen-display.md` |
| 4 | Audiencias y políticas: tamaño de listas, rechazos, requisitos del destino | `x_user_lists`, `x_ads_all` (política), HTML de la página | `05-audiencias-politicas-shopping.md` |
| 5 | Cuenta: aplicación automática, recomendaciones, historial de cambios, automatización de recursos | `x_recommendations`, `x_change_events`, consulta `recommendation_subscription` | `06-cuenta-recomendaciones-informes.md` |
| 6 | Comportamiento en la web por campaña y dispositivo, y página de destino | Clarity, Analytics, HTML con `curl` | `clarity/api-clarity.md` |

## Comportamiento en la web

- Clarity y Analytics solo ven a quien acepta cookies: di siempre cuántas sesiones se vieron frente a cuántos clics pagó la cuenta en el mismo periodo.
- Clarity no trae el nombre de campaña si no hay UTM (el etiquetado automático no lo pone). Se separa por el parámetro `gad_campaignid` de la URL (corte `URL,Channel`). PMax llega con identificadores que no son el de la campaña visible: se asignan a PMax por descarte.
- Medidas que se cruzan con campaña y dispositivo: tiempo activo, profundidad de scroll, clics muertos, clics de rabia, errores de script. Con menos de unas 20 sesiones por grupo se dan los valores sueltos, no medias.
- La página de destino se audita en el HTML (`curl`), nunca en una captura: titular, palabra clave del grupo en el texto, formulario (campos, dónde está), teléfonos, enlaces legales, etiquetas.
- Un formulario se comprueba sin enviarlo: contando los envíos en el servidor si hay acceso, y con un envío vacío que solo devuelva la validación. Nunca un envío real al cliente.

## Informe

Un `informe-<fecha>.md` por cuenta en la carpeta del cliente, renderizado con `agent/render.py` (PDF a la carpeta y a `/mnt/c/Users/PC/Downloads/`).

- Cada hallazgo lleva tres cosas: el **dato** de la cuenta con su rango de fechas, la **norma** oficial con su URL, y la **propuesta**. Sin dato no hay hallazgo; sin norma se dice que es criterio propio.
- Antes de escribir «no convirtió»: qué acciones cuentan como principales, si la medición funcionaba en esas fechas y cuántos clics hubo (pocos clics no demuestran nada).
- Orden por dinero en juego. Lo ya conocido o resuelto va aparte y en corto.
- Nada se aplica: todo cambio en la cuenta es de aprobación de Max, con copia previa (`agent/mutate.py`).
- Sin rayas largas. Horas reales si se citan.

## Trampas que la documentación aclara

- **Horario con días apagados** (desde 01-06-2026): el gasto mensual apunta a 30,4 veces el presupuesto diario aunque la campaña solo salga de lunes a viernes; un día puede gastar el doble. 10 €/día en L-V son hasta 304 €/mes, no 220.
- **PMax no tiene control de canal** ni exclusiones de emplazamientos por campaña. Las negativas solo tocan Búsqueda y Shopping. Con presupuesto corto Google reconoce que el gasto se va a YouTube y Display. Mínimo oficial: 3 veces el CPA al día.
- **Cuota perdida por presupuesto no vale con Maximizar conversiones**; sí con Maximizar clics.
- **Nivel de calidad «--»** es falta de búsquedas exactas, no un fallo. Es diagnóstico, no objetivo.
- **Una acción solo puja si es principal y su objetivo está aplicado a la campaña.** Los objetivos de campaña anulan los de cuenta.
- **Maximizar clics respeta los ajustes de puja**; las estrategias de conversión solo respetan el -100 % de dispositivo.
- **Listas de remarketing**: 100 usuarios activos en 30 días por red para servir.
- **Subida de conversiones sin conexión**: `uploadClickConversions` está cerrado a integraciones nuevas desde el 15-06-2026; se usa la Data Manager API (`agent/datamanager.py`).

## Mantenimiento de las referencias

- Fuente única: documentación oficial de Google Ads (`support.google.com/google-ads`, `support.google.com/adspolicy`, `developers.google.com/google-ads`). Nada de blogs, ni de Google ni de terceros.
- Cobertura real: 331 páginas oficiales distintas, elegidas por tema; no es toda la ayuda. Las transcribieron agentes y solo 18 se han releído contra la página (4 necesitaron corrección). **Antes de citar una norma en un informe, abre su URL y comprueba la frase.**
- Consultadas el 08-10-2026. Lo marcado `[SIN VERIFICAR]` no se pudo confirmar en la página: no se cita en un informe como norma.
- Cada referencia acaba en «Cambios recientes». Si una auditoría se apoya en una regla con más de tres meses, se vuelve a abrir su URL antes de citarla.
