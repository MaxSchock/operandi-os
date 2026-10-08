# H1 — Checklist verde/rojo (plantilla rellenable)

> Copia este bloque al inicio de cada sesión I.A.S. Marca cada casilla solo cuando la respuesta sea **concreta, accionable y verificable**. Una sola casilla sin marcar = gate rojo = no se pasa a fase A.

---

## Activo

- Nombre del activo:
- Slug (kebab-case, sin tildes):
- Fecha (YYYY-MM-DD):

---

## Dimensión 1 — Objetivo concreto del activo

- [ ] **¿Qué activo concreto sale?**
  Pista verde: nombra el entregable + soporte (Word, HTML, slide, código). Sin "algo sobre".
  Respuesta:

- [ ] **¿Para qué se usa y quién lo recibe?**
  Pista verde: persona o rol concreto + contexto de uso (reunión, publicación, pase interno).
  Respuesta:

- [ ] **¿Cuándo se entrega?**
  Pista verde: fecha y franja horaria. "Cuanto antes" no cuenta.
  Respuesta:

---

## Dimensión 2 — Inputs disponibles

- [ ] **¿Qué materiales tengo ahora mismo?**
  Pista verde: lista de archivos con path o URL. Si no puedes apuntar al archivo en 30 segundos, no existe.
  Respuesta:

- [ ] **¿Qué materiales me faltan?**
  Pista verde: lista corta + plan de obtención (lo busco yo / lo pido / la sesión se aborta).
  Respuesta:

- [ ] **¿Algún input está roto, desactualizado o sin permisos?**
  Pista verde: marcado explícito. Mejor "transcripción incompleta, falta minuto 22 al final" que "creo que está bien".
  Respuesta:

---

## Dimensión 3 — Restricciones

- [ ] **Tiempo:** ¿cuánto tiempo de sesión y cuánto tiempo del agente?
  Pista verde: "90 min de sesión, 15 min de agente máximo por iteración".
  Respuesta:

- [ ] **Audiencia:** ¿perfil concreto de quien lee?
  Pista verde: rol + nivel técnico + contexto cultural si aplica. No "audiencia general".
  Respuesta:

- [ ] **Idioma y registro:** ¿idioma + tono?
  Pista verde: "español neutro, sin anglicismos, profesional sobrio".
  Respuesta:

- [ ] **Restricciones legales / compliance:** ¿hay alguna?
  Pista verde: marcar EU AI Act, RGPD, NDA, secreto comercial si aplica. "Ninguna" también es respuesta válida.
  Respuesta:

---

## Dimensión 4 — Formato del output esperado

- [ ] **Estructura del entregable:**
  Pista verde: lista numerada de secciones fijas con tamaño aproximado por sección.
  Respuesta:

- [ ] **Elementos obligatorios:** tablas, gráficos, citas, footer, header, branding.
  Pista verde: lista cerrada. Si dudas, vuelve a la dimensión 1.
  Respuesta:

- [ ] **Soporte y entrega:** ¿dónde queda el archivo final?
  Pista verde: path local + si lleva HTML twin + si va a un destinatario externo.
  Respuesta:

---

## Dimensión 5 — Criterios de aceptación

- [ ] **¿Cuándo está terminado?**
  Pista verde: lista de condiciones binarias verificables por un tercero. "Cuando me guste" no entra.
  Respuesta:

- [ ] **¿Cuándo NO está terminado, aunque parezca?**
  Pista verde: 1–3 fallos típicos que harían rechazar el entregable. Útil para que el agente no se autoengañe.
  Respuesta:

- [ ] **¿Hay criterios de calidad medibles?**
  Pista verde: número mínimo de secciones, longitud máxima, datos cuantificados, citas con fuente.
  Respuesta:

---

## Dimensión 6 — Decisiones congeladas

- [ ] **He listado las decisiones que NO quiero reabrir.**
  Pista verde: ver patrón completo en `h1-decisiones-congeladas.md`. Mínimo 3 decisiones, formato `clave: valor | razón: línea`.
  Respuesta:

- [ ] **He cerrado las preferencias disfrazadas.**
  Pista verde: ningún "preferiblemente", "idealmente", "si te sale". O decisión tomada o no entra al bloque.
  Respuesta:

- [ ] **He añadido la cláusula de bloqueo final al bloque.**
  Pista verde: incluye literalmente "Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas."
  Respuesta:

---

## Gate

- [ ] **Las 6 dimensiones están en verde** (todas las casillas marcadas, todas las respuestas pasan el test de "verificable por un tercero").

Si esta última casilla está marcada, se pasa a fase **A**.
Si no, vuelve a la dimensión que está roja y trabájala antes de seguir.

---

## Notas operativas

- No marques casillas a la ligera para "ir tirando". El gate falso es peor que el gate honesto.
- Si una dimensión sale roja tres veces seguidas, la tarea probablemente está mal escopada. Pártela en dos.
- Este checklist se archiva como parte del activo de salida (sección "Decisiones congeladas" del fichero en `outputs/diarios/`).
