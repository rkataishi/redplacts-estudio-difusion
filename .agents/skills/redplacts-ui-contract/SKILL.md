---
name: redplacts-ui-contract
description: Preserve Red PLACTS viewport expansion and the agreed visual identity when editing this repository's editor, posters, typography, photos or review controls.
---

# Contrato visual de Red PLACTS

Aplica sólo a `flyers_redplacts`. Leer antes de editar UI, estilos, renderizado,
pósters, fotos o sus controles. Una instrucción nueva del usuario prevalece.
Este contrato evita regresiones; no autoriza reformas adicionales ni push.

## Vista correcta y expandida

- La expansión se evalúa sobre el CONTENIDO visible, no sólo sobre el
  workspace, el frame o sus rectángulos DOM. Un contenedor de ancho completo
  con un póster diminuto, controles pequeños o grandes zonas desaprovechadas
  no cumple el pedido aunque los tests geométricos pasen.
- Desde 900 px, la app ocupa todo el ancho y alto del viewport: cabecera de
  60 px y workspace en el espacio restante. Sin `max-width` centrado ni
  mezcla de escritorio con las reglas antiguas de layout apilado.
- Editor izquierdo y preview derecho dentro de la pantalla. El formulario
  scrollea internamente; tabs, navegación y botón Generar permanecen accesibles.
  Escribir, subir/quitar imágenes, cambiar estilos y hacer scroll no mueve
  menús ni cambia accidentalmente la distribución de la UI.
- La preview ocupa el espacio restante después de sus controles, avisos y
  nueve miniaturas. En escritorio, el canvas ocupa TODO el ancho interior
  del frame conservando su proporción; si supera la altura, el frame tiene
  scroll vertical interno para llegar al footer. No reducirlo para encajarlo
  entero en altura ni reinstalar topes de 450/520/620 px. El editor, los
  controles y las miniaturas permanecen fijos al scrollear la pieza.
- Ajustar toda la pieza a la altura disponible NO es por sí solo el criterio
  de aceptación. Comparar visualmente escala, lectura y espacio aprovechado
  antes/después en la ventana real. Si el contenido sigue pequeño, resolver
  su escala y el reparto del área de edición sin deformar la pieza ni cambiar
  las dimensiones de exportación para disimular el problema.
- Avisos de contenido excedido no pueden colapsar la preview ni ocultar sus
  controles. El error debe ser consultable sin desplazar el workspace.
- El rectángulo DOM del canvas coincide con la pieza visible. No deformar
  su caja con `object-fit` ni desfasar coordenadas del selector local.
- Bajo 900 px, editor y preview se apilan con scroll normal de página.
  Ancho completo disponible, sin scroll horizontal ni controles recortados.
- Redimensionar vuelve a calcular el espacio disponible. No resolver un
  fallo de la app maximizando el navegador, reseteando zoom o emulando otra
  pantalla. Verificar también el tamaño y navegador donde falló el usuario.

El bloque responsive final de `index.html` es el punto de integración actual.
Revisar reglas anteriores y su especificidad, en especial 710, 899/900, 970,
1210 y 1650 px. `renderPreview` proporciona `--poster-ratio` real. Corregir
la regla conflictiva; no acumular otro bloque de overrides para ocultarla.

## Nueve pósters, sin jerarquía entre expositores

- Nueve variantes diferentes, cada una con composiciones explícitas para
  2, 3 (default) y 4 expositores. Cambiar la cantidad cambia el layout.
- Cards y fotos del mismo tamaño y tratamiento para todos los expositores.
  Reservar espacio según el texto visible; no imponer una fracción fija de foto.
  En 04/08, afiliaciones largas permiten filas horizontales iguales con aire.
  Títulos y grupos de nombres/afiliaciones centrados; enlace con cápsula,
  degradado y reproducción. Máscaras redondeadas, bisel oscuro y sombras sobre el marco visible de cada foto; variantes elevadas o clásicas. Sombras de separación bajo el header y sobre el footer.
  Los nueve diseños muestran las fotos cargadas; la preferencia antigua
  `socialPhotos` no puede ocultar los retratos de 04–09. No ofrecer el control
  de miniaturas de redes como si afectara a estas composiciones.
  Nunca expositor estrella, podio, escalones ni una card central elevada.
  Revisar especialmente 04, 07 y 08. 06 y 09 deben seguir siendo distintas.
- `insumos/inspiraciones poster` guía distribución, posiciones y proporciones,
  no colores. Mantener los assets y la paleta de Red PLACTS.
- Retratos sin cortar de más cabeza, frente o cabello, especialmente 01/04/08.
  Default actual `{x:50,y:20,zoom:1,fit:'contain'}` en `defaultPersonCrop`. La foto nueva se muestra completa; el control “Mostrar foto completa” permite
  volver al recorte. Preservar encuadres explícitos de proyectos; slider y render usan el mismo valor.
  No deducir que un encuadre está sin editar por un número como 50.
- Nombre centrado en su zona; segundo texto opcional para institución o
  especialidad; omitir las descripciones de investigación en todos los pósters. Moderación alineada a la izquierda, nombre y afiliación solamente. Actividad con título y subtítulo, sin tercera línea. Al faltar textos, recentrar el
  conjunto visible sin reservar huecos. Centrar el grupo verticalmente,
  no cada línea de forma independiente. No pegar nombres a la foto.
- 01: título grande sin quiebre forzado y mejor aprovechamiento de las cards.
  02: fotos grandes sobre nombres y afiliaciones para 2/3/4 expositores; EXPONEN cerca de las cards y textos centrados verticalmente.
  05: fotos amplias. 06: nombres legibles. 07: nombres centrados y moderación
  amplia en área, fuente y foto. 08: cards amplias y bloque de título ancho,
  centrado y bien distribuido. 09: título arriba o centrado, no abajo por defecto.
- Header: “Conversatorio” legible y “Encuentros virtuales de la Red PLACTS”.
  Fecha, hora y zona horaria centradas como grupo dentro de su box.
  Plataforma, acceso y enlace en su propia zona, sin choques ni quiebres absurdos.
- Footer de TODOS: logo original y URL visible `redplacts.org` a la izquierda,
  aire central, TODAS las redes concentradas a la derecha en dos renglones
  (nombre y handle). Nunca repartirlas a lo ancho de todo el footer.
  Instagram @redplacts; X @PlactsRed; Facebook @redplacts; YouTube @RedPLACTS.
  Esta regla reemplaza la antigua indicación de omitir la URL junto al logo.

## Legibilidad y edición

- El usuario pidió “lota”; hoy el código usa Lato. No declarar aprobada esa
  diferencia ni cambiarla silenciosamente al arreglar el viewport.
- Preservar la ampliación de textos pequeños, al menos cuatro puntos sobre
  el diseño antiguo. Baseline actual: escala 115%, mínimo técnico 17 px de
  canvas. Ese mínimo NO demuestra que el texto se lea en la preview.
- Evaluar proporciones, contraste y lectura en exportación y preview real:
  nombres, institución, fecha, moderación y footer. Si no caben, redistribuir
  el área o informar exceso; no recortar ni achicar hasta hacerlo ilegible.
- Sidebar: estilos vibrant, transparent y degrade (`gradient` en código);
  modos default, dark y accent; acentos de marca actuales `#009542`,
  `#0062ad`, `#8b4c78`. Mantener tamaños editables de todos los grupos de
  texto y recuadros, sin mover menús al activar opciones.

## Overlay de revisión, sólo local

- `.local-review/` sólo en localhost y excluido de producción y del push.
  No incluir comentarios, imágenes personales, mocks ni rutas privadas.
- Selección DOM de la app y selección semántica del póster RESULTANTE;
  permite comentar cada variante, no seleccionar imágenes de referencia.
  Cursor crosshair; seleccionar el póster no activa zoom ni lupa `+`.
- Conservar persistencia local de comentarios, selector de nueve variantes
  y botones para cargar/quitar caras, fondos y hero mockup de marzo2026.
  Minimizar el overlay para revisar la app, sin confundir superposición y layout.

## Verificación que obliga a mirar el resultado

Aplicar también la skill `ui-gui-visual-verification` para fixes y tareas de
interfaz. La inspección visual es una condición de cierre, no opcional.

1. Revisar Git root, status y diff. Preservar cambios ajenos y requisitos
   previos; no revertir una reforma para resolver otra.
2. Ejecutar `python3 tests/viewport_e2e.py` y `python3 tests/ui_smoke.py`.
   Si se toca render, textos, estilos, fotos o footer, ejecutar también
   `python3 tests/poster_layouts_e2e.py`.
3. Inspeccionar capturas y el localhost real: escritorio ancho, bajo,
   límites 899/900/970 y móvil; resize de ida y vuelta. Probar las nueve
   variantes, texto, fotos, opciones y scroll. Incluir avisos visibles y
   el proyecto actual, no sólo un ejemplo limpio en un navegador nuevo.
4. Si cambian composiciones: revisar 9 × 2/3/4, con/sin hero y textos
   opcionales. Evaluar tamaño igual, no podio, encuadre, centrado como
   grupo, proporciones, contraste, legibilidad y footer completo.
5. Un test verde ni un workspace de ancho completo sustituyen la inspección
   del contenido visible. Si la expansión sigue siendo insatisfactoria,
   la tarea sigue sin resolver. Si faltan permisos del
   navegador o no se reproduce el fallo, decirlo y pedir captura o tamaño
   exacto; no afirmar que quedó arreglado ni culpar al zoom sin evidencia.

Actualizar este contrato al cambiar un requisito, retirando la regla
contradictoria. No reconstruir las otras skills eliminadas sin pedido.
