# HTML Template Guide — Zoom Meeting Summaries

## Critical Rule
All accent-colored values in CSS MUST use CSS variables, not hardcoded rgba values.
Use `var(--accent)`, `var(--accent-dim)`, `var(--accent-border)` etc. from color_schemes.md.
Exception: semantic colors (--green, --red, --blue, --purple) stay fixed across all schemes.

## HTML Structure

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{MEETING_NAME}} — {{DATE_DISPLAY}}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>/* CSS variables from color_schemes.md + full styles below */</style>
</head>
<body>
  <!-- 1. HERO -->
  <div class="hero">...</div>

  <!-- 2. NAV TIMELINE (sticky) -->
  <nav class="nav-timeline" id="nav">...</nav>

  <!-- 3. TOPIC SECTIONS (one per identified topic) -->
  <div class="section" id="s1">...</div>
  <div class="section" id="s2">...</div>
  <!-- ... up to s8 -->

  <!-- 4. RESOURCES SECTION (URLs from chat) -->
  <div class="section" id="resources">...</div>

  <!-- 5. MINI-SUMMARY SECTION (copyable for School) -->
  <div class="section" id="mini">...</div>

  <!-- 6. FOOTER -->
  <div class="footer">...</div>

  <script>/* Interactions: fade-in, nav scroll, toggle TPs */</script>
</body>
</html>
```

## Section Templates

### HERO
```html
<div class="hero">
  <div class="hero-badge">
    <span class="dot"></span>
    {{BADGE_TEXT}}
  </div>
  <h1>{{MEETING_TITLE}}</h1>
  <p class="subtitle">{{SUBTITLE_DESCRIPTION}}</p>
  <div class="meta">
    <span>📅 {{DATE_LONG}}</span>
    <span>⏱ {{DURATION}} min</span>
    <span>📋 {{TOPIC_COUNT}} temas</span>
    <span>👥 Edición #{{EDITION}}</span>
  </div>
</div>
```

### NAV TIMELINE
```html
<nav class="nav-timeline" id="nav">
  <div class="nav-item active" onclick="scrollTo_('s1')">
    <span class="nav-num">1</span> {{TOPIC_1_SHORT}}
  </div>
  <div class="nav-item" onclick="scrollTo_('s2')">
    <span class="nav-num">2</span> {{TOPIC_2_SHORT}}
  </div>
  <!-- ... -->
  <div class="nav-item" onclick="scrollTo_('resources')">
    <span class="nav-num">🔗</span> Recursos
  </div>
</nav>
```

### TOPIC SECTION
```html
<div class="section" id="s{{N}}">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-num">
        <span class="line"></span> TEMA {{N}}
        <span class="time-badge">⏱ {{MINUTES}} min</span>
      </div>
      <h2>{{EMOJI}} {{TOPIC_TITLE}}</h2>
      <p class="lead">{{TOPIC_SUMMARY}}</p>
    </div>

    <!-- Talking Points -->
    <div class="tp-list fade-in">
      <div class="tp" onclick="this.classList.toggle('open')">
        <div class="tp-icon">{{EMOJI}}</div>
        <div class="tp-content">
          <div class="tp-title">{{POINT_TITLE}}</div>
          <div class="tp-desc">{{POINT_BRIEF}}</div>
          <div class="tp-detail">
            <p>{{POINT_DETAIL}}</p>
            <!-- Optional quote -->
            <div class="tp-quote">{{NOTABLE_QUOTE}}</div>
            <!-- Optional timestamp link -->
            <a href="{{RECORDING_URL}}?t={{TIMESTAMP}}" class="ts-link" target="_blank">▶ {{HH:MM:SS}}</a>
          </div>
        </div>
      </div>
      <!-- More TPs... -->
    </div>
  </div>
</div>
```

### RESOURCES SECTION
```html
<div class="section" id="resources">
  <div class="container">
    <div class="section-header fade-in">
      <h2>🔗 Recursos Compartidos</h2>
      <p class="lead">Links y herramientas mencionados durante la sesión</p>
    </div>

    <div class="resource-grid fade-in">
      <!-- One card per resource group -->
      <div class="resource-card">
        <div class="resource-category">{{CATEGORY}}</div>
        <div class="resource-items">
          <a href="{{URL}}" target="_blank" class="resource-item">
            <span class="resource-icon">🔗</span>
            <div>
              <div class="resource-name">{{LINK_TITLE_OR_DOMAIN}}</div>
              <div class="resource-context">{{WHO_SHARED}} · {{CONTEXT}}</div>
            </div>
          </a>
          <!-- More items... -->
        </div>
      </div>
    </div>
  </div>
</div>
```

### MINI-SUMMARY (for School post)
```html
<div class="section" id="mini">
  <div class="container">
    <div class="mini-summary fade-in">
      <div class="mini-label">📋 Resumen para compartir</div>
      <div class="mini-content" id="copyable">
        <p>{{BULLET_1}}</p>
        <p>{{BULLET_2}}</p>
        <p>{{BULLET_3}}</p>
        <p>{{BULLET_4}}</p>
      </div>
      <button class="copy-btn" onclick="copyMini()">📋 Copiar resumen</button>
    </div>
  </div>
</div>
```

### FOOTER

El footer toma todos los datos del `brand-context/` del operador. NUNCA hardcodear marca, herramienta IA o URL en el HTML público.

```html
<div class="footer">
  <div class="container">
    <p style="color: var(--accent); font-weight: 700;">{{MEETING_NAME}} — {{BRAND_NAME}}</p>
    <p>{{DAY_NAME}} {{DATE_LONG}} · {{TIME}} ({{TIMEZONE}})</p>
    <p style="font-size: 12px;">{{BRAND_WEBSITE}}</p>
  </div>
</div>
```

Variables a resolver desde `brand-context/`:
- `{{BRAND_NAME}}` — `brand-context/identity.md` → `name`
- `{{BRAND_WEBSITE}}` — `brand-context/identity.md` → `website`
- `{{TIMEZONE}}` — `brand-context/identity.md` → `timezone` (ej. `Europe/Madrid`, `America/Mexico_City`)

Si alguna variable falta en `brand-context/`, omitir esa línea del footer (no inventar valores).

## Timestamp Link Format

Timestamps link to the **Loom video** (preferred) or Zoom share URL as fallback.

### Loom format (preferred — used when Loom URL is provided):
- Format: `LOOM_URL?t=XmYs` where X=minutes, Y=seconds
- Convert from total seconds: 635s → `?t=10m35s`, 90s → `?t=1m30s`, 45s → `?t=45s`
- Display: `▶ MM:SS`

```html
<a href="https://www.loom.com/share/abc123?t=10m35s" class="ts-link" target="_blank">▶ 10:35</a>
```

### Zoom format (fallback — when no Loom URL):
- Format: `ZOOM_SHARE_URL?t=SECONDS`

```html
<a href="https://us06web.zoom.us/rec/share/...?t=635" class="ts-link" target="_blank">▶ 10:35</a>
```

## VTT Parsing Rules

Zoom VTT format:
```
WEBVTT

1
00:00:01.440 --> 00:00:05.160
Speaker Name: Text content here

2
00:00:05.500 --> 00:00:08.200
Another Speaker: More text here
```

Parse into segments: `[{start_seconds, end_seconds, speaker, text}]`
- Split on double newline
- Extract timestamp: regex `(\d{2}):(\d{2}):(\d{2})\.\d{3}`
- Extract speaker: regex `^(.+?):\s` at start of text line
- Merge consecutive segments from same speaker within 5s gap

## Chat Parsing Rules

Zoom chat TXT format:
```
18:02:15 From  Alex Doe  to  Everyone:
	https://claude.ai
18:05:22 From  Maria Garcia  to  Everyone:
	Genial, gracias!
```

Parse into messages: `[{timestamp, sender, recipient, message}]`
- Timestamp line regex: `^(\d{2}:\d{2}:\d{2})\s+From\s+(.+?)\s+to\s+(.+?):$`
- Following indented lines = message content
- URL extraction: regex `https?://[^\s]+` from message content

## JavaScript (same for all schemes)

```javascript
// Smooth scroll
function scrollTo_(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Fade-in on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// Active nav on scroll
const sections = document.querySelectorAll('.section');
const navItems = document.querySelectorAll('.nav-item');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });
  navItems.forEach(item => {
    const target = item.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
    item.classList.toggle('active', target === current);
  });
});

// Copy mini-summary
function copyMini() {
  const text = document.getElementById('copyable').innerText;
  navigator.clipboard.writeText(text);
  const btn = document.querySelector('.copy-btn');
  btn.textContent = '✅ Copiado!';
  setTimeout(() => btn.textContent = '📋 Copiar resumen', 2000);
}
```

## Key CSS Classes Reference

All accent-colored properties use CSS variables. The full CSS from the reference template
should be adapted by replacing hardcoded `rgba(196,149,106,X)` values with:
- `rgba(196,149,106,0.08)` → `var(--accent-dim)`
- `rgba(196,149,106,0.15)` → `var(--accent-border)`
- `rgba(196,149,106,0.25)` → increase opacity variant of --accent-border
- `#C4956A` / `var(--accent)` stays as `var(--accent)`

For schemes that pair `--accent` with `--cyan` as secondary (Techy Modern, AI Future), code-related elements additionally use:
- Background: `rgba(77,208,225,0.08)`
- Border: `rgba(77,208,225,0.15)`
- Text: `var(--cyan)`
