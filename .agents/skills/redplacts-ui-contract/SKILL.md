---
name: redplacts-ui-contract
description: Preserve the approved Red PLACTS editor, responsive viewport behavior and nine adaptive poster identities when editing this repository's UI, styles, rendering or assets.
---

# Contrato visual de Red PLACTS

Aplica sólo a `flyers_redplacts`. Lee esta skill antes de modificar la UI,
los pósters, los estilos, las fotos o sus controles. Conserva las reformas
explícitas del usuario. Una nueva instrucción suya puede cambiar este contrato.
No uses este documento para implementar tareas adicionales sin pedido.

## Expansión al navegador

- Desde 900 px, la app ocupa todo el viewport. La cabecera mide 60 px y el
  workspace ocupa el ancho completo y la altura restante. No restaures un
  `max-width` centrado ni mezcles el layout apilado con el de escritorio.
- Editor izquierdo y preview derecho permanecen dentro del viewport. El
  formulario tiene scroll interno. Sus tabs y controles no se desplazan ni
  desaparecen al editar texto, cargar imágenes, cambiar estilos o hacer scroll.
- El área de preview usa todo el espacio disponible, sin el antiguo tope de
  620 px. El póster conserva su proporción y alcanza el mayor tamaño que cabe
  en el área restante, después de controles, avisos y nueve miniaturas.
  Espacio lateral por la proporción del póster es válido. Un límite fijo que
  impide crecer al redimensionar el navegador no lo es.
- El rectángulo DOM del canvas debe coincidir con la pieza visible. No hagas
  una caja deformada con `object-fit` que desplace las coordenadas del selector.
- Por debajo de 900 px, editor y preview se apilan y la página puede scrollear.
  No debe existir scroll horizontal ni controles fuera de pantalla.
- La expansión no depende de maximizar Chrome, resetear zoom ni emulación CDP.
  Ajustar el navegador no sustituye un arreglo de la app.

El bloque responsive final de `index.html` es el punto de integración actual.
Revisa reglas anteriores que puedan contradecirlo, especialmente 710, 900,
970, 1210 y 1650 px. `renderPreview` transmite la proporción real del póster
al frame. No añadas otro bloque de overrides para tapar una contradicción.

## Identidad y distribución de los pósters

- Son nueve variantes distintas. Cada una debe tener tres composiciones
  explícitas para 2, 3 y 4 expositores. Tres es el ejemplo predeterminado.
  Cambiar la cantidad cambia la distribución, no sólo escala el mismo diseño.
- Todos los expositores tienen igual tamaño de card y foto e igual tratamiento
  de texto. No hay expositor estrella. No escalones verticales, podios,
  card central elevada ni otra jerarquía visual. Revisa especialmente 04, 07 y 08.
- 06 y 09 no pueden volver a ser la misma composición.
- Las referencias del directorio `insumos/inspiraciones poster` orientan
  posiciones, proporciones y relaciones de texto y foto, no colores.
- Los retratos conservan frente y cabello. Revisa especialmente 01, 04 y 08.
  El default actual de retratos es `{x:50,y:20,zoom:1}`, centralizado en
  `defaultPersonCrop`. Conserva encuadres explícitos de proyectos existentes.
  El valor visible del slider es exactamente el usado por el render.
  No deduzcas “sin editar” de un valor numérico como 50.
- Nombres centrados en su zona. Pertenencia institucional o especialidad
  opcional debajo del nombre. Descripción breve opcional. Si falta un texto,
  el contenido restante se recentra sin conservar huecos vacíos.
- Todos los textos se centran verticalmente en su zona y según la alineación
  horizontal elegida para la composición. No centres cada línea ignorando el
  conjunto ni dejes nombres pegados al borde de la foto.
- 01 mantiene un título grande sin quiebre forzado y aprovecha el aire de las
  cards. 02 acerca EXPONEN a las cards, no a la cabecera. 05 mantiene fotos
  amplias. 06 mantiene nombres legibles. 07 mantiene moderación amplia en
  área, texto y foto. 08 permite cards más grandes y título ancho y centrado.
  09 sitúa su título arriba o centrado verticalmente, nunca al fondo por defecto.
- Cabecera con tipo “Conversatorio” legible y la serie “Encuentros virtuales
  de la Red PLACTS”. No reduzcas la serie hasta volverla decorativa ilegible.
- Fecha, hora y zona horaria forman un grupo ordenado y centrado en su box.
  Plataforma, acceso y URL usan su propia zona sin colisiones ni quiebres absurdos.
- Footer con el logo original, sin agregar un texto `redplacts.org` separado,
  aire y redes en dos renglones. Conserva Instagram @redplacts,
  X @PlactsRed, Facebook @redplacts y YouTube @RedPLACTS.

## Tipografía y estilos editables

- El usuario pidió “lota”. La implementación actual usa Lato, no Lota.
  No documentes esa diferencia como aprobada ni sustituyas silenciosamente
  la familia. Si el trabajo requiere resolverla, verifica el asset tipográfico
  real y aclara la diferencia. No cambies la fuente por un arreglo de viewport.
- Conserva la ampliación de textos pequeños, al menos cuatro puntos frente
  al diseño antiguo. Baseline actual de tests: escala general 115%, mínimo
  técnico 17 px en el canvas. Ese mínimo no prueba legibilidad visual.
- Evalúa texto a escala de exportación y en la preview real. Nombres,
  pertenencias, fecha, moderación y footer deben leerse sin zoom. Si no caben,
  redistribuye el área o reporta el contenido excedido. No recortes texto ni
  lo reduzcas silenciosamente hasta hacerlo ilegible.
- Mantén edición desde la sidebar por grupo de recuadros, estilos vibrant,
  transparent y degrade, y modos default, dark y accent. La implementación
  llama `gradient` al estilo degrade. Acentos actuales de marca
  `#009542`, `#0062ad`, `#8b4c78`. Conserva assets originales y contraste legible.
- Mantén escala general y tamaños editables de todos los grupos de texto.
  Cambiar un estilo no debe mover controles ni redistribuir la UI accidentalmente.

## Layer de revisión local

- `.local-review/` sólo funciona en localhost, no es producción y no se pushea.
  Mantén su exclusión local. Nunca incluyas comentarios, rutas privadas,
  imágenes personales o mocks en el bundle o commit de producción.
- El selector permite comentar elementos DOM de la UI y elementos semánticos
  del póster resultante, no seleccionar una imagen de referencia.
- Debe poder cambiar entre las nueve variantes. Seleccionar una zona del
  póster no abre el zoom. Conserva cursor crosshair, no lupa `+`.
- Comentarios persisten en el archivo local de revisión. Mantén los botones
  de cargar y quitar caras, background y hero mockup desde marzo2026.
- Minimiza el panel cuando bloquea la inspección visual. No confundas su
  superposición con un problema de dimensiones de la app.

## Puerta de verificación antes de entregar

1. Resuelve Git root y status. Conserva cambios ajenos. Revisa qué reforma
   previa puede romper el diff; no reviertas un requisito para arreglar otro.
2. Ejecuta `python3 tests/viewport_e2e.py`. Prueba tamaños reales, resize,
   límites responsive, las nueve variantes, proporción y ocupación máxima.
3. Ejecuta `python3 tests/ui_smoke.py`. Si cambias pósters, tipografía,
   estilos o encuadre, ejecuta también `python3 tests/poster_layouts_e2e.py`.
4. Usa browser-use sobre localhost para inspección visual. Comprueba desktop
   ancho, desktop bajo, límites 899/900/970 px y móvil. Cambia variantes,
   escribe texto, carga y quita imágenes, activa estilos y scrollea el formulario.
   La estabilidad y legibilidad se comprueban visualmente, no sólo con rectángulos.
5. Si cambias composiciones, revisa 9 variantes por 2/3/4 expositores,
   con y sin hero y textos opcionales relevantes. Mira cabezas, tamaños
   iguales, ausencia de podio, centrado de grupos, contraste y footer completo.
6. No declares verificado lo que no inspeccionaste. Un test verde no reemplaza
   la auditoría visual. Conserva capturas locales cuando aporten evidencia.
7. Haz commit/push sólo cuando el usuario lo pida. Añade rutas exactas,
   nunca `git add .`, y verifica sincronización con origin tras el push.

Esta skill preserva decisiones. El test ejecutable detecta regresiones de
viewport, pero ninguno garantiza por sí solo que toda edición futura sea correcta.
