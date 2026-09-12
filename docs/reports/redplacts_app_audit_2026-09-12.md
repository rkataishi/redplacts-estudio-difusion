# Informe de auditoría de Red PLACTS

Fecha: 2026-09-12
Plan: `plans/done/audit_01_app_exhaustiva.md`
Estado: AUDITORÍA GRADUADA

## Resumen

Se completó el recorrido funcional y visual de los cinco bloques, los diálogos, los estados de carga y recorte, las nueve piezas y las exportaciones. Una segunda pasada con Browser Use recorrió pantallas, scrolls, densidad máxima, textos, imágenes, diálogos y móvil. La suite final terminó 9/9 en código 0, sin errores graves de consola. Se corrigieron los defectos reproducidos de preview, opacidad, densidad de personas, fallback, composición de hero y moderación panorámica; no se modificaron los materiales no versionados del usuario.

## Entorno

- SHA inicial: `4fa2bbc`
- Navegador: Chrome mediante Selenium y Browser Use 0.1.13 sobre un perfil aislado
- Sistema: macOS
- Servidor: `python3 -m http.server 8000 --bind 127.0.0.1`
- Viewports: 1920×1080, 1440×900, 1280×757, 768×1024, 390×844

## Estado por fase

| Paso | Descripción | Salud | Evidencia completa |
| --- | --- | --- | --- |
| 1 | Línea base | CON HALLAZGOS | `.audit/baseline/`, `.audit/measurements/baseline.json` |
| 2 | Editor, navegación, menús y scroll | VERIFICADA | `tests/ui_smoke.py`, `tests/stage_controls_e2e.py` |
| 3 | Contenido | VERIFICADA | `tests/content_meeting_e2e.py`, `tests/image_canvas_e2e.py` |
| 4 | Personas | VERIFICADA | `tests/people_controls_e2e.py`, `.audit/screenshots/phase08/max-output-*.png` |
| 5 | Imágenes | VERIFICADA | `tests/asset_controls_e2e.py`, `tests/downloads_e2e.py` |
| 6 | Bloques 04 y 05 | VERIFICADA | `tests/stage_controls_e2e.py`, `tests/downloads_e2e.py` |
| 7 | Preview | VERIFICADA | `.audit/screenshots/phase07/`, `.audit/measurements/screenshots/final.json` |
| 8 | Nueve piezas | VERIFICADA | `.audit/baseline/posters/`, `.audit/screenshots/phase08/` |
| 9 | Proyectos, diálogos y exportación | VERIFICADA | `tests/project_actions_e2e.py`, `tests/dialogs_e2e.py`, `tests/downloads_e2e.py` |
| 10 | Responsive y accesibilidad básica | VERIFICADA | `.audit/screenshots/phase10/`, `.audit/screenshots/final/` |
| 11 | Limpieza probada | VERIFICADA | `.audit/audit_01_decisions.tsv` |
| 12 | Validación final | VERIFICADA | suite final 9/9, `.audit/screenshots/final/` |
| 13 | Revalidación con Browser Use | VERIFICADA | `.audit/browser-use-2026-09-12/`, `tests/people_controls_e2e.py` |

## Hallazgos

### A01-001 · Preview demasiado pequeño en escritorio bajo

- Estado: resuelto y verificado.
- Severidad: alta, visual.
- Evidencia: a 1280×757 el canvas visible mide 348 px de alto y deja 53 px antes de la vista general.
- Resultado: 398 px a 1280×757 y 721 px a 1920×1080; canvas y vista general permanecen dentro del viewport.

### A01-002 · Fondo ignora la intensidad elegida

- Estado: resuelto y verificado.
- Severidad: alta, visual.
- Evidencia: `drawBackground` fuerza un mínimo de 85% aunque el control expone 0–60% y el ejemplo usa 32%.
- Resultado: el renderer respeta el rango real 0–60%; las exportaciones detectan el fondo al 55% sin exigir rojo puro.

### A01-003 · Piezas sociales desequilibradas

- Estado: resuelto y verificado.
- Severidad: alta, visual.
- Evidencia: `.audit/baseline/posters/output-3.png` a `output-8.png`.
- Resultado: 04/05/07 alinean título y hero; 06/08/09 redistribuyen título, hero y paneles; las variantes sin hero centran el contenido y la densidad máxima no solapa personas.

### A01-004 · Metadatos de formatos sociales incorrectos

- Estado: resuelto y verificado.
- Severidad: media, comprensión.
- Resultado: nombres, descripciones y dimensiones efectivas coinciden en la UI y en las nueve exportaciones.

### A01-005 · Scroll de expositores informado previamente

- Estado: no reproducido en el punto de partida.
- Evidencia: con seis expositores el scroll recorre exactamente `0..1809`; el CTA permanece entre 645–689 px a 1280×757.

### A01-006 · Harness real antiguo

- Estado: fuera del producto.
- Evidencia: `.tmp-ux-review/real-audit/real_audit.py` genera y valida los nueve PNG pero luego busca el selector retirado `copy-caption`.
- Decisión: no modificar archivos preexistentes del usuario; usar las exportaciones válidas y las pruebas versionadas actuales.

### A01-007 · Preview cortado en zoom equivalente y móvil horizontal

- Estado: resuelto y verificado.
- Severidad: alta, visual.
- Evidencia: a 1024×606 el mínimo de altura ocultaba el poster tras las miniaturas; a 844×390 el máximo global lo reducía a 72×90 px.
- Resultado: desktop puede reducir el frame sin superposición; móvil conserva el poster completo y usa scroll explícito.

### A01-008 · Densidad máxima y fallback superpuestos

- Estado: resuelto y verificado.
- Severidad: alta, visual.
- Evidencia: proyecto C con seis expositores en las nueve salidas.
- Resultado: 01 compacta nombres y retratos; 03 conserva un aviso explícito sin solapar logo ni mensaje; las otras ocho piezas mantienen personas, moderación y footer dentro del canvas.

### A01-009 · Moderadores superpuestos en Poster panorámica

- Estado: resuelto y verificado.
- Severidad: alta, visual y de exportación.
- Evidencia previa: `.audit/browser-use-2026-09-12/23-variant-02-expanded.png`.
- Causa: el layout calculaba `item.y` para cada moderador, pero el renderer usaba una coordenada vertical fija.
- Resultado: el primer bloque termina en `603` y el segundo comienza en `728`; el rótulo usa los 314 px reales de su columna; la pieza no informa issues y vuelve a poder descargarse.
- Evidencia posterior: `.audit/browser-use-2026-09-12/28-variant-02-expanded-final.png` y `.audit/browser-use-2026-09-12/30-mobile-main-390x844-final.png`.

## Limpieza

Se eliminaron cinco familias CSS sin referencias en HTML, JavaScript ni pruebas: `collection-nav`, `stage-toolbar`, `segmented`, `page-intro` y `local-state`. El análisis estructural confirmó que las 15 funciones de `designs.js`, incluido el fallback legado, siguen siendo alcanzables; se conservaron.

## Cierre

- Suite funcional posterior al último cambio: 9/9 scripts en código 0.
- Exportación: 9 PNG individuales, ZIP con 12 entradas, proyecto JSON y texto TXT verificados.
- Geometría: cinco viewports, móvil horizontal 844×390 y equivalentes físicos de zoom 80%, 125% y 200%.
- Consola: sin errores `SEVERE` durante los recorridos.
- Alcance Git: cambios limitados a renderer, estilos, harness de captura, aserción de exportación y documentación del plan.

## Limitaciones

La inspección visual y de teclado no constituye una certificación WCAG completa. WebDriver no aplicó los atajos de zoom nativo de Chrome; se probaron tamaños físicos equivalentes (1600×946, 1024×606 y 640×379) y se añadió además 844×390 en orientación horizontal.
