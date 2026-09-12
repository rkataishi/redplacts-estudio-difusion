# Fase 10: responsive, teclado y accesibilidad básica

Estado: COMPLETA

## Objetivo

Confirmar que el editor y sus recorridos esenciales siguen utilizables con distintos tamaños, zoom del navegador y teclado.

## Recorrido

1. Ejecutar proyectos vacío, B y C en 1920×1080, 1440×900, 1280×757, 768×1024 y 390×844.
2. Probar zoom del navegador 80%, 100%, 125% y 200% en el recorrido principal.
3. Tabular desde inicio hasta CTA; verificar orden, foco visible y ausencia de trampas.
4. Activar botones, acordeones, selectores y diálogos con teclado.
5. Cerrar diálogos con Escape y comprobar restauración del foco.
6. Revisar labels, nombres accesibles, estados disabled y mensajes de error asociados.
7. Revisar contraste visual evidente sin declarar conformidad WCAG completa.
8. Forzar scroll de página, sidebar, diálogo y tira de thumbnails por separado.
9. Confirmar ausencia de scroll horizontal accidental y contenido cortado.
10. Revisar orientación portrait/landscape en tablet y móvil.

## Verificación

```sh
python3 tests/ui_smoke.py
python3 tests/dialogs_e2e.py
```

Esperado: tarea central realizable en todos los viewports. Falla: control inaccesible, foco perdido, scroll atrapado o reflow que oculta acciones.

## Resultado

- Se inspeccionaron 1920×1080, 1440×900, 1280×757, 768×1024 y 390×844, más móvil horizontal 844×390.
- Los atajos de zoom nativo fueron ignorados por WebDriver; se verificaron tamaños físicos equivalentes a 80%, 125% y 200%.
- No hay overflow horizontal; foco, teclado, disabled, Escape y navegación por pestañas quedaron cubiertos por los E2E.
- Esta fase verifica accesibilidad básica y no declara conformidad WCAG.
