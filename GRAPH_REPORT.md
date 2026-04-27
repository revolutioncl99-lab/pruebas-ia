# GRAPH_REPORT.md - Editor de Video

## God Nodes (Núcleos funcionales)

### Core
- **video-processor**: Procesamiento de video (codec, resolución, trim)
- **timeline**: Gestión de pista temporal (tracks, clips, keyframes)
- **media-library**: Gestión de activos (videos, audios, imágenes)

### UI
- **editor-ui**: Canvas principal + timeline UI
- **properties-panel**: Inspector de propiedades de clips
- **effects-panel**: Efectos y transiciones

### Infrastructure
- **config**: Configuración global y preferencias
- **storage**: Gestión de proyectos (save/load)
- **plugins**: Sistema de extensiones

## Comunidades por área

```
Editor/
├── video-processor/
├── timeline/
├── media-library/
├── ui/
├── effects/
├── config/
├── storage/
└── plugins/
```

---
Actualizado: 2026-04-27
