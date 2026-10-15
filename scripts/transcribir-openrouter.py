# Compatibilidad: antes transcribia solo .ogg; ahora delega en transcribir-medios.py (audio y video, con troceo).
# Uso igual que antes: python3 -I transcribir-openrouter.py <carpeta con audios>
# Copia del script original: ~/.claude/backups/arnes-20261015/transcribir-openrouter.py.antes-20261015
import os, sys
destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcribir-medios.py")
os.execv(sys.executable, [sys.executable, "-I", destino] + sys.argv[1:])
