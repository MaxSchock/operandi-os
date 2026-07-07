# Anti-patrones

Errores que simulan análisis sin producirlo. Si detectas alguno, párate y corrige.

---

## Sesgos de ancla (Fase 0)

### Bypass de Fase 0
**Síntoma:** saltar directamente a los sombreros sin romper el ancla.
**Corrección:** la divergencia desde el ancla genera variantes del ancla, no alternativas reales. Siempre ejecutar los 4 movimientos.

### Re-formulación cosmética
**Síntoma:** reescribir el problema cambiando palabras pero manteniendo la solución implícita. "¿Cómo implemento X?" se reescribe como "¿Cuál es la mejor forma de implementar X?".
**Corrección:** la re-formulación pura elimina TODA referencia al enfoque. Solo queda: objetivo + restricciones.

### Steel-man débil
**Síntoma:** el argumento a favor del opuesto es una caricatura fácil de tumbar.
**Test:** ¿alguien inteligente que defendiera esa posición se sentiría representado por tu steel-man? Si no, es un straw-man disfrazado.

### Ancla del modelo
**Síntoma:** no es el usuario quien viene anclado, sino que Claude ha convergido prematuramente en su primera interpretación.
**Test:** ¿la primera idea que te vino a la cabeza sigue siendo la que recomiendas tras 5 alternativas? Si sí, puede ser correcta o puede ser ancla propia.

---

## Sesgos de sombreros

### Contaminación cruzada
**Síntoma:** "...pero por otro lado podría ser bueno porque..." dentro del Negro. O "...aunque tiene el riesgo de..." dentro del Amarillo.
**Corrección:** eliminar la frase contaminada. Cada sombrero es monolítico.

### Negro diluido por amabilidad
**Síntoma:** riesgos en condicional suave ("podría ser que quizá...") o genéricos ("hay riesgo de que el mercado cambie").
**Corrección:** riesgos concretos, plausibles, enunciados con seguridad. "Esto romperá X cuando ocurra Y" es válido. "Podría haber complicaciones" no lo es.

### Rojo justificado
**Síntoma:** "siento desconfianza **porque** los plazos son muy ajustados".
**Corrección:** corta en "siento desconfianza". Punto. La razón pertenece al Negro o al Blanco.

### Verde repetitivo
**Síntoma:** las "alternativas" son variantes mínimas del plan original.
**Test:** ¿el coste y el resultado de cada alternativa son distintos? Si no, son la misma.

### Falsa divergencia
**Síntoma:** 5 alternativas que son la misma idea con palabras distintas. El formato está, el contenido no.
**Corrección:** cambiar de marco divergente y forzar 2 más desde un ángulo completamente distinto.

### Marco trofeo
**Síntoma:** usar TRIZ o Random concept "porque queda sofisticado" cuando el problema pedía Inversión simple.
**Test:** ¿elegiste el marco por el problema o por el marco?

### Convergencia disfrazada
**Síntoma:** presentar alternativas en un orden que empuja hacia tu favorita.
**Corrección:** mezclar el orden de presentación. La matriz de convergencia decide, no la secuencia.

### Pseudo-criterios
**Síntoma:** criterios vagos como "encaja con la marca" o "es más elegante" que no se pueden puntuar honestamente.
**Test:** ¿puedes asignar Alto/Medio/Bajo con justificación verificable?

### Azul de cierre indeciso
**Síntoma:** la síntesis ofrece "tres caminos posibles" y deja la decisión al usuario.
**Corrección:** UNA recomendación. Si no puedes elegir, di qué dato te falta.

### Blanco con suposiciones
**Síntoma:** en hechos verificados aparecen frases como "el mercado de X está creciendo" sin fuente.
**Corrección:** todo lo no verificable va en "hechos creídos" o "vacíos de información".

### Análisis inflado
**Síntoma:** 30 párrafos que nadie va a leer.
**Corrección:** cada sombrero en 5-12 líneas. La síntesis puede ser más larga (hasta 20 líneas).

### Sobreactivación
**Síntoma:** lanzar el ritual completo para una pregunta que se responde en 3 líneas.
**Corrección:** si el problema cabe en una respuesta directa, no uses la skill.
