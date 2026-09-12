# Fase 11: limpieza probada

Estado: COMPLETA

## Objetivo

Eliminar únicamente código muerto, duplicado o reemplazado que la evidencia estructural y runtime confirme como innecesario.

## Candidatos a investigar, no a borrar por anticipado

1. CSS anterior sobrescrito por reglas posteriores.
2. Estilos y DOM de diálogos retirados.
3. Toolbar anterior del preview.
4. Renderer social legado duplicado entre `index.html` y `designs.js`.
5. Listeners, selectores y ramas sin elementos/callers alcanzables.
6. Helpers y constantes sin uso.

## Método

1. Consultar símbolos/callers/dependencias con Codebase Memory.
2. Buscar referencias literales en HTML, JS y tests.
3. Forzar el recorrido que podría alcanzar el candidato.
4. Borrar el bloque mínimo sólo si no existe caller ni efecto observado.
5. Ejecutar prueba focal y luego suite completa.
6. Comparar capturas antes/después cuando el candidato afecte render.

## Verificación

```sh
rg -n "SELECTOR_O_SIMBOLO" index.html designs.js tests
git diff --check
for test in tests/*_e2e.py tests/ui_smoke.py; do python3 "$test"; done
```

Esperado: menos código sin cambio de conducta. Falla: eliminación basada sólo en intuición, compatibilidad especulativa o test roto.

## Resultado

- El índice estructural completo encontró 15 funciones exportadas/alcanzables en `designs.js`; no se borraron funciones ni el fallback legado.
- La búsqueda literal probó cinco familias CSS sin referencia en HTML, JavaScript o pruebas: `collection-nav`, `stage-toolbar`, `segmented`, `page-intro` y `local-state`.
- Se eliminaron solamente esas reglas y se repitieron las pruebas focales y la suite completa.
