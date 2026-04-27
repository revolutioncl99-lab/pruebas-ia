# Editor de Video - RevoCL

**Estado:** Estructura base inicializada (2026-04-27)

## Activado

✓ Graphify (análisis de código AST para reducir tokens)  
✓ GRAPH_REPORT.md (mapeo de god nodes)  
✓ Estructura src/ (config, timeline, video_processor)  
✓ tools/ (scripts de validación)  
✓ requirements.txt  

## Flujo de trabajo

```bash
# Validar código
python tools/validate.py

# Actualizar grafo tras cambios
python graphify.py update .

# Consultar grafo (ej: buscar timeline)
python graphify.py query "timeline" --budget 400
```

## Estructura

```
src/
├── config.py       # Config global y preferencias
├── timeline.py     # Timeline, tracks, clips
└── video_processor.py  # Encode, trim, render
tools/
└── validate.py     # Validar integridad
```

## Next Steps

1. Implementar UI (frontend)
2. Sistema de almacenamiento (save/load proyectos)
3. Efectos y transiciones
4. Plugins

---

**Lee CLAUDE.md para reglas de desarrollo.**
