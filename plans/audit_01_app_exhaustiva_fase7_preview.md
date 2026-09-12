# Fase 7: preview, toolbar, zoom y thumbnails

Estado: PENDIENTE

## Objetivo

Dar al poster el máximo espacio útil sin cortar su totalidad vertical ni desplazar herramientas o thumbnails.

## Recorrido

1. Abrir cada pieza desde selector y thumbnail.
2. Confirmar que `Vista previa` y el control de resolución comparten nivel vertical.
3. Medir espacio superior e inferior del preview y eliminar solamente aire sin función.
4. Comprobar ajuste completo de piezas verticales, horizontales y cuadradas.
5. Probar zoom mínimo, medio, máximo, reset y redimensionado del viewport.
6. Verificar que el poster completo puede verse o desplazarse de manera explícita, nunca cortado silenciosamente.
7. Confirmar que la tira de nueve thumbnails permanece visible/alcanzable y no se solapa.
8. Cambiar contenido, personas e imágenes con zoom activo y confirmar estabilidad.
9. Comparar canvas mostrado con PNG exportado.

## Criterios geométricos

Toolbar en una fila cuando haya ancho; preview centrado; canvas contenido dentro de su viewport; espacios superior/inferior mínimos y simétricos; thumbnails en flujo estable.

## Verificación

```sh
python3 tests/stage_controls_e2e.py
python3 tests/image_canvas_e2e.py
```

Esperado: totalidad del poster visible a escala de ajuste y herramientas estables. Falla: corte vertical, toolbar en dos niveles sin necesidad, salto de thumbnails o resolución desalineada.
