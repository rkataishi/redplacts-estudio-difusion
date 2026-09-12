# Fase 4: expositores y moderación

Estado: COMPLETA

## Objetivo

Reproducir el crecimiento que rompe el sidebar y verificar altas, bajas, orden, fotografía y representación visual de personas.

## Recorrido

1. Agregar expositores uno por uno desde cero hasta el máximo que permita la UI.
2. En cada alta, verificar scroll al encabezado y al último control, posición del CTA y acceso a todas las opciones.
3. Editar nombre, rol y organización con longitudes mínima, realista y extrema.
4. Subir foto válida, reemplazarla, recortarla, cancelar el recorte y eliminarla.
5. Reordenar primera↔última y órdenes intermedios; comprobar preview y exportación.
6. Eliminar primera, media y última persona; confirmar que no quedan huecos o índices erróneos.
7. Repetir alta/edición/orden/baja para moderadores.
8. Vaciar una persona parcialmente y comprobar validación localizada.
9. Alternar entre bloques con varias tarjetas abiertas y cerradas.
10. Confirmar que no aparece el texto `3 expositores`.

## Verificación

```sh
python3 tests/people_controls_e2e.py
python3 tests/content_meeting_e2e.py
```

Esperado: orden y datos coherentes; todos los controles alcanzables. Falla: scroll corto, CTA desplazado, tarjeta inaccesible, hueco en poster o foto asociada a otra persona.

## Resultado

- Altas, máximo 6/6, orden, bajas y protección del último expositor quedaron verificadas; moderación alcanzó y liberó 2/2.
- Foto, recorte X/Y, zoom, activación por teclado y eliminación conservaron la persona correcta.
- La pieza 01 compacta seis personas sin pisar moderación; la pieza incompatible muestra un fallback explícito y limpio.
- `people_controls_e2e.py` terminó en código 0 y las nueve salidas máximas fueron abiertas e inspeccionadas.
