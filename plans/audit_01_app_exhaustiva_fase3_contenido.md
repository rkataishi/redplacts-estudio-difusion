# Fase 3: contenido, fecha, modalidad y validación

Estado: PENDIENTE

## Objetivo

Forzar todos los estados de entrada textual y comprobar representación, validación y recuperación.

## Recorrido

1. Probar título vacío, mínimo, realista, largo y con saltos.
2. Probar subtítulo/descripción vacíos, una línea y múltiples párrafos.
3. Probar fecha, hora, zona horaria y modalidad presencial/virtual/híbrida según controles disponibles.
4. Probar sede/enlace vacío, válido y excesivamente largo.
5. Probar caracteres acentuados, comillas, ampersand, guiones y URLs.
6. Pegar texto largo, deshacer manualmente y borrar todo.
7. Intentar compilar con faltantes y comprobar mensajes junto al control responsable.
8. Corregir cada error y comprobar que el mensaje desaparece sin residuos.
9. Alternar opciones que muestran/ocultan campos y comprobar que no quedan huecos ni valores fantasma.
10. Confirmar actualización del preview y de las nueve piezas sin redistribución arbitraria.

## Verificación

```sh
python3 tests/content_meeting_e2e.py
python3 tests/image_canvas_e2e.py
```

Esperado: validación específica, estado recuperable y texto legible. Falla: truncado sin intención, solapamiento, valor oculto que reaparece o preview desincronizado.
