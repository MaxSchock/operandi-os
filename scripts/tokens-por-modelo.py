#!/usr/bin/env python3
"""Tokens gastados por modelo y por sesion en un dia, leidos de los diarios ~/.claude/projects/*/*.jsonl.
Uso: python3 scripts/tokens-por-modelo.py [AAAA-MM-DD]   (por defecto hoy)
Sirve para medir la regla de reparto de modelos (Fable orquesta, sonnet/opus ejecutan). 15-10-2026."""
import json, glob, os, sys, collections, datetime
hoy = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
por_modelo = collections.defaultdict(lambda: collections.Counter())
por_sesion = collections.defaultdict(lambda: collections.Counter())
sesion_modelo = {}
sub = collections.Counter()
for f in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')) + glob.glob(os.path.expanduser('~/.claude/projects/*/*/subagents/*.jsonl')):
    if datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat() < hoy:
        continue
    es_sub = '/subagents/' in f
    with open(f, encoding='utf-8', errors='ignore') as fh:
        for linea in fh:
            if '"usage"' not in linea or not linea.startswith('{'):
                continue
            try: e = json.loads(linea)
            except Exception: continue
            if not (e.get('timestamp','') or '').startswith(hoy): continue
            m = e.get('message') or {}
            u = m.get('usage'); mod = m.get('model')
            if not u or not mod: continue
            c = por_modelo[mod]
            c['out'] += u.get('output_tokens',0); c['in'] += u.get('input_tokens',0)
            c['cache_r'] += u.get('cache_read_input_tokens',0); c['cache_w'] += u.get('cache_creation_input_tokens',0); c['turnos'] += 1
            s = e.get('sessionId','?')[:8] + ('*sub' if es_sub else '')
            por_sesion[s]['out'] += u.get('output_tokens',0); por_sesion[s]['cache_w'] += u.get('cache_creation_input_tokens',0); por_sesion[s]['turnos'] += 1
            sesion_modelo[s] = mod
            if es_sub: sub[mod] += u.get('output_tokens',0)
print(f"== {hoy} por modelo (tokens)")
print(f"{'modelo':34} {'turnos':>7} {'salida':>10} {'entrada':>9} {'cache esc':>11} {'cache lec':>12}")
for mod, c in sorted(por_modelo.items(), key=lambda x: -x[1]['out']):
    print(f"{mod:34} {c['turnos']:7} {c['out']:10,} {c['in']:9,} {c['cache_w']:11,} {c['cache_r']:12,}")
print("\n== salida de subagentes por modelo:", dict(sub))
print("\n== sesiones con mas salida")
for s, c in sorted(por_sesion.items(), key=lambda x: -x[1]['out'])[:14]:
    print(f"{s:14} {sesion_modelo[s]:30} turnos {c['turnos']:5} salida {c['out']:9,} cache esc {c['cache_w']:11,}")
