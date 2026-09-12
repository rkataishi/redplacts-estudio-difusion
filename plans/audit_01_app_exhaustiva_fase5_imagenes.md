# Fase 5: fondo, hero, logo, carga y recorte

Estado: PENDIENTE

## Objetivo

Validar el ciclo completo de archivos e imágenes y su uso consistente en editor y exportaciones.

## Recorrido

1. Cargar cada asset incluido en `insumos/` sin modificarlo.
2. Probar JPG/PNG/WebP válidos y archivo inválido, grande o cancelado.
3. Cargar, reemplazar, recortar y eliminar fondo y hero.
4. Probar posiciones y escalas extremas del recorte; cerrar con escape y con controles visibles.
5. Cambiar opacidad y comprobar valor mínimo, medio y máximo.
6. Verificar que la misma transformación aparece en preview, thumbnails y PNG.
7. Confirmar que un error no borra el asset válido anterior.
8. Cambiar de sección y guardar/cargar proyecto con crops activos.
9. Medir alineación del hero con el bloque de título en 04, 05 y 07.
10. Revisar uso del hero dentro del marco de 01, 02, 08 y 09.

## Verificación

```sh
python3 tests/asset_controls_e2e.py
python3 tests/image_canvas_e2e.py
```

Esperado: preview y export idénticos en contenido/recorte; errores recuperables. Falla: deformación, recorte divergente, desalineación o asset anterior perdido.
