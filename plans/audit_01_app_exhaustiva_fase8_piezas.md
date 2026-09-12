# Fase 8: auditoría de las nueve piezas

Estado: PENDIENTE

## Objetivo

Evaluar cada composición a tamaño real con proyectos A, B y C, comparando jerarquía, equilibrio, hero, legibilidad y uso del espacio.

## Chequeos comunes 01–09

1. Logo/marca, título, hero, personas, moderación, fecha/reunión y pie aparecen cuando corresponde.
2. Ningún bloque se superpone, sale del canvas o queda ilegiblemente pequeño.
3. Textos largos reducen o reordenan de forma predecible, sin huecos arbitrarios.
4. Hero conserva proporción y punto focal razonable.
5. Componentes repetidos conservan ritmo y alineación.
6. Preview, thumbnail y PNG representan la misma composición.

## Chequeos específicos

- 01, 02, 08 y 09: rehacer una distribución inentendible o un uso incorrecto del hero dentro del marco; verificar lectura de arriba abajo.
- 04, 05 y 07: al distribuir horizontalmente, alinear el hero con el bloque de título y compartir ejes/altura visual.
- 04, 06 y 07: eliminar aire innecesario y redistribuir espacio equitativamente o ampliar componentes útiles.
- 03: control de equilibrio cuadrado y densidad con máximas personas.
- Todas: probar sin hero, con hero vertical, horizontal y cuadrado.

## Evidencia

Exportar las nueve piezas para B y C, crear una hoja de contacto solamente con herramientas ya disponibles y abrir cada PNG relevante a tamaño completo.

## Verificación

```sh
python3 tests/downloads_e2e.py
python3 tests/image_canvas_e2e.py
```

Esperado: nueve composiciones legibles y equilibradas. Falla: cualquier requisito explícito sin captura comparativa antes/después.
