# Fase 7: validación y limpieza

Estado: EN EJECUCIÓN, TERCERA REVISIÓN

## Objetivo

Probar el sistema completo, comparar contra el baseline y retirar sólo código demostrado como reemplazado.

## Trabajo

1. Capturar 27 estados posteriores con el mismo viewport y datos.
2. Inspeccionar cada comparación por variante.
3. Exportar nueve PNG y validar dimensiones y contenido.
4. Ejecutar las pruebas de layouts, controles, imágenes, descargas y flujo principal.
5. Revisar consola, foco, reflujo y zoom.
6. Medir la composición antes y después.
7. Buscar funciones o ramas ya inaccesibles y eliminarlas únicamente con evidencia.
8. Comprobar en los 27 estados que todas las cards de una composición comparten ancho y alto.
9. Comparar 06 y 09 con 2, 3 y 4 expositores y rechazar cualquier firma equivalente.
10. Activar el selector local, comprobar el cursor de selección y confirmar que vuelve a `zoom-in` al terminar.
11. Medir línea superior e inferior, tamaño, foto y tipografía de todas las cards en los 27 estados.
12. Probar los nueve cruces de estilo y modo de color, los tres acentos y los cuatro grupos editables.
13. Guardar y abrir un proyecto con ajustes no predeterminados.
14. Revisar la sidebar después de cambios consecutivos y scroll para detectar reflujo o menús rotos.
15. Capturar nueve variantes con tres expositores, con y sin descripciones.
16. Comprobar por geometría el centro vertical de cada grupo de textos.
17. Verificar proporción fotográfica de 05, nombres de 06, moderación de 07 y títulos de 08 y 09.
18. Inspeccionar header, footer y fecha/acceso en los nueve formatos.

## Cierre

Resultado esperado: 27 composiciones válidas, controles correctos, miniaturas completas, exportaciones reales y ninguna regresión. Cualquier resultado no inspeccionado es `INCONCLUSIVE`.

Resultado: 27 capturas posteriores y tres hojas comparativas inspeccionadas. Pasaron diez recorridos E2E, nueve PNG individuales, zoom, ZIP de doce archivos, imágenes, proyecto, diálogos, personas, controles y smoke test sin errores severos de consola.

Revisión 2026-09-14: Browser Use guardó e inspeccionó 27 capturas nuevas y tres hojas de nueve estados. Pasaron `poster_layouts_e2e.py`, `stage_controls_e2e.py`, `downloads_e2e.py`, `image_canvas_e2e.py` y `ui_smoke.py`. La revisión eliminó las recetas jerárquicas reemplazadas, un comentario redundante y una supresión amplia del test.

Segunda revisión 2026-09-14: Browser Use cargó los mockups locales y guardó `final-2-speakers-sheet.png`, `final-3-speakers-sheet.png` y `final-4-speakers-sheet.png`. Las 27 composiciones informaron `valid=true` y ninguna card de 2 o 3 expositores en 04, 05, 07 u 08 quedó elevada. La prueba principal exige fuentes de 17 px o más, cards iguales, filas regulares, nueve cruces de estilo y color, tres acentos y escalas propias en cuatro grupos. `project_actions_e2e.py` guardó y volvió a abrir un proyecto con escala general 125 % y título degradado con acento ciruela.
