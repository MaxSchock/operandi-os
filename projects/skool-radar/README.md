# skool-radar

Lee las comunidades de Skool de Max (posts, hilos, classroom y vídeos) y deja el
material listo para filtrarlo contra sus frentes reales de trabajo.

Skool no tiene API pública. Esto entra como entra un navegador: Playwright con la
sesión de Max, leyendo el JSON que la propia web se sirve (`__NEXT_DATA__`) más el
endpoint interno de comentarios. **Solo lee.** No publica, no comenta, no vota, no
manda mensajes.

## Puesta en marcha

```bash
python3 login.py                 # abre una ventana, Max entra en Skool, se guarda la sesión
python3 collect.py --list        # comunidades de la cuenta
```

## Uso

```bash
python3 collect.py --community <slug> --pages 5 --comments --classroom
python3 video.py --limit 5                  # analiza los vídeos pendientes
python3 review.py --days 7                  # vuelca lo nuevo a out/<fecha>-material.md
```

Luego, en una sesión de Claude Code: leer `out/<fecha>-material.md` contra
`interests.md` y escribir el digest.

## Cómo funciona

| Pieza | Qué hace |
|---|---|
| `login.py` | Chromium visible por WSLg. Guarda `state/skool-session.json` (chmod 600, gitignored). |
| `lib/skool.py` | Lector: feed paginado, comentarios, classroom. Todo desde el JSON de la página. |
| `lib/db.py` | SQLite en `data/radar.db`. Dedupe por el id de Skool: repetir una corrida no duplica nada. |
| `collect.py` | Recorre el feed hasta toparse con lo ya visto y para. |
| `video.py` | YouTube va directo a Gemini (ve la pantalla, no solo el audio). El resto se baja a 480p, se sube a ki-prod-01 y se borra al terminar. |
| `review.py` | Exporta lo no reportado a markdown, con hilos y notas de vídeo. |
| `interests.md` | El criterio de filtrado. Se ajusta aquí, no en el código. |

## Límites conocidos

- **Hilos largos se muestrean, no se agotan.** La API interna corta en 30 comentarios
  por bloque y no expone cursor que funcione: la propia web de Skool solo pide dos
  bloques (destacados y últimos). Eso es lo que se guarda. Para un hilo de 200
  comentarios se ven ~80, no los 200.
- **La sesión caduca.** Cuando `collect.py` diga que la sesión es anónima, hay que
  volver a pasar por `login.py`.
- **Esto raspa una web sin API.** Si Skool cambia la estructura del JSON, el colector
  se queda callado devolviendo cero. Por eso cada corrida imprime cuántos posts nuevos
  trajo: un cero seguido de otro cero no es una comunidad tranquila, es una avería.
- **Vídeo con Gemini cuesta dinero.** Un vídeo de 14 minutos son varios cientos de
  miles de tokens. Por eso `video.py` va por lotes (`--limit`) y salta lo que pase
  de `--max-min`.

## Legalidad y uso

Contenido de comunidades donde Max es miembro, leído para su propio consumo. No se
republica, no se comparte y no sale de su disco.
