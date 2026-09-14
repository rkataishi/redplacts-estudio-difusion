# Fase 7: validación y limpieza

Estado: EN REVISIÓN

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

## Cierre

Resultado esperado: 27 composiciones válidas, controles correctos, miniaturas completas, exportaciones reales y ninguna regresión. Cualquier resultado no inspeccionado es `INCONCLUSIVE`.

Resultado: 27 capturas posteriores y tres hojas comparativas inspeccionadas. Pasaron diez recorridos E2E, nueve PNG individuales, zoom, ZIP de doce archivos, imágenes, proyecto, diálogos, personas, controles y smoke test sin errores severos de consola.
