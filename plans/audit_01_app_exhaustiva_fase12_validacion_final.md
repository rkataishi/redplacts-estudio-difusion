# Fase 12: validación final y cierre

Estado: COMPLETA, PENDIENTE DE GRADUACIÓN

## Objetivo

Probar desde cero que el estado final satisface cada requisito explícito y que no se introdujeron regresiones.

## Recorrido final

1. Sesión limpia y servidor reiniciado desde el worktree final.
2. Repetir proyectos A–E sin reutilizar estado de la línea base.
3. Recorrer los cinco bloques y todos sus controles.
4. Repetir alta masiva de expositores y confirmar scroll/CTA/opciones.
5. Repetir hero/fondo/crops y revisar las nueve piezas.
6. Exportar nueve PNG, ZIP, TXT y proyecto; verificar round-trip.
7. Repetir matriz completa de viewports y teclado.
8. Abrir e inspeccionar todas las capturas finales críticas.
9. Ejecutar suite completa y registrar duración.
10. Revisar consola, requests, diff, status, archivos grandes y residuos.
11. Contrastar requisito por requisito con evidencia autoritativa.
12. Actualizar informe, plan, fases y TSV; no graduar sin aprobación del usuario.

## Comandos de cierre

```sh
curl -fsSI http://127.0.0.1:8000/
for test in tests/*_e2e.py tests/ui_smoke.py; do python3 "$test"; done
git diff --check
git status --short
git diff --stat
```

Esperado: HTTP 200, suite completa en 0, exportaciones válidas, consola limpia y solamente cambios auditados. Falla: cualquier requisito sin evidencia directa o estado `INCONCLUSIVE` no resuelto.

## Gate final

Solicitar aprobación para renombrar/archivar el plan como terminado. Push y publicación requieren autorización separada.

## Resultado

- Suite final: 9/9 scripts en código 0, sin errores graves de consola.
- Recorrido final: cinco bloques, seis expositores, imágenes/crops, nueve piezas, diálogos, proyecto y descargas reales.
- Matriz final: 17 capturas del editor, nueve salidas con hero y nueve salidas máximas sin hero inspeccionadas.
- La graduación/archivo queda abierta para aprobación del usuario; no se hizo push ni publicación.
