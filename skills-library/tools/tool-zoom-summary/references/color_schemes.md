# Color Schemes — Zoom Meeting Summaries

Catálogo de 4 esquemas neutros listos para usar. El operador asigna cada esquema al tipo de reunión recurrente desde `brand-context/meeting-types.md`. Si no hay mapping configurado, la skill pregunta al usuario qué esquema usar.

## Detection Rules

El mapping entre el campo `topic` de Zoom y el esquema lo define el operador en `brand-context/meeting-types.md`. Ejemplo de archivo de mapping:

```yaml
# brand-context/meeting-types.md
meeting_types:
  - id: weekly-call
    match: ["weekly", "all-hands"]          # patterns case-insensitive en el topic
    scheme: warm_professional
    folder: meetings/weekly-calls
    filename_prefix: weekly-call
    badge: "📞 Weekly — {weekday} {time}"
    emojis: ["📞", "💡", "🔧", "🎯", "📚", "💬"]
```

Si no hay archivo de mapping, la skill pide al usuario que elija esquema y carpeta cuando detecta un tipo nuevo.

---

## 1. Warm Professional (Bronze/Gold)

Tono cálido, editorial. Recomendado para clases narrativas, charlas casuales, sesiones de comunidad, contenido conversacional.

```css
:root {
  --bg: #171614;
  --bg2: #1E1D1A;
  --bg3: #252420;
  --accent: #C4956A;
  --accent2: #D4A87A;
  --accent-dim: rgba(196,149,106,0.12);
  --accent-border: rgba(196,149,106,0.15);
  --text: #F0EBE1;
  --muted: #8A8174;
  --green: #4CAF50;
  --red: #E57373;
  --blue: #64B5F6;
  --purple: #B39DDB;
  --orange: #FFB74D;
  --cyan: #4DD0E1;
  --radius: 16px;
}
```

- **Badge dot color**: var(--green) — sugerido
- **Emojis sugeridos**: ☕ 💡 🔧 🎯 📚 💬

---

## 2. Business Clean (Green)

Tono limpio, corporativo. Recomendado para reuniones de gestión, financieras, métricas, status meetings.

```css
:root {
  --bg: #141816;
  --bg2: #1A201D;
  --bg3: #202823;
  --accent: #4CAF50;
  --accent2: #66BB6A;
  --accent-dim: rgba(76,175,80,0.12);
  --accent-border: rgba(76,175,80,0.15);
  --text: #E8F0EA;
  --muted: #7A8A7D;
  --green: #4CAF50;
  --red: #E57373;
  --blue: #64B5F6;
  --purple: #B39DDB;
  --orange: #FFB74D;
  --cyan: #4DD0E1;
  --radius: 16px;
}
```

- **Badge dot color**: var(--accent)
- **Emojis sugeridos**: 💼 📊 🤝 📈 🏗️ 💬

---

## 3. Techy Modern (Orange + Cyan)

Tono técnico, contemporáneo. Recomendado para sesiones de código, demos técnicas, sprints de producto, talleres dev.

```css
:root {
  --bg: #151518;
  --bg2: #1B1B20;
  --bg3: #222228;
  --accent: #FFB74D;
  --accent2: #FFCA80;
  --accent-dim: rgba(255,183,77,0.12);
  --accent-border: rgba(255,183,77,0.15);
  --text: #F0ECE8;
  --muted: #8A8480;
  --green: #4CAF50;
  --red: #E57373;
  --blue: #64B5F6;
  --purple: #B39DDB;
  --orange: #FFB74D;
  --cyan: #4DD0E1;
  --radius: 16px;
}
```

Special: usar `--cyan` (#4DD0E1) como acento secundario para elementos técnicos:
- Code blocks background: `rgba(77,208,225,0.08)`
- Code block borders: `rgba(77,208,225,0.15)`
- Tech badges y tool tags
- Terminal/command references

- **Badge dot color**: var(--cyan)
- **Emojis sugeridos**: 🔥 ⚡ 🛠️ 🚀 💻 💬

---

## 4. AI Future (Electric Blue/Indigo)

Tono futurista, vanguardista. Recomendado para sesiones sobre IA, automatización, herramientas emergentes, prototipos.

```css
:root {
  --bg: #141420;
  --bg2: #1A1A2A;
  --bg3: #202032;
  --accent: #7B6FF0;
  --accent2: #9B8FF8;
  --accent-dim: rgba(123,111,240,0.12);
  --accent-border: rgba(123,111,240,0.15);
  --text: #ECEAF8;
  --muted: #7A7890;
  --green: #4CAF50;
  --red: #E57373;
  --blue: #64B5F6;
  --purple: #B39DDB;
  --orange: #FFB74D;
  --cyan: #4DD0E1;
  --radius: 16px;
}
```

Special: usar `--cyan` como acento secundario para:
- Tool badges y platform tags
- Code/command references
- Tech highlight elements

- **Badge dot color**: var(--accent)
- **Emojis sugeridos**: 🤖 ⚡ 🛠️ 🚀 🎬 💬

---

## Shared across all schemes

- Font: `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
- Google Fonts: `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap`
- Border radius: 16px throughout
- Transitions: all 0.3s
- **Footer y branding**: leer desde `brand-context/` del operador. Nunca hardcodear marca, nombre de producto o URL en el HTML.
