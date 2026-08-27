# Cobertura: qué reglas duelen, cuáles sobran, cuáles faltan

## Resumen

De los 62 ficheros de `memory/` no enlazados en `MEMORY.md`, **15 tienen incidentes reales posteriores a su fecha de creación** (mtime, no hay campo `modified` en el frontmatter) — es decir, siguieron fallando aunque la regla ya estaba escrita, solo que invisible. El caso más caro: `feedback_explicit_step_by_step.md` (creada 02-06, 11 incidentes posteriores) y el par duplicado `feedback_tier_2_no_ask.md` / `feedback_no_pidas_permiso_avanza.md` (≈10 incidentes posteriores entre ambos, mismo hueco escrito dos veces). De reglas escritas y nunca violadas desde su creación (P2), 13 parecen genuinamente cumplidas y **7 son candidatas a archivar** por estar resueltas o referirse a algo que ya no aplica. El hueco sin regla más grande y confirmado es "recall de estado ya establecido" (26 incidentes, 7 de gravedad alta, ninguna regla dedicada en 123 ficheros). Los 106 `OTROS` no esconden un patrón nuevo de 8+: el único clúster que llega a 8 (repaso de canales, 7-8 casos) ya tiene dos reglas escritas y enlazadas — es reincidencia, no un hueco.

## P1 · Reglas invisibles que están costando dinero

Incidentes contados por `fecha > mtime` del fichero, con `regla_implicada`/`que_hizo_mal_claude`/`cita_max` coincidiendo semánticamente con el tema del fichero.

| Regla (fichero) | Creada | Inc. posteriores | Grav. máx | Ejemplo |
|---|---|---:|---|---|
| `feedback_explicit_step_by_step.md` | 02-06 | 11 | media | 27-08: "verificar el tipo de cuenta/entorno real antes de dar instrucciones paso a paso" |
| `feedback_tier_2_no_ask.md` + `feedback_no_pidas_permiso_avanza.md` (mismo hueco, dos ficheros) | 25-05 / 08-06 | ~10 (unión) | media | 26-08: "no preguntar cuándo la respuesta obvia es hacer todo; ejecutar sin pedir permiso" |
| `feedback_plain_spanish_no_jargon.md` | 29-05 | 6 | media | 20-07: "hablar en castellano natural, sin jerga técnica anglo" (falkenlead) |
| `feedback_estimaciones_en_horas_claude.md` | 15-07 | 4 | **alta** | 26-08: "contrastar cualquier estimación de horas contra el ledger de horas reales antes de presentarla" |
| `feedback_plan_mode_recipe.md` | 03-07 | 4 | **alta** | 26-08: "verificar que un prompt de plan mode incluye todo el feedback reciente del cliente antes de darlo por bueno" |
| `feedback_replicate_lora_two_step_pipeline.md` | 28-05 | 3 | media | 19-08: "al traducir un documento completo, traducir/rehacer también los elementos visuales" (identidad Madeleine) |
| `feedback_editable_deliverables_to_drive.md` | 29-06 | 3 | media | 26-08: "verificar visualmente cada diapositiva de un deck de cliente antes de entregarlo" |
| `feedback_verify_code_before_explaining_system_behavior.md` | 10-06 | 3 | media | 24-08: "verificar el diseño real del sistema contra el código/configuración antes de explicar su comportamiento" |
| `feedback_powershell_wsl_entry.md` | 03-06 | 2 | media | 24-06: "buscar capturas de pantalla en la carpeta de Screenshots sin pedirlas, Max trabaja en PowerShell" |
| `feedback_no_inferir_social_context.md` | 05-06 | 2 | media | 17-06: "decidir Du/Sie por cómo se dirige el cliente, no por inferencia de género" |
| `feedback_kaps_reconcile_session_learnings.md` | 03-06 | 2 | media | 03-08: "mantener el estado comercial real de los clientes (activo/parado)" — el propio hueco de Kaps |
| `feedback_client_deliverable_design.md` | 26-05 | 1 | media | 16-06: "dar una valoración crítica real de la calidad visual de un deliverable" |
| `feedback_no_desktop_clutter.md` | 28-05 | 1 | media | 26-08: "verificar la necesidad real de cada pieza de infraestructura antes de incluirla en el plan" |
| `feedback_no_em_dashes_human_typos.md` | 28-05 | 1 | baja | 12-06: "nunca usar em-dashes en contenido generado" (nota: el em-dash ya está en CLAUDE.md global; la parte de typos-humanizados de este fichero no está en ningún sitio más) |

**Caso aparte, más urgente que cualquiera de la tabla**: `project-kaps-parado-revision-septiembre.md` se creó el 03-08, el mismo día del incidente que lo motivó ("no sabía que se había dejado de trabajar con Kaps"). No hay incidente *posterior* que lo confirme porque aún no ha llegado el momento de revisión — pero es exactamente el tipo de fichero que el gate de invisibilidad haría fallar otra vez: **septiembre está a una semana** y el fichero no está enlazado en `MEMORY.md`.

## P2 · Reglas muertas

### Se cumplen (no tocar)

- `feedback_screenshot_folder_convention.md` + `reference_screenshots_location.md`: 0 incidentes tras el 10-06, con varios antes. Caso de éxito real, no falsa calma — la convención de leer capturas de la carpeta se interiorizó.
- `feedback_mc_alias_list_leaks_keys.md`, `feedback_never_source_env_secrets.md`: 0 en todo el periodo. Coherente con el hallazgo de la Sesión 1 (secretos es la única categoría con reincidencia cero, sostenida por el instinct que se dispara solo).
- `feedback_isolate_pending_step_when_user_resumes.md`, `feedback_verify_cancellation_took_effect.md`, `feedback_no_outreach_to_referred_contacts.md`, `feedback_always_name_the_channel.md`, `feedback_env_placeholders.md`, `feedback_separate_n8n_instances_per_company.md`, `feedback_retired_model_and_latent_failures_at_volume.md`, `feedback_deliverables_to_client_drive.md` (la variante no-editable): 0 posteriores. Situaciones específicas y de baja frecuencia; sin evidencia de que se sigan rompiendo.
- `feedback_structural_variety_archetypes_work.md`: no es una regla correctiva sino un patrón positivo documentado ("esto funcionó"); no le corresponde tener incidentes.
- `feedback_linkedin_reply_no_name_address.md`: 0 posteriores, y además ahora lo aplica código en producción (`app/pipeline/comments.py`, ver `deuda_content_engine_comment_responder.md`), no el juicio de Claude en cada turno.

### Obsoletas (archivar)

| Fichero | Por qué |
|---|---|
| `deuda_content_engine_comment_responder.md` | Su propia `description` dice "RESUELTO 2026-06-24"; lo de abajo es roadmap histórico. |
| `project_strategist_tool_results_audit_regression.md` | Su propia `description` dice "Bug resuelto ... Validado E2E". |
| `project_kisult_gcp_service_account.md` (29-05) | Reemplazado explícitamente por `reference_kisult_drive_oauth.md` (11-06), que dice literalmente "Reemplaza el 'pending service account' del 29.05". |
| `reference_kaps_step4b_refactor_routines.md` (08-06) | Rutinas de vigilancia de un cliente que `project-kaps-parado-revision-septiembre.md` confirma parado desde junio; monitorizar algo inactivo no aporta. |
| `reference_hemmersbach_pipeline_state.md` (09-06) | Snapshot del Workflow-A de hace 2.5 meses; los incidentes de Hemmersbach de agosto (fixes 24-27/08, migración de prompts, etc.) lo dejaron desactualizado. `reference_hemmersbach_workflow_anatomy.md` (17-06) es la fuente de verdad más reciente y aun así también convendría revisarla contra el estado de hoy. |
| `deuda_ingolf_new_reference_photos.md` (17-06) | Más de dos meses sin resolución ni mención de que llegaran las fotos; Ingolf sigue apareciendo en incidentes de calidad de contenido pero ninguno toca el gate de `identity_reset` en concreto. Requiere una decisión de Max, no auto-archivar. |
| `deuda_strategist_mcp_deferred.md` (04-06) | Describe una latencia intermitente y "no bloqueante" en un servicio que ya está en producción estable; bajo valor de mantenerlo como debda activa. |

## P3 · Fallos sin regla escrita

| Patrón | Nº incidentes | Gravedad | Formulación propuesta |
|---|---:|---|---|
| Recall de estado/decisiones ya establecidas (sesión actual, sesión anterior, o entre canales) antes de re-preguntar, re-diagnosticar o re-proponer | 26 | 17 media, 7 alta, 2 baja | "Antes de pedir un dato, negar conocimiento de algo ya construido, o proponer de nuevo una decisión: buscar primero en el historial de la sesión actual, en sesiones previas del mismo cliente y en `working-memory.md`. Si ya se dijo o decidió, se aplica sin volver a preguntar." |

Es el único de los 14 patrones raíz sin ningún fichero de memoria dedicado (confirmado cruzando los 26 incidentes contra los 123 ficheros: hay reglas puntuales que rozan el tema — `feedback-revisar-sesiones-abiertas-al-arrancar.md`, `feedback-releer-antes-de-escribir-no-revertir-de-memoria.md`, `feedback_isolate_pending_step_when_user_resumes.md` — pero ninguna cubre el principio general "lo ya establecido no se re-pregunta ni se re-diagnostica"). `NO-PUEDO-SIN-MIRAR` (26 incidentes, 5 alta) tenía el mismo problema hasta hoy: `feedback-no-decir-que-no-puedo-sin-mirar.md` se creó y se enlazó el mismo 27-08, así que ya no es un hueco pero explica por qué esa categoría entera (05-12 a 27-08) queda fuera de la tabla P1.

## P4 · Los 106 sin patrón

No aparece un patrón nuevo de 8 o más incidentes. El clúster más grande dentro de `OTROS` es "repaso de canales al arrancar/cerrar sesión" (7-8 casos: 18-05, 05-08, 27-08 ×2, 17-08, 23-07 ×2), pero **no es un hueco**: ya tiene dos reglas escritas y enlazadas (`feedback-arrancar-sesion-con-repaso-de-canales.md`, `feedback-revisar-sesiones-abiertas-al-arrancar.md`). Su presencia en `OTROS` es un fallo del clasificador automático, no un patrón sin cubrir — y es otro caso de reincidencia de regla ya escrita, coherente con P1.

Otros clústeres explorados (diagnóstico sin datos, cierre de sesión, camino real vs. adyacente, mezcla de contexto entre clientes, solución simple vs. custom, fallo silencioso) se quedan todos por debajo de 8 casos y, además, cada uno ya cae dentro de una categoría raíz existente (`VERIFICAR-ANTES-AFIRMAR`, `ATRIBUCION-ENTIDAD`, `ALCANCE-DISCIPLINA`). Veredicto: los 106 `OTROS` son mayoritariamente casos únicos irrepetibles, tal como adelantaba la Sesión 1.
