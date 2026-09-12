# Fase 1: línea base reproducible

Estado: COMPLETA

## Objetivo

Congelar evidencia funcional, visual y de rendimiento de la versión `4fa2bbc` antes de cualquier cambio de producto.

## Recorrido

1. Confirmar Git root, rama, SHA, upstream y archivos preexistentes.
2. Iniciar el servidor y comprobar HTML, `designs.js`, fuentes e imágenes.
3. Abrir una sesión nueva en navegador integrado y vaciar solamente el estado de la app usado por la auditoría.
4. Capturar editor vacío en los cinco viewports de la matriz.
5. Ejecutar los nueve recorridos E2E existentes y `ui_smoke.py` sin editar código.
6. Cargar el proyecto demo y capturar las cinco secciones laterales, preview y tira de nueve thumbnails.
7. Registrar alturas, scrollTop/scrollHeight/clientHeight, bounding boxes del sidebar, CTA, toolbar, preview y thumbnails.
8. Registrar errores de consola, requests fallidos y duración total.

## Comandos

```sh
curl -fsSI http://127.0.0.1:8000/
for test in tests/*_e2e.py tests/ui_smoke.py; do python3 "$test"; done
```

Esperado: HTTP 200; inventario exacto de aprobados/fallidos; capturas abiertas e inspeccionadas. Falla: cualquier estado sin evidencia, screenshot no revisada o edición previa al cierre.

## Salida

`.audit/baseline/`, `.audit/measurements/baseline.json` y filas de veredicto en el TSV.

## Gate

No comenzar correcciones hasta distinguir fallos reproducidos de observaciones estéticas no demostradas.

## Resultado

- Suite actual: nueve recorridos en código 0.
- Evidencia: 17 capturas del editor y 9 PNG con imágenes reales, todos abiertos e inspeccionados.
- Scroll con seis expositores: extremos `0/1809` alcanzables y CTA estable.
- Defecto reproducido: preview de 348 px de alto a 1280×757 y 53 px reservados antes de la vista general.
- Defectos reproducidos en piezas: 06, 08 y 09 con distribución vertical desequilibrada; 04, 05 y 07 sin diferenciación suficiente; fondo excesivamente dominante.
- Limitación: CUA no ofreció navegador integrado ni Chrome administrado; se usó el Chrome/Selenium ya incluido por el proyecto.
