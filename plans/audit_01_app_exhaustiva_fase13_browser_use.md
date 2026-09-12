# Fase 13: revalidación con Browser Use

Estado: VERIFICADA
Dependencia: fases 1 a 12 completas

## Objetivo

Repetir la auditoría sobre la aplicación real con un navegador controlado mediante la skill `browser-use`, cubrir los estados interactivos y visuales que pueden redistribuir el editor o los pósters, y cerrar cualquier defecto nuevo con reproducción, corrección mínima y prueba de regresión.

## Inventario de recorrido

1. Abrir la aplicación desde un perfil de Chrome aislado y confirmar carga completa, recursos y estado inicial.
2. Abrir, recorrer y llevar hasta su máximo scroll las cinco pantallas del editor: Contenido, Participantes, Imágenes, Reunión y Compartir.
3. Comprobar que tabs, encabezado, pie del editor y acciones permanecen accesibles al cambiar de pantalla y al llegar a ambos extremos del scroll.
4. Cargar el ejemplo de seis participantes mediante sus diálogos de confirmación.
5. Llevar Participantes a la densidad máxima de seis expositores y dos moderadores.
6. Introducir nombres y descripciones extensos dentro de los límites admitidos y comprobar que el formulario conserva tamaño, posición y navegación.
7. Cargar imagen de fondo e imagen principal reales; comprobar nombre, dimensiones, estado de carga y actualización del preview.
8. Cambiar entre las nueve variantes y capturar cada resultado a 1280×900.
9. Ampliar las variantes dudosas para juzgar solapamientos, recortes, jerarquía y legibilidad sobre el canvas real.
10. Repetir la inspección de menús, diálogos, selector de formato, selector de resolución, ampliación y acciones de proyecto/exportación cubiertas por la suite E2E.
11. Repetir un viewport móvil de 390×844, incluyendo navegación, scroll y acceso a controles.
12. Revisar errores de consola y el estado final de los nueve planes compilados.

## Hallazgo reproducido

`A01-009`: la variante 02, Poster panorámica, coloca los dos moderadores en una columna pero el renderer ignora el desplazamiento vertical calculado para el segundo. Avatar, nombre y descripción se superponen.

Evidencia previa: `.audit/browser-use-2026-09-12/23-variant-02-expanded.png`.

## Corrección autorizada

1. Consumir `item.y` en `drawModerators` de `designs.js`, que es el renderer activo de la variante panorámica.
2. No modificar el algoritmo de layout, límites, estilos ni variantes que ya pasan la inspección.
3. Añadir una sola aserción observable al recorrido E2E existente de Participantes: los dos bloques de moderación de la panorámica deben ocupar bandas verticales distintas y no solapadas.

## Verificación

```sh
python3 tests/people_controls_e2e.py
for test in tests/*_e2e.py tests/ui_smoke.py; do python3 "$test"; done
git diff --check
```

Resultado esperado: prueba focal y suite completa en código 0; la captura posterior de variante 02 muestra dos moderadores separados; las otras ocho variantes, menús y scrolls permanecen estables; no aparecen errores graves de consola.

## Cierre

- [x] Recorrido inicial de las cinco pantallas y sus scrolls.
- [x] Densidad máxima, textos e imágenes.
- [x] Inspección de las nueve variantes.
- [x] Defecto `A01-009` reproducido y causa localizada.
- [x] Corrección mínima.
- [x] Prueba focal: separación `603 < 728`, sin issues en la panorámica.
- [x] Captura posterior equivalente: `.audit/browser-use-2026-09-12/28-variant-02-expanded-final.png`.
- [x] Suite completa 9/9, `git diff --check` y móvil 390×844 sin overflow horizontal.
