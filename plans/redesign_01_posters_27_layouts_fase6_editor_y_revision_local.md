# Fase 6: editor y revisión local

Estado: EJECUTADA, PENDIENTE DE APROBACIÓN

## Objetivo

Resolver los dos comentarios del usuario y permitir comentarios asociados a una variante exacta.

## Trabajo

1. Añadir una acción persistente `Descargar PNG` junto a `Exportar los 9`.
2. Eliminar la acción duplicada bajo el canvas.
3. Quitar el título `Vista general`.
4. Distribuir las nueve miniaturas completas dentro de la altura recuperada.
5. Añadir botones 01–09 y selección de elementos internos del póster renderizado en `.local-review/overlay.js`.
6. Guardar `posterElement`, `posterRect`, `composition`, `variantIndex`, `variantName` y `speakerCount` con cada comentario.
7. Cambiar el ejemplo local automático de seis a tres expositores.
8. Reemplazar el cursor `zoom-in` por un cursor de selección mientras está activo el selector de elementos internos del póster.
9. Convertir el paso 03 en `Diseño` y mantener allí las imágenes existentes.
10. Añadir fuente y escala general, con `Lato` y 115 % como valores iniciales.
11. Añadir un editor por grupo para título, expositores, moderación y fecha/acceso.
12. Ofrecer tres estilos, tres modos de color, tres acentos fijos y escala tipográfica por grupo.
13. Añadir pertenencia institucional o especialidad a cada expositor y moderador.
14. Mantener el orden nombre, pertenencia y descripción en formulario, proyecto y canvas.

## Verificación

Seleccionar las nueve variantes desde el layer y desde la app, guardar un comentario y comprobar el JSON. Verificar por teclado la selección y ambas acciones de exportación. Inspeccionar que las nueve miniaturas estén completas a 1440 × 790.

Resultado: selector 01–09 probado desde el layer. Una selección real sobre el título resaltó sólo su caja de 972 × 100 px dentro del póster y el comentario temporal confirmó elemento, coordenadas, composición y variante; después fue retirado sin tocar los dos comentarios del usuario. Las nueve miniaturas quedan dentro de una banda de 64 px y ambos botones de exportación están visibles y contiguos.

Revisión 2026-09-14: el selector interno mostró `crosshair` mientras estuvo activo y recuperó `zoom-in` al seleccionar o cancelar con Escape. Los fallos de inicio del selector ahora aparecen en el estado del layer.

Segunda revisión 2026-09-14: el paso 03 muestra `Lato`, escala general de 115 %, selector de grupo, tres estilos, tres modos de color, tres acentos y escala por recuadro. `stage_controls_e2e.py` cambió expositores a degradado, acento ciruela y 140 %, confirmó el estado y mantuvo las nueve variantes válidas.
