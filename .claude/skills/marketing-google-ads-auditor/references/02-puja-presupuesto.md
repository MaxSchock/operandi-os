# 02 · Puja y presupuesto
> Consultado el 08-10-2026. Fuentes oficiales. Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente.
> Nota de método: las páginas se leyeron con un extractor automático que resume; las cifras citadas entre comillas son literales del extracto. Nombres de campo de la API marcados [SIN VERIFICAR] salvo los de la página de tipos de estrategia (las páginas de referencia de campos/métricas de la API son demasiado grandes y no cargaron).

## Estrategias de puja vigentes: qué hace cada una y para qué objetivo
### Cómo funciona
- Google agrupa por objetivo. Ventas o leads: "Maximizar conversiones" y "CPA objetivo". Beneficio/valor: "ROAS objetivo" y "Maximizar el valor de las conversiones". Clics: Maximizar clics, CPC objetivo (Demand Gen), CPC manual. Visibilidad: cuota de impresiones objetivo (red de búsqueda), CPM, CPMo, vCPM (Display). Vídeo: CPV.
- Desde junio de 2026 "Maximizar conversiones con un CPA objetivo" pasa a llamarse "CPA objetivo" y "Maximizar el valor de las conversiones con un ROAS objetivo" pasa a "ROAS objetivo". Mismo comportamiento. Conviven nombres antiguos y nuevos durante la transición; API, Editor y app móvil se actualizan más tarde. "Maximizar conversiones" y "Maximizar valor" SIN objetivo no cambian de nombre.
- Maximizar clics: ajusta el CPC máximo para conseguir el máximo de clics dentro del presupuesto; "no optimiza hacia cuota de impresiones". Tope de CPC máximo opcional; si se fija demasiado bajo puede impedir alcanzar el objetivo. No es buena opción si necesitas un ranking de anuncio o un coste por conversión concretos. La página no da mínimos ni máximos de puja.
- Maximizar conversiones (sin objetivo): intenta gastar todo el presupuesto diario medio; si hoy gastas muy por debajo, el gasto puede subir de forma significativa. Exige seguimiento de conversiones. Sus ajustes de puja guardados no se usan, salvo dispositivo -100 %. No usar la columna "Cuota de impresiones perdida (presupuesto)" con esta estrategia ("incompatible"); usar simulador de presupuesto y métricas de cuota.
- CPA objetivo: la CPA real puede quedar por encima o por debajo del objetivo. Google recomienda el objetivo sugerido (CPA media de los últimos 30 días ajustada por latencia), evitar límites de puja (solo aplican a subastas de la red de búsqueda y solo en estrategias de cartera) y evitar objetivos por grupo de anuncios. Un objetivo demasiado bajo pierde clics que habrían convertido.
- Maximizar valor de conversión (sin ROAS): gasta el presupuesto diario medio; ignora ajustes de puja salvo dispositivo -100 %. Solo Search, Shopping y Demand Gen según su página (la de presupuesto total lista también PMax: contradicción entre páginas).
- Cuota de impresiones objetivo: ubicaciones "Parte superior" ("Top"), "Absoluta superior" o "En cualquier parte"; aviso literal "It's important not to set this limit too low" sobre el tope de CPC. Recomendada para marca/notoriedad local. Ignora ajustes de puja salvo dispositivo -100 %. Cuenta solo la Red de Búsqueda, sin socios de búsqueda. La página no da rango de porcentaje (ejemplos 65 % y 100 %).
- CPC mejorado (ECPC): retirado para Search y Display desde la semana del 31-03-2025; las campañas no migradas "ahora usan efectivamente CPC manual". En la API, `ManualCpc.enhanced_cpc_enabled = true` no tiene efecto. La página de CPC manual todavía lo menciona (contenido caducado).
- CPC manual: CPC máx. por grupo, palabra clave o ubicación. El CPC real puede superar el máximo por ajustes de puja y por puja manual en socios de búsqueda. Sin periodo de aprendizaje. Google lo sugiere sustituir por Maximizar clics si no puedes gestionar pujas a mano.
- CPM/vCPM/CPV: CPM (YouTube/Display, por mil impresiones), CPMo (alcance único), vCPM (por mil impresiones visibles, no apto para respuesta directa: "compra o formulario"), CPV (visualizaciones y otras interacciones de vídeo).
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Estrategia coherente con el objetivo (leads) | Leads/ventas: Maximizar conversiones o CPA objetivo; acciones a optimizar deben ser "Principales" | Campaña > Configuración > Estrategia de puja. API: `campaign.bidding_strategy_type` [SIN VERIFICAR nombre], conversiones "Include in conversions" | https://support.google.com/google-ads/answer/2472725?hl=es |
| Maximizar clics en cuenta con conversiones | No optimiza hacia ranking ni coste por conversión; solo tope de CPC por campaña | Estrategia = Maximizar clics (API: `TARGET_SPEND`) con conversiones registradas | https://support.google.com/google-ads/answer/6268626?hl=en |
| Tope de CPC bajo | "a limit set too low may keep the strategy from reaching your goal" | Estado "Limitada" por límites de puja; estrategia > tope CPC | https://support.google.com/google-ads/answer/6268626?hl=en |
| Límites de puja en CPA/ROAS | Google no los recomienda; solo en cartera y solo subastas de Search | Estrategias de cartera con CPC mín./máx. | https://support.google.com/google-ads/answer/6268632?hl=es |
| Objetivos CPA por grupo de anuncios | "Avoid ad group targets" | Objetivos a nivel de grupo | https://support.google.com/google-ads/answer/6268632?hl=es |
| Campañas aún en CPC mejorado | Retirado Search/Display, equivale a CPC manual | `enhanced_cpc_enabled` / estrategia CPC manual | https://support.google.com/google-ads/answer/2464964?hl=en |
| Maximizar conversiones con presupuesto sobrante | Gasta todo el presupuesto; su "Lost IS (budget)" no es fiable | Revisar CPA real frente a objetivo del negocio al subir presupuesto | https://support.google.com/google-ads/answer/7381968?hl=en |

## Tabla: estrategia x tipo de campaña x ajustes que respeta
Los iconos de la tabla de ajustes de la página oficial no tienen texto; las celdas "respeta" se infieren de ellos (marcado). Tipos de campaña según páginas de estrategia, presupuesto total y API.

| Estrategia | Tipos de campaña admitidos (fuente) | Dispositivo | Ubicación / horario / audiencias / llamadas / demografía |
|---|---|---|---|
| Maximizar clics (`TARGET_SPEND`) | Search, Shopping, Demand Gen (presupuesto total); estándar y cartera (API). PMax: no listada | Respeta (inferido); "no distingue móvil de escritorio", se combina con ajuste móvil | Respeta (inferido de iconos) |
| Maximizar conversiones (con o sin CPA objetivo) | Estándar: Search, Display, Video, Demand Gen, PMax, App. Cartera: Search, Shopping, PMax (API) | Solo -100 % | Ignorados |
| Maximizar valor de conversión (con o sin ROAS) | Search, Shopping, Demand Gen (su página); PMax también en presupuesto total [contradicción] | Solo -100 % | Ignorados |
| CPA objetivo | Search, Display, Video, Shopping, Demand Gen, App; PMax vía Maximizar conversiones+CPA | Ajuste dispositivo "tratado como ajuste del objetivo" (ej. +40 % sobre 10 EUR = 14 EUR); -100 % bloquea | Ignorados |
| ROAS objetivo | Search, Shopping, Display, App, Demand Gen, vídeo de acción, Hotel, Travel; PMax | Solo -100 % | Ignorados ("no necesitas quitarlos") |
| Cuota de impresiones objetivo | Search (red de búsqueda) | Solo -100 % | Ignorados |
| CPC manual | Search, Shopping, Demand Gen | Respeta | Respeta |
| CPM/vCPM/CPV/CPMo | YouTube/Display/Vídeo | [SIN VERIFICAR] | [SIN VERIFICAR] |
| CPC objetivo (`TARGET_CPC`) | Demand Gen | [SIN VERIFICAR] | [SIN VERIFICAR] |

Fuentes: https://support.google.com/google-ads/answer/2732132?hl=en (tabla de ajustes), https://support.google.com/google-ads/answer/10486938?hl=en (tipos x estrategia), https://developers.google.com/google-ads/api/docs/campaigns/bidding/strategy-types (API), https://support.google.com/google-ads/answer/7684216?hl=en, https://support.google.com/google-ads/answer/9121108?hl=en, https://support.google.com/google-ads/answer/6268637?hl=es

## Ajustes de puja: rangos y reglas de combinación
### Cómo funciona
- Rangos: dispositivo -100 % a +900 %; ubicación, programación, métodos de segmentación, listas de remarketing, interacciones y demografía -90 % a +900 %.
- Se multiplican; el aumento combinado no pasa de +900 % (ejemplo oficial: 1 USD con +900 % dispositivo y +900 % ubicación = 10 USD); el mínimo combinado es -90 %.
- Dispositivo: el ajuste de grupo anula el de campaña salvo que el de campaña sea -100 %. Ubicación: se aplica la más específica (París sobre Francia).
- En Smart Bidding de conversión solo cuenta el -100 % de dispositivo; el resto "se ignora", sin necesidad de borrarlo. Los programas de anuncios se respetan para decidir cuándo mostrar, pero no hay ajuste de puja horario.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Ajustes de ubicación/horario/audiencia sobre Smart Bidding de conversión | Ignorados (solo dispositivo -100 %) | Campaña > Dispositivos/Ubicaciones/Programación con ajustes != 0 y estrategia automática de conversión | https://support.google.com/google-ads/answer/2732132?hl=en |
| Ajuste de dispositivo en CPA objetivo | Cambia el objetivo, no la puja | Revisar % de dispositivo en campañas con CPA objetivo | https://support.google.com/google-ads/answer/6268632?hl=es |
| Apilado de ajustes | Combinado máx. +900 %, mín. -90 % | Suma/producto de ajustes en CPC manual o Maximizar clics | https://support.google.com/google-ads/answer/2732132?hl=en |
| Exclusión de dispositivo | -100 % funciona en todas las estrategias | Dispositivos con -100 % | https://support.google.com/google-ads/answer/7381968?hl=en |

## Volumen de datos para Smart Bidding y qué hacer con pocas conversiones
### Cómo funciona
- Puede activarse sin datos previos, pero Google recomienda alcanzar umbrales. Para evaluar: medir periodos largos (un mes o más) con "como mínimo 30 conversiones (o 50 en el caso de ROAS objetivo)" (página de Smart Bidding). La página de CPA objetivo: sin mínimo para empezar; evaluar sobre 30 días con al menos 30 conversiones.
- Mínimos de ROAS objetivo (página oficial): Search y Shopping, al menos 15 conversiones en 30 días a nivel de seguimiento; Display 15 con valor; vídeo de acción 30 en 30 días; Demand Gen 50 en 35 días (10 en los últimos 7) o 100 en la cuenta; Hotel 50/semana; Travel 50 en 7 días; App 10/día o 300 en 30 días. Conflicto entre páginas: Smart Bidding dice 50 para ROAS, ROAS objetivo dice 15 para Search/Shopping.
- Display: con menos de 30 conversiones la fluctuación puede llegar al 100 % (tabla de Display); ver https://support.google.com/google-ads/answer/10285843?hl=en (citado por búsqueda, no leído entero) [SIN VERIFICAR].
- Con poco dato, Smart Bidding usa datos a nivel de consulta y los refina con aprendizaje bayesiano; también aprende de campañas en puja manual.
- Palancas oficiales con pocas conversiones: estrategias de cartera y presupuestos compartidos para campañas con el mismo objetivo; menos campañas más grandes; para recuperar volumen subir CPA, bajar ROAS u ampliar segmentación; valores reales o proxy (puntuación de lead) y "una sola etapa" del embudo; si el cierre tarda, usar una etapa anterior (lead cualificado). Si no puedes dar valores distintos a cada lead: CPA objetivo sobre leads cualificados. Valores de al menos dos importes distintos para valor.
- Antes de pasar a valor: subir valores durante 3 semanas o 1-2 ciclos de conversión (el mayor); retraso de conversión idealmente menor de 7 días.
- Microconversiones y objetivos de cartera: [SIN VERIFICAR] en esta área (no se leyó una página oficial sobre acciones secundarias frente a principales); la página de estrategias solo exige que las acciones a optimizar estén como "Principales".
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Conversiones en 30 días vs estrategia | Evaluar con >= 30 conv. en 30 días; ROAS: >= 15 (Search/Shopping) | Campaña > Conversiones últimos 30 días (API `metrics.conversions`) | https://support.google.com/google-ads/answer/7065882?hl=es |
| ROAS sin valores distintos | Al menos dos valores distintos; 3 semanas o 1-2 ciclos subiendo valores | Informe de acciones de conversión: valor constante | https://support.google.com/google-ads/answer/15099424?hl=en |
| Acciones optimizadas como "Principales" | Requisito de Smart Bidding | Objetivos de conversión > "Incluir en conversiones" | https://support.google.com/google-ads/answer/2472725?hl=es |
| Cuenta fragmentada con pocas conversiones | Cartera + presupuesto compartido para mismo objetivo | Nº de campañas con < 30 conv./mes con el mismo objetivo | https://support.google.com/google-ads/answer/10970825 |
| Estrategia "Configuración errónea" por falta de acción de conversión | Falta acción web/llamada/app activa e incluida | Estado de estrategia "Configuración errónea" | https://support.google.com/google-ads/answer/6263057?hl=es |
| Retraso de conversión | Idealmente < 7 días; 1-2 ciclos para juzgar | Informe de estrategia de puja: ciclo de conversión | https://support.google.com/google-ads/answer/15099424?hl=en |

## Valor de conversión, reglas de valor y objetivos de captación
### Cómo funciona
- Reglas de valor: ajustan el valor según audiencia, dispositivo o ubicación (condición secundaria posible; todas las reglas de la cuenta con el mismo tipo de condición; solo una regla por conversión; ubicación más específica gana). Las usan ROAS objetivo y Maximizar valor. Para leads Google las recomienda y sugiere importación de conversiones offline o conversiones mejoradas para valorar bien.
- Objetivos de captación de clientes ("customer lifecycle goals"): modo "Solo clientes nuevos" admite Maximizar conversiones, CPA objetivo, ROAS objetivo y Maximizar valor, sin exigir conversión de compra, y es el modo que Google señala para objetivos no de compra como generación de leads ("recomendado solo con presupuestos estrictos de captación o sin objetivos de compra"). Los modos "Valor de cliente nuevo" y "Cliente nuevo de alto valor" exigen conversión Compra y estrategias de valor. Hace falta lista de clientes (primera parte) y etiqueta; mínimo de lista no indicado.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Reglas de valor en leads | Posibles; todas con el mismo tipo de condición | Herramientas > Conversiones > Reglas de valor | https://support.google.com/google-ads/answer/10518330?hl=en |
| Captación de clientes nuevos con leads | Solo modo "Solo clientes nuevos" aplica sin compra | Configuración de campaña > Objetivos del ciclo de vida | https://support.google.com/google-ads/answer/14008174?hl=en |

## Periodo de aprendizaje y estados de la estrategia
### Cómo funciona
- Duración: puede tardar "hasta 50 eventos de conversión o 3 ciclos de conversión" en recalibrar a un objetivo nuevo, menos si hay muchos datos. Depende de volumen de conversiones, longitud del ciclo y estrategia. CPC manual no tiene aprendizaje. Para cambios de objetivo/acción de conversión: "1-2 ciclos de conversión en la mayoría de casos"; PMax más si el tráfico no es de Search/Shopping.
- Disparan "Aprendiendo": estrategia nueva o reactivada, cambio de un ajuste de la estrategia, cambio de composición (añadir o quitar campañas, grupos o palabras clave), en Shopping algunos cambios del objetivo del grupo. Cambiar el objetivo CPA/ROAS "no activa" estado de aprendizaje pero cambia pujas rápido (según la guía de aprendizaje de algoritmos); contradicción parcial con un resumen de terceros, prevalece la oficial.
- Estados ("Estado de la estrategia"): Inactiva, Activa, Aprendiendo, Limitada (inventario: poco volumen de búsqueda; límites de puja: máx./mín. impiden optimizar; presupuesto: muchas palabras limitadas por presupuesto; estrategia de puja, solo campañas: pasar a estrategia totalmente automática), Configuración errónea (presupuesto compartido con distintas estrategias de cartera; o falta acción de conversión).
- Frecuencia y tamaño de cambios de objetivo: el bidder reacciona de inmediato pero necesita 1-2 ciclos para llegar al objetivo; "evita varios cambios de objetivo dentro de un mismo ciclo". Sin porcentaje oficial en CPA/ROAS de Search. Solo se hallaron "incrementos de aprox. 30 %" y esperar 1-2 ciclos en la guía de Shopping/PMax, y "20 % y esperar una semana" en la guía de Display [SIN VERIFICAR para Search]. En PMax: no tocar presupuesto ni objetivo durante el arranque y evaluar tras al menos 6 semanas, excluyendo 1-2 primeras semanas.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Estado "Aprendiendo" prolongado | Hasta 50 conversiones o 3 ciclos; no juzgar antes | Columna Estado de campaña; pasar el ratón sobre el estado. API `campaign.bidding_strategy_system_status` [SIN VERIFICAR nombre del campo] | https://support.google.com/google-ads/answer/13020501?hl=es |
| Cambios frecuentes de objetivo/presupuesto/estrategia | Reinician aprendizaje o confunden al bidder; no varios cambios por ciclo | Historial de cambios de la cuenta | https://support.google.com/google-ads/answer/10433846 |
| Estado "Limitada" y su motivo | Inventario, límites de puja, presupuesto, estrategia | Estado de estrategia > pasar el ratón | https://support.google.com/google-ads/answer/6263057?hl=es |
| Estado "Configuración errónea" | Misma estrategia de cartera para todas las campañas con un presupuesto compartido | Estado de estrategia | https://support.google.com/google-ads/answer/6263057?hl=es |
| Cambio de objetivo de conversión | Esperar 1-2 ciclos | Fechas de cambios de objetivo | https://support.google.com/google-ads/answer/14571185 |
| Evaluación de PMax | Mínimo 6 semanas, sin los 1-2 primeros semanas | Edad de la campaña | https://support.google.com/google-ads/answer/15624876 |

## Presupuesto: diario medio, sobregasto, topes mensuales
### Cómo funciona
- Presupuesto diario medio: un día puede gastar "hasta el doble"; en el mes el gasto facturable no supera 30,4 x presupuesto diario ("you'll never actually pay more than your spending limits"). Gasto servido puede exceder y no se factura el exceso (informe "Billed cost" mide sobreentrega: servido menos facturado).
- Presupuesto mensual manual: divide entre 30,4.
- Cambio a mitad de mes: se puede cambiar cuando se quiera. Regla de pacing (página de 2026): el límite mensual es lo ya gastado más el nuevo presupuesto diario x días naturales restantes del mes.
- Presupuestos compartidos: un presupuesto diario común para varias campañas, el sobrante pasa a las limitadas. Solo Search, Shopping, Display y Video. No compatibles con App, PMax, Hotel con comisión, Smart Shopping, ni presupuesto total; Google recomienda cartera de puja. Simulador de puja de campaña no disponible con presupuestos compartidos.
- Presupuesto total de campaña: solo campañas nuevas, no se puede cambiar el tipo después; Search, Shopping estándar y PMax de 3 a 90 días; Demand Gen y YouTube hasta 1 año. Sin límite diario, "nunca se te cobrará más que tu presupuesto total"; no compatible con publicación acelerada; no admite presupuesto compartido.
- Estado "Limitada por el presupuesto" (solo Campañas): aparece cuando la campaña rinde peor por presupuesto o usa Maximizar clics y más presupuesto aumentaría tráfico. No se da recomendación si rara vez alcanza el presupuesto o hay pocos datos. Insights de pacing: "Limited by budget" = falta al menos 5 % del tráfico semanal potencial; "Projected to be limited by budget" = previsión de al menos 5 % futuro; "Budget remaining" = se prevé terminar el mes con parte significativa sin gastar (sin % definido); "On track".
- Recomendaciones de tamaño: PMax "al menos 3 veces tu CPA" (paso 5) y bajo/medio/alto en la revisión; Demand Gen 10 x CPA; para CPA/ROAS objetivo Google pide poder gastar hasta 2x el diario sin pasar el límite mensual; mantener presupuesto "cómodamente por encima" del gasto medio.
- Publicación estándar vs acelerada: estándar es el valor por defecto y reparte el presupuesto durante el día. La acelerada dejó de estar disponible en Search, Shopping y presupuestos compartidos en 2019 y desde abril de 2020 en cualquier tipo de campaña (según el extracto de búsqueda de la página oficial https://support.google.com/google-ads/answer/7188483?hl=en-GB; no reconfirmado al leer la página completa) [SIN VERIFICAR]. Editor y Scripts aún muestran el valor; obsoleto.
- Programación de anuncios y gasto (cambio 01-06-2026): para programaciones que apagan días enteros de la semana, el pacing apunta ahora a hasta 30,4 x presupuesto diario al mes aunque se publique menos días. Máximo: programación de 15 días o menos = (diario x 2) x días activos; 16 días o más = diario x 30,4. Ejemplo de la página (releída el 08-10-2026): 100 USD/día con 10 días activos apunta a 1.000 USD al mes, con tope de 2.000 por el límite diario; sin ese límite iría a 3.040. [El ejemplo anterior de este fichero, 20 días y 66 USD, no está en la página.] Las programaciones por horas no se ven afectadas. Excluye Local Services, Hotel Commission, Smart y App.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Gasto diario > presupuesto | Hasta 2x diario; mes <= 30,4 x diario | Coste diario por campaña; informe "Billed cost"; API `campaign_budget.amount_micros` | https://support.google.com/google-ads/answer/1704443?hl=en |
| Campaña con "Limitada por el presupuesto" | Subir presupuesto o reducir objetivo; sin recomendación si apenas alcanza el tope | Filtro de estado "Limited by budget"; Insights de pacing | https://support.google.com/google-ads/answer/6385220?hl=en |
| Pacing mensual | Limitada si falta >= 5 % del tráfico semanal | Tabla de pacing de presupuesto | https://support.google.com/google-ads/answer/13685469?hl=en |
| Presupuesto vs CPA | PMax: >= 3 x CPA; CPA/ROAS: poder gastar 2x diario | Presupuesto diario / CPA real | https://support.google.com/google-ads/answer/15865234?hl=en |
| Programación por días de semana tras 01-06-2026 | Gasto mensual puede subir hasta 30,4 x diario | Campañas con días apagados; comparar gasto desde junio | https://support.google.com/google-ads/answer/16913225?hl=en |
| Presupuesto compartido con estrategias distintas | "Configuración errónea" | Estado de estrategia | https://support.google.com/google-ads/answer/6263057?hl=es |
| Presupuesto compartido en PMax o con total | No compatible | Presupuesto compartido (`explicitly_shared` [SIN VERIFICAR]) | https://support.google.com/google-ads/answer/10487241?hl=en |
| Presupuesto total mal usado | Solo nuevas, 3-90 días en Search/PMax; cambios frecuentes desestabilizan | Tipo de presupuesto de campaña (API `total_amount_micros`) | https://support.google.com/google-ads/answer/10486938?hl=en |
| Entrega acelerada | No existe ya; si aparece en Editor/API es obsoleta | `delivery_method` [SIN VERIFICAR] | https://support.google.com/google-ads/answer/7188483?hl=en-GB |

## Estacionalidad y exclusiones de datos
### Cómo funciona
- Ajuste de estacionalidad: solo para cambios repentinos o atípicos de la tasa de conversión (promoción, rebajas, lanzamiento); Smart Bidding ya anticipa estacionalidad predecible. Duración "normalmente de 1 a 7 días" (página de PMax). Original de 2019: eventos raros y campañas Search y Display, con ejemplo +50 %. No hay tope de porcentaje legible en las fuentes consultadas [SIN VERIFICAR].
- Exclusión de datos: para fallos de seguimiento (etiquetas, caída web, importaciones). Solo estrategias de conversión o valor; Search, Display, Shopping y PMax; no Hotel. Afecta solo a lo que aprende Smart Bidding, no a informes. Se basa en clics. Buena práctica: excluir al menos el 90 % de los clics afectados y empezar antes por el retraso de conversión (ejemplo: retraso de 5 días = empezar 5 días antes). No usarlas con frecuencia o durante mucho tiempo, no retirarlas una vez aplicadas. Efecto en pocos días; si hay una semana o más afectada, fluctuaciones de 1-2 ciclos. Para eventos comerciales usar estacionalidad. No añadir exclusiones solo por el cambio de agosto de 2026.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Uso de estacionalidad | Solo cambios atípicos; 1-7 días | Herramientas > Estrategias de puja > Controles avanzados | https://support.google.com/google-ads/answer/12351101?hl=en |
| Estacionalidad habitual en festivos previsibles | Innecesaria, ya la modela Smart Bidding | Ajustes activos | https://support.google.com/google-ads/answer/9461281?hl=en |
| Exclusiones tras caída de seguimiento | Excluir >= 90 % de clics afectados con colchón del retraso | Controles avanzados > Exclusiones de datos | https://support.google.com/google-ads/answer/10370710?hl=en |
| Exclusiones largas o repetidas | No recomendadas | Lista de exclusiones | https://support.google.com/google-ads/answer/10370710?hl=en |

## Cuota de impresiones y posición
### Cómo funciona
- Cuota de impresiones = impresiones / impresiones totales elegibles (estimadas por segmentación, estado de aprobación y calidad). Se ve en campañas, grupos y palabras clave. "--" suele ser pocos datos (puede tardar 24-48 h). Socios de búsqueda excluidos.
- Búsqueda: Search IS; Search lost IS (budget), solo a nivel de campaña, % de tiempo sin mostrar por presupuesto insuficiente; Search lost IS (rank), por Ad Rank bajo; Search exact match IS.
- Posición: "Search top IS" = impresiones recibidas entre anuncios superiores / impresiones elegibles entre anuncios superiores; "Search abs. top IS" = impresiones en la primera posición de los anuncios superiores / elegibles. "Impr. (Top) %" e "Impr. (Abs. Top) %" describen dónde salió el anuncio y Google no recomienda usarlas como objetivo de pujas. Las métricas de cuota sí pueden ser objetivo de puja. Definición de "anuncios superiores" actualizada: normalmente sobre el orgánico, pero a veces debajo; páginas relacionadas con la cuota objetivo actualizadas (fecha de ese aviso no indicada en la página).
- Ad Rank: seis factores (puja, calidad del anuncio y página, umbrales de Ad Rank, competitividad de la subasta, contexto de búsqueda, impacto esperado de recursos). Umbrales mínimos: Google no publica valores; el ejemplo hipotético de su página usa 0 para aparecer y 40 para parte superior. Umbrales dinámicos "recalculados en cada búsqueda", más altos para posiciones superiores.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Pérdida por presupuesto vs ranking | Distintos remedios: presupuesto o Ad Rank (puja/calidad) | Columnas Search lost IS (budget) / (rank); API `metrics.search_budget_lost_impression_share`, `metrics.search_rank_lost_impression_share` [SIN VERIFICAR nombre exacto] | https://support.google.com/google-ads/answer/7103314?hl=en |
| Lost IS (budget) con Maximizar conversiones | No es compatible | Evitar usarla; mirar simulador | https://support.google.com/google-ads/answer/7381968?hl=en |
| Posición real de los anuncios | Impr. (Top/Abs. Top) % no son objetivo de puja | Columnas de posición | https://support.google.com/google-ads/answer/7501826?hl=en |
| Cuota de parte superior/absoluta superior | Objetivo de puja posible; ejemplo sin porcentaje oficial | Search top IS / abs. top IS | https://support.google.com/google-ads/answer/7501826?hl=en |
| Umbrales de Ad Rank | Mínimo variable, más alto arriba; sin cifras oficiales | Cuota perdida por ranking alta con puja baja | https://support.google.com/google-ads/answer/1722122?hl=en |
| Datos de cuota "--" | Pocos datos | Valores "--" | https://support.google.com/google-ads/answer/2497703?hl=en |

## Simuladores y planificador de rendimiento
### Cómo funciona
- Simuladores de puja, presupuesto y objetivo (CPA/ROAS/cuota): estimaciones con los últimos 7 días, no previsiones. No disponibles para campañas nuevas o con pocos clics, si la campaña alcanzó o casi el presupuesto al menos una vez en 7 días (el simulador de puja), con experimentos activos o terminados en los últimos 8 días, en presupuestos compartidos (simulador de campaña) ni en Travel. Las estimaciones de conversión son menos fiables con pocos datos; evitar cambios de seguimiento en las 2 semanas previas. Si la campaña está "Limited by budget" se muestran ideas de presupuesto en lugar del simulador de puja. Simulador de presupuesto y métricas de cuota se recomiendan para Maximizar conversiones y valor.
- Performance Planner: previsiones basadas en 7-10 días con estacionalidad, actualizadas a diario. Elegibles (Search, Shopping estándar, PMax): sin cambio de estrategia en 10 días, al menos 3 clics, 10 impresiones, 1 conversión o valor y gasto > 0 en 17 días. Desde 09-03-2026 no admite Display ni vídeo ni planes con cuota de impresiones como métrica principal. Una cuenta de 10-30 EUR/día con pocas conversiones puede no ser pronosticable.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Disponibilidad de simulador | Requiere datos de 7 días y no estar al tope | Icono de simulador en tabla de campañas | https://support.google.com/google-ads/answer/2470105?hl=en |
| Elegibilidad de Performance Planner | >= 3 clics, 10 impr., 1 conv.; sin cambio de estrategia 10 días | Herramientas > Planificador | https://support.google.com/google-ads/answer/9230124?hl=en |

## Cambios recientes
- 31-03-2025 (semana): CPC mejorado retirado en Search y Display. https://support.google.com/google-ads/answer/2464964?hl=en
- 09-03-2026: Performance Planner deja de admitir Display y vídeo y planes basados en cuota de impresiones. https://support.google.com/google-ads/answer/9230124?hl=en
- 01-06-2026: nuevo pacing con programación de anuncios por días de la semana (hasta 30,4 x diario). https://support.google.com/google-ads/answer/16913225?hl=en
- Junio 2026: renombrado "CPA objetivo" y "ROAS objetivo" (sin cambio de comportamiento). https://support.google.com/google-ads/answer/10353027?hl=en
- 06-07-2026: herramienta "Bid Target Adjustment Tool" (anunciada en la página de CPA objetivo; la página 17061251 no la describe: detalle [SIN VERIFICAR]). https://support.google.com/google-ads/answer/6268632?hl=en
- 17-08-2026 a 27-08-2026: campañas con CPA/ROAS objetivo "Limitada por el presupuesto" (y CPC objetivo de Demand Gen) pasan a optimizar con más fidelidad al objetivo configurado en Search, Shopping, PMax, Demand Gen, Travel (Display y Hotel ya se comportaban así; App y vídeo alcance/visualizaciones no cambian). Google no cambia objetivos ni presupuestos; campañas con presupuesto total y cuota de impresiones objetivo, CPC manual no afectadas; menos de 7 conversiones, sin objetivo recomendado. Revisar campañas que superaban su objetivo; esperar 1-2 ciclos. https://support.google.com/google-ads/answer/17061251?hl=en y https://support.google.com/google-ads/answer/17125145?hl=en
- Presupuestos totales de campaña ampliados a Search, Shopping estándar, PMax y Demand Gen (la referencia de Scripts sigue diciendo solo vídeo, obsoleta). https://support.google.com/google-ads/answer/10486938?hl=en
