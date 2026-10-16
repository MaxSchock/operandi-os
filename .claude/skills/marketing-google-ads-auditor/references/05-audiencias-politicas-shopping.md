# 05 · Audiencias, políticas y Shopping
> Consultado el 08-10-2026. Fuentes: support.google.com/google-ads, support.google.com/adspolicy y developers.google.com/google-ads. Lo marcado [SIN VERIFICAR] no se pudo confirmar en la fuente.

## Tipos de audiencia y segmentación frente a observación
### Cómo funciona
- Tipos vigentes: afinidad, personalizados (palabras clave, URLs, apps), datos demográficos detallados, eventos vitales, con intención de compra (in-market), "tus datos" (antes remarketing: visitantes web/app, listas de clientes) y audiencias que interactuaron con Google.
- Disponibilidad: Search admite afinidad, demográficos, in-market y tus datos; NO admite personalizados ni eventos vitales. Shopping estándar igual que Search. Demand Gen, Display y Video admiten todos.
- Segmentación (Targeting) restringe el alcance; Observación no cambia quién ve el anuncio y sirve para informar y ajustar pujas. Para Search y Shopping Google recomienda Observación; para Display, Segmentación.
- Con Smart Bidding, los segmentos propios añadidos en Observación se usan como señales de la puja inteligente.
- En Performance Max las audiencias son señales, no segmentación dura: el anuncio puede servirse fuera de la señal.
- Ventana de datos de los informes de audiencia: 30 días de retrospectiva actualizados semanalmente en el segmento de audiencia; Search 3 años (actualizado en la primera o segunda semana del mes siguiente).
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Audiencias en Search/Shopping en modo Segmentación sin querer | Para Search "se recomienda Observación"; Segmentación reduce el alcance | Campaña > Audiencias > ajuste de segmentación. API: `campaign_criterion`/`ad_group_criterion` con `bid_only` (`bid_only=false` es Segmentación). Por API el valor por defecto es Segmentación; en la interfaz es Observación | https://support.google.com/google-ads/answer/7365594?hl=en · https://developers.google.com/google-ads/api/docs/targeting/targeting-settings |
| Segmentos de tus datos y de clientes añadidos en campañas con Smart Bidding | "los segmentos propios añadidos en Observación se usarán como señales para Smart Bidding" | Informe Audiencias; sin segmentos en Observación se pierde la señal | https://support.google.com/google-ads/answer/7365594?hl=en |
| Tipos no disponibles aplicados a una campaña | Search no admite personalizados ni eventos vitales | Estado "Apto (limitado)" del segmento o error al añadirlo | https://support.google.com/google-ads/answer/2497941?hl=es |
| Señales de audiencia en PMax tratadas como filtro | No son segmentación dura; el anuncio puede servir fuera de la señal | Grupo de recursos > señales de audiencia. API: `AssetGroupSignal` | https://developers.google.com/google-ads/api/performance-max/asset-group-signals |
| Audiencias personalizadas/in-market en cuentas con poco volumen | Segmentos con al menos 100 usuarios aparecen en Audience insights | Gestor de audiencias > Audience insights | https://support.google.com/google-ads/answer/7558048?hl=en |

## Gestor de audiencias y fuentes de datos
### Cómo funciona
- Fuentes: visitantes del sitio (tras instalar la etiqueta de Google; se crean automáticas "Todos los visitantes" y "Todos los convertidores"), segmentos de clientes (Customer Match; casilla "listas basadas en conversiones" que genera listas automáticas), usuarios de YouTube (requiere vincular el canal), usuarios de app, combinación personalizada (AND de segmentos) y "Llamadores" (automática, no editable a mano).
- La tabla muestra hasta 50 segmentos a la vez. Una lista nueva tarda entre 48 y 72 horas en poblarse del todo.
- Estados: "Estado de pertenencia" (si sigue añadiendo usuarios), Pausado (no sirve pero sigue recogiendo usuarios), Eliminado, "Estado de uso". Un segmento no usado en segmentación durante 540 días pasa a "Cerrado".
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Etiqueta de Google no instalada o sin segmentos de visitantes | Los segmentos de visitantes se crean tras instalar la etiqueta | Gestor de audiencias > Fuentes de datos | https://support.google.com/google-ads/answer/7558048?hl=en |
| Segmentos sin uso | 540 días sin usar en segmentación => estado "Cerrado" | Gestor de audiencias > columna Estado | https://support.google.com/google-ads/answer/2472738?hl=en |
| Segmentos sin poblar | 48-72 h hasta poblarse; mínimo 100 usuarios activos | Columna tamaño del segmento | https://support.google.com/google-ads/answer/7558048?hl=en |

## Listas de remarketing (tus datos)
### Cómo funciona
- Tamaño mínimo: 100 visitantes/usuarios activos en los últimos 30 días para Display, Search y YouTube. Gmail: sin mínimo indicado; solo se añaden usuarios con sesión de Gmail.
- Listas de clientes subidas o actualizadas desde el 1-02-2024: 100 usuarios activos. Las subidas antes de esa fecha deben seguir cumpliendo 1.000 usuarios coincidentes.
- Duración de pertenencia: por defecto 30 días, máximo 540 días (Display y Search). Para YouTube y Gmail la página no da máximo.
- Exclusiones: solo se pueden excluir segmentos de tus datos y personalizados.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Lista por debajo del mínimo (no sirve) | "mínimo de 100 visitantes o usuarios activos en los últimos 30 días" por red | Gestor de audiencias > tamaño por red. API: `user_list.size_for_search`, `size_for_display` | https://support.google.com/google-ads/answer/2472738?hl=en |
| Duración de pertenencia demasiado corta para el ciclo de venta | Defecto 30 días, máximo 540; alinear con ciclo de venta | `user_list.membership_life_span` | https://support.google.com/google-ads/answer/2472738?hl=en |
| Listas heredadas de antes de feb-2024 | Siguen necesitando 1.000 coincidentes | Fecha de subida de la lista | https://support.google.com/google-ads/answer/2472738?hl=en |

## Listas de clientes (Customer Match)
### Cómo funciona
- Requisitos de cuenta: buen historial de cumplimiento de políticas y de pagos. Acceso ampliado (Segmentación y ajustes manuales de puja): más de 90 días de historial y más de 50.000 USD de gasto total. El resto de cuentas solo puede usarlas en Observación y exclusiones.
- Campañas: Search, Shopping, Display, YouTube y Gmail. La página de ayuda no menciona Demand Gen ni PMax; el uso en PMax como señal de audiencia sí figura en la documentación de desarrolladores.
- Solo datos propios (web, apps, tiendas físicas, clientes). Prohibido subir datos de menores de 13 años.
- Caducidad: la pertenencia dura como máximo 540 días (por defecto 540). Para mantener la lista apta debe haber al menos 100 miembros añadidos o actualizados en esos 540 días. La pertenencia infinita ya no se admite desde el 7-04-2025.
- Formato por API: SHA-256 de email, nombre, apellido y teléfono tras recortar espacios y pasar a minúsculas; teléfono en E.164 con "+"; en gmail.com/googlemail.com quitar puntos del usuario y desde el primer "+". Dirección postal requiere país, código postal, nombre y apellido con hash. Un formato incorrecto se acepta pero no coincide.
- Tasa de coincidencia: la ayuda no da cifra. Solo se muestra con subidas de al menos 100 filas coincidentes con usuarios únicos. Se recomienda subir al menos 5.000 miembros para tener suficientes usuarios activos.
- Con Smart Bidding y optimized targeting las listas de clientes de la cuenta se incluyen automáticamente (hay opción de excluirse); la disponibilidad actual de esta inclusión automática es YouTube y YouTube Video Action; Search y In-feed "próximamente".
- Desde el 1-04-2026 la API de Google Ads devuelve `CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE` salvo que el proyecto de Cloud o el developer token tuviera actividad Customer Match entre el 1-10-2025 y el 31-03-2026. Google recomienda Data Manager API para integraciones nuevas.
- IP y marca de tiempo no se admiten en EEE, Reino Unido ni Suiza.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Lista caducada o sin refrescar | Pertenencia máx. 540 días; mínimo 100 miembros añadidos/actualizados en 540 días | Gestor de audiencias > fecha de última actualización. API: recomendación `REFRESH_CUSTOMER_MATCH_LIST` | https://support.google.com/google-ads/answer/6379332?hl=en |
| Cuenta sin acceso ampliado intentando Segmentación | Solo Observación/exclusiones salvo 90 días y 50.000 USD | Mensaje al aplicar segmentación | https://support.google.com/google-ads/answer/6299717?hl=es |
| Subidas sin consentimiento (usuarios EEE) | `consent.ad_user_data` y `consent.ad_personalization` obligatorios en `create`; `DENIED` devuelve `CUSTOMER_NOT_ACCEPTED_CUSTOMER_DATA_TERMS`; sin valor se trata como no consentido | Respuesta del job de subida; informe de estado de la lista | https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/customer-match/get-started |
| Formato de datos incorrecto (match bajo) | SHA-256, minúsculas, E.164; formato mal formado no coincide | Tasa de coincidencia tras el job (requiere 100 filas coincidentes) | https://support.google.com/google-ads/answer/7659867?hl=en |
| Lista pequeña | 5.000 miembros recomendado para tener activos suficientes; mínimo 100 activos para servir | Tamaño de lista (redondeado, solo usuarios activos) | https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/customer-match/get-started |
| Uso de Customer Match con productos sensibles | Prohibido anunciar productos sensibles (p. ej. farmacéuticos) con Customer Match | Revisión de campañas vinculadas | https://support.google.com/google-ads/answer/6299717?hl=es |

## Segmentación optimizada, expansión de audiencia y audiencias similares
### Cómo funciona
- Segmentación optimizada: compatible con Display, Video (objetivos Ventas, Clientes potenciales o Tráfico del sitio web) y Demand Gen. "Se activa automáticamente en todas las campañas"; se desactiva en la configuración del grupo de anuncios. Usa tus segmentos como pista y puede reducir tráfico en señales que rinden peor.
- Expansión de audiencia: función distinta, busca usuarios parecidos a tus segmentos. En Video solo con objetivos de alcance/consideración.
- Segmentos Lookalike (sustitutos de las audiencias similares): solo en Demand Gen; en otros tipos de campaña figuran como "Apto (limitado)" y no sirven. Alcance: estrecho 2,5 %, equilibrado 5 %, amplio 10 %. Semilla: hasta 10 listas; la ayuda exige más de 100 personas activas coincidentes (la página de desarrolladores da 100 en un apartado y 1.000 en otro, sin reconciliar). Se refrescan cada 1-2 días; si la semilla baja del mínimo dejan de servir (hasta 3 días).
- 2026: Lookalike pasa a "modo sugerencia" en Demand Gen por fases a lo largo de 2026; el deslizador deja de funcionar como restricción y se puede optar por mantener el comportamiento anterior (Targeting Constraint) mediante formulario. La página no da fecha exacta de cierre.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Tráfico fuera de señal en campañas de pocos datos | Puede reducir o dejar de servir en tus señales si encuentra tráfico mejor | Informe de segmentos/audiencias | https://support.google.com/google-ads/answer/10537509?hl=en |
| Lookalike como restricción vs sugerencia | Transición a sugerencia durante 2026, con opción de exclusión | Ajustes del grupo de anuncios de Demand Gen | https://support.google.com/google-ads/answer/16902001?hl=en |
| Seguimiento de Lookalike en Demand Gen | Solo Demand Gen; semilla mínima 100 activos | API: `lookalike_user_list`, estado `Ineligible` | https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/lookalike-audiences |

## Política de consentimiento de usuarios de la UE y medición
### Cómo funciona
- Aplica en EEE, Reino Unido y Suiza. El anunciante debe obtener consentimiento de usuarios finales para el uso de datos personales y compartir las señales con Google, para medición, personalización de anuncios y remarketing.
- Parámetros de Consent Mode v2: `ad_user_data` (enviar datos de usuario a Google con fines publicitarios) y `ad_personalization` (publicidad personalizada). Para personalizar deben estar los dos en "granted"; si contradicen, se desactiva la personalización.
- `ad_personalization` denegado: se desactiva el remarketing (Google Ads, DV360, SA360) y la publicidad personalizada. `ad_user_data` denegado: se desactiva el uso de datos personales para publicidad (user_id, datos aportados por el usuario, mejoras de conversiones), se limita la exportación de conversiones por click ID (p. ej. pujas con conversiones de Analytics) y se envían pings sin cookies.
- Sin señal de consentimiento "pierdes las capacidades de personalización de anuncios". No bloquear las etiquetas de Google hasta que el usuario interactúe: Google no puede verificar el consentimiento y "puede producir pérdida de datos".
- Se recomienda un CMP certificado por Google. Con banner propio hay que implementar Consent Mode v2.
- Modelado de conversiones: requiere Consent Mode o IAB TCF v2.0 correctamente implementado y, según la página de modelado, 700 clics de anuncio en 7 días por país y dominio. Otra página de Google indica 100 clics/día por país y dominio para la implementación básica y que el umbral no aplica a la avanzada. Las dos cifras aparecen en fuentes oficiales y no se reconcilian.
- Subidas (Customer Match, ventas en tienda) de usuarios del EEE: ambos valores de consentimiento deben ser GRANTED desde marzo de 2024.
- Verificación: pestaña Diagnóstico de la acción de conversión (Objetivos > Conversiones > Resumen) muestra "Consent mode is implemented" y si el modelado está activo.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Consent Mode v2 ausente en web con tráfico EEE | Obligatorio para personalización y remarketing en EEE | Objetivos > Conversiones > Diagnóstico de la acción; estado de Consent Mode | https://support.google.com/google-ads/answer/13695607?hl=en |
| Etiquetas bloqueadas hasta interacción con banner | Google no puede verificar el consentimiento; pérdida de datos | Revisar CMP/GTM: etiqueta se dispara con default "denied" | https://support.google.com/google-ads/answer/13695607?hl=en |
| `ad_user_data`/`ad_personalization` no enviados | Sin ellos, sin personalización; remarketing sin datos | Parámetro `gcd` y estado en Diagnóstico | https://support.google.com/google-ads/answer/13802165?hl=en |
| Volumen insuficiente para modelar | 700 clics/7 días por país y dominio (modelado) o 100 clics/día (modo básico) [cifras discrepantes] | Diagnóstico: "implemented" sin modelado activo = umbral sin cumplir | https://support.google.com/google-ads/answer/10548233?hl=en · https://support.google.com/google-ads/answer/12445060?hl=en-GB |
| Listas de clientes en EEE sin consentimiento | Ambos campos GRANTED | Job de subida con error | https://support.google.com/google-ads/answer/14009343?hl=en |

## Políticas de anuncios que más rechazan en cuentas pequeñas
### Cómo funciona
- Destino no funciona: se rechazan destinos que no funcionan o están mal configurados, o que devuelven un código de error HTTP a AdsBot. AdsBot debe poder rastrear el destino y debe ser accesible en la ubicación segmentada.
- Destino que no coincide: dominio o extensión de la URL visible distinto de la URL final; redirecciones a otro dominio; plantillas de seguimiento que llevan a contenido distinto.
- Experiencia del destino: contenido difícil de navegar, enlaces que descargan directamente o llevan a un email/archivo; contenido original insuficiente (páginas hechas para mostrar anuncios, solo redirigen, o dicen que no ofrecen servicios).
- Tergiversación: incluye prácticas empresariales inaceptables (ocultar o falsear información del negocio, simular afiliaciones, ofrecer lo que no se puede entregar), representación engañosa (nombre de empresa inexacto), precios deshonestos, ofertas no disponibles, afirmaciones poco fiables, relevancia poco clara. Las prácticas empresariales inaceptables se tratan como flagrantes: suspensión inmediata sin aviso previo.
- Buenas prácticas oficiales: web con información de contacto actualizada y explicación de a qué se dedica la empresa. La falta de contacto figura como buena práctica, no como prohibición independiente.
- Editorial: prohibido número de teléfono en el texto del anuncio; mayúsculas, puntuación o símbolos mal usados; repetición no estándar; espaciado excesivo. Abreviaturas comunes ("ASAP") y marcas pueden permitirse tras revisión.
- Marcas comerciales en el texto: la marca debe aparecer en el texto del anuncio para que se aplique; el uso como palabra clave no está restringido. Se actúa por reclamación del titular. Estado resultante: apto (limitado).
- Nombre de empresa: debe ser el dominio, el nombre reconocido del anunciante o la app; rechazados los genéricos o de ubicación ("Mountain View Plumber") y los promocionales. Máximo 25 caracteres.
- Formularios de clientes potenciales: enlace a la política de privacidad obligatorio; prohibidos para contenido sexual, alcohol, juegos de azar, salud y medicamentos y contenido político; prohibidos afiliados y agregadores de leads. Gasto requerido: más de 50.000 USD, o bien más de 1.000 USD por cuenta (15.000 en todas) con verificación del anunciante.
- Recursos de llamada: números verificados por Google, en servicio y relacionados con el negocio; al atender, empezar nombrando el negocio tal como figura en el anuncio. La política de número no verificado se aplica también a recursos de mensaje (nuevos desde el 1-08-2025, existentes desde el 1-09-2025). Anuncios solo de llamada: sin creación nueva desde febrero de 2026 y sin impresiones desde febrero de 2027 (https://support.google.com/google-ads/answer/16619010?hl=en).
- Sistema de avisos: 1.ª infracción, aviso por correo (una vez). 1.er strike: bloqueo de 3 días. 2.º strike (misma política en 90 días): 7 días. 3.er strike (otra vez en 90 días): suspensión. Máximo un aviso y tres strikes. Cubre solo ciertas políticas (comportamiento deshonesto, engañar con el diseño, clickbait, directorios de llamadas, reparación de crédito, préstamos personales, entre otras). Las demás infracciones graves y flagrantes suspenden sin aviso; el resto avisa al menos 7 días antes.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| URL final con error o bloqueada a AdsBot | "Destinos que devuelven un código de error HTTP a AdsBot" se rechazan | Probar URL con user-agent AdsBot (DevTools); revisar robots.txt y 4xx/5xx. API: `policy_summary` del anuncio | https://support.google.com/adspolicy/answer/6368661?hl=en |
| Dominio de URL visible distinto del final | Debe coincidir dominio y extensión | Revisar `display_url`/rutas y `final_urls` | https://support.google.com/adspolicy/answer/6368661?hl=en |
| Redirecciones a otro dominio / plantilla de seguimiento | No pueden llevar a contenido distinto de la URL final | Revisar plantilla de seguimiento y sufijos | https://support.google.com/adspolicy/answer/6368661?hl=en |
| Falta de información de contacto o negocio en la web | [Comprobado el 08-10-2026: la página 6020955 habla de ocultar u omitir información material sobre la identidad del negocio y no nombra datos de contacto; la 15938071 no se ha releído] | Revisar la web: página de contacto, datos fiscales | https://support.google.com/adspolicy/answer/15938071?hl=en · https://support.google.com/adspolicy/answer/6020955?hl=en |
| Teléfono en titulares/descripciones | "Entering a phone number in ad text" prohibido | Buscar dígitos en textos de anuncio; usar recurso de llamada | https://support.google.com/adspolicy/answer/6021546?hl=en |
| Mayúsculas, signos repetidos, símbolos | Prohibido uso no correcto o gimmicky | Revisar textos del RSA; columna "Detalles de política" | https://support.google.com/adspolicy/answer/6021546?hl=en |
| Marca ajena en el texto | Restricción por reclamación; puede dejar el anuncio "Apto (limitado)" | Estado del anuncio; Policy manager | https://support.google.com/adspolicy/answer/6118?hl=en |
| Nombre de empresa genérico/promocional/>25 car. | Debe ser dominio o nombre reconocido; límite 25 | Recurso de nombre de empresa; si hay verificación, debe coincidir con el nombre verificado | https://support.google.com/adspolicy/answer/14847993?hl=en |
| Lead form sin enlace de privacidad | Obligatorio al crear el recurso | Recurso de formulario > URL de privacidad | https://support.google.com/adspolicy/answer/9472930?hl=en |
| Recurso de llamada con número no verificado/no en servicio | Debe estar verificado, en servicio y relacionado | Estado del recurso de llamada | https://support.google.com/adspolicy/answer/6130299?hl=en · https://support.google.com/adspolicy/answer/16333090?hl=en |
| Avisos o strikes abiertos | 1 aviso, 3 strikes: 3 días, 7 días, suspensión (90 días entre infracciones) | Centro de acciones / Policy manager; correo de la cuenta | https://support.google.com/adspolicy/answer/10922738?hl=en-GB |

## Verificación del anunciante
### Cómo funciona
- Proceso de tareas (preguntas de organización, pagos, documentos, D&B). Parte de la información verificada aparece en el aviso del anuncio (nombre y ubicación) y en el Centro de transparencia de anuncios (incluido historial de cambios de nombre).
- Google dice que todos los anunciantes tendrán que verificarse, en despliegue gradual. Motivos de selección: etiquetado sospechoso, sectores como financiero, anuncios en consultas de marca, funciones mal usadas, apelar una suspensión (requiere verificación), cambios de pagos/facturación/negocio y cambio de razón social (verificación nueva inmediata).
- Plazos: la revisión de cada tarea tarda hasta 5 días laborables y en casos raros hasta 30 días. El plazo no se puede prorrogar. Sin verificar al llegar la fecha límite, la cuenta se pausa y solo se reactiva verificando. Sin plazo asignado la verificación es opcional, aunque puede haber limitaciones de entrega.
- Organizaciones: documentos con nombre y ubicación idénticos al perfil de pagos y a la razón social; los nombres comerciales deben coincidir con el registro. D-U-N-S opcional (tras 3 intentos fallidos hay que subir documentos). Confirmación de método de pago con cargo de hasta 1,95 USD.
- Quienes lo necesitan para apelar una suspensión no pueden apelar si falla 3 veces.
- Pregunta específica de la UE: la verificación incluye confirmar si la cuenta mostrará anuncios políticos de la UE.
- Nombre de empresa en anuncios: con verificación completada, el nombre debe coincidir estrictamente con el dominio o con el nombre enviado en la verificación. Si el nombre legal no coincide o supera 25 caracteres, existe la Brand Verification si se tiene marca registrada. Requisitos de logotipo: no hay reglas en la página leída. [SIN VERIFICAR]
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Plazo de verificación pendiente | No prorrogable; cuenta pausada si no se completa | Admin > Verificación del anunciante / aviso en cuenta | https://support.google.com/adspolicy/answer/15588490?hl=en |
| Nombre legal del perfil de pagos no coincide con documentos | Debe coincidir exactamente nombre y ubicación | Perfil de pagos > información | https://support.google.com/adspolicy/answer/15577076?hl=en |
| Cambio de razón social o dirección | Dispara verificación nueva | Historial de cambios del perfil de pagos | https://support.google.com/adspolicy/answer/9703665?hl=en |
| Nombre de empresa en anuncios vs. nombre verificado | Debe coincidir con dominio o nombre enviado | Recurso de nombre de empresa | https://support.google.com/adspolicy/answer/14847993?hl=en |
| Revisión pendiente | Hasta 5 días laborables (30 en raros casos) | Estado de tareas | https://support.google.com/adspolicy/answer/15588490?hl=en |

## Estados de política, apelaciones y suspensiones
### Cómo funciona
- Estados de anuncio: En revisión (normalmente un día laborable); Apto; Apto (limitado) (restricciones como marcas o juegos de azar); Apto (limitado a todas las ubicaciones); Aprobado y Aprobado (limitado) para recursos; Rechazado (sin impresiones); No apto (campaña o grupo pausado, eliminado, etc.).
- Apelación: máximo 3 por anuncio; luego solo por soporte. Esperar al menos 24 horas entre apelaciones del mismo anuncio. Tras apelación fallida o duplicada, editar un poco el texto o la URL final para forzar nuevo rastreo. Desde el 21-07-2026 no se podrán apelar en la cuenta decisiones de más de 6 meses. Motivos: "Disputar decisión" o "Se hicieron cambios para cumplir la política". Anunciantes de la UE pueden tener vías adicionales bajo la DSA.
- Suspensión: motivos de infracción flagrante (sin aviso), reiteradas (strikes), facturación y pagos, actividad no autorizada. Apelación posible durante al menos 6 meses desde la suspensión; un solo recurso a la vez; el mal uso pausa el procesamiento 7 días. La suspensión se considera permanente salvo apelación aceptada; reinstalación solo en circunstancias excepcionales.
- Prácticas empresariales inaceptables: suspensión inmediata sin advertencia.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Anuncios Rechazados o "Apto (limitado)" | Rechazado = sin impresiones; limitado = no sirve siempre | Columna Estado/Detalles de política. API: `ad_group_ad.policy_summary.approval_status` | https://support.google.com/google-ads/answer/1722129?hl=en |
| Apelaciones agotadas | 3 por anuncio | Policy manager > Historial de apelaciones | https://support.google.com/adspolicy/answer/9338593?hl=en |
| Decisiones antiguas sin apelar | Desde 21-07-2026 solo soporte para decisiones de más de 6 meses | Fecha de la decisión en Policy manager | https://support.google.com/adspolicy/answer/9338593?hl=en |
| Suspensión de cuenta | Apelar en 6 meses; un recurso a la vez | Estado de cuenta | https://support.google.com/adspolicy/answer/9841640?hl=en |

## Shopping y vinculación con Merchant Center (solo ayuda de Google Ads)
### Cómo funciona
- Shopping ads se muestran con campañas Shopping o Performance Max y usan los datos de producto de Merchant Center, no palabras clave.
- Hace falta cuenta de Merchant Center y de Google Ads vinculadas. Condiciones del enlace: ninguna de las dos con infracciones de política a nivel de cuenta; las cuentas de administrador (MCC) no se pueden vincular a Merchant Center; una campaña solo se vincula a una cuenta de Merchant Center (cambiar exige campaña nueva). Un Merchant Center admite hasta 500 cuentas de Google Ads.
- El contenido debe cumplir las políticas de Shopping ads, que son distintas de las políticas de Google Ads. Los datos de producto deben enviarse actualizados "al menos cada 30 días" y cumplir la especificación de datos de producto.
- En el EEE y Suiza se participa en Shopping a través de uno o más servicios de comparación de compras (CSS) a elección.
- Etiquetas personalizadas: 5 (0 a 4), valores de 1 a 100 caracteres, hasta 1.000 valores únicos por atributo y 5.000 en total; tardan 24-48 horas en aparecer en Google Ads. No se muestran en los anuncios.
- Prioridad de campaña (Baja por defecto, Media, Alta) solo se aplica entre campañas Shopping estándar con el mismo producto y país: gana la de mayor prioridad aunque otra puje más; a igual prioridad, la puja mayor. Si la prioritaria agota presupuesto, puja la siguiente.
- Shopping estándar frente a PMax con el mismo producto: si coinciden ubicaciones, idiomas, horarios y otros ajustes, decide el Ad Rank. Los negativos a nivel de campaña no existen en PMax (solo a nivel de cuenta); sí en Shopping estándar.
- Diagnóstico de productos: Campañas > Productos > pestaña Diagnóstico; estados Apto, Apto (limitado), No apto (política, pausado, sin stock).
- Lo que no figura en la ayuda de Google Ads (atributos exactos del feed, GTIN, imágenes, motivos de rechazo de producto, requisitos de la web de la tienda como devoluciones, contacto o pago, fichas gratuitas) está en Merchant Center, fuera del alcance de esta referencia.
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Cuenta sin vincular o vinculación bloqueada | Sin infracciones de cuenta; MCC no se vincula; una campaña, un Merchant Center | Herramientas > Data manager > Productos conectados | https://support.google.com/google-ads/answer/12499498?hl=en |
| Datos de producto desactualizados | Envío "al menos cada 30 días" | Merchant Center vinculado; Diagnóstico de productos | https://support.google.com/google-ads/answer/6275312?hl=en |
| Productos no aptos | Política, pausado o sin stock | Campañas > Productos > Diagnóstico; columna "Incidencias" | https://support.google.com/google-ads/answer/12097493?hl=en |
| Productos no incluidos en ninguna campaña | Exclusión por grupo de listado o filtro de inventario | Diagnóstico > "No hay campañas anunciando este producto" | https://support.google.com/google-ads/answer/12097493?hl=en |
| Campaña Shopping y PMax con los mismos productos | Decide el Ad Rank | Comparar listados de productos entre campañas | https://support.google.com/google-ads/answer/13975266?hl=en |
| Interacción de PMax con otras campañas | Gana la campaña con mayor Ad Rank; una palabra clave exacta de Search tiene preferencia sobre PMax | Informe de canal de PMax | https://support.google.com/google-ads/answer/13810170?hl=en |
| Prioridad de campaña Shopping estándar | Baja por defecto; Alta gana aunque puje menos | Ajustes de campaña Shopping. API: `campaign.shopping_setting.campaign_priority` | https://support.google.com/google-ads/answer/6275296?hl=en |
| Etiquetas personalizadas | 1-100 caracteres; 1.000 valores únicos por atributo | Grupos de listado por etiqueta | https://support.google.com/google-ads/answer/6275295?hl=en |
| Requisitos de campaña Shopping | Cuenta vinculada y productos en el feed; no se puede cambiar el Merchant Center tras crear | Ajustes de campaña | https://support.google.com/google-ads/answer/3455481?hl=en |

## Requisitos legales en la UE (política de requisitos legales)
### Cómo funciona
- El anunciante debe cumplir las leyes de cada zona a la que dirige anuncios, además de las políticas de Google; es su responsabilidad investigarlas.
- En UE y Reino Unido puede aplicar la Directiva de servicios de comunicación audiovisual (anuncios reconocibles como tales, sin tabaco, restricciones de alcohol y medicamentos con receta, protección de menores).
- Sanciones comerciales y retirada de contenido por requerimiento legal pueden causar rechazos.
- Las infracciones de ley local pueden tratarse como flagrantes en casos limitados y suspender la cuenta.
- Google no lista otros controles legales de la web de destino en Alemania o España (el aviso legal no figura en esta política).
### Comprobaciones de auditoría
| Qué mirar | Regla o umbral oficial | Cómo se detecta | Fuente |
|---|---|---|---|
| Cumplimiento legal local del sector anunciado | Responsabilidad del anunciante en cada zona de segmentación | Revisión del sector y la ubicación de segmentación | https://support.google.com/adspolicy/answer/6023676?hl=en |
| Cambios de política (sept. 2026) | Se añaden códigos de autorregulación de otros países; la UE no figura | Registro de cambios de la política | https://support.google.com/adspolicy/answer/17597473?hl=en-IE |

## Cambios recientes
- 2026 (por fases, desde marzo): Lookalike de Demand Gen pasa a modo sugerencia; se puede optar por mantener el comportamiento anterior. https://support.google.com/google-ads/answer/16902001?hl=en
- 1-04-2026: la API de Google Ads rechaza Customer Match (`CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE`) salvo proyectos con actividad entre 1-10-2025 y 31-03-2026; usar Data Manager API. https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/customer-match/get-started
- 21-07-2026: no se podrán apelar en la cuenta decisiones de política de más de 6 meses. https://support.google.com/adspolicy/answer/9338593?hl=en
- Febrero 2026 y febrero 2027: sin creación nueva de anuncios solo de llamada y fin de impresiones de los existentes. https://support.google.com/google-ads/answer/16619010?hl=en
- Ad Rank decide entre Shopping estándar y PMax con los mismos productos (sin prioridad automática de PMax). https://support.google.com/google-ads/answer/13975266?hl=en
- Septiembre 2026: actualización de la política de requisitos legales (códigos de autorregulación de varios países). https://support.google.com/adspolicy/answer/17597473?hl=en-IE
- 1-08-2025 y 1-09-2025: la política de teléfono no verificado se extiende a recursos de mensaje. https://support.google.com/adspolicy/answer/16333090?hl=en
- 7-04-2025: fin de la pertenencia infinita en Customer Match. https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/customer-match/get-started
- 1-02-2024 y marzo de 2024: mínimo de 100 usuarios para listas de clientes; consentimiento obligatorio (`ad_user_data`, `ad_personalization`) en subidas del EEE. https://support.google.com/google-ads/answer/2472738?hl=en · https://support.google.com/google-ads/answer/14009343?hl=en
