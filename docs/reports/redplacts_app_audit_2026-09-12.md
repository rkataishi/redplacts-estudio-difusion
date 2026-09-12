# Informe de auditoría de Red PLACTS

Fecha: 2026-09-12
Plan: `plans/audit_01_app_exhaustiva.md`
Estado: EN EJECUCIÓN

## Resumen

Pendiente de la línea base actual. Este informe se completa durante el recorrido; no se reutilizan capturas de ejecuciones anteriores como evidencia visual.

## Entorno

- SHA inicial: `4fa2bbc`
- Navegador y versión: pendiente
- Sistema: macOS
- Servidor: `python3 -m http.server 8000 --bind 127.0.0.1`
- Viewports: 1920×1080, 1440×900, 1280×757, 768×1024, 390×844

## Estado por fase

| Paso | Descripción | Salud | Evidencia completa |
| --- | --- | --- | --- |
| 1 | Línea base | CON HALLAZGOS | `.audit/baseline/`, `.audit/measurements/baseline.json` |
| 2 | Editor, navegación, menús y scroll | PENDIENTE | `.audit/screenshots/phase02/` |
| 3 | Contenido | PENDIENTE | `.audit/screenshots/phase03/` |
| 4 | Personas | PENDIENTE | `.audit/screenshots/phase04/` |
| 5 | Imágenes | PENDIENTE | `.audit/screenshots/phase05/` |
| 6 | Bloques 04 y 05 | PENDIENTE | `.audit/screenshots/phase06/` |
| 7 | Preview | PENDIENTE | `.audit/screenshots/phase07/` |
| 8 | Nueve piezas | PENDIENTE | `.audit/screenshots/phase08/` |
| 9 | Proyectos, diálogos y exportación | PENDIENTE | `.audit/exports/` |
| 10 | Responsive y accesibilidad básica | PENDIENTE | `.audit/screenshots/phase10/` |
| 11 | Limpieza probada | PENDIENTE | `.audit/audit_01_decisions.tsv` |
| 12 | Validación final | PENDIENTE | `.audit/screenshots/final/` |

## Hallazgos

### A01-001 · Preview demasiado pequeño en escritorio bajo

- Estado: reproducido.
- Severidad: alta, visual.
- Evidencia: a 1280×757 el canvas visible mide 348 px de alto y deja 53 px antes de la vista general.
- Fuente probable: alturas y márgenes del bloque desktop en `index.html`.

### A01-002 · Fondo ignora la intensidad elegida

- Estado: reproducido visualmente y confirmado en fuente.
- Severidad: alta, visual.
- Evidencia: `drawBackground` fuerza un mínimo de 85% aunque el control expone 0–60% y el ejemplo usa 32%.
- Efecto: fondo dominante, contraste pobre y duplicación visual alrededor del hero.

### A01-003 · Piezas sociales desequilibradas

- Estado: reproducido con imágenes y retratos reales.
- Severidad: alta, visual.
- Evidencia: `.audit/baseline/posters/output-3.png` a `output-8.png`.
- Detalle: 06 deja un vacío superior dominante; 08 separa título y hero; 09 sobredimensiona el hero; 04/05/07 repiten casi la misma estructura.

### A01-004 · Metadatos de formatos sociales incorrectos

- Estado: confirmado en fuente.
- Severidad: media, comprensión.
- Evidencia: nombres/descripciones 04–09 anuncian proporciones distintas de sus dimensiones efectivas.

### A01-005 · Scroll de expositores informado previamente

- Estado: no reproducido en el punto de partida.
- Evidencia: con seis expositores el scroll recorre exactamente `0..1809`; el CTA permanece entre 645–689 px a 1280×757.

### A01-006 · Harness real antiguo

- Estado: fuera del producto.
- Evidencia: `.tmp-ux-review/real-audit/real_audit.py` genera y valida los nueve PNG pero luego busca el selector retirado `copy-caption`.
- Decisión: no modificar archivos preexistentes del usuario; usar las exportaciones válidas y las pruebas versionadas actuales.

## Limitaciones

La inspección visual y de teclado no constituye una certificación WCAG completa.
